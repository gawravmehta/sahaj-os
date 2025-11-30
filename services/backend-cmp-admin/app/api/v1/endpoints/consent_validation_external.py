import json
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
from typing import List, Optional
from datetime import UTC, datetime, timezone
import uuid

from app.api.v1.endpoints.dp_bulk_external import SECRET_KEY, TOKEN_EXPIRY_TIME
from app.db.dependencies import (
    get_consent_artifact_collection,
    get_consent_validation_collection,
    get_validation_batch_collection,
    get_vendor_collection,
    get_customer_notifications_collection,
)
from app.db.rabbitmq import publish_message
from app.schemas.consent_validation_schema import VerificationRequest
from app.utils.common import ensure_utc, hash_shake256
from jose import jwt

router = APIRouter()


@router.post("/verify-consent-external")
async def verify_consent_external(
    df_id: str,
    dp_id: Optional[str] = None,
    dp_system_id: Optional[str] = None,
    dp_e: Optional[str] = None,
    dp_m: Optional[str] = None,
    data_elements_hash: Optional[List[str]] = Query(None),
    purpose_hash: Optional[str] = None,
    api_key: str = Query(...),
    api_secret: str = Query(...),
    vendor_master_collection=Depends(get_vendor_collection),
    consent_artifact_collection=Depends(get_consent_artifact_collection),
    consent_validation_collection=Depends(get_consent_validation_collection),
    customer_notifications_collection=Depends(get_customer_notifications_collection),
):
    if not dp_id and not dp_system_id and not (dp_e or dp_m):
        raise HTTPException(
            status_code=400,
            detail="Data Principal ID or Data Principal System ID is required",
        )

    if not data_elements_hash:
        raise HTTPException(status_code=400, detail="At least one data element hash is required")

    if not purpose_hash:
        raise HTTPException(status_code=400, detail="Purpose hash is required")

    if not api_key or not api_secret:
        raise HTTPException(status_code=400, detail="API Key and API Secret are required")

    data_processor_details = await vendor_master_collection.find_one(
        {
            "api_key": api_key,
            "api_secret": api_secret,
        }
    )

    if not data_processor_details:
        raise HTTPException(status_code=401, detail="Invalid API Key or API Secret")

    dp_e = hash_shake256(dp_e) if dp_e else None
    dp_m = hash_shake256(dp_m) if dp_m else None

    query = {"artifact.data_fiduciary.df_id": df_id}
    if dp_id:
        query["artifact.data_principal.dp_id"] = dp_id
    elif dp_system_id:
        query["artifact.data_principal.dp_df_id"] = dp_system_id
    elif dp_e:
        query["artifact.data_principal.dp_e"] = dp_e
    elif dp_m:
        query["artifact.data_principal.dp_m"] = dp_m

    consent_artifacts = await consent_artifact_collection.find(query).to_list(length=None)
    if not consent_artifacts:
        raise HTTPException(status_code=404, detail="Consent Artifact(s) Not Found")

    current_time = datetime.now(timezone.utc)
    matched_elements = set()

    for artifact_doc in consent_artifacts:
        artifact = artifact_doc.get("artifact", {})
        data_elements = artifact.get("consent_scope", {}).get("data_elements", [])

        for element in data_elements:
            element_hash = element.get("de_hash_id")
            if element_hash not in data_elements_hash:
                continue

            for consent in element.get("consents", []):
                if consent.get("purpose_hash_id") != purpose_hash:
                    continue
                if consent.get("consent_status") != "approved":
                    continue

                expiry_str = consent.get("consent_expiry_period")
                if not expiry_str:
                    continue

                try:
                    expiry_date = datetime.fromisoformat(expiry_str)
                    if expiry_date.tzinfo is None:
                        expiry_date = expiry_date.replace(tzinfo=timezone.utc)

                    if expiry_date > current_time:
                        matched_elements.add(element_hash)
                        break
                except (TypeError, ValueError):
                    continue

    all_verified = all(elem in matched_elements for elem in data_elements_hash)

    artifact_for_log = consent_artifacts[0].get("artifact", {})

    verification_log = {
        "request_id": uuid.uuid4().hex,
        "df_id": df_id,
        "dp_id": dp_id or artifact_for_log.get("data_principal", {}).get("dp_id"),
        "dp_system_id": dp_system_id or artifact_for_log.get("data_principal", {}).get("dp_df_id"),
        "dp_e": dp_e or artifact_for_log.get("data_principal", {}).get("dp_e"),
        "dp_m": dp_m or artifact_for_log.get("data_principal", {}).get("dp_m"),
        "internal_external": "Internal",
        "ver_requested_by": {
            "data_processor_name": data_processor_details.get("dpr_name"),
            "data_processor_id": str(data_processor_details.get("_id")),
        },
        "consent_status": all_verified,
        "scope": {
            "data_element_hashes": data_elements_hash,
            "purpose_hash": purpose_hash,
        },
        "status": "successful",
        "timestamp": current_time,
    }

    verification_req = await consent_validation_collection.insert_one(verification_log)

    if not all_verified:
        # Create notification for DP
        dp_id_for_notif = dp_id or artifact_for_log.get("data_principal", {}).get("dp_id")
        if dp_id_for_notif:
            now = datetime.now(UTC)
            notification = {
                "dp_id": dp_id_for_notif,
                "type": "CONSENT_VALIDATION_FAILED",
                "title": "Consent Validation Failed",
                "message": f"A Data Fiduciary attempted to validate your consent for purpose {purpose_hash}, but it was found to be invalid or expired.",
                "status": "unread",
                "created_at": now,
                "verification_request_id": str(verification_req.inserted_id),
                "df_id": df_id,
            }
            await customer_notifications_collection.insert_one(notification)

    return {
        "verified": all_verified,
        "consented_data_elements": matched_elements,
        "verification_request_id": verification_req.inserted_id,
    }


async def generate_jwt_token(df_id: str, vendor_id: str, validation_batch_collection) -> str:
    """Generate a JWT token for the given df_id and save it in MongoDB."""

    expiration = datetime.now(UTC) + TOKEN_EXPIRY_TIME
    payload = {
        "df_id": df_id,
        "vendor_id": vendor_id,
        "exp": expiration,
        "status": "start",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    await validation_batch_collection.update_one(
        {"df_id": df_id},
        {
            "$set": {
                "token": token,
                "status": "start",
                "expiry": expiration,
                "vendor_id": vendor_id,
            }
        },
        upsert=True,
    )

    return token


async def validate_jwt_token(authorization: str = Header(...), validation_batch_collection=Depends(get_validation_batch_collection)):
    """Validate JWT token from Authorization header and return full payload."""
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    df_id = payload.get("df_id")
    vendor_id = payload.get("vendor_id")
    exp_timestamp = payload.get("exp")

    if not df_id or not vendor_id or not exp_timestamp:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    expiry = datetime.fromtimestamp(exp_timestamp, UTC)
    if datetime.now(UTC) > expiry:
        await validation_batch_collection.update_one(
            {"df_id": df_id},
            {"$set": {"status": "end", "token": None}},
        )
        raise HTTPException(status_code=401, detail="Token expired")

    batch_data = await validation_batch_collection.find_one({"df_id": df_id})
    if not batch_data or batch_data.get("token") != token:
        raise HTTPException(status_code=401, detail="Invalid token or session expired")

    return {
        "df_id": df_id,
        "vendor_id": vendor_id,
        "token": token,
        "status": payload.get("status", "start"),
        "exp": exp_timestamp,
    }


@router.post("/authenticate")
async def authenticate(
    api_key: str = Header(..., alias="api-key"),
    api_secret: str = Header(..., alias="api-secret"),
    vendor_master_collection=Depends(get_vendor_collection),
    validation_batch_collection=Depends(get_validation_batch_collection),
):
    """Authenticate API key/secret and generate or reuse JWT token."""
    vendor_doc = await vendor_master_collection.find_one({"api_key": api_key, "api_secret": api_secret})

    if not vendor_doc:
        raise HTTPException(status_code=401, detail="Invalid API Key or Secret")

    df_id = vendor_doc["df_id"]
    batch_data = await validation_batch_collection.find_one({"df_id": df_id})

    if batch_data:
        expiry = ensure_utc(batch_data.get("expiry"))
        token_valid = batch_data.get("status") != "end" and datetime.now(UTC) < expiry
        if token_valid:
            return {
                "message": "Authentication successful, reusing existing token",
                "token": batch_data["token"],
            }

    vendor_id = str(vendor_doc["_id"])

    token = await generate_jwt_token(df_id, vendor_id, validation_batch_collection)
    return {"message": "Authentication successful", "token": token}


@router.post("/verify-consent-external-bulk-api")
async def verify_consent_external_bulk_api(
    request: Request,
    verification_data_list: List[VerificationRequest],
    validated_token: dict = Depends(validate_jwt_token),
    validation_batch_collection=Depends(get_validation_batch_collection),
):
    df_id = validated_token["df_id"]
    token = validated_token["token"]

    if len(verification_data_list) > 1000:
        raise HTTPException(status_code=400, detail="Cannot process more than 1000 records at once")

    batch_data = await validation_batch_collection.find_one({"df_id": df_id, "token": token})

    if not batch_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    expiry = batch_data.get("expiry")
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=UTC)

    if batch_data.get("status") == "end" or datetime.now(UTC) > (expiry or datetime.now(UTC)):
        await validation_batch_collection.update_one(
            {"df_id": df_id, "token": token},
            {"$set": {"status": "end", "token": None, "end_time": datetime.now(UTC)}},
        )
        return {
            "message": "Token has expired, please authenticate again",
            "token": None,
        }

    try:
        message_payload = {
            "df_id": df_id,
            "batch_id": str(batch_data["_id"]),
            "token": token,
            "expiry": (batch_data.get("expiry").isoformat() if batch_data.get("expiry") else None),
            "publish_time": datetime.now(UTC).isoformat(),
            "verification_data_list": [v.dict() for v in verification_data_list],
        }

        await publish_message("consent_bulk_external_verification", json.dumps(message_payload))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish to queue: {e}")

    return {
        "status": "processing_started",
        "message": "Bulk consent verification started in background.",
        "row_count": len(verification_data_list),
        "batch_id": str(batch_data["_id"]),
        "token": token,
    }


@router.get("/get-verification-logs-by-batch/{batch_id}")
async def get_verification_logs_by_batch(
    batch_id: str,
    token_payload: dict = Depends(validate_jwt_token),
    validation_batch_collection=Depends(get_validation_batch_collection),
    consent_validation_collection=Depends(get_consent_validation_collection),
):
    """Get all verification logs related to a specific batch"""
    df_id = token_payload["df_id"]

    vendor_id = token_payload["vendor_id"]

    batch_doc = await validation_batch_collection.find_one(
        {
            "_id": ObjectId(batch_id),
            "df_id": df_id,
            "vendor_id": vendor_id,
        }
    )

    if not batch_doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    request_ids = batch_doc.get("verification_request_ids", [])
    if not request_ids:
        return {
            "message": "No verification logs found for this batch",
            "logs": [],
        }

    logs = await consent_validation_collection.find({"request_id": {"$in": request_ids}}, {"_id": 0}).to_list(None)

    return {
        "batch_id": batch_id,
        "df_id": df_id,
        "logs_found": len(logs),
        "logs": logs,
    }


@router.get("/get-batch-status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    token_payload: dict = Depends(validate_jwt_token),
    validation_batch_collection=Depends(get_validation_batch_collection),
):
    """Get the processing status of a batch by batch_id"""
    df_id = token_payload["df_id"]
    vendor_id = token_payload["vendor_id"]
    if not df_id or not vendor_id:
        raise HTTPException(status_code=404, detail="User Not Found")
    batch_doc = await validation_batch_collection.find_one(
        {
            "_id": ObjectId(batch_id),
            "df_id": df_id,
            "vendor_id": vendor_id,
        }
    )

    if not batch_doc:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "batch_id": batch_id,
        "status": batch_doc.get("status", "unknown"),
        "processed_count": batch_doc.get("processed_count", 0),
        "success_count": batch_doc.get("success_count", 0),
        "failure_count": batch_doc.get("failure_count", 0),
        "completed_at": batch_doc.get("completed_at"),
        "started_at": batch_doc.get("created_at"),
    }
