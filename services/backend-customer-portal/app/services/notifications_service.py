from datetime import datetime, UTC
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.notifications import NotificationOut, PaginatedNotifications
from app.utils.common import clean_mongo_doc
from app.core.logger import app_logger


class NotificationService:
    def __init__(
        self,
        consent_artifact_collection: AsyncIOMotorCollection,
        notifications_collection: AsyncIOMotorCollection,
        renewal_collection: AsyncIOMotorCollection,
    ):
        self.consent_artifact_collection = consent_artifact_collection
        self.notifications_collection = notifications_collection
        self.renewal_collection = renewal_collection

    async def get_user_notifications(self, dp_id: str, page: int = 1, size: int = 10) -> PaginatedNotifications:
        """Fetch paginated notifications for a user, sorted by created_at (latest first)."""

        skip = (page - 1) * size

        total = await self.notifications_collection.count_documents({"dp_id": dp_id})

        cursor = self.notifications_collection.find({"dp_id": dp_id}).sort("created_at", -1).skip(skip).limit(size)

        items = [NotificationOut(**clean_mongo_doc(doc)) async for doc in cursor]

        return PaginatedNotifications(
            total=total,
            page=page,
            size=size,
            items=items,
        )

    async def mark_as_read(self, notification_id: str):
        await self.notifications_collection.update_one({"_id": ObjectId(notification_id)}, {"$set": {"status": "read"}})

    async def generate_notifications(self):
        """Scan renewal collection for all types of expiry events and create notifications."""
        app_logger.info("Generating all expiry notifications...")
        now = datetime.now(UTC)

        cursor = self.renewal_collection.find({"$or": [{"notification_sent": False}, {"notification_sent": {"$exists": False}}]})
        all_events = [doc async for doc in cursor]

        for event in all_events:
            event_id = event.get("_id")
            event_type = event.get("event_type")

            if event_type == "consent_expiry":
                app_logger.info(f"Processing consent renewal event {event_id}...")
                consent_artifact_id = event.get("consent_artifact_id")
                purpose_id = event.get("purpose_id")
                expiry_at = event.get("expiry_at")

                if not all([consent_artifact_id, purpose_id, expiry_at]):
                    app_logger.warning(f"Skipping consent renewal event {event_id} - missing required fields")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_missing_fields"}},
                    )
                    continue

                artifact = await self.consent_artifact_collection.find_one({"_id": ObjectId(consent_artifact_id)})
                if not artifact:
                    app_logger.warning(f"Skipping consent renewal event {event_id} - consent artifact not found")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_artifact_not_found"}},
                    )
                    continue

                artifact_doc = artifact.get("artifact") or {}
                dp_id = (artifact_doc.get("data_principal") or {}).get("dp_id")
                cp_name = artifact_doc.get("cp_name", "")
                agreement_id = artifact_doc.get("agreement_id", "")

                if not dp_id:
                    app_logger.warning(f"Skipping consent renewal event {event_id} - no dp_id found in artifact")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_no_dp_id"}},
                    )
                    continue

                data_element_title = ""
                purpose_title = ""

                for de in artifact_doc["consent_scope"]["data_elements"]:
                    if de["de_id"] == event.get("data_element_id"):
                        data_element_title = de["title"]
                        for consent in de["consents"]:
                            if consent["purpose_id"] == purpose_id:
                                purpose_title = consent["purpose_title"]
                                break
                        break

                if not (data_element_title and purpose_title):
                    app_logger.warning(f"Skipping consent renewal event {event_id} - data element or purpose not found in artifact")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_de_or_purpose_not_found"}},
                    )
                    continue

                exists = await self.notifications_collection.find_one(
                    {
                        "dp_id": dp_id,
                        "artifact_id": consent_artifact_id,
                        "data_element_id": event.get("data_element_id"),
                        "purpose_id": purpose_id,
                        "type": "CONSENT_RENEWAL",
                    }
                )
                if exists:
                    app_logger.info(f"Consent renewal notification already exists for dp_id {dp_id} - purpose {purpose_id}")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now}},
                    )
                    continue

                app_logger.info(f"Creating consent renewal notification for dp_id {dp_id} - purpose {purpose_id}")
                await self.notifications_collection.insert_one(
                    {
                        "dp_id": dp_id,
                        "artifact_id": consent_artifact_id,
                        "type": "CONSENT_RENEWAL",
                        "title": "Consent renewal required",
                        "message": f"Your consent for {data_element_title} (purpose: {purpose_title}) is soon going to expire and requires renewal by {expiry_at}.",
                        "status": "unread",
                        "created_at": now,
                        "expiry_date": datetime.fromisoformat(expiry_at.replace("Z", "+00:00")),
                        "data_element_id": event.get("data_element_id"),
                        "data_element_title": data_element_title,
                        "purpose_id": purpose_id,
                        "purpose_title": purpose_title,
                        "cp_name": cp_name,
                        "agreement_id": agreement_id,
                    }
                )
                await self.renewal_collection.update_one(
                    {"_id": event_id},
                    {"$set": {"notification_sent": True, "updated_at": now}},
                )
            elif event_type == "data_retention_expiry":
                app_logger.info(f"Processing data retention expiry event {event_id}...")
                consent_artifact_id = event.get("consent_artifact_id")
                data_element_id = event.get("data_element_id")
                retention_expiry_at = event.get("retention_expiry_at")

                if not all([consent_artifact_id, data_element_id, retention_expiry_at]):
                    app_logger.warning(f"Skipping data retention event {event_id} - missing required fields")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_missing_fields"}},
                    )
                    continue

                artifact = await self.consent_artifact_collection.find_one({"_id": ObjectId(consent_artifact_id)})
                if not artifact:
                    app_logger.warning(f"Skipping data retention event {event_id} - consent artifact not found")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_artifact_not_found"}},
                    )
                    continue

                artifact_doc = artifact.get("artifact") or {}
                dp_id = (artifact_doc.get("data_principal") or {}).get("dp_id")
                cp_name = artifact_doc.get("cp_name", "")
                agreement_id = artifact_doc.get("agreement_id", "")

                if not dp_id:
                    app_logger.warning(f"Skipping data retention event {event_id} - no dp_id found in artifact")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_no_dp_id"}},
                    )
                    continue

                data_element_title = ""
                for de in artifact_doc["consent_scope"]["data_elements"]:
                    if de["de_id"] == data_element_id:
                        data_element_title = de["title"]
                        break

                if not data_element_title:
                    app_logger.warning(f"Skipping data retention event {event_id} - data element not found in artifact")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_de_not_found"}},
                    )
                    continue

                exists = await self.notifications_collection.find_one(
                    {
                        "dp_id": dp_id,
                        "artifact_id": consent_artifact_id,
                        "data_element_id": data_element_id,
                        "type": "DATA_RETENTION_EXPIRY",
                    }
                )
                if exists:
                    app_logger.info(f"Data retention notification already exists for dp_id {dp_id} - data element {data_element_id}")
                    await self.renewal_collection.update_one(
                        {"_id": event_id},
                        {"$set": {"notification_sent": True, "updated_at": now}},
                    )
                    continue

                app_logger.info(f"Creating data retention notification for dp_id {dp_id} - data element {data_element_id}")
                await self.notifications_collection.insert_one(
                    {
                        "dp_id": dp_id,
                        "artifact_id": consent_artifact_id,
                        "type": "DATA_RETENTION_EXPIRY",
                        "title": "Data retention period expiring",
                        "message": f"The data retention period for {data_element_title} is soon going to expire on {retention_expiry_at}.",
                        "status": "unread",
                        "created_at": now,
                        "expiry_date": datetime.fromisoformat(retention_expiry_at.replace("Z", "+00:00")),
                        "data_element_id": data_element_id,
                        "data_element_title": data_element_title,
                        "cp_name": cp_name,
                        "agreement_id": agreement_id,
                    }
                )
                await self.renewal_collection.update_one(
                    {"_id": event_id},
                    {"$set": {"notification_sent": True, "updated_at": now}},
                )
            else:
                app_logger.warning(f"Unknown event type: {event_type} for event {event_id}. Skipping.")
                await self.renewal_collection.update_one(
                    {"_id": event_id},
                    {"$set": {"notification_sent": True, "updated_at": now, "status": "skipped_unknown_event_type"}},
                )

    async def get_notification(self, notification_id: str):
        return await self.notifications_collection.find_one({"_id": ObjectId(notification_id)})
