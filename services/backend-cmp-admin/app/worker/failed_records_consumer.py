import csv
import os
import json
from datetime import datetime, UTC
from app.core.config import settings
from typing import Optional, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import aio_pika
from minio import Minio
import asyncio
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.core.logger import setup_logging, get_logger

MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

df_register_collection = db["df_register"]
genie_user_collection = db["cmp_users"]
notification_collection = db["notifications"]

s3_client = Minio(
    settings.S3_URL,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=True,
)

QUEUE_NAME = "failed_queue"


async def create_user_notification(
    df_id: Optional[str],
    users_list: Optional[List[str]],
    notification_title: Optional[str],
    notification_message: Optional[str] = None,
    redirection_route: Optional[str] = None,
    cta_url: Optional[str] = None,
    file_url: Optional[str] = None,
    priority: Optional[str] = "normal",
    icon_url: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    Creates a notification document in the database.

    Args:
        df_id (str): The ID of the data fiduciary (mandatory).
        users_list (List[str]): List of user IDs (mandatory, at least one user).
        notification_title (str): Title of the notification.
        notification_message (str): Message content of the notification.
        redirection_route (str): Route to redirect the user when the notification is clicked.
        cta_url (str): Call-to-action URL for the notification.
        file_url (str): URL of any associated file.
        priority (str): Priority of the notification (default: "normal").
        icon_url (str): URL of the notification icon (optional).
        category (str): Category of the notification (optional).

    Returns:
        dict: The created notification document.
    """

    df_checker = await df_register_collection.find_one({"df_id": df_id})
    if not df_checker:
        raise ValueError("df_id is mandatory")
    if not users_list or len(users_list) == 0:
        raise ValueError("users_list must contain at least one user ID")

    for user_id in users_list:
        user_checker = await genie_user_collection.find_one({"_id": ObjectId(user_id)})
        if not user_checker:
            raise ValueError(f"Invalid user ID: {user_id}")

    users_status = {user_id: {"is_read": False, "is_deleted": False} for user_id in users_list}

    notification_doc = {
        "df_id": df_id,
        "users": users_status,
        "notification_title": notification_title,
        "notification_message": notification_message,
        "redirection_route": redirection_route,
        "cta_url": cta_url,
        "file_url": file_url,
        "priority": priority,
        "icon_url": icon_url,
        "category": category,
        "created_at": datetime.now(UTC),
    }

    try:
        notification_collection.insert_one(notification_doc)
    except Exception as e:
        raise Exception(f"Failed to create notification: {str(e)}")


def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Upload the file to MinIO (S3-like storage) only if it has data rows."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) <= 1:
            logger.info(f"No failed records to upload for {file_path}. Only header found. Skipping upload.")
            return False

        s3_client.fput_object(bucket_name, s3_key, file_path)
        logger.info(f"Successfully uploaded {file_path} to MinIO: {bucket_name}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {file_path} to MinIO: {e}")
        return False


def append_failed_records_to_csv(failed_records, file_path):
    """Append failed records to a CSV file."""
    if not file_path:
        raise ValueError("The file path provided is empty.")
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path) and dir_path != "":
        os.makedirs(dir_path, exist_ok=True)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(["dp_system_id", "dp_email", "dp_mobile", "failure_reason"])

        for record in failed_records:
            dp = record["dp"]
            writer.writerow(
                [
                    dp.get("dp_system_id"),
                    ", ".join(dp.get("dp_email", [])),
                    ", ".join(str(m) for m in dp.get("dp_mobile", [])),
                    record["failure_reason"],
                ]
            )


def get_failed_file(df_id):
    """Generate a consistent file name for a df_id per day."""
    today_str = datetime.now().strftime("%Y%m%d")
    return f"failed_records_{df_id}_{today_str}.csv"


async def handle_message(message: aio_pika.IncomingMessage):
    """Callback function to handle failed records and append to CSV."""
    async with message.process():
        try:
            logger.info("Processing new message for failed records consumer.")
            body = message.body.decode()
            data = json.loads(body)
            logger.debug(f"Received message: {data}")
            df_id = data.get("df_id")
            batch_tag = data.get("batch_tag", "")
            failed_records = data.get("failed_records", [])

            local_failed_file = get_failed_file(df_id)

            append_failed_records_to_csv(failed_records, local_failed_file)
            logger.info(f"Failed records for df_id {df_id} appended to {local_failed_file}")

            if batch_tag == "end":
                timestamp_str = datetime.now(UTC).strftime("%H%M%S")
                upload_failed_file_name = f"failed_records_{df_id}_{datetime.now().strftime('%Y%m%d')}_{timestamp_str}.csv"

                object_name = f"failed_records/{upload_failed_file_name}"

                uploaded = upload_file_to_s3(local_failed_file, settings.FAILED_RECORDS_BUCKET_EXTERNAL, object_name)

                if uploaded:
                    cursor = genie_user_collection.find({"df_id": df_id})
                    users = await cursor.to_list(length=None)
                    users_list = [str(u["_id"]) for u in users]
                    notification_title = "Failed-records report ready"
                    notification_message = f"A report of failed records for batch {df_id} is now available."
                    endpoint = settings.S3_URL
                    file_url = f"{endpoint}/{settings.FAILED_RECORDS_BUCKET_EXTERNAL}/{object_name}"
                    try:
                        await create_user_notification(
                            df_id=df_id,
                            users_list=users_list,
                            notification_title=notification_title,
                            notification_message=notification_message,
                            file_url=file_url,
                            category="reports",
                            priority="high",
                        )
                        logger.info("User notification created.")
                    except Exception as notif_err:
                        logger.warning(f"Failed to create user notification: {notif_err}")
                    os.remove(local_failed_file)
                    logger.info(f"Deleted local file {local_failed_file} after upload.")
                else:
                    logger.info(f"Keeping local file {local_failed_file} (either empty or upload failed).")

                logger.info(f"Batch {df_id} processing complete. Uploaded {local_failed_file} as {upload_failed_file_name}")
            else:
                logger.info(f"Failed records for df_id {df_id} received, batch_tag != 'end', continuing to append.")

        except Exception as e:
            logger.critical(f"Error processing message in failed_records_consumer: {e}", exc_info=True)


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    connection, channel = await rabbitmq_pool.get_connection()
    try:
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        logger.info(f"Waiting for messages on '{QUEUE_NAME}'...")

        await queue.consume(handle_message)

        await asyncio.Future()
    finally:

        await rabbitmq_pool.release_connection(connection, channel)


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.failed_records_consumer")
    logger.info("Failed Records Consumer starting up.")
    asyncio.run(main())
