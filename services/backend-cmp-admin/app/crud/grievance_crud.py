from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List
from bson import ObjectId


class GrievanceCRUD:
    def __init__(
        self,
        grievance_collection: AsyncIOMotorCollection,
    ):
        self.grievance_collection = grievance_collection

    async def count_grievances(self) -> int:
        return await self.grievance_collection.count_documents({})

    async def get_grievances(
        self,
        skip: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        projection = {
            "_id": 1,
            "subject": 1,
            "request_status": 1,
            "created_at": 1,
            "last_updated_at": 1,
            "is_verified": 1,
            "is_registered_user": 1,
            "email": 1,
            "mobile_number": 1,
            "dp_type": 1,
            "business_entity": 1,
            "data_processor": 1,
            "ticket_allocated": 1,
        }
        cursor = self.grievance_collection.find({}, projection).skip(skip).limit(limit)
        grievances = await cursor.to_list(length=limit)

        for g in grievances:
            g["_id"] = str(g["_id"])
        return grievances

    async def get_by_id(self, grievance_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(grievance_id):
            return None
        grievance = await self.grievance_collection.find_one({"_id": ObjectId(grievance_id)})
        if grievance:
            grievance["_id"] = str(grievance["_id"])
        return grievance

    async def resolve_grievance(self, grievance_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(grievance_id):
            return None
        grievance = await self.grievance_collection.find_one_and_update(
            {"_id": ObjectId(grievance_id)},
            {"$set": {"request_status": "resolved"}},
        )
        if grievance:
            grievance["_id"] = str(grievance["_id"])
        return grievance
