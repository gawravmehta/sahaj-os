from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
from typing import List, Dict, Any


class VendorCRUD:
    def __init__(
        self,
        vendor_collection: AsyncIOMotorCollection,
        purpose_collection: AsyncIOMotorCollection,
    ):
        self.vendor_collection = vendor_collection
        self.purpose_collection = purpose_collection

    async def get_vendor_by_id(self, vendor_id: str):
        vendor = await self.vendor_collection.find_one({"_id": ObjectId(vendor_id), "status": {"$ne": "archived"}})
        return vendor

    async def create_vendor(self, vendor_data: dict):
        result = await self.vendor_collection.insert_one(vendor_data)
        return result

    async def update_vendor(self, vendor_id: str, update_data: dict):
        result = await self.vendor_collection.update_one({"_id": ObjectId(vendor_id)}, {"$set": update_data})
        return result

    async def count_vendors(self, query: dict) -> int:
        """Count vendors matching query."""
        return await self.vendor_collection.count_documents(query)

    async def get_vendors(
        self,
        query: dict,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> List[dict]:
        """Get paginated vendor list with sorting."""
        sort_dir = ASCENDING if sort_order == "asc" else DESCENDING
        skip = (page - 1) * page_size

        cursor = self.vendor_collection.find(query).sort("created_at", sort_dir).skip(skip).limit(page_size)
        vendors = []
        async for v in cursor:
            v["_id"] = str(v["_id"])
            vendors.append(v)
        return vendors

    async def get_filter_fields(self, df_id: str) -> Dict[str, Any]:
        """Get distinct filter values without aggregation."""
        query = {"df_id": df_id, "status": {"$ne": "archived"}}

        dpr_country = await self.vendor_collection.distinct("dpr_country", query)
        dpr_country_risk = await self.vendor_collection.distinct("dpr_country_risk", query)
        industry = await self.vendor_collection.distinct("industry", query)
        
        # For processing_category, we need to iterate if it's an array of strings
        processing_category_list = []
        async for doc in self.vendor_collection.find(query, {"processing_category": 1}):
            if "processing_category" in doc and isinstance(doc["processing_category"], list):
                processing_category_list.extend(doc["processing_category"])
        processing_category = list(set(processing_category_list)) # Get unique values

        audit_result = await self.vendor_collection.distinct("audit_status.audit_result", query)

        return {
            "dpr_country": sorted([x for x in dpr_country if x]),
            "dpr_country_risk": sorted([x for x in dpr_country_risk if x]),
            "industry": sorted([x for x in industry if x]),
            "processing_category": sorted([x for x in processing_category if x]),
            "cross_border": [True, False],
            "sub_processor": [True, False],
            "audit_result": sorted([x for x in audit_result if x]),
        }

    def archive_vendor(self, vendor_id: str):
        result = self.vendor_collection.update_one(
            {"_id": ObjectId(vendor_id)},
            {"$set": {"status": "archived"}},
        )
        return result

    async def update_purpose_with_vendor(self, purpose_id: str, vendor_details: dict):
        result = await self.purpose_collection.update_one(
            {"_id": ObjectId(purpose_id)},
            {
                "$addToSet": {
                    "data_processor_details": {
                        "data_processor_id": str(vendor_details.get("vendor_id")),
                        "data_processor_name": vendor_details.get("vendor_name"),
                        "cross_border_data_transfer": vendor_details.get("cross_border"),
                    }
                }
            },
        )
        return result
