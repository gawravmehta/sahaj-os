import os
from typing import Dict
from contextlib import asynccontextmanager
from datetime import datetime, UTC

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logger import app_logger, setup_logging


limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    MongoDB.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        await MongoDB.client.admin.command("ping")
        app_logger.info(f"Connected to MongoDB successfully at: {settings.MONGO_URI}")
    except ConnectionFailure as e:
        app_logger.critical(f"Could not connect to MongoDB at {settings.MONGO_URI}. {e}")
    MongoDB.database = MongoDB.client[settings.DB_NAME_COOKIE_MANAGEMENT]
    yield
    if MongoDB.client:
        MongoDB.client.close()
        app_logger.info("MongoDB connection closed gracefully.")


class ConsentPayload(BaseModel):
    category_choices: Dict[str, bool]
    user_id: str | None = None
    website_id: str
    language: str = "eng"


app = FastAPI(
    title="Cookie Consent Collection API",
    description="API to securely collect and rate-limit user cookie consent decisions using SlowAPI and MongoDB, configured via Pydantic Settings.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/v1/consent", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def submit_consent(payload: ConsentPayload, request: Request):
    if MongoDB.database is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection is unavailable.")

    ip_address = request.headers.get("x-forwarded-for", get_remote_address(request)).split(",")[0].strip()
    unique_key = payload.user_id if payload.user_id else ip_address

    audit_collection = MongoDB.database["consent_audit_records"]
    current_collection = MongoDB.database["user_preferences_current"]

    filter_query = {"website_id": payload.website_id, "unique_key": unique_key}
    existing_record = await current_collection.find_one(filter_query)
    action = "updated" if existing_record else "created"
    current_timestamp = datetime.now(UTC)
    data = payload.model_dump()

    current_state_record = {
        "website_id": payload.website_id,
        "unique_key": unique_key,
        "category_choices": data["category_choices"],
        "language": payload.language,
        "last_updated": current_timestamp,
        "initial_timestamp": existing_record.get("initial_timestamp", current_timestamp) if existing_record else current_timestamp,
    }

    audit_record = {
        "website_id": payload.website_id,
        "unique_key": unique_key,
        "action": action,
        "ip_address": ip_address,
        "timestamp": current_timestamp,
        "consent_data": data,
        "user_agent": request.headers.get("user-agent"),
        "country": request.headers.get("x-country", "unknown"),
    }

    try:
        await current_collection.update_one(filter_query, {"$set": current_state_record}, upsert=True)
        result = await audit_collection.insert_one(audit_record)
        app_logger.info(f"Consent {action} for Key '{unique_key}'. Audit ID: {result.inserted_id}")
    except Exception as e:
        app_logger.critical(f"Error writing to MongoDB: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record consent securely due to a server error.")

    return {"message": f"Consent successfully {action} and recorded."}


@app.get("/v1/status")
async def status_check():
    is_db_connected = False
    if MongoDB.client is not None:
        try:
            await MongoDB.client.admin.command("ping")
            is_db_connected = True
        except:
            pass
    return {
        "status": "operational",
        "database_status": "connected" if is_db_connected else "disconnected",
    }
