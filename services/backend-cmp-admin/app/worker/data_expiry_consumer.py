import asyncio
import json
import aio_pika
from app.db.rabbitmq import publish_message, rabbitmq_pool, declare_queues
from app.core.config import settings
from app.core.logger import setup_logging, get_logger


MAX_RETRIES = settings.DATA_RETENTION_MAX_RETRIES if hasattr(settings, "DATA_RETENTION_MAX_RETRIES") else 5


async def process_data_expiry_event(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    """Process messages from data_expiry_queue."""
    consent_artifact_id = "unknown_artifact"
    data_element_id = "unknown_data_element"
    try:
        payload = json.loads(message.body.decode())
        event_type = payload.get("event_type")

        if event_type == "data_retention_expiry" or event_type == "data_retention_expiry_manual":
            consent_artifact_id = payload.get("consent_artifact_id")
            data_element_id = payload.get("data_element_id")
            retention_expiry_at = payload.get("retention_expiry_at")

            logger.info(f"Starting to process data retention expiry event for artifact {consent_artifact_id}, data element {data_element_id}...")
            message_payload = payload

            await publish_message("consent_processing_q", json.dumps(message_payload), channel=channel)

            logger.info(
                f"Data retention expiry event for artifact {consent_artifact_id}, data element {data_element_id} processed successfully. ACKING."
            )
            await message.ack()
        else:
            logger.warning(f"Received unknown event type '{event_type}' on data_expiry_queue. NACKING.")
            await message.nack(requeue=False)

    except Exception as e:
        error_message = str(e)
        logger.error(
            f"Failed to process data retention expiry event for artifact {consent_artifact_id}, data element {data_element_id}: {error_message}"
        )
        await handle_failure(message, consent_artifact_id, data_element_id, error_message, channel)
    finally:
        logger.info(f"Finished processing event for artifact {consent_artifact_id}, data element {data_element_id}.")


async def handle_failure(
    message: aio_pika.IncomingMessage, consent_artifact_id: str, data_element_id: str, error_message: str, channel: aio_pika.Channel
):
    """
    Handle failed data retention expiry events: send to retry queue or DLQ.
    """
    x_death_headers = message.headers.get("x-death", [])
    retries = x_death_headers[0]["count"] if x_death_headers else 0
    current_attempt = retries + 1

    logger.warning(
        f"Handling failure for data retention expiry (Artifact: {consent_artifact_id}, Data Element: {data_element_id}, Attempt {current_attempt})..."
    )

    if current_attempt >= MAX_RETRIES:
        logger.critical(
            f"Data retention expiry (Artifact: {consent_artifact_id}, Data Element: {data_element_id}) reached max retries ({MAX_RETRIES}). Sending to DLQ. CRITICAL ACK REQUIRED."
        )

        await rabbitmq_pool.publish_message("data_expiry_dlq", message.body.decode(), channel)

        try:
            await message.ack()
            logger.info(
                f"Message (Artifact: {consent_artifact_id}, Data Element: {data_element_id}) successfully ACKed from main queue after DLQ copy."
            )
        except Exception as ack_e:
            logger.critical(
                f"CRITICAL ACK FAILURE for (Artifact: {consent_artifact_id}, Data Element: {data_element_id}): Could not acknowledge message after DLQ copy. Error: {ack_e}. This may cause the consumer to stall."
            )
    else:
        logger.warning(
            f"Data retention expiry (Artifact: {consent_artifact_id}, Data Element: {data_element_id}) failed. Nacking to trigger retry (attempt {current_attempt})."
        )
        try:

            await message.nack(requeue=False)
            logger.info(
                f"Message (Artifact: {consent_artifact_id}, Data Element: {data_element_id}) successfully NACKed (requeue=False). Triggering TTL."
            )
        except Exception as nack_e:
            logger.critical(
                f"CRITICAL NACK FAILURE for (Artifact: {consent_artifact_id}, Data Element: {data_element_id}): Could not nack message. Error: {nack_e}"
            )


async def start_worker() -> None:
    await rabbitmq_pool.init_pool()
    await declare_queues()

    while True:
        connection, channel = None, None
        try:
            connection, channel = await rabbitmq_pool.get_connection()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.get_queue("data_expiry_queue")
            logger.info("Waiting for messages on 'data_expiry_queue'...")

            await queue.consume(lambda msg: process_data_expiry_event(msg, channel))

            await asyncio.Future()

        except asyncio.CancelledError:
            logger.info("Data expiry consumer task cancelled gracefully.")
            break
        except Exception as main_e:
            logger.critical(f"CRITICAL EXCEPTION IN DATA EXPIRY CONSUMER LOOP (Restarting): {main_e}")
            await asyncio.sleep(5)
            continue
        finally:
            pass


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.data_expiry_consumer")
    logger.info("Data expiry consumer starting up.")
    asyncio.run(start_worker())
