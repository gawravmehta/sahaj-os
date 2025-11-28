import asyncio
import json
from typing import Optional
import asyncpg
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import app_logger
from motor.motor_asyncio import AsyncIOMotorClient

from minio import Minio, S3Error
import os

pg_pool: Optional[asyncpg.Pool] = None


async def connect_to_mongo(app: FastAPI):
    app_logger.info("Connecting to MongoDB...")
    app.state.motor_client = AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True)
    await app.state.motor_client.admin.command("ping")
    app_logger.info("MongoDB connection established and verified.")


def close_mongo_connection(app: FastAPI):
    if hasattr(app.state, "motor_client") and app.state.motor_client:
        app.state.motor_client.close()
        app_logger.info("MongoDB connection closed.")


async def get_postgres_pool() -> asyncpg.Pool:
    """Get an active PostgreSQL pool (initialize if missing)."""
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(settings.POSTGRES_DATABASE_URL, min_size=1, max_size=5)
    return pg_pool


async def close_postgres_pool():
    """Close the PostgreSQL pool gracefully."""
    global pg_pool
    if pg_pool:
        await pg_pool.close()
        pg_pool = None


def get_s3_client() -> Minio:
    return Minio(
        settings.S3_URL,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.S3_SECURE,
    )


def make_s3_buckets():
    s3_client = get_s3_client()
    bucket_names = [
        settings.NOTICE_WORKER_BUCKET,
        settings.PROCESSED_FILES_BUCKET,
        settings.UNPROCESSED_FILES_BUCKET,
        settings.UNPROCESSED_VERIFICATION_FILES_BUCKET,
        settings.FAILED_RECORDS_BUCKET,
        settings.FAILED_RECORDS_BUCKET_EXTERNAL,
        settings.TRAINING_NUGGETS_BUCKET,
        settings.KYC_DOCUMENTS_BUCKET,
        settings.DPAR_BULK_UPLOAD_BUCKET,
        settings.COOKIE_CONSENT_BUCKET,
    ]

    for bucket in bucket_names:
        if not s3_client.bucket_exists(bucket):
            s3_client.make_bucket(bucket)

            if bucket == settings.COOKIE_CONSENT_BUCKET:
                try:
                    policy_read_only = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket}/*"],
                            }
                        ],
                    }
                    s3_client.set_bucket_policy(bucket, json.dumps(policy_read_only))
                except S3Error as e:
                    app_logger.error(f"Failed to set public policy for {bucket}: {e}", exc_info=True)


def setup_local_folders():
    os.makedirs("./app/uploads", exist_ok=True)
    os.makedirs("./app/temp", exist_ok=True)
