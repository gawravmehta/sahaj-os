from typing import List
import asyncpg
from bson import ObjectId
import json
from datetime import datetime, timedelta
import secrets, string

from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import aio_pika
import asyncio

from app.db.rabbitmq import publish_message, rabbitmq_pool, declare_queues
from app.core.logger import setup_logging, get_logger

ln_tokens_table = "ln_tokens"

BATCH_SIZE = 1000
NOTIFICATION_TOKEN_SIZE = 6

MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

pg_pool: asyncpg.Pool | None = None

consent_notification_table = "consent_notifications"


async def create_tables():
    logger.info("Creating tables if not exist...")
    conn = await asyncpg.connect(settings.POSTGRES_DATABASE_URL)

    await conn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    await conn.execute(
        """
    CREATE TABLE IF NOT EXISTS consent_notifications (
        notification_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        notice_notification_id TEXT NOT NULL,
        df_id TEXT NOT NULL,
        dp_id TEXT NOT NULL,
        dp_email TEXT,
        dp_mobile TEXT,
        preferred_language TEXT,
        notification_medium TEXT[] DEFAULT '{}',
        notification_message TEXT,
        notification_url TEXT,
        cp_id TEXT,
        email_content TEXT,
        token TEXT,
        is_notification_read BOOLEAN DEFAULT FALSE,
        notification_status TEXT,
        created_at TIMESTAMP DEFAULT now(),
        sent_at TIMESTAMP,
        retry_attempts INT DEFAULT 0,
        is_notification_clicked BOOLEAN DEFAULT FALSE
    );
    """
    )

    await conn.execute(
        """
    CREATE TABLE IF NOT EXISTS campaigns (
        notice_notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        notification_medium TEXT[] DEFAULT '{}',
        df_id TEXT,
        created_by TEXT,
        for_dp_email BOOLEAN DEFAULT FALSE,
        for_dp_mobile BOOLEAN DEFAULT FALSE,
        notice_url TEXT,
        notification_status TEXT,
        created_at TIMESTAMP DEFAULT now(),
        dp_preferred_language TEXT[] DEFAULT '{}',
        dp_state TEXT,
        dp_counter INT DEFAULT 0,
        consent TEXT[] DEFAULT '{}'
    );
    """
    )

    await conn.execute(
        """
    CREATE TABLE IF NOT EXISTS global_joint_dps (
        dp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        dp_email TEXT,
        dp_mobile TEXT,
        dp_e TEXT,
        dp_m TEXT,
        df_relations JSONB DEFAULT '{}'
    );
    """
    )

    await conn.execute(
        """
    CREATE TABLE IF NOT EXISTS ln_tokens (
        token CHAR(6) PRIMARY KEY,
        df_id TEXT NOT NULL,
        dp_id TEXT NOT NULL,
        cp_id TEXT,
        expiry_at TIMESTAMP NOT NULL,
        CONSTRAINT ln_token_unique UNIQUE (token, dp_id, df_id)
    );
    """
    )

    await conn.close()
    logger.info("All tables created successfully!")


async def init_postgres_pool():
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(settings.POSTGRES_DATABASE_URL, min_size=1, max_size=5)
    return pg_pool


notice_notification = db["notice_notification"]
cp_master = db["cp_master"]

QUEUE_NAME = "notice_notification_queue"


async def update_campaign_notification_status(notice_notification_id: str, status: str, **kwargs):
    """Update the notification_status in the campaign collection."""
    await notice_notification.update_one(
        {"_id": ObjectId(notice_notification_id)},
        {"$set": {"notification_status": status, **kwargs}},
    )


async def send_email_notification(notice_notification_id: str):
    """Publish a message to the send_email queue to trigger email sending."""
    await publish_message(
        "send_email",
        json.dumps({"notice_notification_id": notice_notification_id}),
    )


async def fetch_dps(dp_tags: List[str]):
    logger.info("Fetching DPs from PostgreSQL...")
    """
    Fetch DPs from PostgreSQL.
    Assumes dpd table schema: (dp_id, dp_email[], dp_mobile[], dp_preferred_lang, dp_tags[], is_deleted)
    """
    pool = await init_postgres_pool()

    if dp_tags:
        query = """
            SELECT 
                dp_id,
                dp_email[1] AS dp_email,
                dp_mobile[1] AS dp_mobile,
                dp_preferred_lang,
                dp_tags
            FROM dpd
            WHERE is_deleted = FALSE
              AND dp_tags && $1::text[]
        """
        params = (dp_tags,)
    else:
        query = """
            SELECT 
                dp_id,
                dp_email[1] AS dp_email,
                dp_mobile[1] AS dp_mobile,
                dp_preferred_lang,
                dp_tags
            FROM dpd
            WHERE is_deleted = FALSE
        """
        params = ()

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        logger.info(f"Fetched {len(rows)} DPs from PostgreSQL.")
        return [dict(r) for r in rows]


async def insert_notifications_in_batches(notifications: list[dict], is_legacy: bool = False, send_email: bool = False):
    """Insert notifications into PostgreSQL in batches."""
    if not notifications:
        return

    try:
        pool = await init_postgres_pool()
        notice_notification_id = notifications[0]["notice_notification_id"]

        for i in range(0, len(notifications), BATCH_SIZE):
            batch = notifications[i : i + BATCH_SIZE]
            rows = [
                (
                    n["notice_notification_id"],
                    n["df_id"],
                    n["dp_id"],
                    n.get("dp_email", ""),
                    n.get("dp_mobile", None),
                    n.get("preferred_language", ""),
                    n.get("notification_medium", []),
                    n.get("notification_message", ""),
                    n.get("notification_url", ""),
                    n.get("cp_id") or "",
                    n.get("token", ""),
                    n.get("is_notification_read", False),
                    n.get("notification_status", ""),
                    n["created_at"],
                )
                for n in batch
            ]

            insert_query = f"""
                INSERT INTO {consent_notification_table} (
                    notice_notification_id, df_id, dp_id, dp_email, dp_mobile, preferred_language,
                    notification_medium, notification_message, notification_url, cp_id,
                    token, is_notification_read, notification_status, created_at
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,
                    $7,$8,$9,$10,$11,
                    $12,$13,$14
                )
            """

            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.executemany(insert_query, rows)

                if is_legacy:
                    ln_rows = [
                        (
                            n["token"],
                            n["df_id"],
                            n["dp_id"],
                            n.get("cp_id") or "",
                            datetime.now() + timedelta(weeks=24),
                        )
                        for n in batch
                    ]
                    ln_insert_query = f"""
                        INSERT INTO {ln_tokens_table} (
                            token, df_id, dp_id, cp_id, expiry_at
                        ) VALUES ($1,$2,$3,$4,$5)
                    """
                    await conn.executemany(ln_insert_query, ln_rows)

        if send_email:
            logger.info(f"Triggering email sending for campaign {notice_notification_id}")
            await send_email_notification(notice_notification_id)
    except Exception as e:
        logger.error(f"Error inserting notifications: {e}")


async def create_notifications_for_campaign(notice_notification_id: str):
    """Fetch DP and create notifications in the background."""
    logger.info(f"Adding notification for campaign {notice_notification_id}")
    await update_campaign_notification_status(notice_notification_id, "fetching_dp")

    campaign = await notice_notification.find_one({"_id": ObjectId(notice_notification_id)})
    if not campaign:
        logger.warning(f"Campaign {notice_notification_id} not found.")
        await update_campaign_notification_status(notice_notification_id, "not_found")
        return

    dp_tags = campaign.get("dp_tags", [])

    dps = await fetch_dps(dp_tags)
    batch_notifications = []
    dp_count = 0
    pool = await init_postgres_pool()

    async with pool.acquire() as conn:
        for dp in dps:
            logger.debug(f"Processing DP: {dp['dp_id']}")
            dp_id = str(dp["dp_id"])

            try:
                query = f"SELECT 1 FROM {consent_notification_table} WHERE notice_notification_id=$1 AND dp_id=$2 LIMIT 1"
                exists = await conn.fetchrow(query, notice_notification_id, dp_id)
                if exists:
                    logger.info(f"Notification already exists for DP: {dp_id}, skipping...")
                    continue
            except Exception as e:
                logger.error(f"Error checking existing notification for DP {dp_id}: {e}")
                continue

            preferred_language = dp.get("dp_preferred_lang", "eng")
            notification_medium = []
            if "email" in campaign.get("sending_medium", []):
                notification_medium.append("email")
            if "sms" in campaign.get("sending_medium", []):
                notification_medium.append("sms")

            if "in-app" in campaign.get("sending_medium", []):
                notification_medium.append("in-app")

            cp_doc = await cp_master.find_one({"_id": ObjectId(campaign["cp_id"])})
            if not cp_doc:
                logger.warning(f"CP for campaign {notice_notification_id} not found.")
                await update_campaign_notification_status(notice_notification_id, "cp_not_found")
                return

            token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(NOTIFICATION_TOKEN_SIZE))

            notification = {
                "notice_notification_id": notice_notification_id,
                "df_id": campaign["df_id"],
                "dp_id": dp_id,
                "dp_email": dp.get("dp_email", ""),
                "dp_mobile": dp.get("dp_mobile", ""),
                "preferred_language": preferred_language,
                "notification_medium": notification_medium,
                "notification_message": "Your consent request is pending.",
                "notification_url": f"{settings.CMP_NOTICE_WORKER_URL}/ln/{token}",
                "cp_id": campaign.get("cp_id"),
                "token": token,
                "is_notification_read": False,
                "notification_status": "pending",
                "created_at": datetime.now(),
            }

            batch_notifications.append(notification)
            dp_count += 1
            logger.debug(f"Batched notifications count: {len(batch_notifications)}")

            if len(batch_notifications) >= BATCH_SIZE:
                await insert_notifications_in_batches(batch_notifications, is_legacy=True, send_email=True)
                batch_notifications = []

    if batch_notifications:
        logger.info("Inserting final batch of notifications...")
        await insert_notifications_in_batches(batch_notifications, is_legacy=True, send_email=True)

    await update_campaign_notification_status(notice_notification_id, "fetched_dp", dp_counter=dp_count)
    logger.info(f"Finished Processing Campaign: {notice_notification_id} | DPs Processed: {dp_count}")


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info(f"Received message for notice notification: {data}")

            await create_tables()
            await create_notifications_for_campaign(data["notice_notification_id"])

        except Exception as e:
            logger.critical(f"Error processing message in notice_notification_consumer: {e}", exc_info=True)


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    # Use a dedicated connection for the consumer to avoid starving the pool
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
        virtualhost=settings.RABBITMQ_VHOST_NAME,
    )
    channel = await connection.channel()
    try:
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        logger.info(f"Waiting for messages on '{QUEUE_NAME}'...")

        await queue.consume(handle_message)

        await asyncio.Future()
    finally:
        if not connection.is_closed:
            await connection.close()


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.notice_notification_consumer")
    logger.info("Notice Notification Consumer starting up.")
    asyncio.run(main())
