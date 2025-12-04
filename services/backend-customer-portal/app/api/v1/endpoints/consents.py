from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from app.db.dependencies import get_consent_artifact_collection, get_purpose_master_collection
from app.schemas.consent_schema import UpdateConsent
from app.services.consent_service import ConsentService
from app.core.logger import app_logger
import httpx
from app.core.config import settings

from app.api.v1.deps import get_current_user

router = APIRouter()


@router.get("/consent-timeline/{agreement_id}/audit")
async def fetch_consent_time(current_user: dict = Depends(get_current_user)):
    dp_id = current_user["dp_id"]
    df_id = current_user["df_id"]

    audit_url = f"{settings.CMP_ADMIN_BACKEND_URL}/api/v1/consent_audit/consent-timeline/{dp_id}/audit"

    headers = {"accept": "application/json"}
    params = {"df_id": df_id}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(audit_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        app_logger.error(f"HTTP error fetching consent timeline: {e.response.status_code} - {e.response.text}")
        raise e
    except httpx.RequestError as e:
        app_logger.error(f"Request error fetching consent timeline: {e}")
        raise e


@router.patch("/revoke-consent/{agreement_id}")
async def revoke_consent(
    agreement_id: str,
    update_consent: UpdateConsent = Body(...),
    artifact_collection=Depends(get_consent_artifact_collection),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /revoke-consent/{agreement_id}")
    service = ConsentService(artifact_collection)
    return await service.revoke_consent(agreement_id, update_consent)


@router.patch("/give-consent/{agreement_id}")
async def give_consent(
    agreement_id: str,
    update_consent: UpdateConsent = Body(...),
    artifact_collection=Depends(get_consent_artifact_collection),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /give-consent/{agreement_id}")
    service = ConsentService(artifact_collection)
    return await service.give_consent(agreement_id, update_consent)


@router.patch("/renew-consent/{agreement_id}")
async def renew_consent(
    agreement_id: str,
    update_consent: UpdateConsent = Body(...),
    artifact_collection=Depends(get_consent_artifact_collection),
    purpose_collection=Depends(get_purpose_master_collection),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /renew-consent/{agreement_id}")
    service = ConsentService(artifact_collection, purpose_collection)
    return await service.renew_consent(agreement_id, update_consent)


@router.get("/pdf-document/{agreement_id}")
async def get_pdf_document(
    agreement_id: str,
    artifact_collection=Depends(get_consent_artifact_collection),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /pdf-document/{agreement_id}")
    service = ConsentService(artifact_collection)
    pdf_buffer = await service.get_pdf_document(agreement_id)

    return StreamingResponse(
        pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=agreement_{agreement_id}.pdf"}
    )
