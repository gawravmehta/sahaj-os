import asyncio
import json
import aio_pika
from app.db.session import get_mongo_master_db, startup_db_clients
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.services.consent_worker_service import ConsentWorkerService
from app.core.config import settings
from app.core.logger import setup_logging, get_logger


MAX_RETRIES = settings.CONSENT_MAX_RETRIES if hasattr(settings, "CONSENT_MAX_RETRIES") else 5

logger = get_logger("worker.consent_processing_consumer")


async def process_consent_processing_event(message: aio_pika.IncomingMessage, channel: aio_pika.Channel, gdb):
    """Process messages from consent_processing_q."""
    agreement_id = "unknown_agreement"
    try:
        payload = json.loads(message.body.decode())

        event_type = payload.get("event_type")

        consent_worker_service = ConsentWorkerService(gdb, channel)

        if event_type == "consent_expiry":
            consent_artifact_id = payload.get("consent_artifact_id")
            data_element_id = payload.get("data_element_id")
            purpose_id = payload.get("purpose_id")
            expiry_at = payload.get("expiry_at")

            logger.info(f"Starting to process consent expiry event for artifact {consent_artifact_id}...", extra={"agreement_id": agreement_id})
            await consent_worker_service.process_consent_expiry_event(consent_artifact_id, data_element_id, purpose_id, expiry_at)
            logger.info(
                f"Consent expiry event for artifact {consent_artifact_id} processed successfully. ACKING.", extra={"agreement_id": agreement_id}
            )
            await message.ack()
            agreement_id = consent_artifact_id
        elif event_type == "data_retention_expiry":
            consent_artifact_id = payload.get("consent_artifact_id")
            data_element_id = payload.get("data_element_id")
            retention_expiry_at = payload.get("retention_expiry_at")

            logger.info(
                f"Starting to process Data expiry event for artifact {consent_artifact_id} at expiry {retention_expiry_at}",
                extra={"agreement_id": agreement_id},
            )
            await consent_worker_service.process_data_expiry_event(consent_artifact_id, data_element_id)
            logger.info(f"Data expiry event for artifact {consent_artifact_id} processed successfully. ACKING.", extra={"agreement_id": agreement_id})
            await message.ack()
            agreement_id = consent_artifact_id
        elif event_type == "data_retention_expiry_manual":
            consent_artifact_id = payload.get("consent_artifact_id")
            data_element_id = payload.get("data_element_id")

            logger.info(
                f"Starting to process Manual Data expiry event for artifact {consent_artifact_id} (instant expiry requested)...",
                extra={"agreement_id": agreement_id},
            )

            await consent_worker_service.process_data_expiry_event(consent_artifact_id, data_element_id, instant_expiry=True)
            logger.info(
                f"Manual Data expiry event for artifact {consent_artifact_id} processed successfully. ACKING.", extra={"agreement_id": agreement_id}
            )
            await message.ack()
            agreement_id = consent_artifact_id

        elif event_type == "otp_verification":
            consent_artifact_id = payload.get("consent_artifact_id")

            logger.info(
                f"Starting to process OTP verification event for artifact {consent_artifact_id}...",
                extra={"agreement_id": agreement_id},
            )

            await consent_worker_service.process_otp_verification_event(consent_artifact_id)
            logger.info(
                f"OTP verification event for artifact {consent_artifact_id} processed successfully. ACKING.", extra={"agreement_id": agreement_id}
            )
            await message.ack()
            agreement_id = consent_artifact_id

        else:

            if "consent_artifact" in payload and "artifact" in payload["consent_artifact"]:
                agreement_id = payload["consent_artifact"]["artifact"].get("agreement_id", "unknown_agreement")

            logger.info(f"Starting to process consent submission for agreement {agreement_id}...", extra={"agreement_id": agreement_id})
            await consent_worker_service.process_consent_submission(payload)
            logger.info(f"Consent submission for agreement {agreement_id} processed successfully. ACKING.", extra={"agreement_id": agreement_id})
            await message.ack()

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to process event for agreement {agreement_id}: {error_message}", exc_info=True, extra={"agreement_id": agreement_id})
        await handle_failure(message, agreement_id, error_message, channel)
    finally:
        logger.info(f"Finished processing event for agreement {agreement_id}.", extra={"agreement_id": agreement_id})


async def handle_failure(message: aio_pika.IncomingMessage, agreement_id: str, error_message: str, channel: aio_pika.Channel):
    """
    Handle failed consent processing events: send to retry queue or DLQ using the consumer channel.
    """
    x_death_headers = message.headers.get("x-death", [])
    retries = x_death_headers[0]["count"] if x_death_headers else 0
    current_attempt = retries + 1

    logger.warning(
        f"Handling failure for consent submission {agreement_id or 'None'} (Attempt {current_attempt})...", extra={"agreement_id": agreement_id}
    )

    if current_attempt >= MAX_RETRIES:
        logger.error(
            f"Consent submission {agreement_id} reached max retries ({MAX_RETRIES}). Sending to DLQ. CRITICAL ACK REQUIRED.",
            extra={"agreement_id": agreement_id},
        )

        await rabbitmq_pool.publish_message("consent_processing_dlq", message.body.decode(), channel)

        try:
            await message.ack()
            logger.info(f"Message {agreement_id} successfully ACKed from main queue after DLQ copy.", extra={"agreement_id": agreement_id})
        except Exception as ack_e:
            logger.critical(
                f"CRITICAL ACK FAILURE for {agreement_id}: Could not acknowledge message after DLQ copy. Error: {ack_e}. This may cause the consumer to stall.",
                exc_info=True,
                extra={"agreement_id": agreement_id},
            )
    else:
        logger.warning(
            f"Consent submission {agreement_id} failed. Nacking to trigger retry (attempt {current_attempt}).", extra={"agreement_id": agreement_id}
        )
        try:
            await message.nack(requeue=False)
            logger.info(f"Message {agreement_id} successfully NACKed (requeue=False). Triggering TTL.", extra={"agreement_id": agreement_id})
        except Exception as nack_e:
            logger.critical(
                f"CRITICAL NACK FAILURE for {agreement_id}: Could not nack message. Error: {nack_e}",
                exc_info=True,
                extra={"agreement_id": agreement_id},
            )


async def start_worker() -> None:
    setup_logging()
    await startup_db_clients()
    await rabbitmq_pool.init_pool()
    await declare_queues()

    gdb = get_mongo_master_db()

    while True:
        connection, channel = None, None
        try:
            connection, channel = await rabbitmq_pool.get_connection()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.get_queue("consent_processing_q")
            logger.info("Waiting for messages on 'consent_processing_q'...")

            await queue.consume(lambda msg: process_consent_processing_event(msg, channel, gdb))

            await asyncio.Future()

        except asyncio.CancelledError:
            logger.info("Consent processing consumer task cancelled gracefully.")
            break
        except Exception as main_e:
            logger.critical(f"CRITICAL EXCEPTION IN CONSENT PROCESSING CONSUMER LOOP (Restarting): {main_e}", exc_info=True)
            await asyncio.sleep(5)
            continue
        finally:
            pass


if __name__ == "__main__":
    asyncio.run(start_worker())
