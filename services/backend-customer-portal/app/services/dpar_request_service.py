from datetime import datetime, timedelta, UTC
from typing import List, Optional
import asyncio
from bson import ObjectId
from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.dpar_request_crud import get_user_requests
from app.schemas.dpar_schema import DPARCreateRequest, DPARRequestOut
from app.utils.common import name_pattern
from fastapi import status
from app.core.logger import app_logger

DATETIME_FIELDS = [
    "created_timestamp",
    "clarification_timestamp",
    "acknowledged_timestamp",
    "approved_timestamp",
    "compiling_start_timestamp",
    "compiling_end_timestamp",
    "rejected_timestamp",
    "completed_timestamp",
    "buy_time_requested_timestamp",
    "buy_time_response_timestamp",
    "deadline",
]


class DPARRequestService:
    def __init__(
        self,
        dpa_requests_collection: AsyncIOMotorCollection,
        consent_artifact_collection: Optional[AsyncIOMotorCollection],
    ):
        self.requests_collection = dpa_requests_collection
        self.consent_artifact_collection = consent_artifact_collection

    async def get_my_requests(self, current_user: dict) -> List[DPARRequestOut]:
        app_logger.info(f"Fetching DPAR requests for user: {current_user.get('email') or current_user.get('mobile')}")
        filters = {"is_deleted": False}

        if current_user.get("is_existing"):
            dp_id = current_user.get("dp_id")
            if not dp_id:
                app_logger.warning("get_my_requests: dp_id is missing for existing user. Returning empty list.")
                return []
            filters.update({"requested_by": dp_id})
        else:

            identifiers = []
            if current_user.get("email"):
                identifiers.append(current_user["email"])
            if current_user.get("mobile"):
                identifiers.append(current_user["mobile"])

            if not identifiers:
                return []

            filters.update(
                {
                    "$or": [
                        {"core_identifier": {"$in": identifiers}},
                        {"secondary_identifier": {"$in": identifiers}},
                    ]
                }
            )
        app_logger.debug(f"DPAR requests query filters: {filters}")
        results = await get_user_requests(self.requests_collection, filters)
        app_logger.info(f"Found {len(results)} DPAR requests for the user.")

        requests_out = []
        for r in results:
            requests_out.append(
                DPARRequestOut(
                    dpar_id=str(r.get("_id")),
                    dp_id=str(r.get("requested_by")),
                    status=r.get("status"),
                    created_timestamp=r.get("created_timestamp"),
                    last_updated=r.get("last_updated"),
                    request_type=r.get("request_type"),
                    request_priority=r.get("request_priority"),
                    first_name=r.get("first_name"),
                    last_name=r.get("last_name"),
                    core_identifier=r.get("core_identifier"),
                    secondary_identifier=r.get("secondary_identifier"),
                    dp_type=r.get("dp_type"),
                    country=r.get("country"),
                    request_message=r.get("request_message"),
                    related_request=r.get("related_request"),
                    related_request_id=r.get("related_request_id"),
                    related_request_type=r.get("related_request_type"),
                    kyc_document=r.get("kyc_document"),
                    kyc_front=r.get("kyc_front"),
                    kyc_back=r.get("kyc_back"),
                    request_attachments=r.get("request_attachments", []),
                    deadline=r.get("deadline"),
                    is_deleted=r.get("is_deleted", False),
                )
            )
        return requests_out

    async def get_one_request(self, dpar_request_id: str) -> DPARRequestOut:
        app_logger.info(f"Fetching DPAR request with ID: {dpar_request_id}")
        filters = {"_id": ObjectId(dpar_request_id), "is_deleted": False}

        result = await self.requests_collection.find_one(filters)
        if not result:
            app_logger.warning(f"get_one_request failed: Request with ID {dpar_request_id} not found.")
            raise HTTPException(status_code=404, detail="Request not found")
        app_logger.info(f"Retrieved DPAR request with ID: {dpar_request_id}")

        result["dpar_id"] = str(result["_id"])

        return DPARRequestOut(**result)

    async def create_request(self, request: Request, payload: DPARCreateRequest, current_user: dict) -> dict:
        app_logger.info(f"Creating new DPAR request for user: {current_user.get('email') or current_user.get('mobile')}, type: {payload.request_type}")
        self._validate_names(payload)

        user_id = str(current_user["dp_id"])
        df_id = current_user.get("df_id")
        if current_user.get("is_existing"):
            dp_id = current_user["dp_id"]
            identifier_filter = {"requested_by": dp_id}
            app_logger.debug(f"Existing user dp_id: {dp_id}")
        else:
            dp_id = None

            core_identifier = payload.core_identifier or current_user.get("email") or current_user.get("mobile")
            secondary_identifier = payload.secondary_identifier

            if not core_identifier and not secondary_identifier:
                app_logger.warning("create_request failed: Missing core or secondary identifier for new user")
                raise HTTPException(status_code=400, detail="Missing core or secondary identifier for new user")

            identifier_filter = {}
            if core_identifier:
                identifier_filter["core_identifier"] = core_identifier
            if secondary_identifier:
                identifier_filter["secondary_identifier"] = secondary_identifier
            app_logger.debug(f"New user identifiers: core={core_identifier}, secondary={secondary_identifier}")

        if payload.request_type == "delete_data":
            if not payload.data_element_id:
                app_logger.warning("create_request failed: data_element_id is required for delete_data request type")
                raise HTTPException(status_code=400, detail="data_element_id is required for delete_data request type")
            app_logger.debug(f"Checking active consents for data_element_id: {payload.data_element_id}")

            active_consents = await self._get_active_consents_for_data_element(
                dp_id=dp_id,
                data_element_id=payload.data_element_id,
                core_identifier=payload.core_identifier or current_user.get("email") or current_user.get("mobile"),
                secondary_identifier=payload.secondary_identifier,
            )

            if active_consents:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Cannot create delete_data request. Active consents must be revoked first.",
                        "active_consents": active_consents,
                    },
                )

        related_request = payload.related_request

        system_fields = self._generate_system_fields(
            request=request,
            df_id=df_id,
            dp_id=dp_id,
            related_request=related_request,
            related_request_id=payload.related_request_id,
        )

        full_request = {**payload.model_dump(), **system_fields}
        full_request["requested_by"] = dp_id

        if not current_user.get("is_existing"):
            full_request["core_identifier"] = payload.core_identifier or current_user.get("email") or current_user.get("mobile")
            if payload.secondary_identifier:
                full_request["secondary_identifier"] = payload.secondary_identifier

        result = await self.requests_collection.insert_one(full_request)
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to create request")

        return {
            "dpar_request_id": str(result.inserted_id),
            "status": full_request["status"],
            "created_timestamp": full_request["created_timestamp"],
        }

    def _validate_names(self, payload: DPARCreateRequest):
        if payload.first_name and not name_pattern.fullmatch(payload.first_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid first_name: only alphabetic characters allowed",
            )
        if payload.last_name and not name_pattern.fullmatch(payload.last_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid last_name: only alphabetic characters allowed",
            )

    async def _enforce_old_threshold(self, request: Request, settings: dict):
        threshold = settings.get("form_fields", {}).get("old_request_threshold")
        if not threshold:
            return

        query_filter = {}
        if hasattr(request, "core_identifier"):
            query_filter["core_identifier"] = request.core_identifier
        elif hasattr(request, "secondary_identifier"):
            query_filter["secondary_identifier"] = request.secondary_identifier

        if query_filter:
            query_filter["created_timestamp"] = {"$gte": datetime.now(UTC) - timedelta(days=threshold)}
            cursor = self.requests_collection.find(query_filter)
            if await cursor.to_list(length=1):
                raise HTTPException(
                    status_code=400,
                    detail=f"You have already submitted a request within the last {threshold} days",
                )

    def _generate_system_fields(
        self,
        request: Request,
        df_id: str,
        dp_id: Optional[str],
        related_request: Optional[str],
        related_request_id: Optional[str] = None,
    ) -> dict:
        now = datetime.now(UTC)
        return {
            "kyc_front": None,
            "kyc_back": None,
            "request_attachments": [],
            "request_headers": request.headers,
            "created_timestamp": now,
            "last_updated": now,
            "revoked_timestamp": None,
            "status": "created",
            "df_id": df_id,
            "requested_by": dp_id,
            "viewed_by": [],
            "clarification_timestamp": None,
            "acknowledged_timestamp": None,
            "acknowledged_by": None,
            "compiling_start_timestamp": None,
            "compiling_end_timestamp": None,
            "rejected_by": None,
            "rejected_timestamp": None,
            "rejected_reason": None,
            "completed_timestamp": None,
            "turn_around_time": None,
            "urgency_level": None,
            "buy_time_requested_by": None,
            "buy_time_required": None,
            "buy_time_requested_at": None,
            "buy_time_request_status": None,
            "buy_time_responded_at": None,
            "clarification_action": [],
            "admin_notes": [],
            "allocated_to": None,
            "allocation_trail": [],
            "escalation_status": {"escalated": False},
            "attachments": [],
            "deadline": now + timedelta(days=30),
            "is_deleted": False,
            "related_request": related_request,
            "related_request_id": related_request_id,
        }

    async def update_request(self, dpar_request_id: str, update_data: DPARCreateRequest, current_user: dict) -> dict:
        user_id = str(current_user["dp_id"])
        df_id = str(current_user["df_id"])
        existing = await self.requests_collection.find_one({"_id": ObjectId(dpar_request_id), "is_deleted": False})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found",
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        result = await self.requests_collection.update_one(
            {"_id": ObjectId(dpar_request_id)},
            {"$set": update_dict},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update the request")

        updated_request = await self.requests_collection.find_one({"_id": ObjectId(dpar_request_id)})
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Updated request not found",
            )

        updated_request["_id"] = str(updated_request["_id"])

        for field in DATETIME_FIELDS:
            if updated_request.get(field) and isinstance(updated_request[field], str):
                updated_request[field] = datetime.fromisoformat(updated_request[field])

        return updated_request

    async def delete_request(self, dpar_request_id: str, current_user: dict) -> dict:
        try:
            user_id = str(current_user["dp_id"])
            df_id = str(current_user["df_id"])

            if not ObjectId.is_valid(dpar_request_id):
                raise HTTPException(status_code=400, detail="Invalid request ID format")

            existing_request = await self.requests_collection.find_one({"_id": ObjectId(dpar_request_id), "is_deleted": False})
            if not existing_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Request not found or already deleted",
                )

            result = await self.requests_collection.update_one(
                {"_id": ObjectId(dpar_request_id)},
                {"$set": {"is_deleted": True}},
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Failed to delete the request")

            return {"detail": "Request successfully deleted"}

        except HTTPException:

            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_active_consents_for_data_element(
        self, dp_id: Optional[str], data_element_id: str, core_identifier: Optional[str] = None, secondary_identifier: Optional[str] = None
    ) -> List[dict]:
        """
        Get all active consents (not denied or expired) for a specific data element.
        Returns formatted consent data for frontend consumption and revocation.
        """
        if self.consent_artifact_collection is None:

            return []

        try:

            query = {}
            if dp_id:
                query["artifact.data_principal.dp_id"] = dp_id
            else:

                identifier_conditions = []
                if core_identifier:
                    identifier_conditions.append({"artifact.data_principal.core_identifier": core_identifier})
                if secondary_identifier:
                    identifier_conditions.append({"artifact.data_principal.secondary_identifier": secondary_identifier})

                if identifier_conditions:
                    query["$or"] = identifier_conditions
                else:

                    return []

            cursor = self.consent_artifact_collection.find(query)
            artifacts = await cursor.to_list(None)

            if not artifacts:
                return []

            latest_by_cp = {}
            for artifact in artifacts:
                cp_name = artifact.get("artifact", {}).get("cp_name", "")
                version = artifact.get("artifact", {}).get("agreement_version", 0)

                if not cp_name:
                    continue

                if cp_name not in latest_by_cp or version > latest_by_cp[cp_name].get("artifact", {}).get("agreement_version", 0):
                    latest_by_cp[cp_name] = artifact

            active_consents = []

            for artifact_doc in latest_by_cp.values():
                artifact = artifact_doc.get("artifact", {})
                agreement_id = artifact.get("agreement_id")
                cp_name = artifact.get("cp_name", "Unknown")
                consent_scope = artifact.get("consent_scope", {})
                data_elements = consent_scope.get("data_elements", [])

                for de in data_elements:
                    if de.get("de_id") == data_element_id:

                        active_purposes = []

                        for consent in de.get("consents", []):
                            consent_status = consent.get("consent_status", "").lower()

                            if consent_status not in ["denied", "expired"]:
                                active_purposes.append(
                                    {
                                        "purpose_id": consent.get("purpose_id"),
                                        "purpose_title": consent.get("purpose_title"),
                                        "consent_status": consent.get("consent_status"),
                                        "consent_timestamp": consent.get("consent_timestamp"),
                                        "consent_expiry_period": consent.get("consent_expiry_period"),
                                    }
                                )

                        if active_purposes:
                            active_consents.append(
                                {
                                    "agreement_id": agreement_id,
                                    "cp_name": cp_name,
                                    "data_element": {"de_id": de.get("de_id"), "de_hash_id": de.get("de_hash_id"), "title": de.get("title")},
                                    "purposes": active_purposes,
                                }
                            )

            return active_consents

        except Exception as e:
            return []
