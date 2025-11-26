from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import Dict, Any, Optional, List
from app.utils.common import convert_objectid_to_str, validate_object_id


class WebhooksCrud:
    def __init__(self, webhooks_collection: AsyncIOMotorCollection):
        self.webhooks_collection = webhooks_collection

    async def create_webhook(self, webhook_data: Dict[str, Any]) -> str:
        """Insert webhook into DB"""
        result = await self.webhooks_collection.insert_one(webhook_data)
        return convert_objectid_to_str(result.inserted_id)

    async def get_webhook_by_url_and_df(self, url: str, df_id: str) -> Optional[Dict[str, Any]]:
        return await self.webhooks_collection.find_one({"url": url, "df_id": df_id, "status": {"$ne": "archived"}})

    async def get_webhook(self, webhook_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(webhook_id)
        query = {
            "_id": object_id,
            "df_id": df_id,
            "status": {"$ne": "archived"},
        }
        doc = await self.webhooks_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def list_all_webhooks_by_df(self, df_id: str) -> List[Dict[str, Any]]:
        """List all non-archived webhooks for a given DF, without pagination."""
        query = {"df_id": df_id, "status": {"$ne": "archived"}}
        cursor = self.webhooks_collection.find(query)
        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))
        return data

    async def list_webhooks_by_df(self, df_id: str, offset: int, limit: int) -> Dict[str, Any]:
        """List non-archived webhooks for a given DF with pagination."""
        query = {"df_id": df_id, "status": {"$ne": "archived"}}
        
        total_items = await self.webhooks_collection.count_documents(query)
        
        cursor = self.webhooks_collection.find(query).skip(offset).limit(limit)
        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))
        return {"data": data, "total": total_items}

    async def update_webhook(self, webhook_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(webhook_id)
        await self.webhooks_collection.update_one({"_id": ObjectId(webhook_id)}, {"$set": update_data})
        updated_data = await self.webhooks_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def delete_webhook(self, webhook_id: str) -> bool:
        result = await self.webhooks_collection.update_one({"_id": ObjectId(webhook_id)}, {"$set": {"status": "archived"}})
        return result.modified_count > 0
