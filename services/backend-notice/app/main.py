import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ipaddr
from slowapi.errors import RateLimitExceeded

from app.api.routers import api_router
from app.core.logger import setup_logging, app_logger
from app.db.session import get_cp_master_collection, get_df_keys_collection, get_redis, startup_db_clients
from app.db.rabbitmq import declare_queues, rabbitmq_pool

limiter = Limiter(key_func=get_ipaddr, default_limits=["100/minute"])

executor = ThreadPoolExecutor(max_workers=10)


async def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app_logger.info("Application startup initiated.")
    await startup_db_clients()

    await rabbitmq_pool.init_pool()
    await declare_queues()

    redis_client = get_redis()

    df_keys = get_df_keys_collection()
    df_data = await df_keys.find({}).to_list(length=None)

    for record in df_data:
        df_id = record.get("df_id")
        if df_id:
            key = f"{df_id}_detail"
            value = json.dumps(record, default=str)
            await redis_client.set(key, value)
            app_logger.info(f"Stored DF key: {key} in Redis")

    cp_master = get_cp_master_collection()
    cp_data = await cp_master.find({"cp_status": "published"}).to_list(length=None)

    for cp_record in cp_data:
        cp_id = str(cp_record.get("_id"))
        key = f"cp:{cp_id}"
        await redis_client.set(key, json.dumps(cp_record, default=str))
        app_logger.info(f"Stored CP record under key={key}")

    app_logger.info("Application startup complete.")
    yield
    await rabbitmq_pool.close_pool()
    app_logger.info("Application shutdown initiated.")
    app_logger.info("Application shutdown complete.")


app = FastAPI(
    title="CMP Notice Backend API",
    description="API for managing Consent Notices.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(api_router, prefix="/api")


@app.get("/")
async def read_root():
    return {"message": "CMP Notice Backend API is running"}
