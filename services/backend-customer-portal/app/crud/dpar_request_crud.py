from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict
from app.core.logger import app_logger

async def get_user_requests(
    collection: AsyncIOMotorCollection, filters: Dict
) -> List[Dict]:
    app_logger.debug(f"Fetching user requests with filters: {filters}")
    cursor = collection.find(filters).sort("created_timestamp", -1)
    results = await cursor.to_list(length=100)
    app_logger.debug(f"Found {len(results)} user requests.")
    return results
