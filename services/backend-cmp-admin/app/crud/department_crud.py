from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


class DepartmentCRUD:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_by_name(self, department_name: str, df_id: str):
        return await self.collection.find_one({"department_name": department_name, "df_id": df_id})

    async def find_by_id(self, department_id: str):
        return await self.collection.find_one({"_id": ObjectId(department_id)})

    async def search_by_name(self, department_name: str, df_id: str):
        regex = f".*{department_name}.*"
        cursor = self.collection.find({"department_name": {"$regex": regex, "$options": "i"}, "df_id": df_id})
        return await cursor.to_list(length=100)

    async def get_all(self, df_id: str, skip: int = 0, limit: int = 10):
        cursor = self.collection.find({"df_id": df_id, "is_deleted": False}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def create(self, department_data: dict):
        result = await self.collection.insert_one(department_data)
        return result

    async def update_department(self, department_id: str, update: dict):
        return await self.collection.update_one({"_id": ObjectId(department_id)}, {"$set": update})

    async def count_departments(self, df_id: str):
        return await self.collection.count_documents({"df_id": df_id, "is_deleted": False})
