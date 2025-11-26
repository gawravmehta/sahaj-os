import json
import asyncio
import aio_pika
import motor.motor_asyncio

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.core.config import settings
from app.db.rabbitmq import publish_message, rabbitmq_pool, declare_queues
from app.crud.webhook_events_crud import WebhookEventCRUD
from app.crud.webhooks_crud import WebhooksCrud
from app.services.event_classification_service import EventClassificationService
from app.services.webhooks_service import WebhooksService
from app.core.logger import setup_logging, get_logger

MAX_RETRIES = settings.CONSENT_MAX_RETRIES if hasattr(settings, "CONSENT_MAX_RETRIES") else 5


db_client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
concur_master_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_MASTER]

webhook_events_collection: AsyncIOMotorCollection = concur_master_db["webhook_events"]
webhooks_collection: AsyncIOMotorCollection = concur_master_db["webhooks"]
business_logs_collection: str = "app-logs-business"

webhook_event_crud = WebhookEventCRUD(collection=webhook_events_collection)
webhooks_crud = WebhooksCrud(webhooks_collection=webhooks_collection)
webhooks_service = WebhooksService(
    webhook_crud=webhooks_crud, business_logs_collection=business_logs_collection, webhook_event_crud=webhook_event_crud
)

consent_classification_service = EventClassificationService(webhooks_service=webhooks_service)


async def process_consent_event(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    event_id = None
    try:
        event_payload = json.loads(message.body.decode())
        event_id = event_payload.get("dp_id", "unknown") + "_" + event_payload.get("event_type", "unknown")

        logger.info(f"Processing consent event {event_id}...")

        await consent_classification_service.classify_and_publish_event(event_payload, channel)

        logger.info(f"Consent event {event_id} processed successfully. ACKING.")
        await message.ack()

    except Exception as e:
        error_message = str(e)
        logger.exception(f"Error processing consent event {event_id}: {error_message}")
        await handle_failure(message, event_id, error_message, channel)
    finally:
        logger.info(f"Finished processing event {event_id}.")


async def handle_failure(message, event_id, error_message, channel):
    x_death_headers = message.headers.get("x-death", [])
    retries = x_death_headers[0]["count"] if x_death_headers else 0
    current_attempt = retries + 1

    logger.warning(f"Retry {current_attempt}/{MAX_RETRIES} for event {event_id}.")

    if current_attempt >= MAX_RETRIES:
        logger.critical(f"Max retries reached for {event_id}. Sending to DLQ.")

        await publish_message("consent_dlq", message.body.decode(), channel)
        await message.ack()
        return

    await message.nack(requeue=False)
    logger.warning(f"NACKed event {event_id}, routed to retry queue.")


async def main():
    logger.info("Consent event worker starting...")
    await rabbitmq_pool.init_pool()
    await declare_queues()

    while True:
        try:
            connection, channel = await rabbitmq_pool.get_connection()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.get_queue("consent_events_q")

            logger.info("Waiting on consent_events_q...")

            await queue.consume(lambda msg: process_consent_event(msg, channel))

            await asyncio.Future()

        except asyncio.CancelledError:
            logger.info("Worker cancelled gracefully.")
            break

        except Exception as e:
            logger.critical(f"Critical failure, restarting consumer loop: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.consent_event_consumer")
    logger.info("Logger initialized for Consent Event Consumer")
    asyncio.run(main())
