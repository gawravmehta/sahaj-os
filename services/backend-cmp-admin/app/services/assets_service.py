from datetime import datetime, UTC
import re
from typing import Dict, Any, List, Optional

from fastapi import HTTPException, status


from app.crud.assets_crud import AssetCrud
from app.utils.business_logger import log_business_event
from app.schemas.assets_schema import AssetInDB, MetaCookies


class AssetService:
    def __init__(
        self,
        crud: AssetCrud,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection

    async def create_asset(self, asset_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new asset in the system."""
        is_duplicate = await self.crud.is_duplicate_name(asset_name=asset_data["asset_name"], df_id=user["df_id"])
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An Asset with the same name already exists.",
            )

        asset_data["created_by"] = user["_id"]
        asset_data["df_id"] = user["df_id"]
        asset_data["asset_status"] = "draft"
        asset_model = AssetInDB(**asset_data)

        created_asset = await self.crud.create_asset(asset_model.model_dump())
        await log_business_event(
            event_type="CREATE_ASSET",
            user_email=user.get("email"),
            context={"asset_id": created_asset["_id"]},
            message="Asset created successfully",
            business_logs_collection=self.business_logs_collection,
        )
        return created_asset

    async def update_asset(self, asset_id: str, update_data: Dict[str, Any], user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Updates an existing asset, only if it's in a 'draft' state."""
        df_id = user["df_id"]
        existing_asset = await self.crud.get_asset(asset_id, df_id)

        if not existing_asset:
            raise HTTPException(status_code=404, detail="Asset not found.")

        if existing_asset["asset_status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail="Only Assets in draft status can be updated.",
            )
        if "asset_name" in update_data:
            is_duplicate = await self.crud.is_duplicate_name(asset_name=update_data["asset_name"], df_id=df_id)
            if is_duplicate:
                raise HTTPException(
                    status_code=400,
                    detail=f"An Asset with name '{update_data['asset_name']}' already exists.",
                )
        update_data["updated_at"] = datetime.now(UTC)
        update_data["updated_by"] = user["_id"]

        updated = await self.crud.update_asset_by_id(asset_id, df_id, update_data)

        await log_business_event(
            event_type="UPDATE_ASSET",
            user_email=user.get("email"),
            context={"asset_id": asset_id},
            message="Asset updated successfully",
            business_logs_collection=self.business_logs_collection,
        )
        return updated

    async def update_asset_cookie_fields(self, asset_id: str, user: Dict[str, Any], meta_cookies: MetaCookies) -> Optional[Dict[str, Any]]:

        df_id = user["df_id"]
        asset = await self.crud.get_asset(asset_id, df_id)

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        if asset.get("category", "").lower() == "website":
            existing_meta_cookies_data = asset.get("meta_cookies", {})
            existing_meta_cookies = MetaCookies(**existing_meta_cookies_data)

            update_fields = meta_cookies.model_dump(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(existing_meta_cookies, field, value)

            update_data = {
                "meta_cookies": existing_meta_cookies.model_dump(),
                "updated_at": datetime.now(UTC),
                "updated_by": user["_id"],
            }
            updated_asset = await self.crud.update_asset_by_id(asset_id, df_id, update_data)
            await log_business_event(
                event_type="UPDATE_ASSET_COOKIE_FIELDS",
                user_email=user.get("email"),
                context={"asset_id": asset_id, "meta_cookies_updated_fields": list(update_fields.keys())},
                message="Asset cookie fields updated successfully",
                business_logs_collection=self.business_logs_collection,
            )
            return updated_asset

        return None

    async def publish_asset(self, asset_id: str, user: dict) -> Optional[dict]:
        """Publishes an asset by changing its status to 'published'."""
        df_id = user["df_id"]
        asset = await self.crud.get_asset(asset_id, df_id)

        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or does not belong to the current domain.",
            )
        if asset["asset_status"] == "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset is already published.",
            )
        elif asset["asset_status"] == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish an archived Asset.",
            )

        update_data = {
            "asset_status": "published",
            "updated_by": user["_id"],
            "updated_at": datetime.now(UTC),
        }
        await log_business_event(
            event_type="PUBLISH_ASSET",
            user_email=user.get("email"),
            context={"asset_id": asset_id, "user_id": user["_id"]},
            message="Asset published successfully",
            business_logs_collection=self.business_logs_collection,
        )
        return await self.crud.update_asset_by_id(asset_id, df_id, update_data)

    async def get_all_assets(
        self, user: Dict[str, Any], current_page: int = 1, data_per_page: int = 20, category: str | None = None
    ) -> Dict[str, Any]:
        """Retrieves a paginated list of assets for a data fiduciary, with optional category filter."""

        offset = (current_page - 1) * data_per_page

        response = await self.crud.get_all_assets(df_id=user["df_id"], offset=offset, limit=data_per_page, category=category)
        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page

        await log_business_event(
            event_type="LIST_ASSETS",
            user_email=user.get("email"),
            context={"current_page": current_page, "data_per_page": data_per_page, "category": category},
            message="Listed Assets from master collection",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "category": category,
            "assets": response.get("data", []),
        }

    async def get_asset(self, asset_id: str, user: Dict[str, Any], for_system: Optional[bool] = False) -> Optional[dict]:
        """Retrieves a single asset by its ID."""
        df_id = user["df_id"]
        asset_data = await self.crud.get_asset(asset_id, df_id)
        if not for_system:
            await log_business_event(
                event_type="GET_ASSET",
                user_email=user.get("email"),
                context={
                    "asset_id": asset_id,
                },
                message="Fetched a specific Asset from master collection",
                business_logs_collection=self.business_logs_collection,
            )
        return asset_data

    async def delete_asset(self, asset_id: str, user: Dict[str, Any]) -> Optional[dict]:
        """Performs a soft delete by archiving the asset."""
        existing_asset = await self.crud.get_asset(asset_id, user["df_id"])

        if not existing_asset or existing_asset.get("asset_status") == "archived":
            return None

        updated_asset = await self.crud.update_asset_by_id(
            asset_id,
            user["df_id"],
            {
                "asset_status": "archived",
                "updated_at": datetime.now(UTC),
                "updated_by": user["_id"],
            },
        )
        await log_business_event(
            event_type="DELETE_ASSET",
            user_email=user.get("email"),
            context={"asset_id": asset_id},
            message="Asset deleted (soft delete)",
            business_logs_collection=self.business_logs_collection,
        )
        return updated_asset
