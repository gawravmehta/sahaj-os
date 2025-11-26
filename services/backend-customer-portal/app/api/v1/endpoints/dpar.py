from typing import List
from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.api.v1.deps import get_dpar_request_service
from app.schemas.dpar_schema import (
    DPARCreateRequest,
    DPARRequestOut,
    DPARRequestResponse,
)
from app.services.dpar_request_service import DPARRequestService
from app.api.v1.deps import get_current_user
from app.core.logger import app_logger

router = APIRouter()


@router.get("/get-my-requests", response_model=List[DPARRequestOut])
async def get_my_requests(
    current_user: dict = Depends(get_current_user),
    dpar_service: DPARRequestService = Depends(get_dpar_request_service),
):
    app_logger.info(f"API Call: /get-my-requests for user: {current_user.get('dp_id')}")
    return await dpar_service.get_my_requests(current_user)


@router.get("/get-one-dpar-request", response_model=DPARRequestOut)
async def get_one_dpar_request(
    dpar_request_id: str,
    dpar_service: DPARRequestService = Depends(get_dpar_request_service),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /get-one-dpar-request for ID: {dpar_request_id}")
    return await dpar_service.get_one_request(dpar_request_id)


@router.post("/create-request", response_model=DPARRequestResponse)
async def create_request(
    request: Request,
    payload: DPARCreateRequest,
    dpar_service: DPARRequestService = Depends(get_dpar_request_service),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /create-request for user: {current_user.get('dp_id')}, type: {payload.request_type}")
    return await dpar_service.create_request(request, payload, current_user)


@router.put("/dpa-requests/{dpar_request_id}")
async def update_request(
    dpar_request_id: str,
    update_data: DPARCreateRequest,
    dpar_service: DPARRequestService = Depends(get_dpar_request_service),
    current_user: dict = Depends(get_current_user),
):
    app_logger.info(f"API Call: /dpa-requests/{dpar_request_id} (PUT) for user: {current_user.get('dp_id')}")
    return await dpar_service.update_request(dpar_request_id, update_data, current_user)


@router.delete("/dpa-requests/{dpar_request_id}")
async def delete_request(
    dpar_request_id: str, dpar_service: DPARRequestService = Depends(get_dpar_request_service), current_user: dict = Depends(get_current_user)
):
    app_logger.info(f"API Call: /dpa-requests/{dpar_request_id} (DELETE) for user: {current_user.get('dp_id')}")
    return await dpar_service.delete_request(dpar_request_id, current_user)
