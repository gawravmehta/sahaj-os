import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.logger import app_logger


async def log_business_event(
    *,
    event_type: str,
    user_email: str,
    context: Dict[str, Any],
    message: str,
    business_logs_collection: AsyncIOMotorCollection,
    log_level: str = "INFO",
    error_details: Optional[str] = None,
) -> None:
    """
    Logs a business-level event to a dedicated MongoDB collection (`business_logs`)
    and application logger.

    Args:
        event_type: e.g. "CREATE_USER"
        user_email: who triggered the event
        context: contextual metadata, e.g. {"user_id": "..."}
        message: description
        business_logs_collection: Mongo collection injected from service
        log_level: INFO / ERROR etc.
        error_details: Optional error traceback / message
    """
    try:
        log_entry = {
            "timestamp": datetime.now(UTC),
            "event_type": event_type,
            "user_email": user_email,
            "context": context,
            "message": message,
            "log_level": log_level,
            "error_details": error_details,
        }
        await business_logs_collection.insert_one(log_entry)

        app_logger.log(
            getattr(logging, log_level.upper(), logging.INFO),
            f"Business Log: {message} | Event: {event_type} | User: {user_email}",
        )
    except Exception as e:
        app_logger.error(f"Failed to log business event to MongoDB: {e}", exc_info=True)
