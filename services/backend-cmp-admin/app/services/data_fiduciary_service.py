from datetime import datetime, UTC
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.crud.data_fiduciary_crud import DataFiduciaryCRUD
from app.schemas.data_fiduciary_schema import UpdateDataFiduciary
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.config import settings
from app.utils.business_logger import log_business_event
from typing import Dict, Any
from app.utils.common import convert_objectid_to_str


class DataFiduciaryService:
    def __init__(
        self,
        crud: DataFiduciaryCRUD,
        business_logs_collection: str,
        user_collection: AsyncIOMotorCollection,
        df_keys_collection: AsyncIOMotorCollection,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection
        self.user_collection = user_collection
        self.df_keys_collection = df_keys_collection

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = ".") -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and v:
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    async def setup(self, df_id: str, payload: UpdateDataFiduciary, user: Dict[str, Any]):
        user_email = user.get("email") or user.get("id") or "system"

        existing_df = await self.crud.get_data_fiduciary(df_id)
        if not existing_df:
            await log_business_event(
                event_type="SETUP_DATA_FIDUCIARY_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "Data fiduciary not found"},
                message=f"Data Fiduciary setup failed: DF with ID '{df_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        update_doc = jsonable_encoder(payload, exclude_unset=True)

        user_basic_info = update_doc.pop("user_basic_info", None)

        now = datetime.now(UTC)

        if update_doc.get("communication"):
            if update_doc["communication"].get("smtp"):
                update_doc["communication"]["smtp"]["audit"] = {
                    "last_updated_by": user_email,
                    "last_updated_at": now,
                }
            if update_doc["communication"].get("sms"):
                update_doc["communication"]["sms"]["audit"] = {
                    "last_updated_by": user_email,
                    "last_updated_at": now,
                }

        if update_doc.get("ai"):
            update_doc["ai"]["audit"] = {
                "last_updated_by": user_email,
                "last_updated_at": now,
            }

        update_ops = self._flatten_dict(update_doc)

        updated = await self.crud.update_data_fiduciary(df_id, update_ops)

        if user_basic_info:
            admin_email = settings.SUPERADMIN_EMAIL
            user_update_doc = jsonable_encoder(user_basic_info, exclude_unset=True)

            user_update_doc["is_org_configured"] = True

            if user_update_doc:
                result = await self.user_collection.update_one(
                    {"email": admin_email},
                    {"$set": user_update_doc},
                )

        if not updated:
            await log_business_event(
                event_type="SETUP_DATA_FIDUCIARY_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "No updates applied"},
                message=f"Data Fiduciary setup failed for DF ID '{df_id}': No updates were applied.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=400, detail="No updates were applied")

        await log_business_event(
            event_type="SETUP_DATA_FIDUCIARY_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id, "updated_fields": list(update_ops.keys())},
            message=f"Data Fiduciary '{df_id}' setup successfully. Fields updated: {', '.join(update_ops.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "msg": "Data fiduciary setup successfully",
            "df_id": df_id,
            "updated_at": now,
        }

    async def get_details(self, df_id: str, user: Dict[str, Any]):
        user_email = user.get("email") or user.get("id") or "system"
        df = await self.crud.get_data_fiduciary(df_id)
        df_keys = await self.df_keys_collection.find_one({"df_id": df_id})
        if not df or not df_keys:
            await log_business_event(
                event_type="GET_DATA_FIDUCIARY_DETAILS_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "Data fiduciary not found"},
                message=f"Failed to fetch Data Fiduciary details: DF with ID '{df_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        await log_business_event(
            event_type="GET_DATA_FIDUCIARY_DETAILS_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id},
            message=f"Data Fiduciary details fetched successfully for DF ID '{df_id}'.",
            business_logs_collection=self.business_logs_collection,
        )
        return {"df": convert_objectid_to_str(df), "df_keys": convert_objectid_to_str(df_keys)}

    async def get_df_name(self, df_id: str, user: Dict[str, Any]) -> str:
        user_email = user.get("email") or user.get("id") or "system"
        df = await self.crud.get_data_fiduciary(df_id)
        if not df:
            await log_business_event(
                event_type="GET_DF_NAME_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "Data fiduciary not found"},
                message=f"Failed to fetch Data Fiduciary name: DF with ID '{df_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        df_name = df.get("org_info", {}).get("name", "")
        await log_business_event(
            event_type="GET_DF_NAME_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id, "df_name": df_name},
            message=f"Data Fiduciary name '{df_name}' fetched successfully for DF ID '{df_id}'.",
            business_logs_collection=self.business_logs_collection,
        )
        return df_name

    async def get_sms_templates(self, df_id: str, user: Dict[str, Any]):
        user_email = user.get("email") or user.get("id") or "system"
        df = await self.crud.get_data_fiduciary(df_id)
        if not df:
            await log_business_event(
                event_type="GET_SMS_TEMPLATES_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "Data fiduciary not found"},
                message=f"Failed to fetch SMS templates: DF with ID '{df_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        communication = df.get("communication", {})
        sms_config = communication.get("sms", {})
        templates = sms_config.get("templates", [])

        await log_business_event(
            event_type="GET_SMS_TEMPLATES_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id, "template_count": len(templates)},
            message=f"SMS templates fetched successfully for DF ID '{df_id}'. Found {len(templates)} templates.",
            business_logs_collection=self.business_logs_collection,
        )
        return templates

    async def get_in_app_notification_templates(self, df_id: str, user: Dict[str, Any]):
        user_email = user.get("email") or user.get("id") or "system"
        df = await self.crud.get_data_fiduciary(df_id)
        if not df:
            await log_business_event(
                event_type="GET_IN_APP_NOTIFICATION_TEMPLATES_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "reason": "Data fiduciary not found"},
                message=f"Failed to fetch in-app notification templates: DF with ID '{df_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Data fiduciary not found")

        communication = df.get("communication", {})
        templates = communication.get("in_app", [])

        await log_business_event(
            event_type="GET_IN_APP_NOTIFICATION_TEMPLATES_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id, "template_count": len(templates)},
            message=f"In-app notification templates fetched successfully for DF ID '{df_id}'. Found {len(templates)} templates.",
            business_logs_collection=self.business_logs_collection,
        )
        return templates
