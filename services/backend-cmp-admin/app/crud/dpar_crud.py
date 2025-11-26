from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List


class DparCRUD:
    def __init__(
        self,
        dpar_collection: AsyncIOMotorCollection,
        dpar_reports_collection: AsyncIOMotorCollection,
        dpar_bulk_upload_collection: AsyncIOMotorCollection,
    ):
        self.dpar_collection = dpar_collection
        self.dpar_reports_collection = dpar_reports_collection
        self.dpar_bulk_upload_collection = dpar_bulk_upload_collection

    async def count_requests(self, filters: Dict[str, Any]) -> int:
        return await self.dpar_collection.count_documents(filters)

    async def get_requests(self, filters: Dict[str, Any], projection: Dict[str, Any], skip: int, limit: int) -> List[Dict[str, Any]]:
        cursor = self.dpar_collection.find(filters, projection).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def insert_request(self, request_data: Dict[str, Any]) -> str:
        result = await self.dpar_collection.insert_one(request_data)
        if not result.acknowledged:
            return None
        return str(result.inserted_id)

    async def get_last_request(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.dpar_collection.find_one({"requested_by": user_id}, sort=[("created_timestamp", -1)])

    async def check_recent_request(self, query_filter: Dict[str, Any]) -> bool:
        count = await self.dpar_collection.count_documents(query_filter)
        return count > 0

    async def get_by_id(self, request_id: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        query = {"_id": ObjectId(request_id), "is_deleted": False}
        if filters:
            query.update(filters)
        return await self.dpar_collection.find_one(query)

    async def update_request(self, request_id: str, update_fields: Dict[str, Any]):
        return await self.dpar_collection.update_one({"_id": ObjectId(request_id)}, update_fields)

    async def insert_report(self, report: dict):
        return await self.dpar_reports_collection.insert_one(report)

    async def add_conversation(self, request_id: str, conversation_entry: dict):
        return await self.dpar_collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$push": {"request_conversation": conversation_entry}},
        )

    async def insert_upload(self, record: Dict):
        return await self.dpar_bulk_upload_collection.insert_one(record)

    async def get_requests_for_export(self, df_id: str, fields: list):
        projection = {field: 1 for field in fields}
        cursor = self.dpar_collection.find({"df_id": df_id, "is_deleted": False}, projection)
        return await cursor.to_list(length=None)
