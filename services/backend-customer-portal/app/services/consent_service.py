from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import shake_256
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.rabbitmq import publish_message
from app.schemas.consent_schema import UpdateConsent
from app.core.logger import app_logger
import json


def generate_agreement_hash(artifact: dict) -> str:
    artifact_str = str(artifact).encode()
    return shake_256(artifact_str).hexdigest(32)


async def publishable_message_formatter(data_elements_consents, dp_id, df_id, collection_point_name, event_type):
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

    message_to_publish = {
        "dp_id": dp_id,
        "df_id": df_id,
        "cp_name": collection_point_name,
        "event_type": event_type,
        "timestamp": str(datetime.now(UTC)),
        "purposes": purposes_list,
    }

    return json.dumps(message_to_publish)


class ConsentService:
    def __init__(self, consent_artifact_collection: AsyncIOMotorCollection, purpose_collection: AsyncIOMotorCollection = None):
        self.artifact_collection = consent_artifact_collection
        self.purpose_collection = purpose_collection

    async def _get_existing_artifact(self, agreement_id: str):
        artifact = await self.artifact_collection.find_one({"artifact.agreement_id": agreement_id})
        if not artifact:
            app_logger.warning(f"Consent agreement not found for ID: {agreement_id}")
            raise HTTPException(status_code=404, detail="Consent agreement not found")
        return artifact

    async def revoke_consent(self, agreement_id: str, update_consent: UpdateConsent):
        existing_artifact = await self._get_existing_artifact(agreement_id)

        new_artifact = deepcopy(existing_artifact)
        new_artifact.pop("_id", None)

        now = datetime.now(UTC)

        for scope in update_consent.consent_scope:
            for artifact_element in new_artifact["artifact"]["consent_scope"]["data_elements"]:
                if artifact_element["de_id"] == scope.de_id:
                    for purpose in scope.consent_purposes:
                        for consent in artifact_element.get("consents", []):
                            if consent["purpose_id"] == purpose.purpose_id:
                                consent["consent_status"] = "denied"
                                consent["consent_timestamp"] = now.isoformat()

        new_artifact["artifact"]["data_fiduciary"]["agreement_date"] = now.isoformat()
        new_artifact["agreement_hash_id"] = generate_agreement_hash(new_artifact["artifact"])

        message_payload = {
            "event_type": "consent_submission",
            "timestamp": now.isoformat(),
            "consent_artifact": new_artifact,
        }
        app_logger.info(f"Publishing consent revocation message for agreement_id: {agreement_id}")
        await publish_message("consent_processing_q", json.dumps(message_payload))

        return {
            "message": "Consent purpose(s) revoked. New artifact created.",
            "linked_to": agreement_id,
            "agreement_hash_id": new_artifact["agreement_hash_id"],
        }

    async def give_consent(self, agreement_id: str, update_consent: UpdateConsent):
        existing_artifact = await self._get_existing_artifact(agreement_id)

        new_artifact = deepcopy(existing_artifact)
        new_artifact.pop("_id", None)

        now = datetime.now(UTC)

        for scope in update_consent.consent_scope:
            for artifact_element in new_artifact["artifact"]["consent_scope"]["data_elements"]:
                if artifact_element["de_id"] == scope.de_id:
                    for purpose in scope.consent_purposes:
                        for consent in artifact_element.get("consents", []):
                            if consent["purpose_id"] == purpose.purpose_id:
                                consent["consent_status"] = "approved"
                                consent["consent_timestamp"] = now.isoformat()

        new_artifact["artifact"]["data_fiduciary"]["agreement_date"] = now.isoformat()
        new_artifact["agreement_hash_id"] = generate_agreement_hash(new_artifact["artifact"])

        message_payload = {
            "event_type": "consent_submission",
            "timestamp": now.isoformat(),
            "consent_artifact": new_artifact,
        }
        app_logger.info(f"Publishing consent grant message for agreement_id: {agreement_id}")
        await publish_message("consent_processing_q", json.dumps(message_payload))

        return {
            "message": "Consent purpose(s) granted. New artifact created.",
            "linked_to": agreement_id,
            "agreement_hash_id": new_artifact["agreement_hash_id"],
        }

    async def renew_consent(self, agreement_id: str, update_consent: UpdateConsent):
        existing_artifact = await self._get_existing_artifact(agreement_id)

        new_artifact = deepcopy(existing_artifact)
        new_artifact.pop("_id", None)

        now = datetime.now(UTC)

        for scope in update_consent.consent_scope:
            for artifact_element in new_artifact["artifact"]["consent_scope"]["data_elements"]:
                if artifact_element.get("de_id") != scope.de_id:
                    continue

                for selected_purpose in scope.consent_purposes or []:
                    purpose_id = selected_purpose.purpose_id
                    consent_doc = await self.purpose_collection.find_one({"_id": ObjectId(purpose_id)})
                    if not consent_doc:
                        app_logger.warning(f"Purpose not found: {purpose_id} during consent renewal for agreement {agreement_id}")
                        raise HTTPException(status_code=404, detail=f"Purpose not found: {purpose_id}")

                    days = consent_doc.get("consent_purpose_consent_time_period", 0)

                    for consent in artifact_element.get("consents", []):
                        if consent.get("purpose_id") == purpose_id:
                            existing_expiry = None
                            if consent.get("consent_expiry_period"):
                                try:
                                    existing_expiry = datetime.fromisoformat(consent["consent_expiry_period"]).replace(tzinfo=UTC)
                                except Exception:
                                    pass
                            base_date = existing_expiry if existing_expiry and existing_expiry > now else now
                            expiry_date = base_date + timedelta(days=days)

                            consent["consent_status"] = "approved"
                            consent["consent_timestamp"] = now.isoformat()
                            consent["consent_expiry_period"] = expiry_date.isoformat()
                            break

        new_artifact["artifact"]["data_fiduciary"]["agreement_date"] = now.isoformat()
        new_artifact["agreement_hash_id"] = generate_agreement_hash(new_artifact["artifact"])

        message_payload = {
            "event_type": "consent_submission",
            "timestamp": now.isoformat(),
            "consent_artifact": new_artifact,
        }
        app_logger.info(f"Publishing consent renewal message for agreement_id: {agreement_id}")
        await publish_message("consent_processing_q", json.dumps(message_payload))

        return {
            "message": "Consent renewed successfully. New artifact created.",
            "linked_to": agreement_id,
            "agreement_hash_id": new_artifact["agreement_hash_id"],
        }
