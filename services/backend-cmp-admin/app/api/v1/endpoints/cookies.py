from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict
import json
from app.api.v1.deps import get_asset_service, get_current_user, get_cookie_service, get_widget_service
from app.services.cookie_service import CookieManagementService
from app.services.assets_service import AssetService
from app.services.cookie_widget_service import WidgetService
from app.schemas.cookie_schema import CookieCreate, CookieUpdate, CookieResponse, CookiesPaginatedResponse
from app.db.rabbitmq import publish_message
from app.db.session import get_s3_client

router = APIRouter()


@router.post("/build-widget", summary="Build and deploy the cookie consent widget")
async def build_cookie_widget(
    asset_id: str = Query(..., description="Selected Asset ID"),
    current_user: dict = Depends(get_current_user),
    widget_service: WidgetService = Depends(get_widget_service),
    s3_service=Depends(get_s3_client),
):
    """
    Initiates the widget build process for a given asset.
    This endpoint triggers the business logic to generate and deploy the cookie consent widget.
    """
    try:
        build_result = await widget_service.prepare_widget_config(user=current_user, asset_id=asset_id, s3_service=s3_service)

        if isinstance(build_result, dict) and build_result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=build_result.get("message", "Widget build failed due to missing cookies.")
            )

        deployed_url = build_result
        if not deployed_url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Widget build failed: No URL returned.")

        return {"message": "Widget build and deployment initiated successfully.", "script_url": f"<script src='{deployed_url}'></script>"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/scan-website-cookies", summary="Request a cookie scan for a given asset")
async def scan_cookies_by_asset(
    asset_id: str = Query(..., description="Selected Asset ID"),
    current_user: dict = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Publishes a message to a RabbitMQ queue to initiate a cookie scan.
    The actual scan will be performed by a separate consumer worker.
    """
    try:
        asset = await service.get_asset(asset_id=asset_id, user=current_user, for_system=True)

        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found.",
            )

        if asset.get("asset_status") != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cookie scan can only be requested for published assets.",
            )

        meta_cookies = asset.get("meta_cookies")
        if meta_cookies and meta_cookies.get("scan_status") == "completed":
            next_scan_date = meta_cookies.get("next_scan_date")
            if next_scan_date:
                return {
                    "message": "A scan has already been completed. The next scheduled scan is on:",
                    "next_scan_date": next_scan_date,
                }

        scan_request_payload = {
            "asset_id": asset_id,
            "user_id": current_user["_id"],
            "df_id": current_user["df_id"],
        }

        await publish_message(queue_name="cookie_scan_queue", message=json.dumps(scan_request_payload))

        return {"message": f"Cookie scan request for asset {asset_id} submitted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get-all-website-assets", summary="Retrieve Assets for a given DF ID with optional category filter")
async def get_all_website_assets(
    current_user: dict = Depends(get_current_user),
    current_page: int = Query(1, ge=1, description="Current page number"),
    data_per_page: int = Query(20, ge=1, description="Number of items per page"),
    service: CookieManagementService = Depends(get_cookie_service),
):
    try:
        assets = await service.get_all_websites_with_cookies(user=current_user, current_page=current_page, data_per_page=data_per_page)
        return assets
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/create-cookie",
    status_code=status.HTTP_201_CREATED,
    response_model=CookieResponse,
    summary="Create a new Cookie",
)
async def create_cookie_endpoint(
    website_id: str,
    cookie_data: CookieCreate,
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):
    try:
        created_cookie = await service.create_cookie(website_id, current_user, cookie_data.model_dump())
        return created_cookie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-cookie/{cookie_id}",
    response_model=CookieResponse,
    summary="Retrieve a Cookie by ID",
)
async def get_cookie_endpoint(
    cookie_id: str,
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):
    try:
        cookie = await service.get_cookie(cookie_id, current_user)
        if not cookie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cookie not found",
            )
        return cookie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get-all-cookies", summary="Retrieve Cookies", response_model=CookiesPaginatedResponse)
async def get_all_cookies_endpoint(
    website_id: str,
    current_page: int = Query(1, ge=1),
    data_per_page: int = Query(20, ge=1),
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):
    try:
        cookies = await service.get_all_cookies_for_website(
            website_id=website_id, current_user=current_user, current_page=current_page, data_per_page=data_per_page
        )

        return cookies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/update-cookie/{cookie_id}",
    response_model=CookieResponse,
    summary="Update an existing cookie",
)
async def update_cookie_endpoint(
    cookie_id: str,
    update_cookie_data: CookieUpdate,
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):
    updated_cookie = await service.update_cookie(
        cookie_id,
        current_user,
        update_cookie_data.model_dump(exclude_unset=True, exclude_defaults=True),
    )
    if not updated_cookie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookie not found or no changes made",
        )
    return updated_cookie


@router.patch(
    "/publish-cookie/{cookie_id}",
    response_model=CookieResponse,
    summary="Publish a Cookie",
)
async def publish_cookie_endpoint(
    cookie_id: str,
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):

    try:
        published_cookie = await service.publish_cookie(cookie_id, current_user)
        return published_cookie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-cookie/{cookie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cookie",
)
async def delete_cookie_endpoint(
    cookie_id: str,
    current_user: dict = Depends(get_current_user),
    service: CookieManagementService = Depends(get_cookie_service),
):
    try:
        deleted_cookie = await service.delete_cookie(cookie_id, current_user)
        if not deleted_cookie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cookie not able to delete",
            )
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
