import json
import uuid
from datetime import UTC, datetime, timezone

from bson import ObjectId
from app.db.rabbitmq import rabbitmq_pool, declare_queues

from app.core.config import settings
import aio_pika
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from minio import Minio
from app.core.logger import setup_logging, get_logger

from app.schemas.consent_validation_schema import VerificationRecord, VerificationResult
from app.utils.common import hash_shake256


MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


s3_client = Minio(
    settings.S3_URL,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=True,
)

consent_artifact_collection = db["consent_latest_artifacts"]
consent_validation_collection = db["consent_validation"]
validation_batch_collection = db["validation_batch"]
vendor_master_collection = db["vendor_master"]


async def process_verification_record(record: VerificationRecord, df_id: str, vendor_details: dict) -> VerificationResult:
    """Process a single verification record"""

    dp_e = hash_shake256(record.dp_e) if record.dp_e else None
    dp_m = hash_shake256(record.dp_m) if record.dp_m else None

    logger.info(f"Processing record: {record.model_dump()}")

    query = {}
    if record.dp_id:
        query["artifact.data_principal.dp_id"] = record.dp_id
    elif record.dp_system_id:
        query["artifact.data_principal.dp_df_id"] = record.dp_system_id
    elif dp_e:
        query["artifact.data_principal.dp_e"] = dp_e
    elif dp_m:
        query["artifact.data_principal.dp_m"] = dp_m

    consent_artifacts = await consent_artifact_collection.find(query).to_list(length=None)
    if not consent_artifacts:
        logger.warning(f"No consent artifacts found for df_id={df_id} with provided identifiers")
        raise ValueError(f"No consent artifacts found for df_id={df_id} with provided identifiers")

    current_time = datetime.now(UTC)
    matched_elements = set()

    for artifact_doc in consent_artifacts:
        artifact = artifact_doc.get("artifact", {})
        data_elements = artifact.get("consent_scope", {}).get("data_elements", [])

        for element in data_elements:
            element_hash = element.get("de_hash_id")
            if element_hash not in record.data_elements_hash:
                continue

            for consent in element.get("consents", []):
                if consent.get("purpose_hash_id") != record.purpose_hash:
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

    all_verified = all(elem in matched_elements for elem in record.data_elements_hash)

    artifact_for_log = consent_artifacts[0].get("artifact", {})

    verification_log = {
        "request_id": uuid.uuid4().hex,
        "df_id": df_id,
        "dp_id": record.dp_id or artifact_for_log.get("data_principal", {}).get("dp_id"),
        "dp_system_id": record.dp_system_id or artifact_for_log.get("data_principal", {}).get("dp_df_id"),
        "dp_e": dp_e or artifact_for_log.get("data_principal", {}).get("dp_e"),
        "dp_m": dp_m or artifact_for_log.get("data_principal", {}).get("dp_m"),
        "internal_external": "External",
        "ver_requested_by": str(vendor_details.get("_id")),
        "consent_status": all_verified,
        "scope": {
            "data_element_hashes": record.data_elements_hash,
            "purpose_hash": record.purpose_hash,
        },
        "status": "successful",
        "timestamp": current_time,
    }

    verification_req = await consent_validation_collection.insert_one(verification_log)

    return VerificationResult(
        record=record,
        verified=all_verified,
        consented_data_elements=matched_elements,
        verification_request_id=str(verification_req.inserted_id),
    )


async def process_batch_verification(batch_data: dict):
    """Process a full batch of verification requests"""

    logger.info(f"Processing batch verification: {batch_data.get('batch_id')}")

    df_id = batch_data["df_id"]
    batch_id = batch_data["batch_id"]
    token = batch_data["token"]
    verification_records = batch_data["verification_data_list"]

    batch_doc = await validation_batch_collection.find_one({"_id": ObjectId(batch_id), "token": token})

    if not batch_doc:
        logger.error(f"Invalid batch credentials: df_id={df_id} batch_id={batch_id}")
        raise ValueError(f"Invalid batch credentials: df_id={df_id} batch_id={batch_id}")

    if batch_doc.get("status") == "end":
        logger.warning(f"Batch already processed: {batch_id}")
        return

    vendor_details = await vendor_master_collection.find_one({"df_id": df_id})
    if not vendor_details:
        raise ValueError(f"No vendor found for df_id: {df_id}")

    results = []
    for record_data in verification_records:
        try:

            record = VerificationRecord(**record_data)
            result = await process_verification_record(record, df_id, vendor_details)
            results.append(result.model_dump())
        except Exception as e:

            error_result = VerificationResult(
                record=record_data,
                verified=False,
                verification_request_id=uuid.uuid4().hex,
                error=f"Processing error: {str(e)}",
            )
            results.append(error_result.model_dump())
            logger.error(f"Verification failed for record: {str(e)}")

    request_ids = [r.get("verification_request_id") for r in results]

    update_data = {
        "status": "end",
        "completed_at": datetime.now(UTC),
        "processed_count": len(results),
        "success_count": sum(1 for r in results if r.get("verified") is True),
        "failure_count": sum(1 for r in results if r.get("error") or not r.get("verified")),
        "verification_request_ids": request_ids,
    }

    validation_batch_collection.update_one({"_id": ObjectId(batch_id)}, {"$set": update_data})

    logger.info(f"Processed batch {batch_id} with {len(results)} verifications")
    return results


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):
        try:
            body = message.body.decode()
            payload = json.loads(body)
            logger.info(f"Received verification batch: {payload['batch_id']}")
            await process_batch_verification(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    connection, channel = await rabbitmq_pool.get_connection()
    try:
        await channel.set_qos(prefetch_count=10)
        QUEUE_NAME = "consent_bulk_external_verification"

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        logger.info(f"Waiting for messages on '{QUEUE_NAME}'...")

        await queue.consume(handle_message)

        await asyncio.Future()
    finally:

        await rabbitmq_pool.release_connection(connection, channel)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.consent_validation_external_consumer")
    logger.info("Consent validation external consumer starting up.")
    asyncio.run(main())
