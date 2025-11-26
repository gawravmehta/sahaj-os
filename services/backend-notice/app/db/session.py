import redis.asyncio as redis
from minio import Minio
from fastapi import Request

from app.core.config import settings
from typing import Optional
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.logger import app_logger
import asyncio
from app.core.config import settings

mongo_master_client: Optional[AsyncIOMotorClient] = None
mongo_counter_client: Optional[AsyncIOMotorClient] = None
pg_pool: Optional[asyncpg.Pool] = None
s3_client: Minio = None


REDIS_PASSWORD = None
REDIS_USERNAME = None
REDIS_MAX_CONNECTIONS = 200

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
        for node in settings.REDIS_STARTUP_NODES:
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


async def connect_to_mongo():
    """Initializes Motor (async MongoDB) clients."""
    global mongo_master_client, mongo_counter_client
    app_logger.info("Connecting to MongoDB instances (Motor)...")
    mongo_master_client = AsyncIOMotorClient(settings.MONGO_MASTER_URI)

    try:
        await mongo_master_client.admin.command("ping")
        app_logger.info("Connected to MongoDB (Motor).")
    except Exception as e:
        app_logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise


def get_mongo_master_db():
    """Dependency to get the master MongoDB database (async)."""

    if mongo_master_client is None:
        app_logger.error("MongoDB master client not initialized. Call connect_to_mongo() during startup.")
        raise RuntimeError("MongoDB master client not initialized.")
    return mongo_master_client[settings.MONGO_MASTER_DB_NAME]


def get_df_keys_collection():
    return get_mongo_master_db()["df_keys"]


def get_cp_master_collection():
    return get_mongo_master_db()["cp_master"]


def connect_to_s3():
    """Initializes the MinIO S3 client."""
    global s3_client
    app_logger.info("Connecting to MinIO S3...")
    try:
        s3_client = Minio(
            settings.S3_ENDPOINT,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_SECURE,
        )

        s3_client.list_buckets()
        app_logger.info("Connected to MinIO S3.")
    except Exception as e:
        app_logger.error(f"Failed to connect to MinIO S3: {e}", exc_info=True)
        raise


def get_s3_client() -> Minio:
    """Dependency to get the MinIO S3 client."""
    if s3_client is None:
        connect_to_s3()
    return s3_client


def get_redis():
    """Dependency to get the Redis client."""
    if redis_client is None:
        connect_with_polling()
    return redis_client


DATABASE_URL = settings.POSTGRESS_URL


async def get_postgres_pool() -> asyncpg.Pool:
    """Get an active PostgreSQL pool (initialize if missing)."""
    global pg_pool
    if pg_pool is None:
        pg_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return pg_pool


async def close_postgres_pool():
    """Close the PostgreSQL pool gracefully."""
    global pg_pool
    if pg_pool:
        await pg_pool.close()
        pg_pool = None


async def startup_db_clients():
    """Initializes all database clients in an async context."""
    app_logger.info("Initializing all database clients...")
    try:
        await connect_with_polling()
        await connect_to_mongo()
        connect_to_s3()

        app_logger.info("All database clients initialized successfully.")
    except Exception as e:
        app_logger.error(f"Failed to initialize one or more database clients: {e}", exc_info=True)
        raise


def get_tracer(request: Request):
    """Dependency to get the OpenTelemetry tracer from request state."""
    return getattr(request.state, "tracer", None)
