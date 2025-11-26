from datetime import UTC, datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING


class IncidentCRUD:
    def __init__(self, incident_collection: AsyncIOMotorCollection):
        self.incident_collection = incident_collection

    async def find_duplicate(self, df_id: str, incident_name: str):
        return await self.incident_collection.find_one({"df_id": df_id, "incident_name": incident_name, "status": "draft"})

    async def insert_incident(self, data: dict) -> str:
        result = await self.incident_collection.insert_one(data)
        return str(result.inserted_id)

    async def update_incident(self, incident_id: str, update_data: dict):
        await self.incident_collection.update_one(
            {"_id": ObjectId(incident_id)},
            {"$set": update_data},
        )

    async def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return await self.incident_collection.find_one({"_id": ObjectId(incident_id)})

    async def count_incidents(self, query: dict) -> int:
        return await self.incident_collection.count_documents(query)

    async def get_incidents(
        self,
        query: dict,
        sort_order: str,
        skip: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        sort_dir = ASCENDING if sort_order == "asc" else DESCENDING
        cursor = self.incident_collection.find(query).sort("created_at", sort_dir).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_filter_fields(self, df_id: str) -> Dict[str, List[str]]:
        query = {"df_id": df_id}

        incident_types = await self.incident_collection.distinct("incident_type", query)
        incident_sensitivities = await self.incident_collection.distinct("incident_sensitivity", query)
        statuses = await self.incident_collection.distinct("status", query)
        current_stages = await self.incident_collection.distinct("current_stage", query)

        return {
            "incident_type": sorted([x for x in incident_types if x]),
            "incident_sensitivity": sorted([x for x in incident_sensitivities if x]),
            "status": sorted([x for x in statuses if x]),
            "current_stage": sorted([x for x in current_stages if x]),
        }

    async def publish_incident(self, incident_id: str):
        result = await self.incident_collection.update_one(
            {"_id": ObjectId(incident_id)},
            {"$set": {"status": "published", "updated_at": datetime.now(UTC)}},
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to publish incident")
        return True
