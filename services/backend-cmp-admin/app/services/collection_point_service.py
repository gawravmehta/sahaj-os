from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud.collection_point_crud import CollectionPointCrud
from app.services.data_fiduciary_service import DataFiduciaryService
from app.utils.business_logger import log_business_event
from app.schemas.collection_point_schema import CollectionPointDB
from app.services.data_element_service import DataElementService
from app.services.purpose_service import PurposeService
from app.services.notice_service import NoticeService

from io import BytesIO
from minio import Minio
from app.core.config import settings


class CollectionPointService:
    def __init__(
        self,
        crud: CollectionPointCrud,
        data_element_service: DataElementService,
        purpose_service: PurposeService,
        notice_service: NoticeService,
        data_fiduciary_service: DataFiduciaryService,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection
        self.data_element_service = data_element_service
        self.purpose_service = purpose_service
        self.notice_service = notice_service
        self.data_fiduciary_service = data_fiduciary_service

    async def _enrich_collection_point_data(self, cp_data: Dict[str, Any], user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetches and enriches data elements and purposes with full object details from the database.
        """
        enriched_data_elements = []
        for de in cp_data.get("data_elements", []):
            de_id = de["de_id"]
            de_obj = await self.data_element_service.get_data_element(de_id, user, for_system=True)
            if not de_obj:
                continue

            enriched_purposes = []
            for purpose_data in de.get("purposes", []):
                purpose_id = purpose_data["purpose_id"]
                purpose_obj = await self.purpose_service.get_purpose(purpose_id, user, for_system=True)
                if purpose_obj:
                    enriched_purposes.append(purpose_obj)

            enriched_data_elements.append({"de_obj": de_obj, "purposes": enriched_purposes})
        return enriched_data_elements

    async def _validate_and_enrich_for_publish(self, enriched_data: List[Dict[str, Any]], user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validates deeply enriched data for publication.
        """
        not_published = {"data_elements": [], "purposes": []}
        not_translated = {"data_elements": [], "purposes": []}

        db_data_elements = []

        for de_entry in enriched_data:
            de_obj = de_entry["de_obj"]
            de_id = de_obj["_id"]
            de_name = de_obj["de_name"]

            if de_obj.get("de_status") != "published":
                not_published["data_elements"].append({"de_id": de_id, "de_name": de_name})
            if not de_obj.get("translations"):
                not_translated["data_elements"].append({"de_id": de_id, "de_name": de_name})

            db_purposes = []
            for purpose_obj in de_entry["purposes"]:
                purpose_id = purpose_obj["_id"]
                purpose_title = purpose_obj["purpose_title"]

                if purpose_obj.get("purpose_status") != "published":
                    not_published["purposes"].append({"purpose_id": purpose_id, "purpose_title": purpose_title})
                if not purpose_obj.get("translations"):
                    not_translated["purposes"].append({"purpose_id": purpose_id, "purpose_title": purpose_title})

                db_purposes.append({"purpose_id": purpose_id, "purpose_title": purpose_title})

            db_data_elements.append({"de_id": de_id, "de_name": de_name, "purposes": db_purposes})

        if not_published["data_elements"] or not_published["purposes"] or not_translated["data_elements"] or not_translated["purposes"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Some Data Elements or Purposes are not valid",
                    "not_published": not_published,
                    "not_translated": not_translated,
                },
            )

        return db_data_elements

    async def _compute_translation_flag(self, enriched_data: List[Dict[str, Any]], user: Dict[str, Any]) -> bool:
        for de_entry in enriched_data:
            if not de_entry["de_obj"].get("translations"):
                return False
            for purpose_obj in de_entry["purposes"]:
                if not purpose_obj.get("translations"):
                    return False
        return True

    async def create_collection_point(self, cp_data: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        is_duplicate = await self.crud.is_duplicate_name(cp_name=cp_data["cp_name"], asset_id=cp_data["asset_id"], df_id=user["df_id"])
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A Collection Point with the same name already exists.",
            )

        deeply_enriched_data = await self._enrich_collection_point_data(cp_data, user)

        if cp_data.get("cp_status") == "published":
            enriched_data_elements_for_db = await self._validate_and_enrich_for_publish(deeply_enriched_data, user)
        else:
            enriched_data_elements_for_db = []
            for de_entry in deeply_enriched_data:
                de_obj = de_entry["de_obj"]
                db_purposes = [{"purpose_id": p["_id"], "purpose_title": p["purpose_title"]} for p in de_entry["purposes"]]
                enriched_data_elements_for_db.append({"de_id": de_obj["_id"], "de_name": de_obj["de_name"], "purposes": db_purposes})

        consolidated_data = await self.notice_service.build_notice_data(deeply_enriched_data, cp_data.get("translated_audio", []))
        notice_html = self.notice_service.render_html(
            consolidated_data,
            df_name=await self.data_fiduciary_service.get_df_name(user["df_id"], user),
            notice_type=cp_data.get("notice_type", "single"),
        )

        is_translation_done = await self._compute_translation_flag(deeply_enriched_data, user)

        cp_data.pop("data_elements", None)

        cp_model = CollectionPointDB(
            **cp_data,
            data_elements=enriched_data_elements_for_db,
            notice_url="",
            is_translation_done=is_translation_done,
            notice_html=notice_html,
            df_id=user["df_id"],
            created_at=datetime.now(UTC),
            created_at_by=user["_id"],
        )

        created_cp = await self.crud.create_cp(cp_model.model_dump())

        await log_business_event(
            event_type="CREATE_COLLECTION_POINT",
            user_email=user.get("email"),
            context={
                "cp_id": str(created_cp["_id"]),
                "cp_name": cp_data.get("cp_name"),
                "asset_id": cp_data.get("asset_id"),
                "df_id": user.get("df_id"),
            },
            message=f"Collection Point '{cp_data.get('cp_name')}' created successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return created_cp

    def _upload_html_to_minio(
        self,
        s3_client,
        file_content: str,
        bucket: str,
        cp_id: str,
    ) -> str:
        file_path = f"notices/{cp_id}.html"
        html_bytes = BytesIO(file_content.encode("utf-8"))

        s3_client.put_object(
            bucket_name=bucket,
            object_name=file_path,
            data=html_bytes,
            length=len(html_bytes.getvalue()),
            content_type="text/html",
        )

        url = s3_client.presigned_get_object(bucket, file_path)
        return url

    async def upload_audio_to_minio(
        self,
        s3_client: Minio,
        file_content: bytes,
        content_type: str,
        file_extension: str,
    ) -> str:
        import uuid

        filename = f"{uuid.uuid4()}.{file_extension}"
        object_name = f"audio/{filename}"
        bucket = settings.NOTICE_WORKER_BUCKET

        file_stream = BytesIO(file_content)

        s3_client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=file_stream,
            length=len(file_content),
            content_type=content_type,
        )

        return f"{settings.CMP_ADMIN_BACKEND_URL}/api/v1/cp/get-audio/{filename}"

    async def get_audio_file(self, s3_client: Minio, filename: str):
        bucket = settings.NOTICE_WORKER_BUCKET
        object_name = f"audio/{filename}"

        try:
            response = s3_client.get_object(bucket, object_name)
            return response
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

    async def delete_audio_from_minio(self, audio_url: str, user: Dict[str, Any], s3_client: Minio):
        try:
            audio_url = audio_url.split("/")[-1]
            s3_client.remove_object(settings.NOTICE_WORKER_BUCKET, f"audio/{audio_url}")
            return True
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

    async def publish_collection_point(self, cp_id: str, user: Dict[str, Any], s3_client: Minio) -> Dict[str, Any]:
        """
        Publishes a Collection Point after validating its contents.
        """
        existing_cp = await self.crud.get_cp_master(cp_id, user["df_id"])
        if not existing_cp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection Point with id '{cp_id}' not found.",
            )

        if existing_cp.get("cp_status") == "published":
            return existing_cp

        deeply_enriched_data = await self._enrich_collection_point_data(existing_cp, user)

        enriched_data_elements_for_db = await self._validate_and_enrich_for_publish(deeply_enriched_data, user)

        consolidated_data = await self.notice_service.build_notice_data(deeply_enriched_data, existing_cp.get("translated_audio", []))
        notice_html = self.notice_service.render_html(
            consolidated_data,
            df_name=await self.data_fiduciary_service.get_df_name(user["df_id"], user),
            notice_type=existing_cp.get("notice_type", "single"),
        )
        is_translation_done = await self._compute_translation_flag(deeply_enriched_data, user)

        minio_url = self._upload_html_to_minio(
            s3_client=s3_client,
            file_content=notice_html,
            bucket=settings.NOTICE_WORKER_BUCKET,
            cp_id=cp_id,
        )

        update_data = {
            "cp_status": "published",
            "data_elements": enriched_data_elements_for_db,
            "is_translation_done": is_translation_done,
            "notice_html": notice_html,
            "notice_url": minio_url,
            "updated_at": datetime.now(UTC),
            "updated_by": user["_id"],
        }

        updated_cp = await self.crud.update_cp_by_id(cp_id, user["df_id"], update_data)

        await log_business_event(
            event_type="PUBLISH_COLLECTION_POINT",
            user_email=user.get("email"),
            context={
                "cp_id": str(updated_cp["_id"]),
                "cp_name": existing_cp.get("cp_name"),
                "df_id": user.get("df_id"),
            },
            message=f"Collection Point '{existing_cp.get('cp_name')}' published successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated_cp

    async def update_collection_point(self, cp_id: str, update_data: Dict[str, Any], user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates an existing Collection Point.
        """

        existing_cp = await self.crud.get_cp_master(cp_id, user["df_id"])
        if not existing_cp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection Point with id '{cp_id}' not found.",
            )

        if "cp_name" in update_data:
            is_duplicate = await self.crud.is_duplicate_name(cp_name=update_data["cp_name"], asset_id=existing_cp["asset_id"], df_id=user["df_id"])
            if is_duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A Collection Point with name '{update_data['cp_name']}' already exists.",
                )

        if "data_elements" in update_data:
            incoming_data_elements = update_data["data_elements"]
            temp_cp_data = {"data_elements": incoming_data_elements}

            deeply_enriched_data = await self._enrich_collection_point_data(temp_cp_data, user)

            if update_data.get("cp_status") == "published" or (
                existing_cp.get("cp_status") == "draft" and update_data.get("cp_status") == "published"
            ):
                enriched_data_elements_for_db = await self._validate_and_enrich_for_publish(deeply_enriched_data, user)
            else:
                enriched_data_elements_for_db = []
                for de_entry in deeply_enriched_data:
                    de_obj = de_entry["de_obj"]
                    db_purposes = [{"purpose_id": p["_id"], "purpose_title": p["purpose_title"]} for p in de_entry["purposes"]]
                    enriched_data_elements_for_db.append(
                        {
                            "de_id": de_obj["_id"],
                            "de_name": de_obj["de_name"],
                            "purposes": db_purposes,
                        }
                    )

            consolidated_data = await self.notice_service.build_notice_data(
                deeply_enriched_data, update_data.get("translated_audio", existing_cp.get("translated_audio", []))
            )

            update_data["notice_html"] = self.notice_service.render_html(
                consolidated_data,
                df_name=await self.data_fiduciary_service.get_df_name(user["df_id"], user),
                notice_type=update_data.get("notice_type", existing_cp.get("notice_type", "single")),
            )
            update_data["is_translation_done"] = await self._compute_translation_flag(deeply_enriched_data, user)
            update_data["data_elements"] = enriched_data_elements_for_db

        else:

            if "notice_type" in update_data:

                existing_deep_data = await self._enrich_collection_point_data({"data_elements": existing_cp.get("data_elements", [])}, user)
                consolidated_data = await self.notice_service.build_notice_data(existing_deep_data, existing_cp.get("translated_audio", []))

                update_data["notice_html"] = self.notice_service.render_html(
                    consolidated_data,
                    df_name=await self.data_fiduciary_service.get_df_name(user["df_id"], user),
                    notice_type=update_data.get("notice_type", "single"),
                )

            update_data["data_elements"] = existing_cp.get("data_elements", [])

        update_data["updated_at"] = datetime.now(UTC)
        update_data["updated_by"] = user["_id"]

        updated_cp = await self.crud.update_cp_by_id(cp_id, user["df_id"], update_data)

        await log_business_event(
            event_type="UPDATE_COLLECTION_POINT",
            user_email=user.get("email"),
            context={
                "cp_id": str(updated_cp["_id"]),
                "cp_name": updated_cp.get("cp_name"),
                "df_id": user.get("df_id"),
                "updated_fields": list(update_data.keys()),
            },
            message=f"Collection Point '{updated_cp.get('cp_name')}' updated successfully. Fields changed: {', '.join(update_data.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated_cp

    async def get_all_collection_points(
        self,
        user: Dict[str, Any],
        current_page: int = 1,
        data_per_page: int = 20,
        is_legacy: Optional[bool] = None,
        is_published: Optional[bool] = None,
    ) -> Dict[str, Any]:
        offset = (current_page - 1) * data_per_page

        additional_filters = {}
        if is_legacy is not None:
            additional_filters["cp_type"] = "legacy"
        if is_published is not None:
            additional_filters["cp_status"] = "published"

        response = await self.crud.get_all_cps(df_id=user["df_id"], offset=offset, limit=data_per_page, additional_filters=additional_filters)

        total_items = response.get("total", 0)
        total_pages = (total_items + data_per_page - 1) // data_per_page
        await log_business_event(
            event_type="LIST_COLLECTION_POINTS",
            user_email=user.get("email"),
            context={
                "current_page": current_page,
                "data_per_page": data_per_page,
                "df_id": user.get("df_id"),
                "is_legacy": is_legacy,
                "is_published": is_published,
            },
            message=f"User listed Collection Points. Page: {current_page}, Items per page: {data_per_page}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "current_page": current_page,
            "data_per_page": data_per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "collection_points": response.get("data", []),
        }

    async def get_collection_point(self, cp_id: str, user: Dict[str, Any]):
        df_id = user["df_id"]
        cp_data = await self.crud.get_cp_master(cp_id, df_id)

        await log_business_event(
            event_type="GET_COLLECTION_POINT",
            user_email=user.get("email"),
            context={
                "cp_id": cp_id,
                "df_id": df_id,
            },
            message=f"User fetched Collection Point with ID '{cp_id}'.",
            business_logs_collection=self.business_logs_collection,
        )

        if not cp_data:
            return None

        return cp_data

    async def delete_collection_point(self, cp_id: str, user: Dict[str, Any]):
        existing_cp = await self.crud.get_cp_master(cp_id, user["df_id"])
        if not existing_cp or existing_cp.get("cp_status") == "archived":
            return None
        updated_cp = await self.crud.update_cp_by_id(
            cp_id,
            user["df_id"],
            {
                "cp_status": "archived",
                "updated_at": datetime.now(UTC),
                "updated_by": user["_id"],
            },
        )

        await log_business_event(
            event_type="DELETE_COLLECTION_POINT",
            user_email=user.get("email"),
            context={
                "cp_id": cp_id,
                "cp_name": existing_cp.get("cp_name"),
                "df_id": user.get("df_id"),
            },
            message=f"Collection Point '{existing_cp.get('cp_name')}' soft-deleted (archived) successfully.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated_cp
