from typing import Dict, Any, List, Optional, Literal
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.webhook_events_schema import WebhookEventInDB, PyObjectId
from datetime import UTC, datetime


class WebhookEventCRUD:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_event(self, event_data: WebhookEventInDB) -> PyObjectId:
        event_dict = event_data.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(event_dict)
        return str(result.inserted_id)

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id": ObjectId(event_id)})

    async def update_event_status(self, event_id: str, status: Literal["sent", "failed"], attempts: int, last_error: Optional[str] = None) -> bool:
        update_data = {"status": status, "attempts": attempts, "updated_at": datetime.now(UTC)}
        if last_error:
            update_data["last_error"] = last_error

        result = await self.collection.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
        return result.modified_count > 0

    async def list_pending_events(self) -> List[Dict[str, Any]]:
        return await self.collection.find({"status": {"$ne": "sent"}}).to_list(None)
