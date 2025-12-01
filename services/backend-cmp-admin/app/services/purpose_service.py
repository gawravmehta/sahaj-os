from datetime import datetime, UTC
from typing import Dict, Any, List, Optional

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud.purpose_crud import PurposeCRUD
from app.utils.business_logger import log_business_event
from app.utils.common import generate_blockchain_hash, generate_id
from app.schemas.purpose_schema import LanguageCodes, PurposeInDB, DataElements
from app.services.data_element_service import DataElementService


class PurposeService:
    def __init__(
        self,
        crud: PurposeCRUD,
        data_element_service: DataElementService,
        business_logs_collection: AsyncIOMotorCollection,
    ):
        self.crud = crud
        self.data_element_service = data_element_service
        self.business_logs_collection = business_logs_collection

    async def create_purpose(self, purpose_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        df_id = user["df_id"]
        is_duplicate = await self.crud.is_duplicate_name(purpose_data["purpose_title"], df_id)
        if is_duplicate:
            raise HTTPException(
                status_code=400,
                detail="Purpose title already exists.",
            )

        purpose_data["created_by"] = user["_id"]
        purpose_data["df_id"] = df_id
        purpose_data["updated_at"] = None

        purpose_model = PurposeInDB(**purpose_data)
        created_purpose = await self.crud.create_purpose(purpose_model.model_dump())

        await log_business_event(
            event_type="CREATE_PURPOSE",
            user_email=user.get("email"),
            context={
                "purpose_id": str(created_purpose["_id"]),
                "purpose_title": purpose_data.get("purpose_title"),
                "df_id": df_id,
            },
            message=f"Purpose '{purpose_data.get('purpose_title')}' created successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return created_purpose

    async def copy_purpose(
        self,
        purpose_id: str,
        user: Dict[str, Any],
        data_elements: List[str],
    ) -> Dict[str, Any]:
        df_id = user["df_id"]
        user_id = user["_id"]

        response = await self.crud.get_all_purpose_templates(id=purpose_id)
        if not response or not response.get("data"):
            raise HTTPException(status_code=404, detail=f"Purpose template with ID '{purpose_id}' not found.")

        purpose_template = response["data"][0]
        purpose_title = purpose_template["translations"].get("eng") or purpose_template["translations"].get("en")

        is_duplicate = await self.crud.is_duplicate_name(purpose_title, df_id)
        if is_duplicate:
            raise HTTPException(
                status_code=400,
                detail=f"Purpose title '{purpose_title}' already exists.",
            )

        purpose_model = PurposeInDB(
            purpose_title=purpose_title,
            purpose_description="",
            purpose_priority="low",
            review_frequency="quarterly",
            consent_time_period=30,
            translations=purpose_template["translations"],
            reconsent=False,
            df_id=df_id,
            created_by=user_id,
            updated_at=None,
            updated_by=None,
        )
        created_purpose = await self.crud.create_purpose(purpose_model.model_dump())

        copied_data_elements = []
        for data_element in data_elements:
            copied_de = await self.data_element_service.copy_data_element_by_title(data_element, user)
            copied_data_elements.append(
                {
                    "de_id": copied_de["_id"],
                    "de_name": copied_de["de_name"],
                    "service_mandatory": False,
                    "service_message": None,
                    "legal_mandatory": False,
                    "legal_message": None,
                }
            )

        if copied_data_elements:
            await self.crud.update_purpose(created_purpose["_id"], df_id, {"data_elements": copied_data_elements})
            created_purpose["data_elements"] = copied_data_elements

        await log_business_event(
            event_type="COPY_PURPOSE_FROM_TEMPLATE",
            user_email=user.get("email"),
            context={
                "purpose_id": str(created_purpose["_id"]),
                "purpose_title": purpose_title,
                "template_id": purpose_id,
                "df_id": df_id,
            },
            message=f"Purpose '{purpose_title}' copied from template (ID: '{purpose_id}') successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return created_purpose

    async def delete_purpose(self, purpose_id: str, user: Dict[str, Any]):
        existing_de = await self.crud.get_purpose_master(purpose_id, user["df_id"])

        if not existing_de or existing_de.get("purpose_status") == "archived":
            return None

        updated_de = await self.crud.update_purpose(
            purpose_id,
            user["df_id"],
            {
                "purpose_status": "archived",
                "updated_at": datetime.now(UTC),
                "updated_by": user["_id"],
            },
        )

        await log_business_event(
            event_type="DELETE_PURPOSE",
            user_email=user.get("email"),
            context={
                "purpose_id": purpose_id,
                "purpose_title": existing_de.get("purpose_title"),
                "df_id": user.get("df_id"),
            },
            message=f"Purpose '{existing_de.get('purpose_title')}' soft-deleted (archived) successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return updated_de

    async def get_all_purpose_templates(
        self,
        user: dict,
        current_page: int,
        data_per_page: int,
        id: Optional[str] = None,
        industry: Optional[str] = None,
        sub_category: Optional[str] = None,
        title: Optional[str] = None,
    ):
        offset = (current_page - 1) * data_per_page

        response = await self.crud.get_all_purpose_templates(
            offset=offset,
            limit=data_per_page,
            id=id,
            industry=industry,
            sub_category=sub_category,
            title=title,
        )

        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page

        await log_business_event(
            event_type="LIST_PURPOSE_TEMPLATES",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": user.get("df_id"),
                "filters": {
                    "template_id": id,
                    "industry": industry,
                    "sub_category": sub_category,
                    "title": title,
                },
            },
            message=f"User listed Purpose Templates with filters (Industry: {industry}, Sub-Category: {sub_category}, Title: {title}, ID: {id}). Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "data": response.get("data", []),
        }

    async def publish_purpose(self, purpose_id: str, user: dict) -> Optional[Dict[str, Any]]:
        df_id = user["df_id"]
        purpose = await self.crud.get_purpose_master(purpose_id, df_id)

        if not purpose:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purpose not found or does not belong to the current domain.",
            )
        if purpose["purpose_status"] == "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purpose is already published.",
            )

        elif purpose["purpose_status"] == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish an archived purpose.",
            )

        if not purpose.get("consent_time_period"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Retention period (consent_time_period) is required before publishing.",
            )

        translations = purpose.get("translations", {})
        if not translations or not isinstance(translations, dict) or not any(v for v in translations.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translations are required and cannot be empty before publishing.",
            )

        update_data = {
            "purpose_status": "published",
            "updated_by": user["_id"],
            "updated_at": datetime.now(UTC),
            "purpose_hash_id": generate_blockchain_hash(),
        }
        await log_business_event(
            event_type="PUBLISH_PURPOSE",
            user_email=user.get("email"),
            context={
                "purpose_id": purpose_id,
                "purpose_title": purpose.get("purpose_title"),
                "df_id": df_id,
                "user_id": user["_id"],
            },
            message=f"Purpose '{purpose.get('purpose_title')}' published successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return await self.crud.update_purpose(purpose_id, df_id, update_data)

    async def get_all_purpose(self, user: Dict[str, Any], current_page: int = 1, data_per_page: int = 20) -> Dict[str, Any]:
        offset = (current_page - 1) * data_per_page
        response = await self.crud.get_all_purpose_master(df_id=user["df_id"], offset=offset, limit=data_per_page)

        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page

        await log_business_event(
            event_type="LIST_PURPOSES",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": user.get("df_id"),
            },
            message=f"User listed Purposes. Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "purposes": response.get("data", []),
        }

    async def get_purpose(self, purpose_id: str, user: Dict[str, Any], for_system: Optional[bool] = False):
        df_id = user["df_id"]
        purpose_data = await self.crud.get_purpose_master(purpose_id, df_id)
        if not for_system:
            await log_business_event(
                event_type="GET_PURPOSE",
                user_email=user.get("email"),
                context={
                    "purpose_id": purpose_id,
                    "df_id": df_id,
                },
                message=f"User fetched Purpose with ID '{purpose_id}'.",
                business_logs_collection=self.business_logs_collection,
            )

        if not purpose_data:
            return None

        return purpose_data

    async def update_purpose_data(self, purpose_id: str, update_data: Dict[str, Any], user: Dict[str, Any]):
        df_id = user["df_id"]
        existing_purpose = await self.crud.get_purpose_master(purpose_id, df_id)
        if not existing_purpose:
            raise HTTPException(
                status_code=404,
                detail="Purpose not found.",
            )

        if existing_purpose["purpose_status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail="Only Purpose in draft status can be updated.",
            )
        if "purpose_title" in update_data:
            is_duplicate = await self.crud.is_duplicate_name(update_data["purpose_title"], df_id)
            if is_duplicate:
                raise HTTPException(
                    status_code=400,
                    detail=f"Purpose title '{update_data['purpose_title']}' already exists.",
                )

        translations = update_data.get("translations")
        if translations:
            invalid_keys = [k for k in translations.keys() if k not in LanguageCodes.__members__]
            if invalid_keys:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid language codes in translations: {invalid_keys}",
                )

        update_data["updated_at"] = datetime.now(UTC)
        update_data["updated_by"] = user["_id"]

        updated = await self.crud.update_purpose(purpose_id, df_id, update_data)

        await log_business_event(
            event_type="UPDATE_PURPOSE",
            user_email=user.get("email"),
            context={
                "purpose_id": purpose_id,
                "purpose_title": existing_purpose.get("purpose_title"),
                "df_id": df_id,
                "updated_fields": list(update_data.keys()),
            },
            message=f"Purpose '{existing_purpose.get('purpose_title')}' updated successfully. Fields changed: {', '.join(update_data.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated

    async def is_translated(self, purpose_id: str, user: Dict[str, Any]) -> bool:
        """
        Checks if a Purpose has valid translations.
        """
        purpose = await self.crud.get_purpose_master(purpose_id, user["df_id"])
        if not purpose:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purpose not found.")

        translations = purpose.get("translations", {})

        return all(translations.get(lang) for lang in LanguageCodes.__members__.keys())

    async def is_published(self, purpose_id: str, user: Dict[str, Any]) -> bool:
        """
        Checks if a Purpose is published.
        """
        purpose = await self.crud.get_purpose_master(purpose_id, user["df_id"])
        if not purpose:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purpose not found.")

        return purpose.get("purpose_status") == "published"
