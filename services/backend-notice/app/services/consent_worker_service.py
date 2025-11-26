import asyncio
import json
from datetime import datetime, UTC
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId
import aio_pika

from app.db.rabbitmq import publish_message
from app.core.logger import get_logger
from app.core.config import settings

import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

logger = get_logger("service.consent_worker_service")


def canonical_ts(value=None) -> str:
    """
    Produce a canonical ISO-8601 timestamp string with timezone.
    - Accepts: None, str, or datetime
    - Always returns: 'YYYY-MM-DDTHH:MM:SS.ssssss+00:00' style
    """
    if isinstance(value, str):

        value = value.replace(" ", "T").replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(value)
        except Exception:
            dt = datetime.now(UTC)
    elif isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.now(UTC)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.isoformat()


class ConsentWorkerService:
    def __init__(self, gdb: AsyncIOMotorDatabase, channel: aio_pika.Channel):
        self.gdb = gdb
        self.channel = channel

    async def _prepare_secure_audit_entry(self, entry: dict) -> dict:
        chain_key = f"{entry['dp_id']}:{entry['df_id']}:{entry['cp_id']}:{entry['agreement_id']}"

        while True:
            try:
                await self.gdb.consent_chain_locks.insert_one({"_id": chain_key, "locked_at": datetime.now(UTC)})
                break
            except Exception:
                await asyncio.sleep(0.02)

        try:

            clean = entry.copy()
            for f in [
                "_id",
                "canonical_record",
                "data_hash",
                "prev_record_hash",
                "record_hash",
                "signature",
                "signed_with_key_id",
            ]:
                clean.pop(f, None)

            canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
            entry["canonical_record"] = canonical

            data_hash = hashlib.sha256(canonical.encode()).hexdigest()
            entry["data_hash"] = data_hash

            prev = await self.gdb.consent_audit_logs.find_one(
                {
                    "dp_id": entry["dp_id"],
                    "df_id": entry["df_id"],
                    "cp_id": entry["cp_id"],
                    "agreement_id": entry["agreement_id"],
                },
                sort=[("timestamp", -1), ("_id", -1)],
            )

            prev_hash = prev["record_hash"] if prev else None
            entry["prev_record_hash"] = prev_hash

            ts = canonical_ts(entry.get("timestamp"))
            entry["timestamp"] = ts

            base_string = (prev_hash or "") + data_hash + ts
            record_hash = hashlib.sha256(base_string.encode()).hexdigest()
            entry["record_hash"] = record_hash

            entry["signature"] = self._sign(record_hash)
            entry["signed_with_key_id"] = getattr(settings, "SIGNING_KEY_ID", "cm-key-2025-01")

            return entry
        finally:
            await self.gdb.consent_chain_locks.delete_one({"_id": chain_key})

    def _sign(self, record_hash: str) -> str:
        """
        Sign the record_hash using ECDSA private key from settings.PRIVATE_KEY_PEM.
        Returns base64-encoded signature.
        """
        private_pem = settings.PRIVATE_KEY_PEM.encode("utf-8")
        private_key = serialization.load_pem_private_key(private_pem, password=None)

        sig = private_key.sign(
            record_hash.encode("utf-8"),
            ec.ECDSA(hashes.SHA256()),
        )
        return base64.b64encode(sig).decode("ascii")

    def _extract_flattened_purposes(self, data_elements_consents: list) -> list:
        purposes_list = []
        seen = set()
        for element in data_elements_consents:
            de_base = {
                "de_id": element.get("de_id"),
                "de_hash_id": element.get("de_hash_id"),
                "title": element.get("title"),
                "data_retention_period": element.get("data_retention_period"),
            }
            for consent in element.get("consents", []):
                unique_key = f"{de_base['de_id']}_{consent.get('purpose_id')}"
                if unique_key in seen:
                    continue
                seen.add(unique_key)
                flattened = {**de_base, **consent}
                purposes_list.append(flattened)
        return purposes_list

    async def _publish_initial_consent_events(self, full_consent_artifact: dict, dp_id: str, df_id: str, channel: aio_pika.Channel):
        data_elements_consents = full_consent_artifact["artifact"]["consent_scope"]["data_elements"]
        collection_point_name = full_consent_artifact["artifact"]["cp_name"]
        timestamp = canonical_ts()

        purposes_list = self._extract_flattened_purposes(data_elements_consents)

        approved_purposes = [p for p in purposes_list if p.get("consent_status") == "approved"]
        denied_purposes = [p for p in purposes_list if p.get("consent_status") == "denied"]

        if approved_purposes:
            message_to_publish_granted = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_name": collection_point_name,
                "event_type": "consent_granted",
                "timestamp": timestamp,
                "purposes": approved_purposes,
            }
            await publish_message("consent_events_q", json.dumps(message_to_publish_granted), channel=channel)

        if denied_purposes:
            message_to_publish_withdrawn = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_name": collection_point_name,
                "event_type": "consent_withdrawn",
                "timestamp": timestamp,
                "purposes": denied_purposes,
            }
            await publish_message("consent_events_q", json.dumps(message_to_publish_withdrawn), channel=channel)

    async def _compare_and_publish_consent_changes(self, old_artifact: dict, new_artifact: dict, dp_id: str, df_id: str, channel: aio_pika.Channel):
        old_flattened_purposes = self._extract_flattened_purposes(old_artifact["artifact"]["consent_scope"]["data_elements"])
        new_flattened_purposes = self._extract_flattened_purposes(new_artifact["artifact"]["consent_scope"]["data_elements"])

        old_consents_map = {f"{p['de_id']}_{p['purpose_id']}": p["consent_status"] for p in old_flattened_purposes}
        new_consents_map = {f"{p['de_id']}_{p['purpose_id']}": p["consent_status"] for p in new_flattened_purposes}

        new_purposes_map_full = {f"{p['de_id']}_{p['purpose_id']}": p for p in new_flattened_purposes}

        cp_name = new_artifact["artifact"]["cp_name"]
        timestamp = canonical_ts()

        changed_granted_purposes = []
        changed_withdrawn_purposes = []

        for key, new_status in new_consents_map.items():
            old_status = old_consents_map.get(key)
            if new_status != old_status:
                purpose_obj = new_purposes_map_full.get(key)
                if purpose_obj:
                    if new_status == "approved":
                        changed_granted_purposes.append(purpose_obj)
                    elif new_status == "denied":
                        changed_withdrawn_purposes.append(purpose_obj)

        if changed_granted_purposes:
            message_to_publish_granted = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_name": cp_name,
                "event_type": "consent_granted",
                "timestamp": timestamp,
                "purposes": changed_granted_purposes,
            }
            await publish_message("consent_events_q", json.dumps(message_to_publish_granted), channel=channel)

        if changed_withdrawn_purposes:
            message_to_publish_withdrawn = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_name": cp_name,
                "event_type": "consent_withdrawn",
                "timestamp": timestamp,
                "purposes": changed_withdrawn_purposes,
            }
            await publish_message("consent_events_q", json.dumps(message_to_publish_withdrawn), channel=channel)

    async def process_consent_submission(self, payload: dict):
        full_consent_artifact = payload["consent_artifact"]

        agreement_id = full_consent_artifact["artifact"]["agreement_id"]
        dp_id = full_consent_artifact["artifact"]["data_principal"]["dp_id"]
        df_id = full_consent_artifact["artifact"]["data_fiduciary"]["df_id"]
        cp_id = full_consent_artifact["artifact"]["cp_id"]
        timestamp = canonical_ts(payload.get("timestamp"))

        existing_artifact = await self.gdb.consent_latest_artifacts.find_one(
            {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                "agreement_id": agreement_id,
            }
        )

        if existing_artifact:

            new_version = existing_artifact.get("version", 0) + 1
            operation = "update"

            artifact_to_spread = full_consent_artifact.copy()
            artifact_to_spread.pop("_id", None)
            artifact_to_spread.pop("version", None)
            artifact_to_spread.pop("operation", None)

            update_fields = {
                "timestamp": timestamp,
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                **artifact_to_spread,
                "version": new_version,
            }

            await self.gdb.consent_latest_artifacts.update_one(
                {"dp_id": dp_id, "df_id": df_id, "cp_id": cp_id, "agreement_id": agreement_id},
                {"$set": update_fields},
            )

            await self._compare_and_publish_consent_changes(existing_artifact, full_consent_artifact, dp_id, df_id, self.channel)
        else:

            new_version = 1
            operation = "insert"

            artifact_to_spread = full_consent_artifact.copy()
            artifact_to_spread.pop("_id", None)
            artifact_to_spread.pop("version", None)
            artifact_to_spread.pop("operation", None)

            latest_artifact_entry = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                "agreement_id": agreement_id,
                "timestamp": timestamp,
                **artifact_to_spread,
                "version": new_version,
            }
            await self.gdb.consent_latest_artifacts.insert_one(latest_artifact_entry)

            await self._publish_initial_consent_events(full_consent_artifact, dp_id, df_id, self.channel)

        audit_log_entry = {
            "dp_id": dp_id,
            "df_id": df_id,
            "cp_id": cp_id,
            "agreement_id": agreement_id,
            "timestamp": timestamp,
            **full_consent_artifact.copy(),
            "version": new_version,
            "operation": operation,
        }
        audit_log_entry.pop("_id", None)

        audit_log_entry = await self._prepare_secure_audit_entry(audit_log_entry)
        await self.gdb.consent_audit_logs.insert_one(audit_log_entry)

        logger.info(f"Processed consent for agreement_id: {agreement_id}", extra={"agreement_id": agreement_id})

    async def process_consent_expiry_event(self, consent_artifact_id: str, data_element_id: str, purpose_id: str, expiry_at: str):
        """
        Processes a consent expiry event by atomically updating the consent status to 'expired'
        and publishing a consent_withdrawn event.
        """
        logger.info(
            f"Processing expiry for artifact_id: {consent_artifact_id}, de_id: {data_element_id}, purpose_id: {purpose_id}",
            extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id, "purpose_id": purpose_id},
        )

        object_id_artifact_id = ObjectId(consent_artifact_id)

        existing_artifact = await self.gdb.consent_latest_artifacts.find_one({"_id": object_id_artifact_id})

        if not existing_artifact:
            logger.warning(
                f"Artifact with ID {consent_artifact_id} not found for expiry processing.", extra={"consent_artifact_id": consent_artifact_id}
            )
            return

        dp_id = existing_artifact["artifact"]["data_principal"]["dp_id"]
        df_id = existing_artifact["artifact"]["data_fiduciary"]["df_id"]
        cp_id = existing_artifact["artifact"]["cp_id"]
        agreement_id = existing_artifact["artifact"]["agreement_id"]
        cp_name = existing_artifact["artifact"]["cp_name"]

        current_consent = None
        for de in existing_artifact["artifact"]["consent_scope"]["data_elements"]:
            if de["de_id"] == data_element_id:
                for consent in de["consents"]:
                    if consent["purpose_id"] == purpose_id:
                        current_consent = consent
                        break
            if current_consent:
                break

        if not current_consent:
            logger.warning(
                f"Purpose {purpose_id} not found in artifact {consent_artifact_id}. Skipping expiry.",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
            )
            return

        if current_consent.get("consent_status") != "approved":
            logger.info(
                f"Consent for purpose {purpose_id} in artifact {consent_artifact_id} is already '{current_consent.get('consent_status')}'. Skipping expiry.",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id, "current_status": current_consent.get("consent_status")},
            )
            return

        db_expiry_period_str = current_consent.get("consent_expiry_period")
        if not db_expiry_period_str:
            logger.warning(
                f"No expiry period found in DB for purpose {purpose_id} in artifact {consent_artifact_id}. Skipping expiry.",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
            )
            return

        try:
            db_expiry_dt = datetime.fromisoformat(db_expiry_period_str).replace(tzinfo=UTC)
            current_time = datetime.now(UTC)
            if current_time < db_expiry_dt:
                logger.info(
                    f"Current Time{current_time} Consent for purpose {purpose_id} in artifact {consent_artifact_id} "
                    f"has not yet expired based on DB (Expiry: {db_expiry_dt}). Skipping expiry.",
                    extra={
                        "consent_artifact_id": consent_artifact_id,
                        "purpose_id": purpose_id,
                        "current_time": current_time.isoformat(),
                        "db_expiry_dt": db_expiry_dt.isoformat(),
                    },
                )
                return
        except ValueError:
            logger.error(
                f"Invalid expiry date format in DB for purpose {purpose_id}: {db_expiry_period_str}. Skipping expiry.",
                exc_info=True,
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id, "db_expiry_period_str": db_expiry_period_str},
            )
            return

        update_result = await self.gdb.consent_latest_artifacts.find_one_and_update(
            {
                "_id": object_id_artifact_id,
                "artifact.consent_scope.data_elements.de_id": data_element_id,
                "artifact.consent_scope.data_elements.consents": {
                    "$elemMatch": {
                        "purpose_id": purpose_id,
                        "consent_status": "approved",
                        "consent_expiry_period": db_expiry_period_str,
                        "consent_expiry_notification_sent": True,
                    }
                },
            },
            {
                "$set": {
                    "artifact.consent_scope.data_elements.$[de].consents.$[c].consent_status": "expired",
                    "artifact.consent_scope.data_elements.$[de].consents.$[c].consent_expiry_notification_sent": True,
                    "timestamp": canonical_ts(),
                },
                "$inc": {"version": 1},
            },
            array_filters=[
                {"de.de_id": data_element_id},
                {"c.purpose_id": purpose_id},
            ],
            return_document=True,
        )

        if update_result:
            logger.info(
                f"Successfully updated consent status to 'expired' for purpose_id: {purpose_id} in artifact: {consent_artifact_id}",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
            )

            new_version = update_result.get("version", 0)
            audit_ts = canonical_ts()
            audit_log_entry = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                "agreement_id": agreement_id,
                "timestamp": audit_ts,
                **update_result.copy(),
                "version": new_version,
                "operation": "consent_expired",
            }
            audit_log_entry.pop("_id", None)
            audit_log_entry = await self._prepare_secure_audit_entry(audit_log_entry)
            await self.gdb.consent_audit_logs.insert_one(audit_log_entry)
            logger.info(
                f"Audit log created for consent expiry of purpose_id: {purpose_id} in artifact: {consent_artifact_id}",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
            )

            expired_purpose = None
            for de in update_result["artifact"]["consent_scope"]["data_elements"]:
                if de["de_id"] == data_element_id:
                    for consent in de["consents"]:
                        if consent["purpose_id"] == purpose_id:
                            expired_purpose = {
                                "de_id": de["de_id"],
                                "de_hash_id": de.get("de_hash_id"),
                                "title": de.get("title"),
                                "data_retention_period": de.get("data_retention_period"),
                                **consent,
                            }
                            break
                    if expired_purpose:
                        break

            if expired_purpose:
                event_ts = canonical_ts()
                message_to_publish_withdrawn = {
                    "dp_id": dp_id,
                    "df_id": df_id,
                    "cp_name": cp_name,
                    "event_type": "consent_expired",
                    "timestamp": event_ts,
                    "purposes": [expired_purpose],
                }
                await publish_message("consent_events_q", json.dumps(message_to_publish_withdrawn), channel=self.channel)
                logger.info(
                    f"Published 'consent_expired' event for expired purpose_id: {purpose_id} in artifact: {consent_artifact_id}",
                    extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
                )
            else:
                logger.warning(
                    "Could not find expired purpose in updated artifact to publish 'consent_withdrawn' event.",
                    extra={"consent_artifact_id": consent_artifact_id},
                )
        else:
            logger.error(
                f"Failed to update consent status for purpose_id: {purpose_id} in artifact: {consent_artifact_id}. Document not found or matched.",
                extra={"consent_artifact_id": consent_artifact_id, "purpose_id": purpose_id},
            )

    async def process_data_expiry_event(self, consent_artifact_id: str, data_element_id: str, instant_expiry: Optional[bool] = False):
        """
        Processes a data retention expiry event by atomically updating the data element
        to mark that its retention notification has been sent and publishing a data_expired event.
        An optional instant_expiry flag can be set to bypass the retention period check.
        """
        logger.info(
            f"Processing data retention expiry for artifact_id: {consent_artifact_id}, de_id: {data_element_id}",
            extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
        )

        object_id_artifact_id = ObjectId(consent_artifact_id)

        existing_artifact = await self.gdb.consent_latest_artifacts.find_one({"_id": object_id_artifact_id})

        if not existing_artifact:
            logger.warning(
                f"Artifact with ID {consent_artifact_id} not found for data retention expiry processing.",
                extra={"consent_artifact_id": consent_artifact_id},
            )
            return

        dp_id = existing_artifact["artifact"]["data_principal"]["dp_id"]
        df_id = existing_artifact["artifact"]["data_fiduciary"]["df_id"]
        cp_id = existing_artifact["artifact"]["cp_id"]
        agreement_id = existing_artifact["artifact"]["agreement_id"]
        cp_name = existing_artifact["artifact"]["cp_name"]

        current_data_element = None
        for de in existing_artifact["artifact"]["consent_scope"]["data_elements"]:
            if de["de_id"] == data_element_id:
                current_data_element = de
                break

        if not current_data_element:
            logger.warning(
                f"Data element {data_element_id} not found in artifact {consent_artifact_id}. Skipping data retention expiry.",
                extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
            )
            return

        db_retention_period_str = current_data_element.get("data_retention_period")
        if not db_retention_period_str:
            logger.warning(
                f"No data retention period found in DB for data element {data_element_id} in artifact {consent_artifact_id}. Skipping expiry.",
                extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
            )
            return

        if not instant_expiry:
            try:
                db_retention_dt = datetime.fromisoformat(db_retention_period_str).replace(tzinfo=UTC)
                current_time = datetime.now(UTC)
                if current_time < db_retention_dt:
                    logger.info(
                        f"Current Time {current_time} Data retention for data element {data_element_id} in artifact {consent_artifact_id} "
                        f"has not yet expired based on DB (Expiry: {db_retention_dt}). Skipping expiry.",
                        extra={
                            "consent_artifact_id": consent_artifact_id,
                            "data_element_id": data_element_id,
                            "current_time": current_time.isoformat(),
                            "db_retention_dt": db_retention_dt.isoformat(),
                        },
                    )
                    return
            except ValueError:
                logger.error(
                    f"Invalid retention date format in DB for data element {data_element_id}: {db_retention_period_str}. Skipping expiry.",
                    exc_info=True,
                    extra={
                        "consent_artifact_id": consent_artifact_id,
                        "data_element_id": data_element_id,
                        "db_retention_period_str": db_retention_period_str,
                    },
                )
                return

        update_result = await self.gdb.consent_latest_artifacts.find_one_and_update(
            {
                "_id": object_id_artifact_id,
                "artifact.consent_scope.data_elements.de_id": data_element_id,
                "artifact.consent_scope.data_elements": {
                    "$elemMatch": {
                        "de_id": data_element_id,
                        "de_status": "active",
                        "data_retention_period": db_retention_period_str,
                    }
                },
            },
            {
                "$set": {
                    "artifact.consent_scope.data_elements.$[de].data_retention_notification_sent": True,
                    "artifact.consent_scope.data_elements.$[de].de_status": "inactive",
                    "timestamp": canonical_ts(),
                },
                "$inc": {"version": 1},
            },
            array_filters=[
                {"de.de_id": data_element_id},
            ],
            return_document=True,
        )

        if update_result:
            logger.info(
                f"Successfully marked data retention notification sent for data_element_id: {data_element_id} in artifact: {consent_artifact_id}",
                extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
            )

            new_version = update_result.get("version", 0)
            audit_ts = canonical_ts()
            audit_log_entry = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                "agreement_id": agreement_id,
                "timestamp": audit_ts,
                **update_result.copy(),
                "version": new_version,
                "operation": "data_erasure_retention_triggered" if not instant_expiry else "data_erasure_manual_triggered",
            }
            audit_log_entry.pop("_id", None)

            audit_log_entry = await self._prepare_secure_audit_entry(audit_log_entry)
            await self.gdb.consent_audit_logs.insert_one(audit_log_entry)

            logger.info(
                f"Audit log created for data retention expiry of data_element_id: {data_element_id} in artifact: {consent_artifact_id}",
                extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
            )

            expired_data_element = None
            for de in update_result["artifact"]["consent_scope"]["data_elements"]:
                if de["de_id"] == data_element_id:
                    expired_data_element = de
                    break

            if expired_data_element:
                event_type_to_publish = "data_erasure_manual_triggered" if instant_expiry else "data_erasure_retention_triggered"
                event_ts = canonical_ts()
                message_to_publish_data_expired = {
                    "dp_id": dp_id,
                    "df_id": df_id,
                    "cp_name": cp_name,
                    "event_type": event_type_to_publish,
                    "timestamp": event_ts,
                    "data_elements": [expired_data_element],
                }
                await publish_message("consent_events_q", json.dumps(message_to_publish_data_expired), channel=self.channel)
                logger.info(
                    f"Published '{event_type_to_publish}' event for data_element_id: {data_element_id} in artifact: {consent_artifact_id}",
                    extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id, "event_type": event_type_to_publish},
                )
            else:
                logger.warning(
                    "Could not find expired data element in updated artifact to publish data erasure event.",
                    extra={"consent_artifact_id": consent_artifact_id},
                )
        else:
            logger.error(
                f"Failed to update data retention status for data_element_id: {data_element_id} in artifact: {consent_artifact_id}. Document not found or matched.",
                extra={"consent_artifact_id": consent_artifact_id, "data_element_id": data_element_id},
            )

    async def process_otp_verification_event(self, consent_artifact_id: str):
        """
        Processes an OTP verification event by updating the dp_verification status to True.
        """
        logger.info(
            f"Processing OTP verification for agreement_id: {consent_artifact_id}",
            extra={"consent_artifact_id": consent_artifact_id},
        )

        agreement_id = consent_artifact_id

        existing_artifact = await self.gdb.consent_latest_artifacts.find_one({"agreement_id": agreement_id})

        if not existing_artifact:
            logger.warning(
                f"Artifact with agreement_id {agreement_id} not found for OTP verification processing.",
                extra={"agreement_id": agreement_id},
            )
            return

        if existing_artifact.get("artifact", {}).get("data_principal", {}).get("dp_verification") is True:
            logger.info(
                f"Artifact with agreement_id {agreement_id} is already verified. Skipping update.",
                extra={"agreement_id": agreement_id},
            )
            return

        dp_id = existing_artifact["artifact"]["data_principal"]["dp_id"]
        df_id = existing_artifact["artifact"]["data_fiduciary"]["df_id"]
        cp_id = existing_artifact["artifact"]["cp_id"]

        update_result = await self.gdb.consent_latest_artifacts.find_one_and_update(
            {"agreement_id": agreement_id},
            {
                "$set": {
                    "artifact.data_principal.dp_verification": True,
                    "timestamp": canonical_ts(),
                },
                "$inc": {"version": 1},
            },
            return_document=True,
        )

        if update_result:
            logger.info(
                f"Successfully updated dp_verification to True for agreement_id: {agreement_id}",
                extra={"agreement_id": agreement_id},
            )

            new_version = update_result.get("version", 0)
            audit_ts = canonical_ts()
            audit_log_entry = {
                "dp_id": dp_id,
                "df_id": df_id,
                "cp_id": cp_id,
                "agreement_id": agreement_id,
                "timestamp": audit_ts,
                **update_result.copy(),
                "version": new_version,
                "operation": "otp_verified",
            }
            audit_log_entry.pop("_id", None)

            audit_log_entry = await self._prepare_secure_audit_entry(audit_log_entry)
            await self.gdb.consent_audit_logs.insert_one(audit_log_entry)
            logger.info(
                f"Audit log created for OTP verification of agreement_id: {agreement_id}",
                extra={"agreement_id": agreement_id},
            )
        else:
            logger.error(
                f"Failed to update dp_verification for agreement_id: {agreement_id}. Document not found or matched.",
                extra={"agreement_id": agreement_id},
            )
