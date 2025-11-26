from app.db.session import get_redis
from app.core.config import settings
import json
from datetime import datetime
from app.core.logger import app_logger

BLOCK_WINDOW_HOURS = 24
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


async def parse_ts(ts: str) -> datetime:
    """Convert stored string timestamp back to datetime"""
    try:
        return datetime.fromisoformat(ts)
    except Exception as e:
        app_logger.warning(f"Failed to parse timestamp '{ts}' using fromisoformat: {e}. Trying strptime.")
        try:
            return datetime.strptime(ts, TIME_FORMAT)
        except Exception as e_strptime:
            app_logger.error(f"Failed to parse timestamp '{ts}' using strptime either: {e_strptime}. Returning current datetime.")
            return datetime.now()


async def store_otp(user_input: str, otp_data: dict):
    redis = get_redis()
    key = f"otp:{user_input}"
    try:
        await redis.setex(key, settings.OTP_EXPIRY_SECONDS, json.dumps(otp_data))
        app_logger.debug(f"OTP stored for {user_input} with expiry {settings.OTP_EXPIRY_SECONDS} seconds.")
    except Exception as e:
        app_logger.error(f"Failed to store OTP for {user_input}: {e}", exc_info=True)
        raise


async def get_otp(user_input: str) -> dict:
    redis = get_redis()
    key = f"otp:{user_input}"
    try:
        data = await redis.get(key)
        if data:
            app_logger.debug(f"OTP retrieved for {user_input}.")
            return json.loads(data)
        app_logger.debug(f"No OTP found for {user_input}.")
        return None
    except Exception as e:
        app_logger.error(f"Failed to get OTP for {user_input}: {e}", exc_info=True)
        return None


async def delete_otp(user_input: str):
    redis = get_redis()
    try:
        await redis.delete(f"otp:{user_input}")
        app_logger.debug(f"OTP deleted for {user_input}.")
    except Exception as e:
        app_logger.error(f"Failed to delete OTP for {user_input}: {e}", exc_info=True)
        raise


async def get_attempts(key: str):
    redis = get_redis()
    try:
        data = await redis.get(key)
        if data:
            app_logger.debug(f"Attempts retrieved for key: {key}.")
            return json.loads(data)
        app_logger.debug(f"No attempts found for key: {key}.")
        return []
    except Exception as e:
        app_logger.error(f"Failed to get attempts for key: {key}: {e}", exc_info=True)
        return []


async def store_attempts(key: str, attempts: list):
    redis = get_redis()
    try:
        await redis.set(key, json.dumps(attempts), ex=BLOCK_WINDOW_HOURS * 3600)
        app_logger.debug(f"Attempts stored for key: {key} with expiry {BLOCK_WINDOW_HOURS * 3600} seconds.")
    except Exception as e:
        app_logger.error(f"Failed to store attempts for key: {key}: {e}", exc_info=True)
        raise
