import httpx
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List
from bson import ObjectId

from app.utils.common import validate_object_id, convert_objectid_to_str
from app.core.config import settings


class DataElementCRUD:
    def __init__(
        self,
        de_template_collection: AsyncIOMotorCollection,
        de_master_collection: AsyncIOMotorCollection,
        de_master_translated_collection: AsyncIOMotorCollection,
    ):
        self.de_template_collection = de_template_collection
        self.de_master_collection = de_master_collection
        self.de_master_translated_collection = de_master_translated_collection
        self.external_base_url = settings.DATA_VEDA_URL

    async def get_all_de_templates(
        self,
        domain: Optional[str] = None,
        title: Optional[str] = None,
        id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Fetch data elements from external service.
        """
        params = {
            "offset": offset,
            "limit": limit,
        }
        if title:
            params["title"] = title
        if domain:
            params["domain"] = domain
        if id:
            params["id"] = id

        url = f"{self.external_base_url}/data-elements"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
        return response.json()

    async def create_de(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new data element master.
        """
        result = await self.de_master_collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def get_de_master(self, de_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single data element by ID and DF ID in draft or published state.
        """
        object_id = validate_object_id(de_id)
        query = {
            "_id": object_id,
            "df_id": df_id,
            "de_status": {"$in": ["draft", "published"]},
        }
        doc = await self.de_master_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def get_de_master_by_name(self, de_title: str, df_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single data element by name and DF ID in draft or published state.
        """

        query = {
            "de_name": de_title,
            "df_id": df_id,
            "de_status": {"$in": ["draft", "published"]},
        }
        doc = await self.de_master_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def get_all_de_master(self, df_id: str, offset: int, limit: int, is_core_identifier: Optional[bool] = None) -> Dict[str, Any]:
        """
        Fetch paginated list of all data elements for a DF ID.
        """
        query = {"df_id": df_id, "de_status": {"$in": ["draft", "published"]}}
        if is_core_identifier is not None:
            query["is_core_identifier"] = is_core_identifier
        cursor = self.de_master_collection.find(query).skip(offset).limit(limit)
        total = await self.de_master_collection.count_documents(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))

        return {"data": data, "total": total}

    async def update_data_element_by_id(self, de_id: str, df_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
        """
        Update an existing data element by ID and DF ID.
        """
        object_id = validate_object_id(de_id)
        await self.de_master_collection.update_one(
            {"_id": object_id, "df_id": df_id},
            {"$set": update_data},
        )
        updated_data = await self.de_master_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def is_duplicate_name(self, de_name: str, df_id: str) -> bool:
        """
        Check for duplicate DE name in draft or published status.
        """
        query = {
            "de_name": de_name,
            "df_id": df_id,
            "de_status": {"$in": ["draft", "published"]},
        }
        existing = await self.de_master_collection.find_one(query)
        return existing is not None

    async def count_data_elements(self, df_id: str) -> int:
        """
        Count the number of data elements for a DF ID.
        """
        query = {"df_id": df_id, "de_status": {"$in": ["draft", "published"]}}
        return await self.de_master_collection.count_documents(query)
