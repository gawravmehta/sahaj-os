import time
from typing import Optional
from fastapi import FastAPI
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import asyncpg
import redis.asyncio as redis
from app.core.logger import app_logger
import asyncio

mongo_master_client: AsyncIOMotorClient = None
mongo_counter_client: AsyncIOMotorClient = None
s3_client: Minio = None


NODES = [{"host": settings.REDIS_HOST, "port": settings.REDIS_PORT}]
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_USERNAME = settings.REDIS_USERNAME
REDIS_MAX_CONNECTIONS = settings.REDIS_MAX_CONNECTIONS


pg_pool: Optional[asyncpg.Pool] = None


redis_client: Optional[redis.Redis] = None


async def create_redis_connection(node) -> Optional[redis.Redis]:
    """Attempt to create a Redis/KeyDB connection with pooling."""
    try:
        pool = redis.ConnectionPool(
            host=node["host"],
            port=node["port"],
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            max_connections=REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        client = redis.Redis(connection_pool=pool)

        if await client.ping():
            app_logger.info(f"Connected to KeyDB node {node['host']}:{node['port']} successfully!")
            return client
    except Exception as e:
        app_logger.error(f"Failed to connect to KeyDB node {node['host']}:{node['port']}: {e}")
    return None


async def connect_with_polling() -> Optional[redis.Redis]:
    """Try each node until a connection is successful."""
    global redis_client
    retries = 0
    while True:
        for node in NODES:
            app_logger.info(f"Attempting to connect to KeyDB node {node['host']}:{node['port']}...")
            client = await create_redis_connection(node)
            if client:
                app_logger.info("KeyDB client is ready to use.")
                redis_client = client
                return client
        retries += 1
        sleep_time = min(2**retries, 30)
        app_logger.warning(f"Retrying all nodes in {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)


def get_redis() -> Optional[redis.Redis]:
    """Dependency to get the Redis client."""

    return redis_client


async def connect_to_mongo(app: FastAPI):
    app.state.motor_client = AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True)
    await app.state.motor_client.admin.command("ping")


def close_mongo_connection(app: FastAPI):
    if hasattr(app.state, "motor_client") and app.state.motor_client:
        app.state.motor_client.close()


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


def connect_to_s3():
    """Initializes the MinIO S3 client."""
    global s3_client
    app_logger.info("Connecting to MinIO S3...")
    s3_client = Minio(
        settings.S3_URL,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.S3_SECURE,
    )
    app_logger.info("Connected to MinIO S3.")


def get_s3_client() -> Minio:
    """Dependency to get the MinIO S3 client."""
    if s3_client is None:
        connect_to_s3()
    return s3_client
