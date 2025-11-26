from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Any, Optional
from bson import ObjectId


class RoleCRUD:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_by_name(self, role_name: str, df_id: str):
        return await self.collection.find_one({"role_name": role_name, "df_id": df_id, "is_deleted": False})

    async def insert(self, role_data: dict):
        return await self.collection.insert_one(role_data)

    async def get_roles_paginated(self, df_id: str, skip: int, limit: int) -> List[Dict[str, Any]]:
        cursor = (
            self.collection.find(
                {"is_deleted": False, "df_id": df_id},
                {"_id": 1, "role_name": 1, "role_description": 1, "routes_accessible": 1},
            )
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_roles(self, df_id: str) -> int:
        return await self.collection.count_documents({"is_deleted": False, "df_id": df_id})

    async def find_by_id(self, role_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(role_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(role_id), "is_deleted": False})

    async def update_role(self, role_id: str, update_fields: dict):
        return await self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": update_fields},
        )

    async def get_role_users(self, role_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(role_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(role_id), "is_deleted": False}, {"role_users": 1})

    async def update_role_users(self, role_id: str, updated_users: list):
        return await self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": {"role_users": updated_users}},
        )

    async def update_role_permissions(self, role_id: str, routes: list):
        return await self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {
                "$set": {
                    "routes_accessible": routes,
                }
            },
        )

    async def search_roles(self, df_id: str, role_name: str):
        regex_pattern = {"$regex": role_name, "$options": "i"}
        cursor = self.collection.find(
            {
                "role_name": regex_pattern,
                "df_id": df_id,
                "is_deleted": False,
            },
            {"_id": 1, "role_name": 1, "role_description": 1},
        )
        return await cursor.to_list(length=None)

    async def soft_delete_role(self, role_id: str, updated_data: dict):
        return await self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": updated_data},
        )

    async def add_user_to_role(self, role_id: str, user_id: str):
        return await self.collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$addToSet": {"role_users": user_id}},
        )

    async def add_user_to_roles(self, role_ids: List[str], user_id: str):
        object_ids = [ObjectId(role_id) for role_id in role_ids]

        result = await self.collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$addToSet": {"role_users": user_id}},
        )
        return result
