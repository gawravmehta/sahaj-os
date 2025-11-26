import csv
from io import StringIO
import json
import mimetypes
import os
import re
from time import time
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse
import uuid
from bson import ObjectId
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from app.crud.dpar_crud import DparCRUD
from app.schemas.dpar_schema import DPARCreateRequest, DPARReportCreate
from datetime import datetime, timezone, timedelta, UTC
from app.db.rabbitmq import publish_message

from app.utils.common import convert_objectid_to_str
from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from app.utils.business_logger import log_business_event


EXPORT_FIELDS = [
    "first_name",
    "last_name",
    "core_identifier",
    "secondary_identifier",
    "dp_type",
    "country",
    "request_type",
    "request_message",
]


class DPARequestService:
    def __init__(
        self,
        dpa_crud: DparCRUD,
        user_collection,
        s3_client,
        bucket_name: str,
        consent_artifact_crud: ConsentArtifactCRUD,
        business_logs_collection: str,
    ):
        self.dpa_crud = dpa_crud
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.user_collection = user_collection
        self.consent_artifact_crud = consent_artifact_crud
        self.business_logs_collection = business_logs_collection

    async def get_all_requests(
        self,
        request: Request,
        current_user: dict,
        page: int,
        page_size: int,
        status: Optional[str],
        dp_type: Optional[str],
        created_from: Optional[str],
        created_to: Optional[str],
    ) -> Dict[str, Any]:

        df_id = current_user.get("df_id")
        filters = {"is_deleted": False}

        if status:
            filters["status"] = status
        if dp_type:
            filters["dp_type"] = dp_type
        if created_from or created_to:
            filters["created_timestamp"] = {}
            if created_from:
                filters["created_timestamp"]["$gte"] = datetime.strptime(created_from, "%Y-%m-%d")
            if created_to:
                filters["created_timestamp"]["$lte"] = datetime.strptime(created_to, "%Y-%m-%d")

        projection = {
            "_id": 1,
            "dpar_request_id": 1,
            "request_origin": 1,
            "created_timestamp": 1,
            "first_name": 1,
            "last_name": 1,
            "core_identifier": 1,
            "secondary_identifier": 1,
            "status": 1,
            "last_updated": 1,
            "urgency_level": 1,
            "deadline": 1,
            "dp_type": 1,
        }

        total_records = await self.dpa_crud.count_requests(filters)
        total_pages = (total_records + page_size - 1) // page_size
        skip = (page - 1) * page_size

        dpa_requests = await self.dpa_crud.get_requests(filters, projection, skip, page_size)

        allowed_statuses = {"new", "completed", "rejected"}
        datetime_fields = ["created_timestamp", "last_updated", "deadline"]

        for req in dpa_requests:
            req["_id"] = str(req["_id"])
            for field in datetime_fields:
                if isinstance(req.get(field), datetime):
                    req[field] = req[field].isoformat()
            if req.get("status") not in allowed_statuses:
                req["status"] = "in-progress"

        await log_business_event(
            event_type="LIST_DPAR_REQUESTS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "page": page,
                "page_size": page_size,
                "status_filter": status,
                "dp_type_filter": dp_type,
                "created_from": created_from,
                "created_to": created_to,
                "total_records": total_records,
            },
            message=f"User listed DPAR requests. Page: {page}, Size: {page_size}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "data": dpa_requests,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    async def create_request(self, request: DPARCreateRequest, request_details: Request, current_user: dict) -> Dict[str, Any]:

        dpar_default_deadline = 30
        core_identifier_type = None

        dpar_default_deadline = 30

        
        previous_request = await self.dpa_crud.get_last_request(str(current_user["_id"]))
        if previous_request:
            request.related_request = str(previous_request["_id"])

        
        conversation_entry = []
        if request.message:
            conversation_entry = [
                {
                    "message_id": str(uuid.uuid4()),
                    "sender": current_user.get("first_name") or "data_principal",
                    "sender_image": current_user.get("image_url"),
                    "subject": request.subject,
                    "message": request.message,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": "sent",
                }
            ]

        
        system_fields = {
            "kyc_front": None,
            "kyc_back": None,
            "request_conversation": conversation_entry,
            "request_attachments": [],
            "request_headers": request_details.headers,
            "created_timestamp": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
            "revoked_timestamp": None,
            "core_identifier_type": core_identifier_type,
            "status": "created",
            "df_id": str(current_user.get("df_id")),
            "requested_by": str(current_user.get("_id")),
            "pre_flight_check": False,
            "pre_flight_check_timestamp": None,
            "pre_flight_match_id": None,
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
            "deadline": datetime.now(UTC) + timedelta(days=dpar_default_deadline),
            "is_deleted": False,
        }

        
        full_request = {**request.model_dump(exclude={"message", "subject"}), **system_fields}

        
        inserted_id = await self.dpa_crud.insert_request(full_request)
        if not inserted_id:
            await log_business_event(
                event_type="CREATE_DPAR_REQUEST_FAILED",
                user_email=current_user.get("email"),
                context={
                    "df_id": str(current_user.get("df_id")),
                    "requested_by": str(current_user.get("_id")),
                    "request_type": request.request_type,
                    "error": "Failed to insert into DB",
                },
                message=f"Failed to create DPAR request for user {current_user.get('email')}.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to create request")

        await log_business_event(
            event_type="CREATE_DPAR_REQUEST_SUCCESS",
            user_email=current_user.get("email"),
            context={
                "df_id": str(current_user.get("df_id")),
                "requested_by": str(current_user.get("_id")),
                "dpar_request_id": str(inserted_id),
                "request_type": request.request_type,
                "status": full_request["status"],
            },
            message=f"DPAR request '{inserted_id}' created successfully by user {current_user.get('email')}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "dpar_request_id": inserted_id,
            "status": full_request["status"],
            "created_timestamp": full_request["created_timestamp"],
        }

    async def get_one_request(self, request_id: str, current_user: dict) -> Dict[str, Any]:
        request_doc = await self.dpa_crud.get_by_id(request_id, {"df_id": current_user["df_id"]})
        if not request_doc:
            await log_business_event(
                event_type="GET_DPAR_REQUEST_FAILED",
                user_email=current_user.get("email"),
                context={
                    "df_id": current_user["df_id"],
                    "request_id": request_id,
                    "error": "DPA request not found",
                },
                message=f"Failed to fetch DPAR request '{request_id}': Not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        
        request_doc["_id"] = str(request_doc["_id"])
        for key, value in request_doc.items():
            if isinstance(value, datetime):
                request_doc[key] = value.isoformat()

        await log_business_event(
            event_type="GET_DPAR_REQUEST_SUCCESS",
            user_email=current_user.get("email"),
            context={
                "df_id": current_user["df_id"],
                "request_id": request_id,
            },
            message=f"User fetched DPAR request '{request_id}'.",
            business_logs_collection=self.business_logs_collection,
        )
        return convert_objectid_to_str(request_doc)

    async def set_status(self, request_id: str, status: str, status_details: str, current_user: dict):
        df_id = current_user["df_id"]
        user_email = current_user.get("email")

        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})
        if not dpa_request:
            await log_business_event(
                event_type="SET_DPAR_STATUS_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "status": status,
                    "error": "DPAR request not found",
                },
                message=f"Failed to set status for DPAR request '{request_id}': Not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        created_ts = dpa_request["created_timestamp"]

        
        if created_ts.tzinfo is None:
            created_ts = created_ts.replace(tzinfo=timezone.utc)

        now = datetime.now(UTC)
        user_id = str(current_user["_id"])
        
        action_map = {
            "rejected": {
                "updates": {
                    "status": "rejected",
                    "rejected_by": user_id,
                    "rejected_timestamp": now,
                    "rejected_reason": status_details,
                },
                "message": f"DPA request '{request_id}' was rejected",
            },
            "new": {
                "updates": {"status": "new"},
                "message": f"DPA request '{request_id}' first step approved",
            },
            "kyc": {
                "updates": {"status": "kyc"},
                "message": f"DPA request '{request_id}' second step approved",
            },
            "review": {
                "updates": {"status": "review"},
                "message": f"DPA request '{request_id}' third step approved",
            },
            "related_req": {
                "updates": {"status": "related_req"},
                "message": f"DPA request '{request_id}' fourth step approved",
            },
            
            "approved": {
                "updates": {
                    "status": "completed",
                    "completed_by": user_id,
                    "completed_timestamp": now,
                    "turn_around_time": (now - created_ts).total_seconds(),
                },
                "message": f"DPA request '{request_id}' was marked completed",
            },
        }

        query = {
            "df_id": current_user["df_id"],
            "dp_id": dpa_request["requested_by"],  
            "artifact.consent_scope.data_elements.de_id": dpa_request["data_element_id"],
        }

        cursor = self.consent_artifact_crud.get_filtered_consent_artifacts(query, -1, 0, 1)
        artifact = await cursor.to_list(length=1)
        if not artifact:
            await log_business_event(
                event_type="SET_DPAR_STATUS_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "status": status,
                    "error": "Consent artifact not found",
                    "consent_query": query,
                },
                message=f"Failed to set status for DPAR request '{request_id}': Consent artifact not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Consent artifact not found")

        artifact = artifact[0]
        artifact_id = str(artifact["_id"])
        data_retention_period_str = artifact["artifact"]["consent_scope"]["data_elements"][0]["data_retention_period"]
        request_type = dpa_request.get("request_type")

        if status == "approved":

            event_type = "data_retention_expiry"
            if request_type == "update_data":
                event_type = "data_update_requested"
                updated_data_element = next(
                    (de for de in artifact["artifact"]["consent_scope"]["data_elements"] if de["de_id"] == dpa_request["data_element_id"]), None
                )
                if not updated_data_element:
                    raise HTTPException(status_code=404, detail=f"Data element {dpa_request['data_element_id']} not found in consent artifact.")

                message_to_publish = {
                    "event_type": event_type,
                    "dp_id": dpa_request["requested_by"],
                    "df_id": current_user["df_id"],
                    "cp_name": artifact["artifact"]["cp_name"],  
                    "timestamp": str(datetime.now(UTC)),
                    "data_elements": [updated_data_element],  
                }
                await publish_message("consent_events_q", json.dumps(message_to_publish))
                await log_business_event(
                    event_type="DPAR_DATA_UPDATE_MESSAGE_PUBLISHED",
                    user_email=user_email,
                    context={
                        "df_id": df_id,
                        "request_id": request_id,
                        "artifact_id": artifact_id,
                        "request_type": request_type,
                        "event_type": event_type,
                    },
                    message=f"DPAR data update message for request '{request_id}' published to queue.",
                    business_logs_collection=self.business_logs_collection,
                )

            elif request_type == "delete_data":
                event_type = "data_retention_expiry_manual"
                message = {
                    "event_type": event_type,
                    "consent_artifact_id": artifact_id,
                    "data_element_id": dpa_request.get("data_element_id"),
                    "retention_expiry_at": data_retention_period_str,
                }
                await publish_message("data_expiry_delay_queue", json.dumps(message), expiration=20)
                await log_business_event(
                    event_type="DPAR_DATA_DELETE_MESSAGE_PUBLISHED",
                    user_email=user_email,
                    context={
                        "df_id": df_id,
                        "request_id": request_id,
                        "artifact_id": artifact_id,
                        "request_type": request_type,
                        "event_type": event_type,
                    },
                    message=f"DPAR data deletion message for request '{request_id}' published to queue.",
                    business_logs_collection=self.business_logs_collection,
                )
            else:
                message = {
                    "event_type": event_type,
                    "consent_artifact_id": artifact_id,
                    "data_element_id": dpa_request.get("data_element_id"),
                    "retention_expiry_at": data_retention_period_str,
                }
                await publish_message("data_expiry_delay_queue", json.dumps(message), expiration=20)
                await log_business_event(
                    event_type="DPAR_DATA_EXPIRY_MESSAGE_PUBLISHED",
                    user_email=user_email,
                    context={
                        "df_id": df_id,
                        "request_id": request_id,
                        "artifact_id": artifact_id,
                        "request_type": request_type,
                        "event_type": event_type,
                    },
                    message=f"DPAR data expiry message for request '{request_id}' published to queue.",
                    business_logs_collection=self.business_logs_collection,
                )

        if status not in action_map:
            await log_business_event(
                event_type="SET_DPAR_STATUS_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "status": status,
                    "error": "Invalid status provided",
                },
                message=f"Failed to set status for DPAR request '{request_id}': Invalid status '{status}'.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid status")

        updates = action_map[status]["updates"]
        updates["last_updated"] = now

        modified = await self.dpa_crud.update_request(request_id, {"$set": updates})
        if modified.modified_count == 0:
            await log_business_event(
                event_type="SET_DPAR_STATUS_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "status": status,
                    "error": "Failed to update DPAR request in DB",
                },
                message=f"Failed to set status for DPAR request '{request_id}': DB update failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        await log_business_event(
            event_type="SET_DPAR_STATUS_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "new_status": status,
            },
            message=f"DPAR request '{request_id}' status updated to '{status}' by user {user_email}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": action_map[status]["message"]}

    async def request_kyc(self, request_id: str, current_user: dict):
        df_id = current_user["df_id"]
        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})

        if not dpa_request:
            raise HTTPException(status_code=404, detail="DPA request not found")

        

        modified = await self.dpa_crud.update_request(
            request_id,
            {
                "$set": {"status": "kyc_requested", "last_updated": datetime.now(UTC)},
            },
        )
        if modified == 0:
            await log_business_event(
                event_type="REQUEST_KYC_FAILED",
                user_email=current_user.get("email"),
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Failed to update DPAR request status in DB",
                },
                message=f"Failed to request KYC for DPAR request '{request_id}': DB update failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        await log_business_event(
            event_type="REQUEST_KYC_SUCCESS",
            user_email=current_user.get("email"),
            context={
                "df_id": df_id,
                "request_id": request_id,
                "new_status": "kyc_requested",
            },
            message=f"KYC requested for DPAR request '{request_id}' by user {current_user.get('email')}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Resend KYC requested successfully"}

    async def clarification_request(self, request_id: str, clarification_details: Dict[str, Any], current_user: dict):
        df_id = current_user["df_id"]
        user_email = current_user.get("email")

        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})
        if not dpa_request:
            await log_business_event(
                event_type="CLARIFICATION_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "DPAR request not found",
                },
                message=f"Failed to send clarification request for DPAR request '{request_id}': Not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        clarification_data = clarification_details.model_dump()
        clarification_data.update(
            {
                "clarification_asked_by": current_user["_id"],
                "email_sent": False,
                "email_response": "",
                "reminder_count": 0,
            }
        )

        update_fields = {
            "status": "clarification_requested",
            "last_updated": datetime.now(),
            "clarification_action": dpa_request.get("clarification_action", []) + [clarification_data],
        }

        modified_count = await self.dpa_crud.update_request(request_id, {"$set": update_fields})

        if modified_count.modified_count == 0:
            await log_business_event(
                event_type="CLARIFICATION_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Failed to update DPAR request in DB",
                    "clarification_details": clarification_details.model_dump(),
                },
                message=f"Failed to send clarification request for DPAR request '{request_id}': DB update failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to update clarification request")

        await log_business_event(
            event_type="CLARIFICATION_REQUEST_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "status": "clarification_requested",
                "clarification_details": clarification_details.model_dump(),
            },
            message=f"Clarification requested for DPAR request '{request_id}' by user {user_email}.",
            business_logs_collection=self.business_logs_collection,
        )
        return {"message": "Clarification requested successfully", "request_id": request_id}

    async def add_notes(self, request_id: str, note_title: str, note_str: str, current_user: dict):
        df_id = current_user["df_id"]
        user_email = current_user.get("email")

        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})

        if not dpa_request:
            await log_business_event(
                event_type="ADD_NOTE_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "DPAR request not found",
                },
                message=f"Failed to add note to DPAR request '{request_id}': Not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        admin_note_to_add = {
            "_id": str(ObjectId()),
            "admin_id": current_user["_id"],
            "timestamp": datetime.now(UTC),
            "title": note_title,
            "message": note_str,
        }

        result = await self.dpa_crud.update_request(
            request_id,
            {
                "$push": {
                    "admin_notes": admin_note_to_add,
                },
                "$set": {
                    "last_updated": datetime.now(UTC),
                },
            },
        )

        if result.modified_count == 0:
            await log_business_event(
                event_type="ADD_NOTE_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Failed to update DPAR request in DB",
                    "note_title": note_title,
                },
                message=f"Failed to add note '{note_title}' to DPAR request '{request_id}': DB update failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to add note")

        await log_business_event(
            event_type="ADD_NOTE_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "note_title": note_title,
            },
            message=f"Note '{note_title}' added successfully to DPAR request '{request_id}' by user {user_email}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Note added successfully", "request_id": request_id}

    async def delete_notes(self, request_id: str, note_id: str, current_user: dict):
        df_id = current_user["df_id"]
        user_email = current_user.get("email")

        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})

        if not dpa_request:
            await log_business_event(
                event_type="DELETE_NOTE_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "note_id": note_id,
                    "error": "DPAR request not found",
                },
                message=f"Failed to delete note '{note_id}' from DPAR request '{request_id}': Request not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        result = await self.dpa_crud.update_request(
            request_id,
            {
                "$pull": {
                    "admin_notes": {"_id": note_id},
                },
                "$set": {
                    "last_updated": datetime.now(UTC),
                },
            },
        )

        if result.modified_count == 0:
            await log_business_event(
                event_type="DELETE_NOTE_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "note_id": note_id,
                    "error": "Failed to update DPAR request in DB",
                },
                message=f"Failed to delete note '{note_id}' from DPAR request '{request_id}': DB update failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to delete note")

        await log_business_event(
            event_type="DELETE_NOTE_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "note_id": note_id,
            },
            message=f"Note '{note_id}' deleted successfully from DPAR request '{request_id}' by user {user_email}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Note deleted successfully", "request_id": request_id}

    async def update_request(self, request_id: str, update_data: DPARCreateRequest, current_user: dict):
        user_id = str(current_user.get("_id"))
        df_id = current_user.get("df_id")
        user_email = current_user.get("email")

        existing_request = await self.dpa_crud.get_by_id(
            request_id,
            {
                "df_id": df_id,
            },
        )

        if not existing_request:
            await log_business_event(
                event_type="UPDATE_DPAR_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Request not found or not owned by the user",
                },
                message=f"Failed to update DPAR request '{request_id}': Not found or unauthorized access.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(
                status_code=404,
                detail="Request not found or not owned by the user",
            )

        update_data_dict = update_data.model_dump(exclude_unset=True)
        update_data_dict["last_updated"] = datetime.now(UTC)

        result = await self.dpa_crud.update_request(request_id, {"$set": update_data_dict})

        if result.modified_count == 0:
            await log_business_event(
                event_type="UPDATE_DPAR_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "updated_fields": list(update_data_dict.keys()),
                    "error": "Failed to update the request in DB",
                },
                message=f"Failed to update DPAR request '{request_id}': DB update failed or no changes.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Failed to update the request")

        updated_request = await self.dpa_crud.get_by_id(
            request_id,
            {
                "df_id": df_id,
            },
        )

        if not updated_request:
            await log_business_event(
                event_type="UPDATE_DPAR_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Updated request not found after successful DB write",
                },
                message=f"DPAR request '{request_id}' updated but retrieval failed post-update.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=404,
                detail="Updated request not found",
            )

        updated_request["_id"] = str(updated_request["_id"])

        datetime_fields = [
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

        for field in datetime_fields:
            if updated_request.get(field) and isinstance(updated_request[field], str):
                updated_request[field] = datetime.fromisoformat(updated_request[field])

        await log_business_event(
            event_type="UPDATE_DPAR_REQUEST_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "updated_fields": list(update_data_dict.keys()),
            },
            message=f"DPAR request '{request_id}' updated successfully. Fields: {', '.join(update_data_dict.keys())}.",
            business_logs_collection=self.business_logs_collection,
        )

        return updated_request

    async def allocate_request(self, request_id: str, assignee_id: str, current_user: dict):
        df_id = current_user["df_id"]
        user_email = current_user.get("email")

        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})

        if not dpa_request:
            await log_business_event(
                event_type="ALLOCATE_DPAR_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "assignee_id": assignee_id,
                    "error": "DPAR request not found",
                },
                message=f"Failed to allocate DPAR request '{request_id}': Request not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPA request not found")

        if not await self.user_collection.find_one({"_id": ObjectId(assignee_id), "df_id": df_id}):
            await log_business_event(
                event_type="ALLOCATE_DPAR_REQUEST_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "assignee_id": assignee_id,
                    "error": "Assignee not found",
                },
                message=f"Failed to allocate DPAR request '{request_id}': Assignee '{assignee_id}' not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Assignee not found")

        allocation_trail = {
            "allocated_to": assignee_id,
            "allocated_by": current_user["_id"],
            "allocated_at": datetime.now(UTC),
        }

        await self.dpa_crud.update_request(
            request_id,
            {
                "$set": {"assignee_id": assignee_id, "last_updated": datetime.now(UTC)},
                "$push": {"allocation_trail": allocation_trail},
            },
        )

        await log_business_event(
            event_type="ALLOCATE_DPAR_REQUEST_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "assignee_id": assignee_id,
            },
            message=f"DPAR request '{request_id}' allocated to '{assignee_id}' by user {user_email}.",
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Request allocated successfully"}

    async def upload_file_to_s3(self, file: UploadFile, field_name: str) -> str:
        try:
            
            file_extension = file.filename.split(".")[-1].lower()
            unique_filename = f"{field_name}_{uuid.uuid4()}.{file_extension}"

            
            local_dir = "app/uploads"
            os.makedirs(local_dir, exist_ok=True)
            local_path = f"{local_dir}/{unique_filename}"

            
            contents = await file.read()
            with open(local_path, "wb") as buf:
                buf.write(contents)

            
            self.s3_client.fput_object(self.bucket_name, unique_filename, local_path, file.content_type)

            
            os.remove(local_path)

            
            return f"http://164.52.205.97:9000/{self.bucket_name}/{unique_filename}"

        except Exception as e:
            await log_business_event(
                event_type="UPLOAD_FILE_TO_S3_FAILED",
                user_email="system",  
                context={
                    "field_name": field_name,
                    "error": str(e),
                },
                message=f"Failed to upload file '{file.filename}' to S3: {e}",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail=f"Failed to upload file to S3: {e}")

    async def upload_kyc_documents(
        self,
        request_id: str,
        current_user: dict,
        kyc_front: Optional[UploadFile | str] = None,
        kyc_back: Optional[UploadFile | str] = None,
        upload_attachments: Optional[List[UploadFile | str]] = None,
    ):
        if isinstance(kyc_front, str) and not kyc_front.strip():
            kyc_front = None
        if isinstance(kyc_back, str) and not kyc_back.strip():
            kyc_back = None
        if upload_attachments:
            upload_attachments = [f for f in upload_attachments if isinstance(f, UploadFile)]

        if not current_user:
            await log_business_event(
                event_type="UPLOAD_KYC_FAILED",
                user_email="anonymous",
                context={"error": "Unauthorized user"},
                message="Unauthorized attempt to upload KYC documents.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=401, detail="Unauthorized")
        user_id = str(current_user.get("_id"))
        df_id = str(current_user.get("df_id"))
        user_email = current_user.get("email")

        user_request = await self.dpa_crud.get_by_id(request_id, {"requested_by": user_id})

        if not user_request:
            await log_business_event(
                event_type="UPLOAD_KYC_FAILED",
                user_email=user_email,
                context={
                    "df_id": df_id,
                    "request_id": request_id,
                    "error": "Request not found or unauthorized access",
                },
                message=f"Failed to upload KYC for DPAR request '{request_id}': Request not found or unauthorized access.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Request not found or unauthorized access")

        update_data = {"last_updated": datetime.now(UTC)}
        kyc_front_url, kyc_back_url, attachment_urls = None, None, []

        
        if kyc_front:
            try:
                kyc_front_url = await self.upload_file_to_s3(kyc_front, "kyc_front")
                update_data["kyc_front"] = kyc_front_url
            except HTTPException as e:
                await log_business_event(
                    event_type="UPLOAD_KYC_FAILED",
                    user_email=user_email,
                    context={"df_id": df_id, "request_id": request_id, "file_type": "kyc_front", "error": str(e.detail)},
                    message=f"Failed to upload front KYC for request '{request_id}': {e.detail}.",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise e  

        
        if kyc_back:
            try:
                kyc_back_url = await self.upload_file_to_s3(kyc_back, "kyc_back")
                update_data["kyc_back"] = kyc_back_url
            except HTTPException as e:
                await log_business_event(
                    event_type="UPLOAD_KYC_FAILED",
                    user_email=user_email,
                    context={"df_id": df_id, "request_id": request_id, "file_type": "kyc_back", "error": str(e.detail)},
                    message=f"Failed to upload back KYC for request '{request_id}': {e.detail}.",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise e  

        
        if upload_attachments:
            for file in upload_attachments:
                try:
                    file_url = await self.upload_file_to_s3(file, "request_attachment")
                    attachment_urls.append(file_url)
                except HTTPException as e:
                    await log_business_event(
                        event_type="UPLOAD_KYC_FAILED",
                        user_email=user_email,
                        context={
                            "df_id": df_id,
                            "request_id": request_id,
                            "file_type": "attachment",
                            "filename": file.filename,
                            "error": str(e.detail),
                        },
                        message=f"Failed to upload attachment '{file.filename}' for request '{request_id}': {e.detail}.",
                        business_logs_collection=self.business_logs_collection,
                        log_level="ERROR",
                    )
                    raise e  

            update_data["request_attachments"] = attachment_urls

        if len(update_data) == 1:  
            await log_business_event(
                event_type="UPLOAD_KYC_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "request_id": request_id, "error": "No files provided"},
                message=f"No KYC files or attachments provided for DPAR request '{request_id}'.",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",  
            )
            raise HTTPException(
                status_code=400,
                detail="No KYC files or attachments provided for upload",
            )

        
        result = await self.dpa_crud.update_request(request_id, {"$set": update_data})
        if result.modified_count == 0:
            await log_business_event(
                event_type="UPLOAD_KYC_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "request_id": request_id, "error": "DB update failed"},
                message=f"Failed to update DPAR request '{request_id}' with KYC/attachment URLs in DB.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to update KYC information in database")

        await log_business_event(
            event_type="UPLOAD_KYC_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "kyc_front_uploaded": bool(kyc_front_url),
                "kyc_back_uploaded": bool(kyc_back_url),
                "num_attachments_uploaded": len(attachment_urls),
            },
            message=f"KYC documents and attachments uploaded successfully for DPAR request '{request_id}'.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Files uploaded and KYC information updated successfully",
            "kyc_front_url": kyc_front_url,
            "kyc_back_url": kyc_back_url,
            "request_attachments": attachment_urls if attachment_urls else None,
            "request_id": request_id,
        }

    def _guess_mime_from_url(self, file_url: str) -> str | None:
        mime, _ = mimetypes.guess_type(file_url)
        return mime

    async def get_presigned_url(self, file_url: str, current_user: dict):
        df_id = current_user.get("df_id")
        user_email = current_user.get("email")
        try:
            await log_business_event(
                event_type="GET_PRESIGNED_URL_START",
                user_email=user_email,
                context={"df_id": df_id, "file_url": file_url},
                message=f"Attempting to generate presigned URL for '{file_url}'.",
                business_logs_collection=self.business_logs_collection,
            )

            parsed = urlparse(file_url)
            
            parts = parsed.path.lstrip("/").split("/", 1)
            if len(parts) != 2:
                await log_business_event(
                    event_type="GET_PRESIGNED_URL_FAILED",
                    user_email=user_email,
                    context={"df_id": df_id, "file_url": file_url, "error": "Invalid object URL format"},
                    message=f"Failed to get presigned URL for '{file_url}': Invalid object URL format.",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(status_code=400, detail="Invalid object URL")

            bucket_from_url, object_key = parts[0], parts[1]
            object_key = unquote(object_key)  

            
            try:
                self.s3_client.stat_object(bucket_from_url, object_key)
            except Exception:
                await log_business_event(
                    event_type="GET_PRESIGNED_URL_FAILED",
                    user_email=user_email,
                    context={"df_id": df_id, "object_key": object_key, "error": "Object not found or not accessible"},
                    message=f"Failed to get presigned URL for '{object_key}': Object not found or not accessible.",
                    business_logs_collection=self.business_logs_collection,
                    log_level="WARNING",
                )
                raise HTTPException(status_code=404, detail="Object not found or not accessible")

            content_type = self._guess_mime_from_url(file_url)

            url = self.s3_client.presigned_get_object(
                bucket_name=bucket_from_url,  
                object_name=object_key,
                expires=timedelta(seconds=60 * 60),
                response_headers=({"response-content-type": content_type} if content_type else None),
            )
            await log_business_event(
                event_type="GET_PRESIGNED_URL_SUCCESS",
                user_email=user_email,
                context={"df_id": df_id, "object_key": object_key},
                message=f"Successfully generated presigned URL for object '{object_key}'.",
                business_logs_collection=self.business_logs_collection,
            )
            return {"url": url}

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="GET_PRESIGNED_URL_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "file_url": file_url, "error": str(e)},
                message=f"Failed to get presigned URL for '{file_url}': {e}.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def send_dpar_report(self, request_id: str, payload: DPARReportCreate, current_user: dict):
        df_id = current_user.get("df_id")
        user_email = current_user.get("email")

        if not current_user:
            await log_business_event(
                event_type="SEND_DPAR_REPORT_FAILED",
                user_email="anonymous",
                context={"error": "Unauthorized user"},
                message="Unauthorized attempt to send DPAR report.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=401, detail="Unauthorized")

        
        dpa_request = await self.dpa_crud.get_by_id(request_id, {"df_id": df_id})
        if not dpa_request:
            await log_business_event(
                event_type="SEND_DPAR_REPORT_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "request_id": request_id, "error": "DPAR request not found"},
                message=f"Failed to send DPAR report for request '{request_id}': Request not found.",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="DPAR request not found")

        
        recipient = dpa_request.get("core_identifier") if payload.send_to == "core" else dpa_request.get("secondary_identifier")
        if not recipient:
            await log_business_event(
                event_type="SEND_DPAR_REPORT_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "request_id": request_id, "send_to": payload.send_to, "error": "Recipient identifier not available"},
                message=f"Failed to send DPAR report for request '{request_id}': {payload.send_to} identifier not available.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail=f"{payload.send_to} identifier not available for this request",
            )

        
        report = {
            "request_id": request_id,
            "df_id": df_id,
            "report_type": payload.report_type,
            "template": payload.template_id,
            "send_to": payload.send_to,
            "recipient_identifier": recipient,
            "subject": payload.subject,
            "message": payload.message,
            "status": "sent",
            "sent_at": datetime.now(UTC),
            "is_deleted": False,
        }
        result = await self.dpa_crud.insert_report(report)

        if not result.inserted_id:
            await log_business_event(
                event_type="SEND_DPAR_REPORT_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "request_id": request_id, "error": "Failed to insert report into DB"},
                message=f"Failed to send DPAR report for request '{request_id}': DB insert failed.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=500, detail="Failed to send report")

        
        sender_display_name = "data_fiduciary" if not df_id else f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()

        conversation_entry = {
            "message_id": str(uuid.uuid4()),
            "sender": sender_display_name,
            "sender_image": current_user.get("image_url"),
            "subject": payload.subject,
            "message": payload.message,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "sent",
        }

        
        await self.dpa_crud.add_conversation(
            {"_id": ObjectId(request_id)},
            {"$push": {"request_conversation": conversation_entry}},
        )

        await log_business_event(
            event_type="SEND_DPAR_REPORT_SUCCESS",
            user_email=user_email,
            context={
                "df_id": df_id,
                "request_id": request_id,
                "report_id": str(result.inserted_id),
                "recipient": recipient,
                "report_type": payload.report_type,
            },
            message=f"DPAR report '{result.inserted_id}' sent successfully for request '{request_id}' to '{recipient}'.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "Report sent successfully",
            "report_id": str(result.inserted_id),
            "recipient": recipient,
        }


    async def bulk_upload(self, request: Request, file: UploadFile, current_user: dict):
        df_id = current_user.get("df_id")
        genie_user_id = current_user.get("_id")
        user_email = current_user.get("email")

        if not df_id or not genie_user_id:
            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_FAILED",
                user_email="anonymous",
                context={"error": "Unauthorized user or missing DF/Genie ID"},
                message="Unauthorized attempt for DPAR bulk upload.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=401, detail="Unauthorized")

        file_type = file.filename.rsplit(".", 1)[-1].lower()
        if file_type not in ["csv"]:
            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "file_type": file_type, "error": "Unsupported file type"},
                message=f"DPAR bulk upload failed for user {user_email}: Unsupported file type '{file_type}'.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(415, "Unsupported file type")

        
        filename, file_url = await self.upload_file_to_s3(file, f"{df_id}_{genie_user_id}_dpar_bulk")

        
        try:
            await self.dpa_crud.insert_upload(
                {
                    "df_id": df_id,
                    "genie_user_id": genie_user_id,
                    "filename": filename,
                    "file_url": file_url,
                    "uploaded_at": datetime.now(UTC),
                    "is_deleted": False,
                }
            )
            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_DB_RECORD_SUCCESS",
                user_email=user_email,
                context={"df_id": df_id, "filename": filename, "file_url": file_url},
                message=f"DPAR bulk upload record saved to DB for file '{filename}'.",
                business_logs_collection=self.business_logs_collection,
            )
        except Exception as e:
            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "filename": filename, "error": str(e)},
                message=f"DPAR bulk upload failed for file '{filename}': Error saving upload record: {e}.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(500, f"Error saving upload record: {str(e)}")

        
        try:
            message = json.dumps(
                {
                    "df_id": df_id,
                    "genie_user_id": str(genie_user_id),
                    "filename": filename,
                    "file_url": file_url,
                    "file_type": file_type,
                }
            )

            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_MESSAGE_PUBLISHED",
                user_email=user_email,
                context={"df_id": df_id, "filename": filename, "queue": "dpa_bulk_requests"},
                message=f"DPAR bulk upload message for '{filename}' published to RabbitMQ.",
                business_logs_collection=self.business_logs_collection,
            )
        except Exception as e:
            await log_business_event(
                event_type="BULK_UPLOAD_DPAR_FAILED",
                user_email=user_email,
                context={"df_id": df_id, "filename": filename, "error": str(e)},
                message=f"DPAR bulk upload failed for file '{filename}': Error publishing message: {e}.",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(500, f"Error processing file: {str(e)}")

        await log_business_event(
            event_type="BULK_UPLOAD_DPAR_INITIATED_SUCCESS",
            user_email=user_email,
            context={"df_id": df_id, "filename": filename, "file_url": file_url},
            message=f"DPAR bulk upload initiated successfully for file '{filename}'.",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "message": "DPA bulk upload initiated successfully",
            "filename": filename,
            "file_url": file_url,
            "df_id": df_id,
            "genie_user_id": str(genie_user_id),
        }

    def serialize_row(self, doc):
        return {field: str(doc.get(field, "")) for field in EXPORT_FIELDS}

    async def export_requests(self, current_user: dict):
        if not current_user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        df_id = current_user["df_id"]
        dpa_requests = await self.dpa_crud.get_requests_for_export(df_id, EXPORT_FIELDS)

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
        writer.writeheader()

        for req in dpa_requests:
            writer.writerow(self.serialize_row(req))

        output.seek(0)
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dpar_export_{now_str}.csv"

        await log_business_event(
            event_type="EXPORT_DPAR_REQUESTS_SUCCESS",
            user_email=current_user.get("email"),
            context={"df_id": df_id, "num_requests_exported": len(dpa_requests), "filename": filename},
            message=f"DPAR requests exported successfully by user {current_user.get('email')}. {len(dpa_requests)} records exported.",
            business_logs_collection=self.business_logs_collection,
        )

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
