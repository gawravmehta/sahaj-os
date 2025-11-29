from fastapi import APIRouter, Depends, Header, Request, Query
from typing import Optional, List, Literal
from app.api.v1.deps import get_consent_artifact_service, get_current_user
from app.services.consent_artifact_service import ConsentArtifactService
from app.schemas.consent_artifact_schema import DFAckPayload, ExpiringConsentsByDpIdResponse
from fastapi import HTTPException
import json
import hmac
import hashlib
import os
from datetime import UTC, datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.dependencies import get_df_ack_collection, get_customer_notifications_collection, get_consent_artifact_collection
from app.core.logger import get_logger

CMP_WEBHOOK_SECRET = "cmp_webhook_secret"

router = APIRouter()
logger = get_logger("api.consent_artifact")


@router.get("/get-all-consent-artifact")
async def get_all_consent_artifact(
    request: Request,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = Query(None),
    cp_names_query: Optional[List[str]] = Query(None),
    purposes_query: Optional[List[str]] = Query(None),
    data_elements_query: Optional[List[str]] = Query(None),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: ConsentArtifactService = Depends(get_consent_artifact_service),
):
    return await service.get_all_consent_artifact(
        page,
        limit,
        search,
        cp_names_query,
        purposes_query,
        data_elements_query,
        sort_order,
        start_date,
        end_date,
        current_user,
    )


@router.get("/export-csv")
async def download_consent_artifact(
    request: Request,
    search: Optional[str] = Query(None),
    cp_names_query: Optional[List[str]] = Query(None),
    purposes_query: Optional[List[str]] = Query(None),
    data_elements_query: Optional[List[str]] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query("desc"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: ConsentArtifactService = Depends(get_consent_artifact_service),
):
    return await service.download_consent_artifact(
        search,
        cp_names_query,
        purposes_query,
        data_elements_query,
        sort_order,
        start_date,
        end_date,
        current_user,
    )


@router.get("/get-consent-artifact-by-id")
async def get_consent_artifact_by_id(
    request: Request,
    consent_artifact_id: str = Query(..., alias="id"),
    current_user: dict = Depends(get_current_user),
    service: ConsentArtifactService = Depends(get_consent_artifact_service),
):
    return await service.get_consent_artifact_by_id(consent_artifact_id, current_user)


@router.get("/get-expiring-consents", response_model=List[ExpiringConsentsByDpIdResponse])
async def get_expiring_consents(
    dp_id: Optional[str] = Query(None),
    days_to_expire: Optional[Literal["7", "15", "30"]] = Query(None, description="Filter by days until expiry (7, 15, or 30)"),
    current_user: dict = Depends(get_current_user),
    service: ConsentArtifactService = Depends(get_consent_artifact_service),
):
    df_id = current_user.get("df_id")
    if not df_id:
        logger.warning(f"User {current_user.get('email')} attempted to get expiring consents without df_id.")
        raise HTTPException(status_code=404, detail="User Not Found")
    logger.info(f"User {current_user.get('email')} is getting expiring consents for DF {df_id}.")
    return await service.get_expiring_consents(df_id, dp_id, days_to_expire)


def verify_signature(payload: dict, signature: str) -> bool:
    """
    Regenerates the HMAC hash of the received payload and compares it.
    """
    if not signature:
        return False

    payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    expected_sig = hmac.new(
        CMP_WEBHOOK_SECRET.encode(),
        msg=payload_str.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_sig, signature)


@router.post("/consent-ack")
async def consent_ack(
    request: Request,
    payload: DFAckPayload,
    x_df_signature: str = Header(None, alias="X-DF-Signature"),
    df_ack_collection: AsyncIOMotorCollection = Depends(get_df_ack_collection),
    notification_collection: AsyncIOMotorCollection = Depends(get_customer_notifications_collection),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
):
    """
    Receives acknowledgment from Data Fiduciary that processing has halted.
    """
    try:

        raw_body = await request.json()

        if not x_df_signature:
            logger.warning(f"Missing signature header from DF for DP {payload.dp_id}.")
            raise HTTPException(status_code=401, detail="Missing X-DF-Signature header")

        if not verify_signature(raw_body, x_df_signature):
            logger.warning(f"Invalid signature from DF for DP {payload.dp_id}.")
            raise HTTPException(status_code=401, detail="Invalid signature")

        try:
            ack_time = datetime.fromisoformat(payload.ack_timestamp.replace("Z", "+00:00"))
            if datetime.now(UTC) - ack_time > timedelta(minutes=5):
                raise HTTPException(status_code=400, detail="Request expired")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")

        logger.info(
            f"ACK RECEIVED: DP={payload.dp_id}, Status={payload.ack_status}, Type={payload.original_event_type}, DE={payload.de_id}, Purpose={payload.purpose_id}"
        )

        ack = await df_ack_collection.insert_one(payload.dict())

        await send_user_notification(payload, notification_collection, consent_artifact_collection)

        logger.info(f"Consent acknowledgment processed and user notification sent for DP {payload.dp_id}. Ack ID: {str(ack.inserted_id)}")
        return {"status": "received", "forwarded": True, "ack_id": str(ack.inserted_id)}

    except HTTPException as he:
        logger.error(f"HTTPException processing /consent-ack request for DP {payload.dp_id}: {he.detail}")
        raise he
    except Exception as e:
        logger.critical(f"Server Error processing /consent-ack request for DP {payload.dp_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Server error processing acknowledgment")


async def send_user_notification(
    ack_details: DFAckPayload,
    notification_collection: AsyncIOMotorCollection,
    consent_artifact_collection: AsyncIOMotorCollection,
):
    """
    Creates a user notification when a Data Fiduciary acknowledges a consent revocation/expiry (HALTED).
    Fetches friendly names (titles) from the Consent Artifact.
    """
    try:
        artifact = await consent_artifact_collection.find_one(
            {
                "dp_id": ack_details.dp_id,
                "artifact.consent_scope.data_elements": {
                    "$elemMatch": {
                        "de_id": ack_details.de_id,
                        "consents.purpose_id": ack_details.purpose_id,
                    }
                },
            }
        )

        if not artifact:
            logger.warning(f"Notification skipped: Artifact not found for DP {ack_details.dp_id}")
            return

        data_element_title = "Unknown Data"
        purpose_title = "Unknown Purpose"
        cp_name = artifact.get("artifact", {}).get("cp_name", "Unknown CP")
        agreement_id = artifact.get("agreement_id")
        consent_artifact_id = artifact.get("_id")

        data_elements = artifact.get("artifact", {}).get("consent_scope", {}).get("data_elements", [])

        found_de = False
        for de in data_elements:
            if de.get("de_id") == ack_details.de_id:
                data_element_title = de.get("title", data_element_title)

                for consent in de.get("consents", []):
                    if consent.get("purpose_id") == ack_details.purpose_id:
                        purpose_title = consent.get("purpose_title", purpose_title)
                        found_de = True
                        break
            if found_de:
                break

        now = datetime.now(UTC)

        notification = {
            "dp_id": ack_details.dp_id,
            "artifact_id": str(consent_artifact_id) if consent_artifact_id else None,
            "type": "CONSENT_HALTED",
            "title": "Data Processing Halted",
            "message": f"Data processing for {data_element_title} (purpose: {purpose_title}) has been halted. {ack_details.message or ''}",
            "status": "unread",
            "created_at": now,
            "expiry_date": None,
            "data_element_id": ack_details.de_id,
            "data_element_title": data_element_title,
            "purpose_id": ack_details.purpose_id,
            "purpose_title": purpose_title,
            "cp_name": cp_name,
            "agreement_id": agreement_id,
            "original_event_type": ack_details.original_event_type,
        }

        await notification_collection.insert_one(notification)
        logger.info(f"Notification sent to DP {ack_details.dp_id} for halted processing.")

    except Exception as e:
        logger.critical(f"Failed to send user notification for DP {ack_details.dp_id}: {e}", exc_info=True)
