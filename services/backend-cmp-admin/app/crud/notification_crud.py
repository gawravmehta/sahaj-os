from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


class NotificationCRUD:
    def __init__(self, notification_collection: AsyncIOMotorCollection):
        self.notification_collection = notification_collection

    async def count_notifications(self, filter: dict) -> int:
        return await self.notification_collection.count_documents(filter)

    async def get_notifications(self, filter: dict, sort_field: str, sort_order: int, page: int, limit: int) -> list:
        cursor = self.notification_collection.find(filter).sort(sort_field, sort_order).skip((page - 1) * limit).limit(limit)
        return await cursor.to_list(length=limit)

    async def mark_as_read(self, notification_id: str, user_id: str):
        return await self.notification_collection.update_one(
            {"_id": ObjectId(notification_id), f"users.{user_id}.is_deleted": False},
            {"$set": {f"users.{user_id}.is_read": True}},
        )

    async def mark_all_as_read(self, user_id: str):
        return await self.notification_collection.update_many(
            {f"users.{user_id}.is_deleted": False, f"users.{user_id}.is_read": False},
            {"$set": {f"users.{user_id}.is_read": True}},
        )
