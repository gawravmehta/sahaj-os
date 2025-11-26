from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ipaddr
from slowapi.errors import RateLimitExceeded

from app.api.routers import api_router
from app.core.config import settings
from app.db.session import close_postgres_pool, connect_to_mongo, close_mongo_connection, get_postgres_pool, make_s3_buckets, setup_local_folders
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.logger import setup_logging, app_logger
from app.core.init_admin import create_initial_admin
from app.db.rabbitmq import create_vhost, set_user_permissions, declare_queues, rabbitmq_pool
from app.middleware.request_context import RequestContextMiddleware
from fastapi.responses import PlainTextResponse

limiter = Limiter(key_func=get_ipaddr, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app_logger.info("Application startup initiated.")

    try:
        await connect_to_mongo(app)
    except Exception as e:
        app_logger.critical(f"Failed to connect to MongoDB during startup: {e}")
        raise

    await get_postgres_pool()

    make_s3_buckets()
    setup_local_folders()

    client = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.motor_client = client

    await create_initial_admin(client)
    await create_vhost()
    await rabbitmq_pool.init_pool()
    await set_user_permissions()
    await declare_queues()
    app_logger.info("Application startup complete.")
    yield
    app_logger.info("Application shutdown initiated.")
    close_mongo_connection(app)
    await rabbitmq_pool.close_pool()
    await close_postgres_pool()
    app_logger.info("Application shutdown complete.")


app = FastAPI(
    title="CMP Admin Backend API",
    description="API for managing CMP operations, including Data Elements, Consents, etc.",
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


@app.get("/", response_class=PlainTextResponse)
async def root():
    message = """
        8888888b.  8888888b.  8888888b.  8888888b.     d8888         .d8888b.   .d8888b.   .d8888b.   .d8888b. 
        888  "Y88b 888   Y88b 888  "Y88b 888   Y88b   d88888        d88P  Y88b d88P  Y88b d88P  Y88b d88P  Y88b
        888    888 888    888 888    888 888    888  d88P888               888 888    888        888      .d88P
        888    888 888   d88P 888    888 888   d88P d88P 888             .d88P 888    888      .d88P     8888" 
        888    888 8888888P"  888    888 8888888P" d88P  888         .od888P"  888    888  .od888P"       "Y8b.
        888    888 888        888    888 888      d88P   888 888888 d88P"      888    888 d88P"      888    888
        888  .d88P 888        888  .d88P 888     d8888888888        888"       Y88b  d88P 888"       Y88b  d88P
        8888888P"  888        8888888P"  888    d88P     888        888888888   "Y8888P"  888888888   "Y8888P" 
    
    
    Get Ready for DPDPA, 2023 Compliance

    The Digital Personal Data Protection Act (DPDPA), 2023 is here, and it's crucial to ensure your organization is compliant. 
    With increased focus on safeguarding personal data, DPDPA compliance is now more important than ever.

    We're here to help you navigate this new landscape with ease.
    Whether you're just starting or need assistance with compliance processes, Concur offers a streamlined approach to get your data protection operations in place.

    Why is DPDPA Compliance Important?
    - Protect Personal Data: Ensure your data handling practices are secure and transparent.
    - Avoid Penalties: Stay ahead of the legal framework and avoid hefty fines.
    - Build Trust: Show your customers and stakeholders that you care about their privacy and data security.

    Start your DPDPA compliance journey today!
    Get your keys and take the first step towards compliance with Concur. 
    We'll guide you through everything from consent management to data breach notifications.
    
    """
    return message
