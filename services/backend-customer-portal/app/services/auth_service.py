from datetime import UTC, datetime, timedelta
import random
from typing import Optional
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_jwt_token

from app.services.email_templates import generate_email_template
from app.utils.hashing import hash_shake256
from app.utils.mail_utils import mailSender, get_email_credentials
from app.core.logger import app_logger
from app.utils.otp_utils import store_otp, get_otp, delete_otp


def _generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


async def handle_login(email: Optional[str], mobile: Optional[str], df_id: str, pool, df_register_collection):
    app_logger.info(f"Handling login for email: {email}, mobile: {mobile}, df_id: {df_id}")
    if not df_id:
        app_logger.warning("Login failed: df_id is required")
        raise HTTPException(status_code=400, detail="df_id is required")
    if not email and not mobile:
        app_logger.warning("Login failed: Email or mobile required")
        raise HTTPException(status_code=400, detail="Email or mobile required")

    table_name = "dpd"
    column, user_input = ("dp_e", email) if email else ("dp_m", mobile)
    hashed = hash_shake256(user_input)

    query = f"""
        SELECT dp_id
        FROM {table_name}
        WHERE $1 = ANY({column})
        LIMIT 1
    """

    async with pool.acquire() as conn:
        result = await conn.fetchrow(query, hashed)

    is_existing = bool(result)
    dp_id = str(result["dp_id"]) if is_existing else None
    app_logger.debug(f"User existence check: is_existing={is_existing}, dp_id={dp_id}")

    otp = _generate_otp()
    app_logger.info(f"Generated OTP for {user_input}")

    await store_otp(
        user_input,
        {
            "otp": otp,
            "df_id": df_id,
            "dp_id": dp_id,
            "email": email,
            "mobile": mobile,
            "field": column,
            "hash": hashed,
            "is_existing": is_existing,
        },
    )

    if email:
        email_template = generate_email_template("There!", otp)
        credentials = await get_email_credentials(df_id, df_register_collection)
        if credentials:
            await mailSender(destination_email=email, subject="Your OTP for Concur Login", email_template=email_template, credentials=credentials)
        else:
            app_logger.info(f"Skipping email sending for {email} due to missing credentials.")
        app_logger.info(f"OTP email sent to {email}")

    return {"success": True, "message": "OTP sent successfully"}


async def handle_otp_verification(email, mobile, df_id, otp_input):
    app_logger.info(f"Handling OTP verification for email: {email}, mobile: {mobile}, df_id: {df_id}")
    user_input = email or mobile
    otp_record = await get_otp(user_input)
    if not otp_record:
        app_logger.warning(f"OTP verification failed for {user_input}: OTP expired or not requested")
        raise HTTPException(status_code=400, detail="OTP expired or not requested")

    if otp_input != otp_record["otp"]:
        app_logger.warning(f"OTP verification failed for {user_input}: Invalid OTP")
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if df_id and df_id != otp_record["df_id"]:
        app_logger.warning(f"OTP verification failed for {user_input}: df_id mismatch. Expected {otp_record['df_id']}, got {df_id}")
        raise HTTPException(status_code=400, detail="df_id mismatch")

    app_logger.info(f"OTP successfully verified for {user_input}. Deleting OTP record.")
    await delete_otp(user_input)

    jwt_payload = {
        "df_id": otp_record["df_id"],
        "field": otp_record["field"],
        "hash": otp_record["hash"],
        "email": email,
        "mobile": mobile,
        "dp_id": otp_record.get("dp_id"),
        "is_existing": otp_record["is_existing"],
    }

    token = create_jwt_token(jwt_payload, settings.JWT_EXPIRY_MINUTES)
    return {"success": True, "access_token": token, "token_type": "bearer"}


MAX_RESEND_LIMIT = 3


async def handle_resend_otp(email: Optional[str], mobile: Optional[str], df_id: str, pool, df_register_collection):
    app_logger.info(f"Handling OTP resend for email: {email}, mobile: {mobile}, df_id: {df_id}")
    if not df_id:
        app_logger.warning("OTP resend failed: df_id is required")
        raise HTTPException(status_code=400, detail="df_id is required")
    if not email and not mobile:
        app_logger.warning("OTP resend failed: Email or mobile required")
        raise HTTPException(status_code=400, detail="Email or mobile required")

    user_input = email or mobile
    column, hashed = ("dp_e", hash_shake256(email)) if email else ("dp_m", hash_shake256(mobile))
    table_name = f"dpd"

    attempts_key = f"otp_attempts:{df_id}:{hashed}"
    attempts = await get_attempts(attempts_key)

    now = datetime.now(UTC)

    attempts = [parse_ts(ts) for ts in attempts]

    attempts = [ts for ts in attempts if ts > now - timedelta(hours=BLOCK_WINDOW_HOURS)]
    app_logger.debug(f"Current OTP attempts for {user_input}: {len(attempts)}")

    if len(attempts) >= MAX_RESEND_LIMIT:
        app_logger.warning(f"OTP resend failed for {user_input}: Too many requests")
        raise HTTPException(
            status_code=429,
            detail=f"Too many OTP requests. Please try again after {BLOCK_WINDOW_HOURS} hours.",
        )

    attempts.append(now)
    await store_attempts(attempts_key, [ts.isoformat() for ts in attempts])

    query = f"""
        SELECT dp_id
        FROM {table_name}
        WHERE $1 = ANY({column})
        LIMIT 1
    """

    async with pool.acquire() as conn:
        result = await conn.fetchrow(query, hashed)

    is_existing = bool(result)
    dp_id = str(result["dp_id"]) if is_existing else None
    app_logger.debug(f"User existence check for resend: is_existing={is_existing}, dp_id={dp_id}")

    otp = _generate_otp()
    app_logger.info(f"Generated new OTP for {user_input} during resend")

    await store_otp(
        user_input,
        {
            "otp": otp,
            "df_id": df_id,
            "field": column,
            "hash": hashed,
            "email": email,
            "mobile": mobile,
            "dp_id": dp_id,
            "is_existing": is_existing,
        },
    )

    if email:
        email_template = generate_email_template("There!", otp)
        credentials = await get_email_credentials(df_id, df_register_collection)
        if credentials:
            await mailSender(destination_email=email, subject="Your New OTP for Concur Login", email_template=email_template, credentials=credentials)
        else:
            app_logger.info(f"Skipping email sending for {email} due to missing credentials.")
        app_logger.info(f"New OTP email sent to {email}")

    return {"success": True, "message": "OTP resent successfully"}
