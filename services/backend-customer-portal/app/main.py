from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ipaddr
from slowapi.errors import RateLimitExceeded

from app.api.routers import api_router

from app.db.dependencies import (
    get_consent_artifact_collection_direct,
    get_notifications_collection_direct,
    get_renewal_collection_direct,
)
from app.db.session import (
    close_mongo_connection,
    connect_to_mongo,
    connect_to_s3,
    get_s3_client,
    connect_with_polling,
    get_postgres_pool,
    close_postgres_pool,
)
from app.services.notifications_schedular import start_notification_scheduler
from app.utils.s3_utils import make_s3_bucket
from app.core.config import settings
from app.middleware.request_context import RequestContextMiddleware
from app.db.rabbitmq import rabbitmq_pool
from app.core.logger import setup_logging, app_logger

limiter = Limiter(key_func=get_ipaddr, default_limits=["100/minute"])

client = get_s3_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        setup_logging()
        app_logger.info("Starting application...")
        await connect_to_mongo(app)
        await connect_with_polling()
        await get_postgres_pool()
        connect_to_s3()

        consent_artifact_collection = get_consent_artifact_collection_direct(app)
        notifications_collection = get_notifications_collection_direct(app)
        renewal_collection = get_renewal_collection_direct(app)

        await start_notification_scheduler(
            consent_artifact_collection,
            notifications_collection,
            renewal_collection,
        )
        make_s3_bucket([settings.KYC_DOCUMENTS_BUCKET], client)

        await rabbitmq_pool.init_pool()

    except Exception as e:
        app_logger.error(f"Application startup failed: {e}", exc_info=True)
        raise

    yield
    await rabbitmq_pool.close_pool()
    await close_postgres_pool()
    app_logger.info("Shutting down application...")
    close_mongo_connection(app)


app = FastAPI(
    title="CMP Customer Portal API",
    description="API for managing customer preferences.",
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
app.add_middleware(RequestContextMiddleware)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def read_root():
    return {"message": "CMP Customer Portal API is running"}
