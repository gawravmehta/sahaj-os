import json
import asyncio
import aio_pika
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.core.config import settings
from app.services.cookie_service import CookieManagementService
from app.services.assets_service import AssetService
from app.services.cookie_scan_service import CookieScanService
from app.crud.cookie_crud import CookieCrud
from app.crud.assets_crud import AssetCrud
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.core.logger import setup_logging, get_logger

db_client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)

concur_master_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_MASTER]
concur_logs_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_LOGS]


cookie_master_collection: AsyncIOMotorCollection = concur_master_db["cookie_master"]
asset_master_collection: AsyncIOMotorCollection = concur_master_db["asset_master"]
df_register_collection: AsyncIOMotorCollection = concur_master_db["df_register"]
business_logs_collection: AsyncIOMotorCollection = "app-logs-business"

asset_crud = AssetCrud(assets_master_collection=asset_master_collection)
cookie_crud = CookieCrud(cookie_collection=cookie_master_collection)
asset_service = AssetService(crud=asset_crud, business_logs_collection=business_logs_collection)
cookie_scan_service = CookieScanService(df_register_collection=df_register_collection)

cookie_management_service = CookieManagementService(
    crud=cookie_crud,
    asset_service=asset_service,
    cookie_scan_service=cookie_scan_service,
    business_logs_collection=business_logs_collection,
)


async def process_message(message: aio_pika.IncomingMessage):
    """
    Callback function to process messages from the queue.
    """
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            asset_id = payload.get("asset_id")
            user_id = payload.get("user_id")
            df_id = payload.get("df_id")

            if not asset_id or not user_id:
                logger.warning("Invalid message payload. Skipping.")
                return

            logger.info(f"Received scan request for asset {asset_id} by user {user_id}")

            user_payload = {"_id": user_id, "df_id": df_id}
            await cookie_management_service.scan_website_cookies(user=user_payload, asset_id=asset_id, classify=True)

            logger.info(f"Successfully processed scan request for asset {asset_id}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON received. Message body: ", message.body.decode())
        except Exception as e:
            logger.error(f"Error processing message for asset {asset_id}: {e}")


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    connection, channel = await rabbitmq_pool.get_connection()
    try:
        await channel.set_qos(prefetch_count=10)
        QUEUE_NAME = "cookie_scan_queue"

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        logger.info(f"Waiting for messages on '{QUEUE_NAME}'...")

        await queue.consume(process_message)

        await asyncio.Future()
    finally:

        await rabbitmq_pool.release_connection(connection, channel)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.cookie_scan_consumer")
    logger.info("Cookie scan consumer starting up.")
    asyncio.run(main())
