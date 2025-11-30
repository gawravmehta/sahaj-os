from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from app.api.v1.deps import get_current_user, get_asset_service
from app.schemas.assets_schema import (
    AssetCreate,
    AssetPaginatedResponse,
    AssetResponse,
    AssetUpdate,
)
from app.services.assets_service import AssetService

from app.core.logger import get_logger

router = APIRouter()
logger = get_logger("api.assets")


class PublishMessageRequest(BaseModel):
    routing_key: str = "data_element_translation"


@router.post(
    "/create-asset",
    status_code=status.HTTP_201_CREATED,
    response_model=AssetResponse,
    summary="Create a new Asset",
)
async def create_asset_endpoint(
    asset_data: AssetCreate,
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Creates a new Asset in the system.
    Requires authentication.
    """
    try:
        created_asset = await service.create_asset(asset_data.model_dump(), current_user)
        logger.info(f"Asset '{created_asset.get('asset_name')}' (ID: {created_asset.get('id')}) created by user {current_user.get('email')}.")
        return created_asset
    except HTTPException as e:
        logger.error(f"HTTPException while creating asset for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while creating asset for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    "/update-asset/{asset_id}",
    response_model=AssetResponse,
    summary="Update an existing Asset",
)
async def update_asset_endpoint(
    asset_id: str,
    update_asset_data: AssetUpdate,
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Updates an existing Asset.
    Requires authentication.
    """
    try:
        updated_asset = await service.update_asset(
            asset_id,
            update_asset_data.model_dump(exclude_unset=True, exclude_defaults=True),
            current_user,
        )
        if not updated_asset:
            logger.warning(f"Asset {asset_id} not found or no changes made by user {current_user.get('email')}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or no changes made",
            )
        logger.info(f"Asset {asset_id} updated by user {current_user.get('email')}.")
        return updated_asset
    except HTTPException as e:
        logger.error(f"HTTPException while updating asset {asset_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while updating asset {asset_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/publish-asset/{asset_id}",
    response_model=AssetResponse,
    summary="Publish an Asset",
)
async def publish_asset_endpoint(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Publishes a draft Asset.
    Requires authentication.
    """
    try:
        published_asset = await service.publish_asset(asset_id, current_user)
        logger.info(f"Asset {asset_id} published by user {current_user.get('email')}.")
        return published_asset
    except HTTPException as e:
        logger.error(f"HTTPException while publishing asset {asset_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while publishing asset {asset_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-all-assets",
    response_model=AssetPaginatedResponse,
    summary="Retrieve all Assets",
)
async def get_all_assets_endpoint(
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Retrieves a paginated list of all Assets for the current user's domain.
    Requires authentication.
    """
    try:
        assets = await service.get_all_assets(
            user=current_user,
            current_page=current_page,
            data_per_page=data_per_page,
        )
        logger.info(f"User {current_user.get('email')} retrieved all assets. Page: {current_page}, Size: {data_per_page}")
        return assets
    except HTTPException as e:
        logger.error(f"HTTPException while retrieving all assets for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while retrieving all assets for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/get-asset/{asset_id}",
    response_model=AssetResponse,
    summary="Retrieve an Asset by ID",
)
async def get_asset_endpoint(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Retrieves a single Asset by its unique ID.
    Requires authentication.
    """
    try:
        asset = await service.get_asset(asset_id, current_user)
        if not asset:
            logger.warning(f"Asset {asset_id} not found for user {current_user.get('email')}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )
        logger.info(f"User {current_user.get('email')} retrieved asset {asset_id}.")
        return asset
    except HTTPException as e:
        logger.error(f"HTTPException while retrieving asset {asset_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while retrieving asset {asset_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-asset/{asset_id}",
    response_model=AssetResponse,
    summary="Delete an Asset (Soft Delete)",
)
async def delete_asset_endpoint(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Deletes an Asset from the system by archiving it.
    Requires authentication.
    """
    try:
        deleted_asset = await service.delete_asset(asset_id, current_user)

        if not deleted_asset:
            logger.warning(f"Asset {asset_id} not found or already deleted for user {current_user.get('email')}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or already deleted.",
            )
        logger.info(f"Asset {asset_id} soft-deleted by user {current_user.get('email')}.")
        return deleted_asset
    except HTTPException as e:
        logger.error(f"HTTPException while soft-deleting asset {asset_id} for user {current_user.get('email')}: {e.detail}")
        raise
    except Exception as e:
        logger.critical(f"Internal Server Error while soft-deleting asset {asset_id} for user {current_user.get('email')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
