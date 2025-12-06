from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.services.consent_audit_service import ConsentAuditService
from app.api.v1.deps import get_current_user, get_consent_audit_service
from app.core.config import settings

router = APIRouter()


@router.get("/consents/{dp_id}/audit")
async def get_dp_audit(
    dp_id: str,
    current_user: dict = Depends(get_current_user),
    service: ConsentAuditService = Depends(get_consent_audit_service),
):
    try:
        df_id = current_user["df_id"]
        logs = await service.get_dp_audit_history(dp_id, current_user)

        return {"dp_id": dp_id, "df_id": df_id, "count": len(logs), "logs": logs}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/consent-timeline/{dp_id}/audit")
async def get_dp_audit(
    dp_id: str,
    df_id: str,
    service: ConsentAuditService = Depends(get_consent_audit_service),
):
    try:
        logs = await service.get_dp_audit_history_internal(dp_id, df_id)

        return {"dp_id": dp_id, "df_id": df_id, "count": len(logs), "logs": logs}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
