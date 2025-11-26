from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.dependencies import get_consent_artifact_collection, get_notifications_collection, get_renewal_collection
from app.services.notifications_service import NotificationService

scheduler = AsyncIOScheduler()


async def start_notification_scheduler(
    consent_artifact_collection: AsyncIOMotorCollection = Depends(get_consent_artifact_collection),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
    renewal_collection: AsyncIOMotorCollection = Depends(get_renewal_collection),
):
    """Initialize APScheduler to run notification jobs."""
    service = NotificationService(consent_artifact_collection, notifications_collection, renewal_collection)
    scheduler.add_job(service.generate_notifications, "interval", minutes=2)
    scheduler.start()
