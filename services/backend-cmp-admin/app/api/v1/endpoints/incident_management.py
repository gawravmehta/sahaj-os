from typing import Literal, Optional
from fastapi import APIRouter, Depends
from fastapi.params import Query

from app.schemas.incident_management_schema import (
    IncidentCreate,
    AddStepRequest,
    UpdateStageRequest,
)
from app.services.incident_management_service import IncidentService
from app.api.v1.deps import get_current_user, get_incident_service

router = APIRouter()


@router.post("/create-or-update")
async def create_or_update_incident(
    data: IncidentCreate,
    incident_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.create_or_update_incident(data, current_user, incident_id)


@router.get("/get-all-incidents")
async def list_incidents(
    incident_type: Optional[str] = Query(None),
    incident_sensitivity: Optional[Literal["low", "medium", "high"]] = Query(None),
    status: Optional[Literal["archived", "draft", "in_progress", "published"]] = Query(None),
    current_stage: Optional[str] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):

    return await service.list_incidents(
        incident_type=incident_type,
        incident_sensitivity=incident_sensitivity,
        status=status,
        current_stage=current_stage,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )


@router.get("/get-incidents/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.get_incident(incident_id, current_user)


@router.post("/{incident_id}/publish")
async def publish_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.publish_incident(incident_id, current_user)


@router.post("/{incident_id}/move-to-next-stage")
async def move_to_next_stage(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.move_to_next_stage(incident_id, current_user)


@router.post("/{incident_id}/add-step")
async def add_step_to_stage(
    incident_id: str,
    body: AddStepRequest,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.add_step_to_stage(incident_id, body, current_user)


@router.post("/{incident_id}/update-stage")
async def update_stage_manually(
    incident_id: str,
    body: UpdateStageRequest,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.update_stage_manually(incident_id, body, current_user)


@router.post("/send-notification/{incident_id}")
async def send_incident_notification(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
):
    return await service.send_incident_notifications(
        incident_id,
        current_user,
    )
