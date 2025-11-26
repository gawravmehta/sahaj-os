import httpx
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List
from bson import ObjectId
from app.utils.common import convert_objectid_to_str, validate_object_id


class CollectionPointCrud:
    def __init__(
        self,
        cp_master_collection: AsyncIOMotorCollection,
    ):
        self.cp_master_collection = cp_master_collection

    async def create_cp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.cp_master_collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    async def get_all_cps(self, df_id: str, offset: int, limit: int, additional_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = {"df_id": df_id, "cp_status": {"$in": ["draft", "published"]}}
        if additional_filters:
            query.update(additional_filters)
        cursor = self.cp_master_collection.find(query).skip(offset).limit(limit)
        total = await self.cp_master_collection.count_documents(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))
        return {"data": data, "total": total}

    async def get_cp_master(self, cp_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(cp_id)
        query = {
            "_id": object_id,
            "df_id": df_id,
            "cp_status": {"$in": ["draft", "published"]},
        }
        doc = await self.cp_master_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def update_cp_by_id(self, cp_id: str, df_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        object_id = validate_object_id(cp_id)
        await self.cp_master_collection.update_one(
            {"_id": object_id, "df_id": df_id},
            {"$set": update_data},
        )
        updated_data = await self.cp_master_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def is_duplicate_name(self, cp_name: str, asset_id: str, df_id: str):
        existing = await self.cp_master_collection.find_one(
            {
                "cp_name": cp_name,
                "asset_id": asset_id,
                "df_id": df_id,
                "cp_status": {"$in": ["draft", "published"]},
            }
        )
        return existing is not None

    async def count_collection_points(self, df_id: str) -> int:
        return await self.cp_master_collection.count_documents({"df_id": df_id, "cp_status": {"$in": ["draft", "published"]}})
