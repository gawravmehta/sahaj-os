import asyncio
import aio_pika
import json
from app.core.config import settings
import os
from minio import Minio
import hashlib
from datetime import datetime, UTC, timezone
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
import asyncpg
import pandas as pd
import re
import uuid
import io
import ast
from bson import ObjectId
import csv
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.core.logger import setup_logging, get_logger


CHUNK_SIZE = 1000
REQUIRED_FIELDS = ["dp_identifiers", "dp_system_id"]
BOOLEAN_FIELDS = ["is_active", "is_deleted", "is_legacy"]

COPY_MIN_ROWS = 1000

MONGO_URL = settings.MONGO_URI
DB_NAME = settings.DB_NAME_CONCUR_MASTER

client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

pg_pool: asyncpg.Pool | None = None


async def init_postgres_pool():
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(settings.POSTGRES_DATABASE_URL, min_size=1, max_size=5)
    return pg_pool


dp_file_processing_collection: AsyncIOMotorCollection = db["dp_file_processing"]
df_register_collection: AsyncIOMotorCollection = db["df_register"]
genie_user_collection: AsyncIOMotorCollection = db["cmp_users"]
notification_collection: AsyncIOMotorCollection = db["notifications"]


class BulkImportDataPrincipal(BaseModel):
    dp_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dp_system_id: str
    dp_identifiers: List[str]
    dp_email: Optional[List[str]] = []
    dp_mobile: Optional[List[str]] = []
    dp_other_identifier: Optional[List[str]] = []
    dp_preferred_lang: str
    dp_country: str
    dp_state: str
    dp_active_devices: List[str]
    dp_tags: Optional[List[str]] = []
    is_active: bool
    is_legacy: bool
    created_at_df: datetime
    last_activity: datetime

    added_by: str
    added_with: str = "upload"
    is_deleted: bool = False
    consent_status: str = "unsent"

    @field_validator("dp_preferred_lang", "dp_country", "dp_tags", "dp_state", mode="before")
    def lowercase_str_fields(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("dp_email", "dp_active_devices", mode="before")
    def lowercase_list_fields(cls, v):
        if isinstance(v, list):
            return [item.lower() for item in v if isinstance(item, str)]
        return v

    @computed_field
    @property
    def dp_e(self) -> str:
        if self.dp_email:
            hashed_emails = [hashlib.shake_256(str(email).strip().encode("utf-8")).hexdigest(32) for email in self.dp_email if email]
        else:
            hashed_emails = []

        return hashed_emails

    @computed_field
    @property
    def dp_m(self) -> Optional[str]:
        if self.dp_mobile:
            hashed_mobiles = [hashlib.shake_256(str(mobile).strip().encode("utf-8")).hexdigest(32) for mobile in self.dp_mobile if mobile]
        else:
            hashed_mobiles = []

        return hashed_mobiles


s3_client = Minio(settings.S3_URL, access_key=settings.MINIO_ROOT_USER, secret_key=settings.MINIO_ROOT_PASSWORD, secure=settings.S3_SECURE)

QUEUE_NAME = "dp_processing"


def safe_json_parse(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parts = [part.strip().strip("'\"") for part in value.split(",") if part.strip()]
                return parts if len(parts) > 0 else value
    return value


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
    logger.info(f"Creating user notification for DF: {df_id}, Title: {notification_title}")

    df_checker = await df_register_collection.find_one({"df_id": df_id})
    if not df_checker:
        logger.error(f"Failed to create notification: df_id {df_id} is mandatory or not found.")
        raise ValueError("df_id is mandatory")
    if not users_list or len(users_list) == 0:
        logger.error("Failed to create notification: users_list must contain at least one user ID.")
        raise ValueError("users_list must contain at least one user ID")

    for user_id in users_list:
        user_checker = await genie_user_collection.find_one({"_id": ObjectId(user_id)})
        if not user_checker:
            logger.error(f"Failed to create notification: Invalid user ID: {user_id}")
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
        await notification_collection.insert_one(notification_doc)
        logger.info(f"Notification '{notification_title}' created successfully for {df_id}.")
    except Exception as e:
        logger.critical(f"Failed to create notification: {str(e)}")
        raise Exception(f"Failed to create notification: {str(e)}")


def quote_ident(ident: str) -> str:
    """Double-quote an identifier safely for SQL constructing column list."""
    return '"' + ident.replace('"', '""') + '"'


async def process_file(
    contents: bytes,
    filename: str,
    df_id: str,
    genie_user_id: str,
    is_legacy: bool = False,
    dp_tags: Optional[List[str]] = None,
):
    """
    Reworked to use PostgreSQL (asyncpg) instead of ClickHouse.
    Important: expected PostgreSQL table naming convention: <df_id>_dpd
    where df_id only contains [A-Za-z0-9_].
    """

    table_name = f"dpd"

    try:
        await dp_file_processing_collection.find_one_and_update(
            {"filename": filename},
            {"$set": {"status": "processing", "started_at": datetime.now(timezone.utc)}},
        )

        if filename.endswith(".csv"):
            chunks = pd.read_csv(
                io.StringIO(contents.decode("utf-8")),
                chunksize=CHUNK_SIZE,
                keep_default_na=False,
                converters={
                    "dp_identifiers": safe_json_parse,
                    "dp_email": safe_json_parse,
                    "dp_mobile": lambda x: [str(i) for i in safe_json_parse(x)] if pd.notna(x) else [],
                    "dp_active_devices": safe_json_parse,
                },
            )
        else:
            df = pd.read_excel(io.BytesIO(contents))
            chunks = (df.iloc[i : i + CHUNK_SIZE] for i in range(0, len(df), CHUNK_SIZE))
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}", exc_info=True)
        await dp_file_processing_collection.find_one_and_update(
            {"filename": filename},
            {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc), "message": f"Error reading file: {e}"}},
        )
        return

    existing_emails = {}
    existing_email_legacy = {}
    existing_mobiles = {}
    existing_mobile_legacy = {}

    pool = await init_postgres_pool()

    async with pool.acquire() as conn:
        try:

            email_query = f"""
                SELECT dp_email, is_legacy
                FROM {table_name}
                WHERE dp_email IS NOT NULL
            """
            rows = await conn.fetch(email_query)
            for row in rows:
                dp_email = row["dp_email"]
                row_legacy = row["is_legacy"]

                emails = dp_email if isinstance(dp_email, (list, tuple)) else [dp_email] if dp_email is not None else []

                for email in emails:
                    if email is None:
                        continue
                    existing_email_legacy[email] = bool(row_legacy)

        except Exception as e:
            logger.error(f"Error fetching existing emails for {table_name}: {e}", exc_info=True)
            await dp_file_processing_collection.find_one_and_update(
                {"filename": filename},
                {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc), "message": f"Error fetching existing emails: {e}"}},
            )
            return

        try:
            mobile_query = f"""
                SELECT dp_mobile, is_legacy
                FROM {table_name}
                WHERE dp_mobile IS NOT NULL
            """
            rows = await conn.fetch(mobile_query)
            for row in rows:
                dp_mobile = row["dp_mobile"]
                row_legacy = row["is_legacy"]

                mobiles = dp_mobile if isinstance(dp_mobile, (list, tuple)) else [dp_mobile] if dp_mobile is not None else []
                for mobile in mobiles:
                    if mobile is None:
                        continue
                    m = str(mobile)
                    existing_mobile_legacy[m] = bool(row_legacy)

        except Exception as e:
            logger.error(f"Error fetching existing mobiles for {table_name}: {e}", exc_info=True)
            await dp_file_processing_collection.find_one_and_update(
                {"filename": filename},
                {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc), "message": f"Error fetching existing mobiles: {e}"}},
            )
            return

        failed_records = []
        success_count = 0
        update_count = 0
        batch = []
        seen_system_ids = set()

        for chunk in chunks:
            for index, row in chunk.iterrows():
                record = row.where(pd.notnull(row), None).to_dict()
                try:

                    for field in [
                        "dp_identifiers",
                        "dp_email",
                        "dp_mobile",
                        "dp_other_identifier",
                        "dp_active_devices",
                        "dp_tags",
                    ]:
                        if field in record:
                            parsed = safe_json_parse(record[field])
                            if isinstance(parsed, list):
                                record[field] = parsed
                            elif parsed is None:
                                record[field] = []
                            else:
                                record[field] = [parsed]

                    core_identifiers = record.get("dp_identifiers", [])
                    if "email" in core_identifiers and not record.get("dp_email"):
                        failed_records.append(
                            {
                                "row": index + 1,
                                "error": "Email is required when 'email' is in core identifiers",
                                **{k: str(v) for k, v in record.items()},
                            }
                        )
                        continue

                    if "mobile" in core_identifiers and not record.get("dp_mobile"):
                        failed_records.append(
                            {
                                "row": index + 1,
                                "error": "Mobile is required when 'mobile' is in core identifiers",
                                **{k: str(v) for k, v in record.items()},
                            }
                        )
                        continue

                    if not record.get("dp_email") and not record.get("dp_mobile"):
                        failed_records.append(
                            {
                                "row": index + 1,
                                "error": "Either email or mobile must be provided",
                                **{k: str(v) for k, v in record.items()},
                            }
                        )
                        continue

                    invalid_emails = []
                    for email in record.get("dp_email", []):
                        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", str(email) if email else ""):
                            invalid_emails.append(str(email))

                    if invalid_emails:
                        failed_records.append(
                            {
                                "row": index + 1,
                                "error": f"Invalid email format(s): {', '.join(invalid_emails)}",
                                **{k: str(v) for k, v in record.items()},
                            }
                        )
                        continue

                    invalid_mobiles = []
                    for mobile in record.get("dp_mobile", []):
                        if not re.match(r"^\d{10}$", str(mobile)):
                            invalid_mobiles.append(str(mobile))

                    if invalid_mobiles:
                        failed_records.append(
                            {
                                "row": index + 1,
                                "error": f"Mobile(s) must be 10 digits: {', '.join(invalid_mobiles)}",
                                **{k: str(v) for k, v in record.items()},
                            }
                        )
                        continue

                    dp_system_id = record.get("dp_system_id")
                    if dp_system_id:
                        if dp_system_id in seen_system_ids:
                            failed_records.append(
                                {
                                    "row": index + 1,
                                    "error": f"Duplicate dp_system_id in file: {dp_system_id}",
                                    **{k: str(v) for k, v in record.items()},
                                }
                            )
                            continue
                        seen_system_ids.add(dp_system_id)

                    if dp_tags:
                        record_tags = set(record.get("dp_tags", []))
                        record_tags.update(dp_tags)
                        record["dp_tags"] = list(record_tags)

                    existing_row_found = False
                    for email in record.get("dp_email", []):
                        if email in existing_emails:
                            existing_row_found = True
                    for mobile in record.get("dp_mobile", []):
                        m = str(mobile)
                        if m in existing_mobiles:
                            existing_row_found = True

                    priority_legacy = any(existing_email_legacy.get(e, False) for e in record.get("dp_email", []))
                    if not priority_legacy:
                        priority_legacy = any(existing_mobile_legacy.get(str(m), False) for m in record.get("dp_mobile", []))

                    if existing_row_found and not priority_legacy:
                        continue

                    record["is_legacy"] = is_legacy

                    record["added_by"] = genie_user_id
                    record["dp_id"] = str(uuid.uuid4())

                    validated = BulkImportDataPrincipal(**record)
                    batch.append(validated.model_dump())
                    success_count += 1

                except Exception as e:
                    logger.error(f"Error processing row {index + 1} in file {filename}: {e}", exc_info=True)
                    failed_records.append(
                        {
                            "row": index + 1,
                            "error": str(e),
                            **{k: str(v) for k, v in record.items()},
                        }
                    )

            if batch:
                try:
                    cols = list(batch[0].keys())

                    formatted_batch = []
                    for item in batch:
                        formatted_item = {}
                        for key, value in item.items():

                            if isinstance(value, list):
                                formatted_item[key] = value
                            else:
                                formatted_item[key] = value
                        formatted_batch.append(formatted_item)

                    columns_sql = ", ".join(quote_ident(c) for c in cols)

                    placeholders = []
                    for i, c in enumerate(cols):
                        if c in ["dp_active_devices", "dp_identifiers", "dp_email", "dp_mobile", "dp_e", "dp_m"]:
                            placeholders.append(f"${i+1}::text[]")
                        else:
                            placeholders.append(f"${i+1}")

                    insert_query = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({', '.join(placeholders)})"

                    vals = [tuple(item[c] for c in cols) for item in formatted_batch]

                    await conn.executemany(insert_query, vals)
                    batch.clear()

                except Exception as e:

                    for i, item in enumerate(batch):
                        failed_records.append(
                            {
                                "row": i + 1,
                                "error": str(e),
                                **{k: str(v) for k, v in item.items()},
                            }
                        )
                    success_count -= len(batch)
                    batch.clear()

                    logger.error(f"Batch insert error for {filename}: {e}", exc_info=True)

    total = success_count + len(failed_records) + update_count

    if failed_records:
        logger.warning(f"Processed {total}: {success_count} succeeded, {len(failed_records)} failed for file {filename}.")
        try:

            failed_records_dir = os.path.dirname("failed_records.csv")
            if failed_records_dir and not os.path.exists(failed_records_dir):
                os.makedirs(failed_records_dir, exist_ok=True)

            with open("failed_records.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=failed_records[0].keys())
                writer.writeheader()
                for rec in failed_records:
                    writer.writerow(rec)
            s3_client.fput_object(settings.FAILED_RECORDS_BUCKET, filename, "failed_records.csv")
            logger.info(f"Uploaded failed records file {filename} to S3 bucket {settings.FAILED_RECORDS_BUCKET}.")
        except Exception as e:
            logger.error(f"Error uploading failed records for {filename}: {e}", exc_info=True)

        await dp_file_processing_collection.find_one_and_update(
            {"filename": filename},
            {
                "$set": {
                    "status": "rejected",
                    "completed_at": datetime.now(timezone.utc),
                    "total_records": total,
                    "failed_count": len(failed_records),
                    "message": f"{len(failed_records)} of {total} records failed processing.",
                }
            },
        )
        await create_user_notification(
            df_id=df_id,
            users_list=[genie_user_id],
            notification_title="Bulk Import Failed",
            notification_message=f"{len(failed_records)} of {total} records failed",
            redirection_route="",
            cta_url="",
            file_url=f"{settings.FAILED_RECORDS_BUCKET}/{filename}",
            priority="high",
            icon_url="",
            category="bulk_import",
        )
    else:
        if update_count > 0:
            logger.info(f"Processed {total}: {success_count} Inserted, {update_count} Updated for file {filename}.")
        else:
            logger.info(f"Processed all {total} records successfully for file {filename}.")
        await dp_file_processing_collection.find_one_and_update(
            {"filename": filename},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc),
                    "total_records": total,
                    "failed_count": 0,
                    "message": f"Processed {total} records successfully.",
                }
            },
        )
        await create_user_notification(
            df_id=df_id,
            users_list=[genie_user_id],
            notification_title="Bulk Import Successful",
            notification_message=f"Processed {total} records successfully",
            redirection_route="",
            cta_url="",
            file_url="",
            priority="normal",
            icon_url="",
            category="bulk_import",
        )


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)
            logger.info(f"Received message for DP processing: {data.get('filename')}")

            filename = data.get("filename")
            df_id = data.get("df_id")
            genie_user_id = data.get("genie_user_id")
            is_legacy = data.get("is_legacy", False)
            dp_tags = data.get("dp_tags", [])

            if not filename or not df_id or not genie_user_id:
                logger.warning(f"Invalid message, missing required fields for file {filename}: {data}")
                return

            local_temp_path = os.path.join("/data/uploads/", filename)

            os.makedirs(os.path.dirname(local_temp_path), exist_ok=True)

            s3_client.fget_object(settings.UNPROCESSED_FILES_BUCKET, filename, local_temp_path)

            if not os.path.exists(local_temp_path):
                logger.error(f"File not found locally after S3 download: {local_temp_path}")
                return

            with open(local_temp_path, "rb") as f:
                contents = f.read()

            await process_file(
                contents=contents,
                filename=filename,
                df_id=df_id,
                genie_user_id=genie_user_id,
                is_legacy=is_legacy,
                dp_tags=dp_tags,
            )

            logger.info(f"Processed file: {filename} for DF: {df_id}")
        except Exception as e:
            logger.critical(f"Error processing message for file {filename}: {e}", exc_info=True)


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

    logger = get_logger("worker.dp_processing_consumer")
    logger.info("DP Processing Consumer starting up.")
    asyncio.run(main())
