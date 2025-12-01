import asyncio
import csv
from datetime import UTC, datetime, timezone
import hashlib
import io
import json
import os
from typing import Optional
import uuid
from bson import ObjectId
from fastapi import HTTPException

from app.schemas.consent_validation_schema import VerificationRequest
from app.core.config import settings
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient
import aio_pika
from app.core.logger import setup_logging, get_logger

MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


s3_client = Minio(settings.S3_URL, access_key=settings.MINIO_ROOT_USER, secret_key=settings.MINIO_ROOT_PASSWORD, secure=settings.S3_SECURE)


user_collection = db["cmp_users"]
consent_artifact_collection = db["consent_latest_artifacts"]
consent_validation_collection = db["consent_validation"]
consent_validation_files_collection = db["consent_validation_files"]
customer_notifications_collection = db["customer_notifications"]


def hash_shake256(value: str) -> str:
    if value:
        return hashlib.shake_256(value.encode()).hexdigest(length=32)
    else:
        return ""


async def verify_consent_internal(
    request: VerificationRequest,
    df_id: str,
    genie_user_id: str,
    bulk_file_name: Optional[str] = None,
):

    dp_id = request.dp_id
    dp_system_id = request.dp_system_id
    dp_e = hash_shake256(request.dp_e)
    dp_m = hash_shake256(request.dp_m)
    data_elements_hash = request.data_elements_hash
    purpose_hash = request.purpose_hash

    if not df_id:
        logger.error("User Not Found: df_id is missing.")
        raise HTTPException(status_code=404, detail="User Not Found")

    if not dp_id and not dp_system_id and not (dp_e or dp_m):
        logger.error("Data Principal ID or Data Principal System ID is required for internal verification.")
        raise HTTPException(
            status_code=400,
            detail="Data Principal ID or Data Principal System ID is required",
        )

    if not purpose_hash:
        logger.error("Purpose hash is required for internal verification.")
        raise HTTPException(
            status_code=400,
            detail="Purpose hash is required",
        )

    if not data_elements_hash:
        logger.error("At least one data element hash is required for internal verification.")
        raise HTTPException(
            status_code=400,
            detail="At least one data element hash is required",
        )

    query = {}
    if dp_id:
        query["artifact.data_principal.dp_id"] = dp_id
    elif dp_system_id:
        query["artifact.data_principal.dp_df_id"] = dp_system_id
    elif dp_e:
        query["artifact.data_principal.dp_e"] = dp_e
    elif dp_m:
        query["artifact.data_principal.dp_m"] = dp_m

    consent_artifacts = await consent_artifact_collection.find(query).to_list(length=None)
    if not consent_artifacts:
        raise HTTPException(status_code=404, detail="Consent Artifact(s) Not Found")

    current_time = datetime.now(timezone.utc)
    matched_elements = set()

    for artifact_doc in consent_artifacts:
        artifact = artifact_doc.get("artifact", {})
        data_elements = artifact.get("consent_scope", {}).get("data_elements", [])

        for element in data_elements:
            element_hash = element.get("de_hash_id")
            if element_hash not in data_elements_hash:
                continue

            for consent in element.get("consents", []):
                if consent.get("purpose_hash_id") != purpose_hash:
                    continue
                if consent.get("consent_status") != "approved":
                    continue

                expiry_str = consent.get("consent_expiry_period")
                if not expiry_str:
                    continue

                try:
                    expiry_date = datetime.fromisoformat(expiry_str)
                    if expiry_date.tzinfo is None:
                        expiry_date = expiry_date.replace(tzinfo=timezone.utc)

                    if expiry_date > current_time:
                        matched_elements.add(element_hash)
                        break
                except (TypeError, ValueError):
                    continue

    all_verified = all(elem in matched_elements for elem in data_elements_hash)

    artifact_for_log = consent_artifacts[0].get("artifact", {})

    verification_log = {
        "request_id": uuid.uuid4().hex,
        "df_id": df_id,
        "dp_id": dp_id or artifact_for_log.get("data_principal", {}).get("dp_id"),
        "dp_system_id": dp_system_id or artifact_for_log.get("data_principal", {}).get("dp_df_id"),
        "dp_e": dp_e or artifact_for_log.get("data_principal", {}).get("dp_e"),
        "dp_m": dp_m or artifact_for_log.get("data_principal", {}).get("dp_m"),
        "internal_external": "Internal",
        "ver_requested_by": genie_user_id,
        "consent_status": all_verified,
        "scope": {
            "data_element_hashes": data_elements_hash,
            "purpose_hash": purpose_hash,
        },
        "status": "successful",
        "timestamp": current_time,
        "bulk_file_name": bulk_file_name,
    }

    verification_req = await consent_validation_collection.insert_one(verification_log)

    if not all_verified:
        # Create notification for DP
        dp_id_for_notif = dp_id or artifact_for_log.get("data_principal", {}).get("dp_id")
        if dp_id_for_notif:
            now = datetime.now(UTC)
            notification = {
                "dp_id": dp_id_for_notif,
                "type": "CONSENT_VALIDATION_FAILED",
                "title": "Consent Validation Failed",
                "message": f"A Data Fiduciary attempted to validate your consent for purpose {purpose_hash}, but it was found to be invalid or expired.",
                "status": "unread",
                "created_at": now,
                "verification_request_id": str(verification_req.inserted_id),
                "df_id": df_id,
            }
            await customer_notifications_collection.insert_one(notification)

    return {
        "verified": all_verified,
        "consented_data_elements": matched_elements,
        "verification_request_id": str(verification_req.inserted_id),
    }


async def process_file(contents, filename, df_id, genie_user_id):

    logger.info(f"Processing file: {filename} for DF: {df_id} and Genie User ID: {genie_user_id}")

    await consent_validation_files_collection.find_one_and_update(
        {"filename": filename},
        {"$set": {"status": "processing", "started_at": datetime.now(UTC)}},
    )

    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        error_message = "Unable to decode file as UTF-8."
        await consent_validation_files_collection.find_one_and_update(
            {"filename": filename},
            {
                "$set": {
                    "status": "failed",
                    "message": error_message,
                    "completed_at": datetime.now(UTC),
                }
            },
        )
        logger.error(f"Error for {filename}: {error_message}")
        return

    csv_reader = csv.DictReader(io.StringIO(text))
    results = []
    row_number = 0

    for row in csv_reader:
        row_number += 1

        dp_id = (row.get("dp_id") or "").strip() or None
        dp_system_id = (row.get("dp_system_id") or "").strip() or None
        dp_e = (row.get("dp_e") or "").strip() or None
        dp_m = (row.get("dp_m") or "").strip() or None
        raw_hashes = (row.get("data_elements_hash") or "").strip()
        purpose_hash = (row.get("purpose_hash") or "").strip() or None

        logger.debug(f"Raw hashes for row {row_number}: {raw_hashes}")
        data_element_hashes = [t.strip() for t in raw_hashes.split(",") if t.strip()] if raw_hashes else []

        row_errors = []
        if not dp_id and not dp_system_id:
            row_errors.append("Either dp_id or dp_system_id is required.")
        if not data_element_hashes:
            row_errors.append("At least one data_element_hash is required.")
        if not (purpose_hash):
            row_errors.append("Either purpose_hash or purpose_id is required.")

        if row_errors:
            logger.warning(f"Validation errors for row {row_number}: {'; '.join(row_errors)}")
            results.append(
                {
                    "row": row_number,
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "requested_data_element_hashes": data_element_hashes,
                    "purpose_hash": purpose_hash,
                    "status": "failed",
                    "message": " ".join(row_errors),
                }
            )
            continue

        try:
            verification_request = VerificationRequest(
                dp_id=dp_id,
                dp_system_id=dp_system_id,
                dp_e=dp_e,
                dp_m=dp_m,
                data_elements_hash=data_element_hashes,
                purpose_hash=purpose_hash,
            )

            verification_result = await verify_consent_internal(
                request=verification_request,
                df_id=df_id,
                genie_user_id=genie_user_id,
                bulk_file_name=filename,
            )

            verification_result.update(
                {
                    "row": row_number,
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "requested_data_element_hashes": data_element_hashes,
                    "purpose_hash": purpose_hash,
                    "status": ("success" if verification_result.get("verified") else "no_consent"),
                }
            )
            results.append(verification_result)

        except HTTPException as e:

            results.append(
                {
                    "row": row_number,
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "requested_data_element_hashes": data_element_hashes,
                    "purpose_hash": purpose_hash,
                    "status": "failed",
                    "message": e.detail,
                }
            )
            logger.error(f"HTTPException for row {row_number}: {e.detail}")
        except Exception as e:
            logger.critical(f"Unexpected error for row {row_number}: {e}")
            results.append(
                {
                    "row": row_number,
                    "dp_id": dp_id,
                    "dp_system_id": dp_system_id,
                    "requested_data_element_hashes": data_element_hashes,
                    "purpose_hash": purpose_hash,
                    "status": "error",
                    "message": str(e),
                }
            )

    await consent_validation_files_collection.find_one_and_update(
        {"filename": filename},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(UTC),
                "row_count": row_number,
            }
        },
    )

    logger.info(f"Finished processing file {filename}. Results: {len(results)} total rows.")


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):
        try:
            body = message.body.decode()
            payload = json.loads(body)

            filename = payload.get("filename")
            df_id = payload.get("df_id")
            genie_user_id = payload.get("genie_user_id")

            if not filename or not df_id or not genie_user_id:
                logger.warning(f"Invalid message, missing required fields: {payload}")
                return

            local_temp_path = os.path.join("/data/uploads/", filename)
            s3_client.fget_object(
                settings.UNPROCESSED_VERIFICATION_FILES_BUCKET,
                filename,
                local_temp_path,
            )

            if not os.path.exists(local_temp_path):
                logger.error(f"File not found: {local_temp_path}")
                return

            with open(local_temp_path, "rb") as f:
                contents = f.read()

            await process_file(
                contents=contents,
                filename=filename,
                df_id=df_id,
                genie_user_id=genie_user_id,
            )

            logger.info(f"Processed file: {filename} for DF: {df_id}")

        except Exception as e:
            logger.critical(f"Error processing message: {e}")

            raise


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    connection, channel = await rabbitmq_pool.get_connection()
    try:
        await channel.set_qos(prefetch_count=10)
        QUEUE_NAME = "consent_bulk_verification"

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        logger.info(f"Waiting for messages on '{QUEUE_NAME}'...")

        await queue.consume(handle_message)

        await asyncio.Future()
    finally:

        await rabbitmq_pool.release_connection(connection, channel)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.consent_validation_internal_consumer")
    logger.info("Consent validation internal consumer starting up.")
    asyncio.run(main())
