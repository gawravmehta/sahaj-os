from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Optional
from app.utils.common import convert_objectid_to_str


class DataFiduciaryCRUD:
    def __init__(self, df_register_collection: AsyncIOMotorCollection):
        self.df_register_collection = df_register_collection

    async def get_data_fiduciary(self, df_id: str) -> Optional[Dict]:
        doc = await self.df_register_collection.find_one({"df_id": df_id})
        return convert_objectid_to_str(doc) if doc else None

    async def update_data_fiduciary(self, df_id: str, update_data: Dict) -> Optional[Dict]:
        result = await self.df_register_collection.update_one(
            {"df_id": df_id},
            {"$set": update_data},
            upsert=False,
        )
        if result.matched_count == 0:
            return None
        updated_doc = await self.get_data_fiduciary(df_id)
        return updated_doc
