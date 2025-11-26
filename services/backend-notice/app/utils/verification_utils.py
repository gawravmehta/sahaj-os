import json
import secrets
import hmac

from fastapi import HTTPException
from app.core.config import settings
from jose import jwt, JWTError

OTP_LENGTH = 6
OTP_TTL_SECONDS = 5 * 60
OTP_MAX_ATTEMPTS = 5


def gen_otp() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def session_key(payload: dict) -> str:
    return f"session:{payload.get('df_id')}:{payload.get('dp_id')}:{payload.get('request_id')}"


def otp_key(payload: dict) -> str:
    return f"otp:{payload.get('df_id')}:{payload.get('dp_id')}:{payload.get('request_id')}"


def redis_json_encode(d: dict) -> bytes:
    return json.dumps(d, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def redis_json_decode(v):
    if v is None:
        return None
    if isinstance(v, bytes):
        v = v.decode("utf-8")
    return json.loads(v)


def ct_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


async def validate_token_and_session(token: str, redis_client):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    skey = session_key(payload)
    saved = await redis_client.get(skey)
    if not saved:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    saved = saved.decode("utf-8") if isinstance(saved, bytes) else saved
    if not ct_eq(saved, token):
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return payload


def otp_verified_key(payload) -> str:

    base = session_key(payload)
    return f"{base}:otp_verified"
