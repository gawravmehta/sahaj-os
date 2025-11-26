import httpx
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional
from bson import ObjectId
from app.utils.common import validate_object_id, convert_objectid_to_str
from app.core.config import settings


class PurposeCRUD:
    def __init__(
        self,
        purpose_template_collection: AsyncIOMotorCollection,
        purpose_master_collection: AsyncIOMotorCollection,
        purpose_master_translated_collection: AsyncIOMotorCollection,
    ):
        self.purpose_template_collection = purpose_template_collection
        self.purpose_master_collection = purpose_master_collection
        self.purpose_master_translated_collection = purpose_master_translated_collection
        self.external_base_url = settings.DATA_VEDA_URL

    async def get_all_purpose_templates(
        self,
        offset: int = 0,
        limit: int = 20,
        id: Optional[str] = None,
        industry: Optional[str] = None,
        sub_category: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {
            "offset": offset,
            "limit": limit,
        }
        if id:
            params["id"] = id
        if industry:
            params["industry"] = industry
        if sub_category:
            params["sub_category"] = sub_category
        if title:
            params["title"] = title

        url = f"{self.external_base_url}/purposes"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

        return response.json()

    async def create_purpose(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.purpose_master_collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def get_purpose_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(template_id)
        doc = await self.purpose_master_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(doc) if doc else None

    async def update_purpose(self, purpose_id: str, df_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(purpose_id)
        await self.purpose_master_collection.update_one({"_id": object_id, "df_id": df_id}, {"$set": data})
        updated_data = await self.purpose_master_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def delete_purpose_template(self, template_id: str) -> bool:
        object_id = validate_object_id(template_id)
        result = await self.purpose_master_collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def get_all_purpose_master(self, df_id: str, offset: int, limit: int) -> Optional[Dict[str, Any]]:
        query = {"df_id": df_id, "purpose_status": {"$in": ["draft", "published"]}}
        cursor = self.purpose_master_collection.find(query).skip(offset).limit(limit)
        total = await self.purpose_master_collection.count_documents(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))

        return {"data": data, "total": total}

    async def get_purpose_master(self, purpose_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(purpose_id)
        query = {
            "_id": object_id,
            "df_id": df_id,
            "purpose_status": {"$in": ["draft", "published"]},
        }
        doc = await self.purpose_master_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def create_purpose_master(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.purpose_master_collection.insert_one(data)
        data["_id"] = result.inserted_id
        return convert_objectid_to_str(data)

    async def is_duplicate_name(self, purpose_title: str, df_id: str) -> bool:
        """
        Check for duplicate Purpose name in draft or published status.
        """
        query = {
            "purpose_title": purpose_title,
            "df_id": df_id,
            "purpose_status": {"$in": ["draft", "published"]},
        }
        existing = await self.purpose_master_collection.find_one(query)
        return existing is not None

    async def count_consent_purposes(self, df_id: str) -> int:
        """
        Count the number of consent purposes for a DF ID.
        """
        query = {"df_id": df_id, "purpose_status": {"$in": ["draft", "published"]}}
        return await self.purpose_master_collection.count_documents(query)
