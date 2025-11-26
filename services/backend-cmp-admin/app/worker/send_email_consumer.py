from io import BytesIO
import os
import time
from bson import ObjectId
import json

from datetime import datetime
import requests
from urllib.parse import quote_plus
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
from app.core.config import settings
from fastapi import HTTPException
from minio import Minio
import aio_pika
import asyncio
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.utils.mail_sender_utils import mail_sender
from app.utils.sms_sender_utils import send_sms_notification
from app.core.logger import setup_logging, get_logger

BATCH_SIZE = 2
MAX_RETRIES = 3
UPDATE_THRESHOLD = 10
QUEUE_NAME = "send_email"


MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

pg_pool: asyncpg.Pool | None = None


async def init_postgres_pool():
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(settings.POSTGRES_DATABASE_URL, min_size=1, max_size=5)
    return pg_pool


cp_master = db["cp_master"]
df_register_collection = db["df_register_collection"]
notice_notification = db["notice_notification"]
df_register_collection = db["df_register"]


s3_client = Minio(
    settings.S3_URL,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    secure=True,
)


async def generate_dynamic_html(cp_id: str, token: str, html_template: str, notification_id: str, df_id: str):
    logger.info(f"Generating dynamic HTML for notification {notification_id}, DF {df_id}")

    df_data = await df_register_collection.find_one({"df_id": df_id})
    if not df_data:
        logger.error(f"DF data not found for df_id: {df_id}")
    df_name = df_data.get("org_info", {}).get("name", "Data Fiduciary")
    df_logo_url = df_data.get("org_info", {}).get("df_logo_url", "")
    df_website_url = df_data.get("org_info", {}).get("website_url")
    df_address = df_data.get("org_info", {}).get("address", "N/A")

    dpo_name = df_data.get("dpo_information", {}).get("full_name", "N/A")
    dpo_email = df_data.get("dpo_information", {}).get("email", "N/A")
    dpo_mobile = df_data.get("dpo_information", {}).get("mobile", "N/A")

    base_url = f"{settings.CMP_ADMIN_BACKEND_URL}/api/v1/notice-notification"

    notice_worker_base_url = f"{settings.CMP_NOTICE_WORKER_URL}/api/v1/ln"

    pixel_url = f"{base_url}/track/{notification_id}.png"

    cp_data = await cp_master.find_one({"_id": ObjectId(cp_id)})

    data_elements = cp_data["data_elements"]

    data_collection_items = "".join(f"<li>{item['de_name']}</li>" for item in data_elements)

    purpose_rows = ""
    for de in data_elements:
        de_name = de["de_name"]
        purposes = de.get("purposes", [])
        purpose_count = len(purposes)
        if purpose_count == 0:
            purpose_rows += f"<tr><td>{de_name}</td><td></td></tr>"
        else:
            for idx, purpose in enumerate(purposes):
                if idx == 0:

                    rowspan_attr = f' rowspan="{purpose_count}"' if purpose_count > 1 else ""
                    purpose_rows += f"""
                        <tr>
                            <td{rowspan_attr}>{de_name}</td>
                           <td style="width: 385.087px">{purpose['purpose_title']}</td>
                        </tr>
                    """
                else:
                    purpose_rows += f"""
                        <tr>
                           <td style="width: 385.087px">{purpose['purpose_title']}</td>
                        </tr>
                    """

    purpose_table_html = f"""
    <li>
    <h5 class="list-heading">Purpose Of Data Processing</h5>
    <p class="para-div list1">
        Each type of collected data will be used for specific purposes:
    </p>
    <table style="font-size: 12px; margin-bottom: 20px; border-collapse: collapse;">
        <thead>
        <tr>
            <th>Data Element</th>
            <th>Purpose</th>
        </tr>
        </thead>
        <tbody>
        {purpose_rows}
        </tbody>
    </table>
    </li>
    """

    html_content = html_template.replace("{{ data_collection_items }}", data_collection_items)

    html_content = html_content.replace("{{ purpose_processing_table }}", purpose_table_html)

    html_content = html_content.replace("{{pixel_url}}", pixel_url)

    html_content = html_content.replace("{{token}}", token)

    html_content = html_content.replace("{{event_id}}", str(notification_id))

    html_content = html_content.replace("{{df_name}}", df_name)
    html_content = html_content.replace("{{df_logo_url}}", df_logo_url)
    html_content = html_content.replace("{{df_website_url}}", df_website_url)
    html_content = html_content.replace("{{df_address}}", df_address)

    html_content = html_content.replace("{{dpo_name}}", dpo_name)
    html_content = html_content.replace("{{dpo_email}}", dpo_email)
    html_content = html_content.replace("{{dpo_mobile}}", dpo_mobile)

    html_content = html_content.replace("{{base_url}}", base_url)

    html_content = html_content.replace("{{notice_worker_base_url}}", notice_worker_base_url)

    return html_content


def read_email_template(template_name: str) -> str:
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, template_name)

        with open(template_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read template: {e}")


async def prepare_notification_content(notification):
    """Generate and upload HTML content for a notification (shared by both email and SMS)"""
    email_html = read_email_template("legacy_notice.html")
    email_html = await generate_dynamic_html(
        notification["cp_id"],
        notification["token"],
        email_html,
        notification["notification_id"],
        notification["df_id"],
    )

    if not s3_client.bucket_exists(settings.NOTICE_WORKER_BUCKET):
        s3_client.make_bucket(settings.NOTICE_WORKER_BUCKET)

    file_path = f"legacy_notices/{notification['df_id']}/{notification['cp_id']}_{notification['notification_id']}.html"
    html_bytes = BytesIO(email_html.encode("utf-8"))

    s3_client.put_object(
        bucket_name=settings.NOTICE_WORKER_BUCKET,
        object_name=file_path,
        data=html_bytes,
        length=len(html_bytes.getvalue()),
        content_type="text/html",
    )

    return email_html


async def update_notification_status(notification_id, new_status, retry_attempts, sent_at):
    update_query = """
        UPDATE consent_notifications
        SET 
            notification_status = $1,
            sent_at = $2,
            retry_attempts = $3
        WHERE notification_id = $4
    """
    try:
        async with pg_pool.acquire() as conn:
            await conn.execute(update_query, new_status, sent_at, retry_attempts, notification_id)
        logger.info(f"Updated notification {notification_id} status to {new_status}")
    except Exception as e:
        logger.error(f"Failed to update notification {notification_id}: {e}")


async def send_email_notification(notification, email_html):
    if not notification["dp_email"]:
        logger.warning(f"No email provided for notification {notification.get('notification_id')} — skipping email.")
        return False

    email_html = email_html.replace("/mln", "/ln")

    for attempt in range(MAX_RETRIES):
        try:
            await mail_sender(
                destination_email=notification["dp_email"],
                subject="Action Required: Your Consent Request is Pending",
                email_template=email_html,
                df_register_collection=df_register_collection,
            )
            logger.info(f"Email sent to {notification['dp_email']} (Attempt {attempt+1}) for notification {notification.get('notification_id')}")
            return True
        except Exception as e:
            logger.error(
                f"Email attempt {attempt+1} failed for {notification.get('dp_email')}, notification {notification.get('notification_id')}: {e}"
            )
            time.sleep(1)

    return False


async def fetch_pending_notifications(notice_notification_id):
    query = """
        SELECT 
            notification_id,
            notice_notification_id,
            df_id,
            dp_id,
            dp_email,
            dp_mobile,
            preferred_language,
            notification_medium,
            notification_message,
            notification_url,
            cp_id,
            email_content,
            token,
            is_notification_read,
            notification_status,
            retry_attempts
        FROM consent_notifications
        WHERE notice_notification_id = $1
          AND notification_status IN ('pending', 'error')
        LIMIT $2
    """
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(query, notice_notification_id, BATCH_SIZE)
    return rows


async def get_remaining_notifications(notice_notification_id):
    query = """
        SELECT COUNT(*)
        FROM consent_notifications
        WHERE notice_notification_id = $1
          AND notification_status IN ('pending', 'error')
    """
    async with pg_pool.acquire() as conn:
        row = await conn.fetchval(query, notice_notification_id)
    return row


async def process_pending_notifications(notice_notification_id):
    notifications = await fetch_pending_notifications(notice_notification_id)

    if not notifications:
        logger.info(f"No pending notifications to process for campaign {notice_notification_id}.")
        return

    campaigns = {}
    for notification in notifications:
        cid = notification["notice_notification_id"]
        if cid not in campaigns:
            campaigns[cid] = []
        campaigns[cid].append(dict(notification))

    for cid, campaign_notifications in campaigns.items():
        logger.info(f"Processing campaign: {cid} ({len(campaign_notifications)} notifications)")

        for notification in campaign_notifications:
            logger.info(f"Sending notification: {notification['notification_id']}")
            notification_other_details = await notice_notification.find_one({"_id": ObjectId(notification["notice_notification_id"])})

            mediums = notification.get("notification_medium", [])
            if not mediums:
                logger.warning(f"No notification medium specified for notification {notification.get('notification_id')} — skipping.")
                continue

            email_html = await prepare_notification_content(notification)
            email_success = None

            if "email" in mediums:
                email_success = await send_email_notification(notification, email_html)

            if "sms" in mediums:
                logger.info(f"Sending SMS notification for notification {notification.get('notification_id')}")
                try:
                    sms_success = await send_sms_notification(
                        notification["dp_mobile"],
                        notification["token"],
                        df_register_collection,
                        notification_other_details.get("sms_template_name"),
                    )
                except Exception as e:
                    logger.error(f"SMS sending failed for notification {notification.get('notification_id')}: {e}")
                    sms_success = False

            if "email" in mediums:
                new_status = "sent" if email_success else "error"
            elif "sms" in mediums:
                new_status = "sent" if sms_success else "error"
            elif "in-app" in mediums:
                new_status = "sent"
            else:
                new_status = "error"

            retry_attempts = notification.get("retry_attempts", 0) + 1
            sent_at = datetime.now()

            await update_notification_status(
                notification["notification_id"],
                new_status,
                retry_attempts,
                sent_at,
            )

        remaining = await get_remaining_notifications(cid)
        if remaining == 0:
            await notice_notification.update_one(
                {"_id": ObjectId(cid)},
                {"$set": {"notification_status": "completed"}},
            )
            logger.info(f"Campaign {cid} marked as completed.")

    logger.info("Finished processing all campaigns.")


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info(f"Received message for send_email_consumer: {data}")

            await process_pending_notifications(data["notice_notification_id"])

        except Exception as e:
            logger.critical(f"Error processing message in send_email_consumer: {e}", exc_info=True)


async def main() -> None:

    await init_postgres_pool()

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
    logger = get_logger("worker.send_email_consumer")
    logger.info("Send Email Consumer starting up.")
    asyncio.run(main())
