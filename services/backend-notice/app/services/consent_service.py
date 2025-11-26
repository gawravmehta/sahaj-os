import uuid
import json
from datetime import UTC, datetime

from fastapi import Request, HTTPException, BackgroundTasks
from app.db.rabbitmq import publish_message
from app.db.session import get_redis
from app.utils.request_utils import get_client_ip

from app.services.consent_artifact_service import (
    get_dp_info_from_postgres,
    consent_artifact_creation,
    data_element_consent_creation,
    hash_headers,
    validate_jwt_token,
    get_dp_email_and_mobile,
)
from bson import ObjectId

from app.services.otp_service import send_otp_if_required
from app.utils.verification_utils import otp_verified_key
from app.core.logger import get_logger


logger = get_logger("service.consent_service")


async def handle_submit_consent(
    request: Request,
    token_model,
    gdb,
    background_tasks: BackgroundTasks,
):
    try:
        redis_client = get_redis()
        payload = await validate_jwt_token(token_model.token)

        dp_id = payload.get("dp_id")
        df_id = payload.get("df_id")
        collection_point_id = payload.get("cp_id")
        request_id = payload.get("request_id")

        agreement_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        binded_ip = get_client_ip(request)
        redis_key = f"session:{df_id}:{dp_id}:{request_id}"

        saved_token = await redis_client.get(redis_key)
        submitted_token = token_model.token.strip()
        stored_token = (saved_token or "").strip()

        if not stored_token:
            raise HTTPException(status_code=401, detail="Session expired")
        if submitted_token != stored_token:
            raise HTTPException(status_code=401, detail="Token mismatch")

        request_headers_hash = await hash_headers(request.headers)

        cp_doc = await gdb.cp_master.find_one({"_id": ObjectId(collection_point_id), "df_id": df_id})
        collection_point_name = cp_doc.get("cp_name") if cp_doc else "Unknown"

        logger.debug(f"Dp id that is being processed: {dp_id}", extra={"dp_id": dp_id})
        is_verification_required = cp_doc.get("is_verification_required", False) if cp_doc else False
        data_principal = await get_dp_info_from_postgres(dp_id, redis_client, payload, is_verification_required)
        logger.debug("Data Principal Information after fetching from Postgres", extra={"data_principal": data_principal})

        data_elements_consents = await data_element_consent_creation(token_model, df_id, collection_point_id, gdb)

        consent_artifact = await consent_artifact_creation(
            collection_point_name,
            collection_point_id,
            binded_ip,
            request_headers_hash,
            dict(request.headers),
            data_principal,
            df_id,
            data_elements_consents,
            agreement_id=agreement_id,
        )

        message_payload = {
            "event_type": "consent_submission",
            "timestamp": datetime.now(UTC).isoformat(),
            "consent_artifact": consent_artifact,
        }
        await publish_message("consent_processing_q", json.dumps(message_payload))

        needs_otp = bool(cp_doc.get("is_verification_required") and cp_doc.get("verification_done_by") == "sahaj")

        if needs_otp:

            verified_key = otp_verified_key(payload)
            is_verified = await redis_client.get(verified_key)

            if not is_verified:

                pending_key = f"pending_agreement:{df_id}:{dp_id}:{request_id}"
                await redis_client.setex(pending_key, 3600, agreement_id)

                dp_details = await get_dp_email_and_mobile(dp_id)
                dp_email = dp_details.get("dp_email")
                dp_mobile = dp_details.get("dp_mobile")

                await send_otp_if_required(
                    redis_client=redis_client,
                    background_tasks=background_tasks,
                    payload=payload,
                    cp=cp_doc,
                    dp_email=dp_email,
                    dp_mobile=dp_mobile,
                    db=gdb,
                )

                redirection_url, fallback_url = await get_redirection_and_fallback_url(collection_point_id, gdb)

                return {
                    "status": "OTP_REQUIRED",
                    "message": "OTP sent successfully. Please verify.",
                    "otp_required": True,
                    "dp_id": dp_id,
                    "agreement_id": agreement_id,
                    "redirection_url": redirection_url,
                    "fallback_url": fallback_url,
                }

        redirection_url, fallback_url = await get_redirection_and_fallback_url(collection_point_id, gdb)

        return {
            "status": "Consent Submitted!",
            "message": "Consent submitted successfully!",
            "otp_required": False,
            "dp_id": dp_id,
            "agreement_id": agreement_id,
            "redirection_url": redirection_url,
            "fallback_url": fallback_url,
        }
    except HTTPException as e:
        logger.warning(f"HTTPException: {e.detail}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Error in handle_submit_consent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_redirection_and_fallback_url(collection_point_id: str, gdb):
    """Get redirection URL from Redis or MongoDB."""
    redis_client = get_redis()
    redis_key = f"cp:{collection_point_id}"
    redis_data = await redis_client.get(redis_key)
    matching_cp = json.loads(redis_data) if redis_data else None
    if not matching_cp:
        logger.info("Collection Point not found in Redis, checking MongoDB", extra={"collection_point_id": collection_point_id})
        matching_cp = await gdb.cp_master.find_one({"_id": ObjectId(collection_point_id)})
    if not matching_cp:
        logger.error(f"Collection Point {collection_point_id} not found in database.", extra={"collection_point_id": collection_point_id})
        raise HTTPException(status_code=404, detail="Collection Point not found in database.")
    redirection_url = matching_cp.get("redirection_url")
    fallback_url = matching_cp.get("fallback_url")

    return redirection_url, fallback_url
