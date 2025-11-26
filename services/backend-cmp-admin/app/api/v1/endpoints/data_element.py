from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.v1.deps import get_current_user, get_data_element_service
from app.schemas.data_element_schema import (
    DEPaginatedResponse,
    DETemplatePaginatedResponse,
    DataElementCreate,
    DataElementDB,
    DataElementResponse,
    DataElementUpdate,
)
from app.services.data_element_service import DataElementService
from typing import List, Optional

router = APIRouter()


@router.get(
    "/templates",
    summary="List all Data Element Templates",
    response_model=DETemplatePaginatedResponse,
)
async def list_data_element_templates_endpoint(
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    domain: Optional[str] = None,
    title: Optional[str] = None,
    id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    try:
        """
        Retrieves filtered Data Element Templates with pagination.
        """
        return await service.get_all_data_element_templates(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
            domain=domain,
            title=title,
            id=id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/create-data-element",
    status_code=status.HTTP_201_CREATED,
    response_model=DataElementResponse,
    summary="Create a new Data Element",
)
async def create_data_element_endpoint(
    de_data: DataElementCreate,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    """
    Creates a new Data Element in the system.
    Requires authentication.
    """
    try:
        created_de = await service.create_data_element(de_data.model_dump(), current_user)
        return created_de
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/copy-data-element",
    response_model=DataElementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Copy Data Element",
)
async def copy_data_element_endpoint(
    de_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    """
    Creates a new Data Element Template in the system.
    Requires authentication.
    """
    try:
        copied_de = await service.copy_data_element(de_id, current_user)
        return copied_de
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/update-data-element/{de_id}",
    response_model=DataElementDB,
    summary="Update an existing Data Element Template",
)
async def update_data_element_endpoint(
    de_id: str,
    update_de_data: DataElementUpdate,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    try:
        """
        Updates an existing Data Element Template.
        Requires authentication.
        """
        updated_template = await service.update_data_element(
            de_id,
            update_de_data.model_dump(exclude_unset=True, exclude_defaults=True),
            current_user,
        )
        if not updated_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data Element Template not found or no changes made",
            )
        return updated_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/publish-data-element/{de_id}",
    response_model=DataElementResponse,
    summary="Publish a Data Element Master",
)
async def publish_de_endpoint(
    de_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    try:
        published_de = await service.publish_data_element(de_id, current_user)
        return published_de
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-all-data-element",
    response_model=DEPaginatedResponse,
    summary="Retrieve a Data Element by ID",
)
async def get_all_de_endpoint(
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    is_core_identifier: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    """
    Retrieves a single Data Element by its unique ID.
    Requires authentication.
    """
    try:
        return await service.get_all_data_element(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
            is_core_identifier=is_core_identifier,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/get-data-element/{de_id}",
    response_model=DataElementResponse,
    summary="Retrieve a Data Element by ID",
)
async def get_data_element_endpoint(
    de_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    """
    Retrieves a single Data Element by its unique ID.
    Requires authentication.
    """
    try:
        data_element = await service.get_data_element(de_id, current_user)
        if not data_element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data Element not found",
            )
        return data_element
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-data-element/{de_id}",
    summary="Delete a Data Element Template",
)
async def delete_data_element_endpoint(
    de_id: str,
    current_user: dict = Depends(get_current_user),
    service: DataElementService = Depends(get_data_element_service),
):
    """
    Deletes a Data Element Template from the system.
    Requires authentication.
    """
    try:
        deleted_de = await service.delete_data_element(de_id, current_user)

        if not deleted_de:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data Element not found or already deleted.",
            )
        return deleted_de
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
