import asyncio
import aio_pika
import json
from datetime import datetime, timedelta, UTC
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.core.config import settings
from app.db.rabbitmq import rabbitmq_pool, publish_message
from app.core.logger import setup_logging, get_logger


db_client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
concur_master_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_MASTER]
consent_artifacts_collection: AsyncIOMotorCollection = concur_master_db["consent_latest_artifacts"]
renewal_notification: AsyncIOMotorCollection = concur_master_db["renewal_notification"]


def format_utc_datetime(dt: datetime) -> str:
    return dt.replace(tzinfo=None).isoformat(timespec="microseconds")


async def run_expiry_scheduler(interval_seconds=180, window_days=31):
    await rabbitmq_pool.init_pool()
    logger.info(f"Expiry Scheduler started at {format_utc_datetime(datetime.now(UTC))}. Running checks every {interval_seconds} seconds...")

    connection = None
    channel = None
    try:
        connection, channel = await rabbitmq_pool.get_connection()

        while True:
            now = datetime.now(UTC)

            expiry_window = now + timedelta(days=window_days)
            logger.info(
                f"Expiry Scheduler: Running check at {format_utc_datetime(now)}. Looking for consents expiring before {format_utc_datetime(expiry_window)} (next {window_days} days)."
            )

            expiry_window_iso_str = expiry_window.replace(tzinfo=None).isoformat(timespec="microseconds")

            query = {
                "artifact.consent_scope.data_elements.consents": {
                    "$elemMatch": {
                        "consent_status": "approved",
                        "consent_expiry_period": {"$lt": expiry_window_iso_str},
                        "consent_expiry_notification_sent": {"$ne": True},
                    }
                }
            }

            async for consent_artifact_doc in consent_artifacts_collection.find(query):
                artifact_id = str(consent_artifact_doc["_id"])

                for de_index, data_element in enumerate(consent_artifact_doc.get("artifact", {}).get("consent_scope", {}).get("data_elements", [])):

                    for c_index, consent in enumerate(data_element.get("consents", [])):
                        consent_status = consent.get("consent_status")
                        consent_expiry_period_str = consent.get("consent_expiry_period")
                        consent_expiry_notification_sent = consent.get("consent_expiry_notification_sent", False)

                        if consent_status == "approved" and consent_expiry_period_str and not consent_expiry_notification_sent:
                            try:
                                expiry_at = datetime.fromisoformat(consent_expiry_period_str).replace(tzinfo=UTC)
                            except ValueError:
                                logger.error(
                                    f"Expiry Scheduler: Invalid expiry date format for consent in artifact {artifact_id}: {consent_expiry_period_str}"
                                )
                                continue

                            if expiry_at < expiry_window:
                                delay_seconds = (expiry_at - now).total_seconds()

                                delay_for_rabbitmq = max(0, int(delay_seconds))

                                logger.info(
                                    f"Expiry Scheduler: Found soon-to-expire consent in artifact {artifact_id} "
                                    f"(Expiry: {format_utc_datetime(expiry_at)}). "
                                    f"Publishing with a delay of {delay_for_rabbitmq} seconds ({delay_seconds} raw seconds)."
                                )

                                message = {
                                    "event_type": "consent_expiry",
                                    "consent_artifact_id": artifact_id,
                                    "data_element_id": data_element.get("de_id"),
                                    "purpose_id": consent.get("purpose_id"),
                                    "expiry_at": consent_expiry_period_str,
                                }

                                await publish_message("consent_expiry_delay_queue", json.dumps(message), channel, expiration=delay_for_rabbitmq)
                                await renewal_notification.insert_one(message)
                                update_result = await consent_artifacts_collection.update_one(
                                    {
                                        "_id": consent_artifact_doc["_id"],
                                    },
                                    {"$set": {"artifact.consent_scope.data_elements.$[de].consents.$[c].consent_expiry_notification_sent": True}},
                                    array_filters=[
                                        {"de.de_id": data_element.get("de_id")},
                                        {"c.purpose_id": consent.get("purpose_id")},
                                    ],
                                )
                                if update_result.modified_count > 0:
                                    logger.info(
                                        f"Expiry Scheduler: Marked consent (purpose_id: {consent.get('purpose_id')}) "
                                        f"in artifact {artifact_id} as expiry_notification_sent. Modified count: {update_result.modified_count}"
                                    )
                                else:
                                    logger.warning(
                                        f"Expiry Scheduler: Failed to mark consent (purpose_id: {consent.get('purpose_id')}) "
                                        f"in artifact {artifact_id} as expiry_notification_sent. Modified count: {update_result.modified_count}"
                                    )

            logger.info(f"Expiry Scheduler: Sleeping for {interval_seconds} seconds at {format_utc_datetime(datetime.now(UTC))}...")
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Consent expiry scheduler task cancelled gracefully.")
    except Exception as e:
        logger.critical(f"Expiry Scheduler: A critical error occurred in the main loop: {e}")
    finally:
        if connection and channel:
            await rabbitmq_pool.release_connection(connection, channel)
            logger.info("Expiry Scheduler: Released RabbitMQ connection and channel.")


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.consent_expiry_scheduler")
    logger.info("Consent expiry scheduler starting up.")
    asyncio.run(run_expiry_scheduler())
