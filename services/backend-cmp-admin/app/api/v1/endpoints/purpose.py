from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from app.api.v1.deps import (
    get_current_user,
    get_purpose_service,
)
from app.schemas.purpose_schema import (
    PurposeCreate,
    PurposePaginatedResponse,
    PurposeResponse,
    PurposeTemplatePaginatedResponse,
    PurposeUpdate,
)
from app.services.purpose_service import PurposeService

router = APIRouter()


@router.get(
    "/templates",
    summary="List all Purpose Templates",
    response_model=PurposeTemplatePaginatedResponse,
)
async def list_purpose_templates_endpoint(
    purpose_id: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    sub_category: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        return await service.get_all_purpose_templates(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
            id=purpose_id,
            industry=industry,
            sub_category=sub_category,
            title=title,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/create-purpose",
    status_code=status.HTTP_201_CREATED,
    response_model=PurposeResponse,
    summary="Create a new Purpose",
)
async def create_purpose_endpoint(
    purpose_data: PurposeCreate,
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        created_purpose = await service.create_purpose(purpose_data.model_dump(), current_user)
        return created_purpose
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/copy-purpose",
    response_model=PurposeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Copy Purpose from Template",
)
async def copy_purpose_endpoint(
    purpose_id: str,
    data_elements: List[str],
    current_user: dict = Depends(get_current_user),
    purpose_service: PurposeService = Depends(get_purpose_service),
):
    try:
        copied = await purpose_service.copy_purpose(purpose_id, current_user, data_elements)
        return copied
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/update-purpose/{purpose_id}",
    response_model=PurposeResponse,
    summary="Update an existing Purpose Template",
)
async def update_purpose_endpoint(
    purpose_id: str,
    update_data: PurposeUpdate,
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        updated = await service.update_purpose_data(purpose_id, update_data.model_dump(exclude_unset=True, exclude_defaults=True), current_user)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purpose Template not found or no changes made",
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/publish-purpose/{purpose_id}",
    response_model=PurposeResponse,
    summary="Publish Purpose Template",
)
async def publish_purpose_endpoint(
    purpose_id: str,
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        published = await service.publish_purpose(purpose_id, current_user)
        return published
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get-all-purposes", summary="Retrieve a Purpose Template by ID", response_model=PurposePaginatedResponse)
async def get_all_purposes_endpoint(
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        purposes = await service.get_all_purpose(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
        )
        if not purposes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purpose Template not found",
            )
        return purposes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-purpose/{purpose_id}",
    response_model=PurposeResponse,
    summary="Retrieve a Purpose Template by ID",
)
async def get_purpose_endpoint(
    purpose_id: str,
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        purpose = await service.get_purpose(purpose_id, current_user)
        if not purpose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purpose Template not found",
            )
        return purpose
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-purpose/{purpose_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Purpose Template",
)
async def delete_purpose_endpoint(
    purpose_id: str,
    current_user: dict = Depends(get_current_user),
    service: PurposeService = Depends(get_purpose_service),
):
    try:
        success = await service.delete_purpose(purpose_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purpose Template not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
