import asyncio
import uuid
import aio_pika
import json
from app.core.config import settings
from minio import Minio
import hashlib
from datetime import datetime, UTC
from pydantic import BaseModel, computed_field, field_validator
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
import re

from app.db.rabbitmq import publish_message, rabbitmq_pool, declare_queues
from app.core.logger import setup_logging, get_logger


CHUNK_SIZE = 1000
REQUIRED_FIELDS = ["dp_identifiers", "dp_system_id"]
BOOLEAN_FIELDS = ["is_active", "is_deleted", "is_legacy"]

COPY_MIN_ROWS = 1000

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


dp_file_processing_collection = db["dp_file_processing"]
df_register_collection = db["df_register"]
genie_user_collection = db["cmp_users"]
notification_collection = db["notifications"]
batch_collection = db["batch_process"]


s3_client = Minio(
    settings.S3_URL,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.S3_SECURE
)


RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_USER = settings.RABBITMQ_USER
RABBITMQ_PASSWORD = settings.RABBITMQ_PASSWORD
RABBITMQ_VHOST = settings.RABBITMQ_VHOST_NAME
QUEUE_NAME = "dp_external"


EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
MOBILE_REGEX = re.compile(r"^\d{10}$")


class BulkDpApiModel(BaseModel):
    dp_system_id: str
    dp_identifiers: List[str]
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[int]] = []
    dp_other_identifier: Optional[List[str]] = []
    dp_preferred_lang: Optional[str] = "eng"
    dp_country: Optional[str] = ""
    dp_state: Optional[str] = ""
    dp_active_devices: Optional[List[str]] = []
    dp_tags: Optional[List[str]] = []
    is_active: Optional[bool] = False
    is_legacy: bool
    created_at_df: datetime
    last_activity: Optional[datetime]

    @field_validator("dp_preferred_lang", "dp_country", "dp_state", "dp_tags", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("dp_email", "dp_active_devices", mode="before")
    def lowercase_list_fields(cls, v):
        if isinstance(v, list):
            return [item.lower() for item in v if isinstance(item, str)]
        return v


class AddBulkDPModel(BulkDpApiModel):
    added_by: str
    added_with: str = "/api/v1/data_principal/add_bulk"
    is_deleted: bool = False
    consent_status: str = "unsent"

    @computed_field
    @property
    def dp_e(self) -> List[str]:
        if self.dp_email:
            return [hashlib.shake_256(email.strip().encode("utf-8")).hexdigest(32) for email in self.dp_email]
        return []

    @computed_field
    @property
    def dp_m(self) -> List[str]:
        if self.dp_mobile:
            return [hashlib.shake_256(str(mobile).strip().encode("utf-8")).hexdigest(32) for mobile in self.dp_mobile]
        return []


def validate_dp_data(dp: BulkDpApiModel) -> List[str]:
    errors = []
    if "email" in dp.dp_identifiers and not dp.dp_email:
        errors.append("'email' identifier present but no dp_email provided")
    if "mobile" in dp.dp_identifiers and not dp.dp_mobile:
        errors.append("'mobile' identifier present but no dp_mobile provided")
    if not (dp.dp_email or dp.dp_mobile):
        errors.append("Missing both email and mobile")

    for email in dp.dp_email or []:
        if not EMAIL_REGEX.match(email):
            errors.append(f"Invalid email format: {email}")
    for mobile in dp.dp_mobile or []:
        if not MOBILE_REGEX.match(str(mobile)):
            errors.append(f"Invalid mobile number: {mobile}")

    return errors


def collect_incoming_keys(dp_data_list: List[BulkDpApiModel]):
    ids = {dp.dp_system_id for dp in dp_data_list}
    emails = {e for dp in dp_data_list for e in (dp.dp_email or [])}
    mobiles = {str(m) for dp in dp_data_list for m in (dp.dp_mobile or [])}
    return ids, emails, mobiles


async def fetch_existing_rows(ids, emails, mobiles):
    pool = await init_postgres_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT dp_system_id, dp_email, dp_mobile
            FROM dpd
            WHERE dp_system_id = ANY($1)
               OR dp_email && $2
               OR dp_mobile && $3
            """,
            list(ids),
            list(emails),
            list(mobiles),
        )
        return rows


def duplicate_handler(existing_rows, dp_data_list):
    to_insert, to_fail = [], []
    existing_ids = {row[0] for row in existing_rows}
    existing_emails = {e for row in existing_rows for e in (row[1] or [])}
    existing_mobiles = {str(m) for row in existing_rows for m in (row[2] or [])}

    failure_reasons = {}
    seen_dp_system_ids = set()
    seen_emails = set()
    seen_mobiles = set()

    for dp in dp_data_list:
        sid = dp.dp_system_id
        emails = set(dp.dp_email or [])
        mobiles = {str(m) for m in (dp.dp_mobile or [])}

        if sid in seen_dp_system_ids or any(email in seen_emails for email in emails) or any(mobile in seen_mobiles for mobile in mobiles):
            failure_reasons[sid] = "Duplicate record in batch"
            to_fail.append(dp)
        else:
            seen_dp_system_ids.add(sid)
            seen_emails.update(emails)
            seen_mobiles.update(mobiles)

            if sid in existing_ids or emails & existing_emails or mobiles & existing_mobiles:
                failure_reasons[sid] = "Duplicate record in database"
                to_fail.append(dp)
            else:
                to_insert.append(dp)

    return to_insert, to_fail, failure_reasons


async def bulk_insert_records(df_id, to_insert):
    if not to_insert:
        return 0

    pool = await init_postgres_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            records = []
            for dp in to_insert:
                dp_model = AddBulkDPModel(
                    dp_system_id=dp.dp_system_id,
                    dp_identifiers=dp.dp_identifiers,
                    dp_email=dp.dp_email,
                    dp_mobile=dp.dp_mobile,
                    dp_other_identifier=dp.dp_other_identifier,
                    dp_preferred_lang=dp.dp_preferred_lang,
                    dp_country=dp.dp_country,
                    dp_state=dp.dp_state,
                    dp_active_devices=dp.dp_active_devices,
                    dp_tags=dp.dp_tags,
                    is_active=dp.is_active,
                    is_legacy=dp.is_legacy,
                    created_at_df=dp.created_at_df,
                    last_activity=dp.last_activity,
                    added_by="",
                    added_with="/api/v1/dp-bulk-external",
                    is_deleted=False,
                    consent_status="unsent",
                )
                records.append(
                    (
                        str(uuid.uuid4()),
                        dp_model.dp_system_id,
                        dp_model.dp_identifiers,
                        dp_model.dp_email,
                        [str(m) for m in (dp_model.dp_mobile or [])],
                        [str(o) for o in (dp_model.dp_other_identifier or [])],
                        dp_model.dp_preferred_lang,
                        dp_model.dp_country,
                        dp_model.dp_state,
                        dp_model.dp_active_devices,
                        dp_model.dp_tags,
                        dp_model.is_active,
                        dp_model.is_legacy,
                        dp_model.added_by,
                        dp_model.added_with,
                        dp_model.created_at_df,
                        dp_model.last_activity,
                        dp_model.dp_e,
                        dp_model.dp_m,
                        dp_model.is_deleted,
                        dp_model.consent_status,
                    )
                )

            await conn.executemany(
                """
                INSERT INTO dpd (
                    dp_id,
                    dp_system_id,
                    dp_identifiers,
                    dp_email,
                    dp_mobile,
                    dp_other_identifier,
                    dp_preferred_lang,
                    dp_country,
                    dp_state,
                    dp_active_devices,
                    dp_tags,
                    is_active,
                    is_legacy,
                    added_by,
                    added_with,
                    created_at_df,
                    last_activity,
                    dp_e,
                    dp_m,
                    is_deleted,
                    consent_status
                )
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
                        $11,$12,$13,$14,$15,$16,$17,$18, $19, $20, $21)
                """,
                records,
            )
    return len(records)


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    try:
        body = message.body.decode()
        data = json.loads(body)
        logger.info(f"Received message for external DP processing: {data.get('batch_tag')}")

        valid_dps_raw = data.get("valid_data", [])
        df_id = data.get("df_id")
        batch_tag = data.get("batch_tag")
        token = data.get("token")
        valid_dps = [BulkDpApiModel(**dp) for dp in valid_dps_raw]

        await message.ack()

        all_failed = []
        valid_final = []
        for dp in valid_dps:
            errors = validate_dp_data(dp)
            if errors:
                all_failed.append(
                    {
                        "dp": json.loads(dp.model_dump_json()),
                        "failure_reason": "; ".join(errors),
                    }
                )
            else:
                valid_final.append(dp)

        ids, emails, mobiles = collect_incoming_keys(valid_final)
        existing_rows = await fetch_existing_rows(ids, emails, mobiles)
        to_insert, to_fail_dupes, failure_reasons = duplicate_handler(existing_rows, valid_final)

        for dp in to_fail_dupes:
            all_failed.append(
                {
                    "dp": json.loads(dp.model_dump_json()),
                    "failure_reason": failure_reasons.get(dp.dp_system_id, "Duplicate record"),
                }
            )

        inserted_count = await bulk_insert_records(df_id, to_insert)
        logger.info(f"Inserted {inserted_count} records for df_id {df_id}")
        logger.warning(f"Failed records count: {len(all_failed)}")

        if all_failed:
            failed_message = json.dumps(
                {
                    "df_id": df_id,
                    "batch_tag": batch_tag,
                    "failed_records": all_failed,
                }
            )
            logger.warning(f"Publishing failed records message for df_id {df_id} with batch_tag {batch_tag}")
            await publish_message("failed_queue", failed_message)
            logger.warning(f"Failed records sent to failed_queue for df_id {df_id} with batch_tag {batch_tag}")

        if batch_tag == "end":
            end_time = datetime.now(UTC)
            await batch_collection.update_one(
                {"df_id": df_id, "token": token},
                {"$set": {"status": "end", "token": None, "end_time": end_time}},
            )
            end_message = json.dumps({"df_id": df_id, "batch_tag": "end", "failed_records": []})
            await publish_message("failed_queue", end_message)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in dp_external_processing_consumer: {e!r}")
        await message.reject(requeue=False)
    except Exception as e:
        logger.critical(f"Failed to process message in dp_external_processing_consumer: {e!r}")

        await message.nack(requeue=True)


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
    logger = get_logger("worker.dp_external_processing_consumer")
    logger.info("DP External Processing Consumer starting up.")
    asyncio.run(main())
