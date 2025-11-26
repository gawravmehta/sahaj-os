import asyncio
import json
import aio_pika


import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.core.config import settings
from app.db.rabbitmq import declare_queues, rabbitmq_pool, publish_message
from app.core.logger import setup_logging, get_logger
from bson import ObjectId


db_client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
concur_master_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_MASTER]
consent_artifacts_collection: AsyncIOMotorCollection = concur_master_db["consent_latest_artifacts"]


async def process_consent_expiry_event(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    artifact_id = "unknown_artifact"
    try:
        payload = json.loads(message.body.decode())
        artifact_id = payload.get("consent_artifact_id", "unknown_artifact")
        data_element_id = payload.get("data_element_id")
        purpose_id = payload.get("purpose_id")
        expiry_at = payload.get("expiry_at")

        logger.info(f"Starting to process consent expiry for artifact {artifact_id}, purpose {purpose_id}...")

        message_payload = payload

        await publish_message("consent_processing_q", json.dumps(message_payload), channel=channel)

        logger.info(f"Consent expiry for artifact {artifact_id}, purpose {purpose_id} processed and sent to consent_processing_q. ACKING.")
        await message.ack()

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to process consent expiry event for artifact {artifact_id}: {error_message}")

        await message.nack(requeue=False)
    finally:
        logger.info(f"Finished processing event for artifact {artifact_id}.")


async def start_expiry_consumer() -> None:
    await rabbitmq_pool.init_pool()

    await declare_queues()

    while True:
        connection, channel = None, None
        try:
            connection, channel = await rabbitmq_pool.get_connection()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.get_queue("consent_expiry_queue")
            logger.info("Waiting for messages on 'consent_expiry_queue'...")

            await queue.consume(lambda msg: process_consent_expiry_event(msg, channel))

            await asyncio.Future()

        except asyncio.CancelledError:
            logger.info("Consent expiry consumer task cancelled gracefully.")
            break
        except Exception as main_e:
            logger.critical(f"CRITICAL EXCEPTION IN CONSENT EXPIRY CONSUMER LOOP (Restarting): {main_e}")
            await asyncio.sleep(5)
            continue


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.consent_expiry_consumer")
    logger.info("Logger initialized for Consent Expiry Consumer")
    asyncio.run(start_expiry_consumer())
