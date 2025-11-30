from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, Header
import hmac
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from fastapi.responses import HTMLResponse, JSONResponse
from app.db.session import get_mongo_master_db, get_redis
from app.schemas.consent_schema import TokenModel
from app.services.consent_service import handle_submit_consent, get_redirection_and_fallback_url
from app.services.notice_service import retrieve_notice_html, retrieve_otp_html
from pymongo.database import Database
from app.db.rabbitmq import publish_message

from app.utils.verification_utils import (
    OTP_LENGTH,
    OTP_MAX_ATTEMPTS,
    OTP_TTL_SECONDS,
    ct_eq,
    otp_key,
    otp_verified_key,
    redis_json_decode,
    redis_json_encode,
    session_key,
    validate_token_and_session,
)
from app.core.logger import get_logger


router = APIRouter()

logger = get_logger("api.notice_endpoint")


@router.get("/get-notice/{token}", response_class=HTMLResponse, tags=["Notices"])
async def get_notice(request: Request, token: str):
    """Decode JWT token and retrieve the notice HTML."""
    logger.debug(f"Received token: {token}")

    try:
        html = await retrieve_notice_html(token=token, request=request)
        return HTMLResponse(
            content=html,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )
    except HTTPException as http_exc:
        logger.warning(f"HTTPException in get_notice: {http_exc.detail}", exc_info=True)
        raise http_exc
    except Exception as e:
        logger.error(f"Internal server error in get_notice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get-otp-page/{token}", response_class=HTMLResponse, tags=["Notices"])
async def get_notice(request: Request, token: str):
    """Decode JWT token and retrieve the notice HTML."""

    logger.debug(f"Received token for OTP page: {token}")

    try:
        html = await retrieve_otp_html(token=token, request=request)
        return HTMLResponse(
            content=html,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )
    except HTTPException as http_exc:
        logger.warning(f"HTTPException in get_otp_page: {http_exc.detail}", exc_info=True)
        raise http_exc
    except Exception as e:
        logger.error(f"Internal server error in get_otp_page: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-otp", tags=["Notices"])
async def verify_otp(request: Request, token: str, otp: str, gdb: Database = Depends(get_mongo_master_db)):
    """
    Checks OTP against Redis and returns redirect URL when valid.
    """
    redis_client = get_redis()
    if callable(redis_client):
        redis_client = redis_client()

    payload = await validate_token_and_session(token, redis_client)
    key = otp_key(payload)

    data = redis_json_decode(await redis_client.get(key))
    if not data:
        raise HTTPException(status_code=400, detail="OTP expired. Please resend.")

    if data.get("locked"):
        raise HTTPException(status_code=423, detail="Too many attempts. Please resend OTP.")

    if len(otp) != OTP_LENGTH or not otp.isdigit():
        raise HTTPException(status_code=400, detail="Invalid OTP format.")

    if not ct_eq(otp, data["otp"]):
        data["attempts"] = int(data.get("attempts", 0)) + 1
        if data["attempts"] >= OTP_MAX_ATTEMPTS:
            data["locked"] = True

        ttl = await redis_client.ttl(key)
        ttl = ttl if ttl and ttl > 0 else 60
        await redis_client.setex(key, ttl, redis_json_encode(data))
        raise HTTPException(status_code=400, detail="Incorrect OTP.")

    sess_key = session_key(payload)

    await redis_client.delete(key)
    await redis_client.expire(session_key(payload), OTP_TTL_SECONDS * 3)

    verified_key = otp_verified_key(payload)

    remaining = await redis_client.ttl(sess_key)
    ttl = remaining if remaining and remaining > 0 else OTP_TTL_SECONDS * 3
    await redis_client.setex(verified_key, ttl, "1")

    df_id = payload.get("df_id")
    dp_id = payload.get("dp_id")
    request_id = payload.get("request_id")
    pending_key = f"pending_agreement:{df_id}:{dp_id}:{request_id}"

    agreement_id = await redis_client.get(pending_key)
    if agreement_id:
        agreement_id = agreement_id.decode("utf-8") if isinstance(agreement_id, bytes) else agreement_id

        message_payload = {
            "event_type": "otp_verification",
            "consent_artifact_id": agreement_id,
        }
        await publish_message("consent_processing_q", json.dumps(message_payload))
        logger.info(f"Published OTP verification event for agreement {agreement_id}.")

        await redis_client.delete(pending_key)

    collection_point_id = payload.get("cp_id")
    redirection_url, fallback_url = await get_redirection_and_fallback_url(collection_point_id, gdb)

    return {
        "status": "Consent Submitted!",
        "message": "Consent submitted successfully!",
        "verified": True,
        "dp_id": dp_id,
        "agreement_id": agreement_id,
        "redirection_url": redirection_url,
        "fallback_url": fallback_url,
    }


@router.post("/submit-consent", tags=["Consent"])
async def submit_consent(
    request: Request,
    token_model: TokenModel,
    background_tasks: BackgroundTasks,
    gdb: Database = Depends(get_mongo_master_db),
):
    """Submit consent and generate DPAR token."""
    try:
        result = await handle_submit_consent(request, token_model, gdb, background_tasks)
        return result
    except HTTPException as http_exc:
        logger.warning(f"HTTPException in submit_consent: {http_exc.detail}", exc_info=True)
        raise http_exc
    except Exception as e:
        logger.error(f"Internal server error in submit_consent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def verify_signature(payload: dict, signature: str, gdb: Database) -> bool:
    """Verify HMAC-SHA256 signature from headers."""
    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    cmp_secret = (await gdb.df_keys.find_one({}) or {}).get("cmp_webhook_secret")
    computed_sig = hmac.new(
        cmp_secret.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed_sig, signature)


@router.post("/dp-verification-ack", tags=["Consent"])
async def dp_verification_ack(
    request: Request, x_df_signature: str = Header(None, alias="X-DF-Signature"), gdb: Database = Depends(get_mongo_master_db)
):
    if not x_df_signature:
        raise HTTPException(status_code=401, detail="Missing signature header")

    payload = await request.json()

    timestamp_str = payload.get("ack_timestamp")
    if not timestamp_str:
        raise HTTPException(status_code=400, detail="Missing timestamp")

    try:
        req_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - req_time > timedelta(minutes=5):
            raise HTTPException(status_code=400, detail="Request timestamp expired")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")

    if not await verify_signature(payload, x_df_signature, gdb):
        raise HTTPException(status_code=401, detail="Invalid signature")

    redis_client = get_redis()
    if callable(redis_client):
        redis_client = redis_client()

    df_id = payload.get("df_id")
    dp_id = payload.get("dp_id")
    request_id = payload.get("request_id")

    if not all([df_id, dp_id, request_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    pending_key = f"pending_agreement:{df_id}:{dp_id}:{request_id}"

    agreement_id = await redis_client.get(pending_key)
    if agreement_id:
        agreement_id = agreement_id.decode("utf-8") if isinstance(agreement_id, bytes) else agreement_id

        message_payload = {
            "event_type": "otp_verification",
            "consent_artifact_id": agreement_id,
        }
        await publish_message("consent_processing_q", json.dumps(message_payload))
        logger.info(f"Published OTP verification event for agreement {agreement_id}.")

        await redis_client.delete(pending_key)
        logger.info(f"DP verification acknowledged for agreement {agreement_id}.", extra={"agreement_id": agreement_id})
        return {"status": "ok", "verified": True}
    else:
        logger.warning(f"Pending agreement key not found: {pending_key}", extra={"pending_key": pending_key})
        return {"status": "ok", "message": "Agreement not found or expired"}
