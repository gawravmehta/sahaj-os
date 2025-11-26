from typing import List, Dict, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.cookie_schema import CookieCreate
from app.utils.common import convert_objectid_to_str, validate_object_id


class CookieCrud:
    def __init__(self, cookie_collection: AsyncIOMotorCollection):
        self.cookie_collection = cookie_collection

    async def create_cookie(self, cookie_doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a new cookie document asynchronously."""
        result = await self.cookie_collection.insert_one(cookie_doc)
        if result.inserted_id:
            cookie_doc["_id"] = str(result.inserted_id)
            return cookie_doc
        return None

    async def get_cookies_for_website(self, website_id: str, df_id: str, offset: int, limit: int) -> Optional[Dict[str, Any]]:
        query = {"website_id": website_id, "df_id": df_id, "cookie_status": {"$in": ["draft", "published"]}}
        cursor = self.cookie_collection.find(query).skip(offset).limit(limit)
        total = await self.cookie_collection.count_documents(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))

        return {"data": data, "total": total}

    async def _get_published_cookies_for_website(self, website_id: str, df_id: str) -> Dict[str, Any]:
        """
        Internal CRUD function to fetch all published cookies for a given website (no pagination).
        """
        query = {
            "website_id": website_id,
            "df_id": df_id,
            "cookie_status": "published",
        }

        cursor = self.cookie_collection.find(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))

        return {"data": data, "total": len(data)}

    async def get_cookie_master(self, cookie_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(cookie_id)
        doc = await self.cookie_collection.find_one({"_id": object_id, "df_id": df_id, "cookie_status": {"$in": ["draft", "published"]}})
        return convert_objectid_to_str(doc) if doc else None

    async def update_cookie_master(self, cookie_id: str, df_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Updates an existing cookie document asynchronously."""
        object_id = validate_object_id(cookie_id)
        await self.cookie_collection.update_one({"_id": object_id, "df_id": df_id}, {"$set": data})
        updated_data = await self.cookie_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def delete_cookie_master(self, cookie_id: str) -> bool:
        """Deletes a cookie document asynchronously."""
        result = await self.cookie_collection.delete_one({"_id": ObjectId(cookie_id)})
        return result.deleted_count == 1

    async def is_duplicate(self, cookie_data: dict, website_id: str) -> bool:
        """
        Checks if a cookie with the same name, hostname, and path already exists.
        This is a low-level database check.
        """
        query = {
            "website_id": website_id,
            "cookie_name": cookie_data["cookie_name"],
            "hostname": cookie_data["hostname"],
            "path": cookie_data.get("path", "/"),
            "cookie_status": {"$in": ["draft", "published"]},
        }
        count = await self.cookie_collection.count_documents(query)
        return count > 0
