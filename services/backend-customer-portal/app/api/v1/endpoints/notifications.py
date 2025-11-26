from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.deps import get_current_user
from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.dependencies import get_consent_artifact_collection, get_notifications_collection, get_renewal_collection
from app.schemas.notifications import PaginatedNotifications
from app.services.notifications_service import NotificationService
from app.core.logger import app_logger
from app.utils.common import clean_mongo_doc

router = APIRouter()


@router.get("/get-all-notifications", response_model=PaginatedNotifications)
async def get_notifications(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
    renewal_collection: AsyncIOMotorCollection = Depends(get_renewal_collection),
):
    """
    Fetch paginated notifications for the authenticated user.
    """
    app_logger.info(f"API Call: /get-all-notifications for dp_id: {current_user['dp_id']}, page: {page}, size: {size}")
    service = NotificationService(consent_artifact_collection, notifications_collection, renewal_collection)

    result = await service.get_user_notifications(current_user["dp_id"], page=page, size=size)

    if not result.items and result.total > 0 and page > 1:
        app_logger.warning(f"Notifications not found for dp_id: {current_user['dp_id']} on page {page}. Total items: {result.total}")
        raise HTTPException(status_code=404, detail="Page not found")

    return result


@router.post("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
    renewal_collection: AsyncIOMotorCollection = Depends(get_renewal_collection),
):
    service = NotificationService(consent_artifact_collection, notifications_collection, renewal_collection)
    await service.mark_as_read(notification_id)
    return {"status": "ok"}


@router.get("/notifications/{notification_id}")
async def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
    renewal_collection: AsyncIOMotorCollection = Depends(get_renewal_collection),
):
    service = NotificationService(consent_artifact_collection, notifications_collection, renewal_collection)
    return clean_mongo_doc(await service.get_notification(notification_id))
