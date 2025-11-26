from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional
from bson import ObjectId
from app.schemas.auth_schema import UserInDB
from app.utils.common import validate_object_id, convert_objectid_to_str


class UserCRUD:
    def __init__(self, users_collection: AsyncIOMotorCollection):
        self.users_collection = users_collection

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_doc = await self.users_collection.find_one({"email": email})

        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        object_id = validate_object_id(user_id)
        user_doc = await self.users_collection.find_one({"_id": ObjectId(object_id)})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def find_by_ids(self, user_ids: list) -> list:
        object_ids = [ObjectId(uid) for uid in user_ids if validate_object_id(uid)]
        cursor = self.users_collection.find({"_id": {"$in": object_ids}})
        users = await cursor.to_list(length=len(object_ids))
        return [convert_objectid_to_str(user) for user in users]

    async def insert_user_data(self, user_data: Dict[str, Any]) -> ObjectId:
        result = await self.users_collection.insert_one(user_data)
        return result.inserted_id

    async def add_role_to_user(self, user_id: str, role_id: str):
        return await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"user_roles": role_id}},
        )

    async def add_department_to_user(self, user_id: str, department_id: str):
        return await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"user_departments": department_id}},
        )

    async def count_users(self, df_id: str) -> int:
        return await self.users_collection.count_documents({"df_id": df_id})
