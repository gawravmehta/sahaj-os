from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List
from bson import ObjectId

from app.utils.common import validate_object_id, convert_objectid_to_str


class AssetCrud:
    def __init__(
        self,
        assets_master_collection: AsyncIOMotorCollection,
    ):
        self.assets_master_collection = assets_master_collection

    async def create_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new asset."""
        # Create a copy of the data to prevent modifying the input dictionary in place during the insert operation.
        data_to_insert = data.copy()
        result = await self.assets_master_collection.insert_one(data_to_insert)
        data_to_insert["_id"] = str(result.inserted_id)
        return data_to_insert

    async def get_asset(self, asset_id: str, df_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single asset by ID and DF ID in draft or published state."""
        object_id = validate_object_id(asset_id)
        query = {
            "_id": object_id,
            "df_id": df_id,
            "asset_status": {"$in": ["draft", "published"]},
        }
        doc = await self.assets_master_collection.find_one(query)
        return convert_objectid_to_str(doc) if doc else None

    async def get_all_assets(self, df_id: str, offset: int, limit: int, category: str | None = None) -> Dict[str, Any]:
        """Fetch a paginated list of all assets for a DF ID with optional category filter."""

        query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}

        if category:
            query["category"] = category

        cursor = self.assets_master_collection.find(query).skip(offset).limit(limit)
        total = await self.assets_master_collection.count_documents(query)

        data = []
        async for doc in cursor:
            data.append(convert_objectid_to_str(doc))

        return {"data": data, "total": total}

    async def update_asset_by_id(self, asset_id: str, df_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
        """Update an existing asset by ID and DF ID."""
        object_id = validate_object_id(asset_id)
        await self.assets_master_collection.update_one(
            {"_id": object_id, "df_id": df_id},
            {"$set": update_data},
        )
        updated_data = await self.assets_master_collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated_data)

    async def is_duplicate_name(self, asset_name: str, df_id: str) -> bool:
        """Check for duplicate asset names in draft or published status."""
        existing = await self.assets_master_collection.find_one(
            {
                "asset_name": asset_name,
                "df_id": df_id,
                "asset_status": {"$in": ["draft", "published"]},
            }
        )
        return existing is not None

    async def count_assets(self, df_id: str) -> int:
        """Count the number of assets for a DF ID."""
        query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
        return await self.assets_master_collection.count_documents(query)

    async def get_assets_categories(self, df_id: str) -> List[str]:
        """Get a list of unique categories for assets in draft or published status."""
        query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
        categories = await self.assets_master_collection.distinct("category", query)
        return categories

    async def get_total_cookie_count(self, df_id: str) -> int:
        """Get the total number of cookies for a DF ID without aggregation."""

        query = {
            "df_id": df_id,
            "asset_status": {"$in": ["draft", "published"]}
        }

        cursor = self.assets_master_collection.find(
            query,
            {"meta_cookies": 1, "_id": 0}
        )

        total = 0

        async for doc in cursor:
            meta = doc.get("meta_cookies")
            if meta and isinstance(meta, dict):
                total += meta.get("cookies_count", 0)

        return total
