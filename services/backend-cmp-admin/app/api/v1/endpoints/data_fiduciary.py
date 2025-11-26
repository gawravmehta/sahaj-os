from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import get_current_user
from app.schemas.data_fiduciary_schema import UpdateDataFiduciary
from app.services.data_fiduciary_service import DataFiduciaryService
from app.api.v1.deps import get_data_fiduciary_service

router = APIRouter()


@router.post("/setup-data-fiduciary")
async def setup_data_fiduciary(
    payload: UpdateDataFiduciary,
    user=Depends(get_current_user),
    service: DataFiduciaryService = Depends(get_data_fiduciary_service),
):
    try:
        df_id = user.get("df_id")
        return await service.setup(df_id, payload, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-fiduciary-details")
async def get_data_fiduciary_details(
    user=Depends(get_current_user),
    service: DataFiduciaryService = Depends(get_data_fiduciary_service),
):
    try:
        df_id = user.get("df_id")
        return await service.get_details(df_id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-sms-templates")
async def get_all_sms_templates(
    user=Depends(get_current_user),
    service: DataFiduciaryService = Depends(get_data_fiduciary_service),
):
    try:
        df_id = user.get("df_id")
        return await service.get_sms_templates(df_id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-in-app-notification-templates")
async def get_all_in_app_notification_templates(
    user=Depends(get_current_user),
    service: DataFiduciaryService = Depends(get_data_fiduciary_service),
):
    try:
        df_id = user.get("df_id")
        return await service.get_in_app_notification_templates(df_id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
