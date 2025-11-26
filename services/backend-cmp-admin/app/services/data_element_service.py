from datetime import UTC, datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException, status


from app.crud.data_element_crud import DataElementCRUD
from app.utils.business_logger import log_business_event
from app.schemas.data_element_schema import DataElementDB, LanguageCodes
from app.utils.common import generate_blockchain_hash


class DataElementService:
    def __init__(
        self,
        crud: DataElementCRUD,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection

    async def get_all_data_element_templates(
        self,
        user: Dict[str, Any],
        current_page: int = 1,
        data_per_page: int = 20,
        domain: Optional[str] = None,
        title: Optional[str] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        offset = (current_page - 1) * data_per_page

        response = await self.crud.get_all_de_templates(domain=domain, title=title, id=id, offset=offset, limit=data_per_page)

        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page

        await log_business_event(
            event_type="LIST_DATA_ELEMENT_TEMPLATES",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "domain": domain,
                "title": title,
                "template_id": id,
                "df_id": user.get("df_id"),
            },
            message=f"User listed Data Element Templates with filters (Domain: {domain}, Title: {title}, ID: {id}). Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "data": response.get("data", []),
        }

    async def create_data_element(self, de_data, user) -> Dict[str, Any]:
        is_duplicate = await self.crud.is_duplicate_name(de_name=de_data["de_name"], df_id=user["df_id"])
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A Data Element with the same name already exists.",
            )

        de_data["created_by"] = user["_id"]
        de_data["df_id"] = user["df_id"]
        de_data["updated_at"] = None
        de_model = DataElementDB(**de_data)

        created_template = await self.crud.create_de(de_model.model_dump())
        await log_business_event(
            event_type="CREATE_DATA_ELEMENT",
            user_email=user.get("email"),
            context={
                "de_id": str(created_template["_id"]),
                "de_name": de_data.get("de_name"),
                "df_id": user.get("df_id"),
            },
            message=f"Data Element '{de_data.get('de_name')}' created successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return created_template

    async def copy_data_element(self, de_id: str, user) -> Dict[str, Any]:
        response = await self.crud.get_all_de_templates(id=de_id)
        data = response.get("data", [])
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {de_id} not found.",
            )
        de_template_data = response.get("data")[0]
        de_name = de_template_data["title"]
        is_duplicate = await self.crud.is_duplicate_name(de_name=de_name, df_id=user["df_id"])
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A Data Element with the same name already exists for this Data Fiduciary.",
            )
        de_model_data = DataElementDB(
            de_name=de_name,
            de_description=de_template_data["description"],
            de_original_name=de_name,
            de_data_type="string",
            de_sensitivity="low",
            is_core_identifier=False,
            de_retention_period=30,
            de_status="draft",
            translations=de_template_data.get("translations", {}),
            df_id=user["df_id"],
            created_by=user["_id"],
            updated_at=None,
        )

        created_template = await self.crud.create_de(de_model_data.model_dump())
        await log_business_event(
            event_type="COPY_DATA_ELEMENT_FROM_TEMPLATE",
            user_email=user.get("email"),
            context={
                "de_id": str(created_template["_id"]),
                "de_name": de_name,
                "template_id": de_id,
                "df_id": user.get("df_id"),
            },
            message=f"Data Element '{de_name}' copied from template (ID: {de_id}) successfully.",
            business_logs_collection=self.business_logs_collection,
        )
        return created_template

    async def copy_data_element_by_title(self, de_title: str, user: dict) -> Dict[str, Any]:
        response = await self.crud.get_all_de_templates(title=de_title)
        data = response.get("data", [])
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with title '{de_title}' not found.",
            )

        de_template_data = data[0]
        de_name = de_template_data["title"]

        existing_de = await self.crud.get_de_master_by_name(de_name, user["df_id"])
        if existing_de:
            return existing_de

        de_model_data = DataElementDB(
            de_name=de_name,
            de_description=de_template_data["description"],
            de_original_name=de_name,
            de_data_type="string",
            de_sensitivity="low",
            is_core_identifier=False,
            de_retention_period=30,
            de_status="draft",
            translations=de_template_data.get("translations", {}),
            df_id=user["df_id"],
            created_by=user["_id"],
            updated_at=None,
        )

        created_template = await self.crud.create_de(de_model_data.model_dump())

        await log_business_event(
            event_type="COPY_DATA_ELEMENT_BY_TITLE",
            user_email=user.get("email"),
            context={
                "de_id": str(created_template["_id"]),
                "de_name": de_name,
                "template_title": de_title,
                "df_id": user.get("df_id"),
            },
            message=f"Data Element '{de_name}' copied from template (Title: '{de_title}') by title successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return created_template

    async def update_data_element(self, de_id: str, update_data: Dict[str, Any], user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        df_id = user["df_id"]
        existing_de = await self.crud.get_de_master(de_id, df_id)

        if not existing_de:
            raise HTTPException(
                status_code=404,
                detail="Data Element not found.",
            )

        if existing_de["de_status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail="Only Data Elements in draft status can be updated.",
            )

        if "de_name" in update_data:
            is_duplicate = await self.crud.is_duplicate_name(update_data["de_name"], df_id)
            if is_duplicate:
                raise HTTPException(
                    status_code=400,
                    detail="Data Element name already exists.",
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

        updated = await self.crud.update_data_element_by_id(de_id, df_id, update_data)

        await log_business_event(
            event_type="UPDATE_DATA_ELEMENT",
            user_email=user.get("email"),
            context={
                "de_id": de_id,
                "de_name": existing_de.get("de_name"),
                "df_id": df_id,
                "updated_fields": list(update_data.keys()),
            },
            message=f"Data Element '{existing_de.get('de_name')}' updated successfully. Fields changed: {', '.join(update_data.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated

    async def publish_data_element(self, de_id: str, user: dict) -> Optional[dict]:
        df_id = user["df_id"]
        de = await self.crud.get_de_master(de_id, df_id)

        if not de:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data Element not found or does not belong to the current domain.",
            )
        if de["de_status"] == "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data Element is already published.",
            )

        elif de["de_status"] == "archived":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish an archived Data Element.",
            )

        if not de.get("de_retention_period"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Retention period (de_retention_period) is required before publishing.",
            )

        translations = de.get("translations", {})
        if not translations or not isinstance(translations, dict) or not any(v for v in translations.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translations are required and cannot be empty before publishing.",
            )

        update_data = {
            "de_status": "published",
            "updated_by": user["_id"],
            "updated_at": datetime.now(UTC),
            "de_hash_id": generate_blockchain_hash(),
        }
        await log_business_event(
            event_type="PUBLISH_DATA_ELEMENT",
            user_email=user.get("email"),
            context={
                "de_id": de_id,
                "de_name": de.get("de_name"),
                "df_id": df_id,
                "user_id": user["_id"],
            },
            message=f"Data Element '{de.get('de_name')}' published successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return await self.crud.update_data_element_by_id(de_id, df_id, update_data)

    async def get_all_data_element(
        self, user: Dict[str, Any], current_page: int = 1, data_per_page: int = 20, is_core_identifier: Optional[bool] = None
    ) -> Dict[str, Any]:
        offset = (current_page - 1) * data_per_page
        response = await self.crud.get_all_de_master(df_id=user["df_id"], offset=offset, limit=data_per_page, is_core_identifier=is_core_identifier)

        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page

        await log_business_event(
            event_type="LIST_DATA_ELEMENTS",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": user.get("df_id"),
                "is_core_identifier": is_core_identifier,
            },
            message=f"User listed Data Elements. Page: {current_page}, Items per page: {data_per_page}. Is Core Identifier: {is_core_identifier}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "data_elements": response.get("data", []),
        }

    async def get_data_element(self, de_id: str, user: Dict[str, Any], for_system: Optional[bool] = False):
        df_id = user["df_id"]
        de_data = await self.crud.get_de_master(de_id, df_id)
        if not for_system:
            await log_business_event(
                event_type="GET_DATA_ELEMENT",
                user_email=user.get("email"),
                context={
                    "de_id": de_id,
                    "df_id": df_id,
                },
                message=f"User fetched Data Element with ID '{de_id}'.",
                business_logs_collection=self.business_logs_collection,
            )

        if not de_data:
            return None

        return de_data

    async def delete_data_element(self, de_id: str, user: Dict[str, Any]):
        existing_de = await self.crud.get_de_master(de_id, user["df_id"])

        if not existing_de or existing_de.get("de_status") == "archived":
            return None

        updated_de = await self.crud.update_data_element_by_id(
            de_id,
            user["df_id"],
            {
                "de_status": "archived",
                "updated_at": datetime.now(UTC),
                "updated_by": user["_id"],
            },
        )

        await log_business_event(
            event_type="DELETE_DATA_ELEMENT",
            user_email=user.get("email"),
            context={
                "de_id": de_id,
                "de_name": existing_de.get("de_name"),
                "df_id": user.get("df_id"),
            },
            message=f"Data Element '{existing_de.get('de_name')}' soft-deleted (archived) successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated_de

    async def is_translated(self, de_id: str, user: Dict[str, Any]) -> bool:
        de = await self.crud.get_de_master(de_id, user["df_id"])
        if not de:
            raise HTTPException(status_code=404, detail="Data Element not found.")

        translations = de.get("translations", {})
        return all(translations.get(lang) for lang in LanguageCodes.__members__.keys())

    async def is_published(self, de_id: str, user: Dict[str, Any]) -> bool:
        de = await self.crud.get_de_master(de_id=de_id, df_id=user["df_id"])
        if not de:
            raise HTTPException(status_code=404, detail="Data Element not found.")
        return de.get("de_status") == "published"
