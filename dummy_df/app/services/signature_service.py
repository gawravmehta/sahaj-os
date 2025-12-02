import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings
from app.core.logging_config import logger

def verify_signature(payload: dict, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from headers."""
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    computed_sig = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    logger.debug(f"Computed signature: {computed_sig}")
    return hmac.compare_digest(computed_sig, signature)


def generate_signature(payload: dict) -> str:
    """Generates HMAC-SHA256 signature for the payload."""
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hmac.new(
        settings.CMP_WEBHOOK_SECRET.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_request(payload: dict, signature: str, timestamp_str: str) -> bool:
    """Verifies signature and checks for replay attacks (timestamp)."""
    if not signature:
        logger.warning("Missing signature for request verification.")
        return False

    try:
        req_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        if datetime.now(settings.DATETIME_UTC) - req_time > timedelta(minutes=5):
            logger.warning("Request timestamp expired, possible replay attack.")
            return False
    except ValueError:
        logger.warning("Invalid timestamp format for request verification.")
        return False

    expected_sig = generate_signature(payload)
    return hmac.compare_digest(expected_sig, signature)
