from typing import Literal, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, UTC

from app.schemas.incident_management_schema import (
    IncidentCreate,
    AddStepRequest,
    UpdateStageRequest,
)
from app.crud.incident_management_crud import IncidentCRUD
from app.services.data_principal_service import DataPrincipalService
from app.utils.business_logger import log_business_event


class IncidentService:
    def __init__(
        self,
        crud: IncidentCRUD,
        user_collection,
        business_logs_collection: str,
        data_principal_service: DataPrincipalService,
        customer_notifications_collection,
    ):
        self.crud = crud
        self.user_collection = user_collection
        self.business_logs_collection = business_logs_collection
        self.data_principal_service = data_principal_service
        self.customer_notifications_collection = customer_notifications_collection

    async def create_or_update_incident(
        self,
        data: IncidentCreate,
        user: dict,
        incident_id: str = None,
    ):
        user_id = user.get("_id")
        user_email = user.get("email")
        df_id = user.get("df_id")

        if not incident_id:
            duplicate = await self.crud.find_duplicate(df_id, data.incident_name)
            if duplicate:
                await log_business_event(
                    event_type="INCIDENT_CREATE_FAILED",
                    user_email=user_email,
                    context={"user_id": user_id, "df_id": df_id, "incident_name": data.incident_name, "reason": "Duplicate incident name"},
                    message=f"Duplicate incident name '{data.incident_name}' detected during creation",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Stage already open for incident '{data.incident_name}'.",
                )

            incident_data = data.model_dump()
            incident_data.update(
                {
                    "df_id": df_id,
                    "created_at": datetime.now(UTC),
                    "date_closed": None,
                    "current_stage": data.workflow[0].stage_name,
                }
            )

            new_id = await self.crud.insert_incident(incident_data)
            await log_business_event(
                event_type="INCIDENT_CREATED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": new_id, "incident_name": data.incident_name},
                message="Incident created successfully",
                business_logs_collection=self.business_logs_collection,
                log_level="INFO",
            )

            return {"incident_id": new_id, "message": "Incident created successfully"}

        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        existing_incident = await self.crud.get_incident_by_id(incident_id)
        if not existing_incident:
            await log_business_event(
                event_type="INCIDENT_UPDATE_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found during update",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        if existing_incident.get("df_id") != df_id:
            raise HTTPException(status_code=403, detail="Access denied to this incident")

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(UTC)

        await self.crud.update_incident(incident_id, update_data)
        await log_business_event(
            event_type="INCIDENT_UPDATED",
            user_email=user_email,
            context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "updated_fields": list(update_data.keys())},
            message="Incident updated successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {"incident_id": incident_id, "message": "Incident updated successfully"}

    async def list_incidents(
        self,
        incident_type: Optional[str],
        incident_sensitivity: Optional[Literal["low", "medium", "high"]],
        status: Optional[Literal["archived", "draft", "in_progress", "published"]],
        current_stage: Optional[str],
        sort_order: Literal["asc", "desc"],
        page: int,
        page_size: int,
        current_user: dict,
    ):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        query = {"df_id": df_id}
        if incident_type:
            query["incident_type"] = {"$regex": incident_type, "$options": "i"}
        if incident_sensitivity:
            query["incident_sensitivity"] = incident_sensitivity
        if current_stage:
            query["current_stage"] = {"$regex": current_stage, "$options": "i"}
        if status:
            query["status"] = {"$regex": status, "$options": "i"}
        else:
            query["status"] = {"$ne": "archived"}

        skip = (page - 1) * page_size
        total_count = await self.crud.count_incidents(query)
        incidents = await self.crud.get_incidents(query, sort_order, skip, page_size)

        formatted_incidents = []
        for inc in incidents:
            workflow = inc.get("workflow") or []
            stage_names = [s.get("stage_name") for s in workflow if s.get("stage_name")]

            formatted_incidents.append(
                {
                    "_id": str(inc["_id"]),
                    "incident_name": inc.get("incident_name"),
                    "incident_type": inc.get("incident_type"),
                    "incident_sensitivity": inc.get("incident_sensitivity"),
                    "description": inc.get("description"),
                    "status": inc.get("status"),
                    "current_stage": inc.get("current_stage"),
                    "workflow_stages": stage_names,
                    "date_discovered": inc.get("date_discovered"),
                    "deadline": inc.get("deadline"),
                    "created_at": inc.get("created_at"),
                }
            )

        filter_fields = await self.crud.get_filter_fields(df_id)

        await log_business_event(
            event_type="INCIDENT_LIST_SUCCESS",
            user_email=user_email,
            context={
                "user_id": user_id,
                "df_id": df_id,
                "incident_type": incident_type,
                "incident_sensitivity": incident_sensitivity,
                "status": status,
                "current_stage": current_stage,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
                "total_incidents_found": total_count,
            },
            message="Incidents listed successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {
            "pagination": {
                "total_incidents": total_count,
                "current_page": page,
                "page_size": page_size,
                "total_pages": max(1, (total_count + page_size - 1) // page_size),
            },
            "filter_fields": filter_fields,
            "sort_order_used": sort_order,
            "incidents": formatted_incidents,
        }

    async def get_incident(self, incident_id: str, current_user: dict):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="GET_INCIDENT_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        await log_business_event(
            event_type="GET_INCIDENT_SUCCESS",
            user_email=user_email,
            context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "incident_name": incident.get("incident_name")},
            message="Incident fetched successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        incident["_id"] = str(incident["_id"])
        for key, value in list(incident.items()):
            if isinstance(value, ObjectId):
                incident[key] = str(value)

        return incident

    async def publish_incident(self, incident_id: str, current_user: dict):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            await log_business_event(
                event_type="PUBLISH_INCIDENT_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Invalid incident ID format"},
                message="Invalid incident ID format for publishing incident",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="PUBLISH_INCIDENT_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found for publishing",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        if incident.get("status") != "draft":
            await log_business_event(
                event_type="PUBLISH_INCIDENT_FAILED",
                user_email=user_email,
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "incident_id": incident_id,
                    "current_status": incident.get("status"),
                    "reason": "Incident not in draft state",
                },
                message="Incident is not in draft state for publishing",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Incident is not in draft state")

        missing_fields = [f for f in ["date_occurred", "date_discovered", "deadline"] if incident.get(f) is None]
        if missing_fields:
            await log_business_event(
                event_type="PUBLISH_INCIDENT_FAILED",
                user_email=user_email,
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "incident_id": incident_id,
                    "missing_fields": missing_fields,
                    "reason": "Missing required fields",
                },
                message=f"Cannot publish incident due to missing required fields: {', '.join(missing_fields)}",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish. The following fields are required: {', '.join(missing_fields)}",
            )

        await self.crud.publish_incident(incident_id)
        await log_business_event(
            event_type="INCIDENT_PUBLISHED",
            user_email=user_email,
            context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "incident_name": incident.get("incident_name")},
            message="Incident published successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {"message": "Incident published successfully"}

    async def move_to_next_stage(self, incident_id: str, current_user: dict):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            await log_business_event(
                event_type="MOVE_TO_NEXT_STAGE_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Invalid incident ID format"},
                message="Invalid incident ID format for moving incident to next stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="MOVE_TO_NEXT_STAGE_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found for moving to next stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        workflow = incident.get("workflow") or []
        current_stage = incident.get("current_stage")

        stage_names = [s.get("stage_name") for s in workflow]
        if current_stage not in stage_names:
            await log_business_event(
                event_type="MOVE_TO_NEXT_STAGE_FAILED",
                user_email=user_email,
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "incident_id": incident_id,
                    "current_stage": current_stage,
                    "reason": "current_stage not found in workflow",
                },
                message="current_stage not found in workflow for moving incident to next stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="current_stage not found in workflow")

        idx = stage_names.index(current_stage)

        update_data: dict = {"updated_at": datetime.now(UTC)}

        if idx == len(stage_names) - 1:
            update_data["status"] = "closed"
            update_data["date_closed"] = datetime.now(UTC)
        else:
            update_data["current_stage"] = stage_names[idx + 1]

        await self.crud.update_incident(incident_id, update_data)

        new_status = update_data.get("status", incident.get("status"))
        new_current_stage = update_data.get("current_stage", current_stage)

        await log_business_event(
            event_type="INCIDENT_STAGE_MOVED",
            user_email=user_email,
            context={
                "user_id": user_id,
                "df_id": df_id,
                "incident_id": incident_id,
                "old_stage": current_stage,
                "new_stage": new_current_stage,
                "new_status": new_status,
            },
            message="Incident moved to next stage successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {
            "incident_id": incident_id,
            "message": "Stage updated successfully",
            "new_status": new_status,
            "new_current_stage": new_current_stage,
        }

    async def add_step_to_stage(
        self,
        incident_id: str,
        body: AddStepRequest,
        current_user: dict,
    ):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            await log_business_event(
                event_type="ADD_STEP_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Invalid incident ID format"},
                message="Invalid incident ID format for adding step to incident stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="ADD_STEP_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found for adding step to incident stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        workflow = incident.get("workflow") or []
        stage_found = False

        for stage in workflow:
            if stage.get("stage_name") == body.stage_name:
                if "steps" not in stage or stage["steps"] is None:
                    stage["steps"] = []
                stage["steps"].append(body.step.model_dump())
                stage_found = True
                break

        if not stage_found:
            await log_business_event(
                event_type="ADD_STEP_FAILED",
                user_email=user_email,
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "incident_id": incident_id,
                    "stage_name": body.stage_name,
                    "reason": "stage_name not found in workflow",
                },
                message=f"Stage name '{body.stage_name}' not found in workflow for adding step",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail=f"stage_name '{body.stage_name}' not found in workflow",
            )

        await self.crud.update_incident(
            incident_id,
            {"workflow": workflow, "updated_at": datetime.now(UTC)},
        )
        await log_business_event(
            event_type="STEP_ADDED",
            user_email=user_email,
            context={
                "user_id": user_id,
                "df_id": df_id,
                "incident_id": incident_id,
                "stage_name": body.stage_name,
                "step_description": body.step.step_description,
            },
            message="Step added successfully to incident stage",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {
            "incident_id": incident_id,
            "message": "Step added successfully",
        }

    async def update_stage_manually(
        self,
        incident_id: str,
        body: UpdateStageRequest,
        current_user: dict,
    ):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            await log_business_event(
                event_type="UPDATE_STAGE_MANUALLY_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Invalid incident ID format"},
                message="Invalid incident ID format for manually updating incident stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="UPDATE_STAGE_MANUALLY_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found for manually updating incident stage",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        workflow = incident.get("workflow") or []
        stage_names = [s.get("stage_name") for s in workflow]

        if body.new_stage not in stage_names:
            await log_business_event(
                event_type="UPDATE_STAGE_MANUALLY_FAILED",
                user_email=user_email,
                context={
                    "user_id": user_id,
                    "df_id": df_id,
                    "incident_id": incident_id,
                    "new_stage": body.new_stage,
                    "available_stages": stage_names,
                    "reason": "new_stage not found in workflow",
                },
                message=f"New stage '{body.new_stage}' not found in workflow for manual update",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail=f"new_stage '{body.new_stage}' must be one of {stage_names}",
            )

        await self.crud.update_incident(
            incident_id,
            {"current_stage": body.new_stage, "updated_at": datetime.now(UTC)},
        )
        await log_business_event(
            event_type="INCIDENT_STAGE_UPDATED_MANUALLY",
            user_email=user_email,
            context={
                "user_id": user_id,
                "df_id": df_id,
                "incident_id": incident_id,
                "old_stage": incident.get("current_stage"),
                "new_stage": body.new_stage,
            },
            message="Incident stage updated manually successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {
            "incident_id": incident_id,
            "message": "Current stage updated successfully",
            "new_current_stage": body.new_stage,
        }

    async def send_incident_notifications(
        self,
        incident_id: str,
        current_user: dict,
    ):
        user_id = current_user.get("_id")
        user_email = current_user.get("email")
        df_id = current_user.get("df_id")

        if not ObjectId.is_valid(incident_id):
            await log_business_event(
                event_type="SEND_NOTIFICATION_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Invalid incident ID format"},
                message="Invalid incident ID format for sending notifications",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=400, detail="Invalid incident ID")

        incident = await self.crud.get_incident_by_id(incident_id)
        if not incident:
            await log_business_event(
                event_type="SEND_NOTIFICATION_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Incident not found"},
                message="Incident not found for sending notifications",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(status_code=404, detail="Incident not found")

        notification_needed = incident.get("notification_needed")
        data_elements = incident.get("data_element")
        mitigation_steps = incident.get("mitigation_steps")
        incident_name = incident.get("incident_name")

        if not notification_needed:
            await log_business_event(
                event_type="SEND_NOTIFICATION_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Notifications not marked as needed"},
                message="Notifications not marked as needed for this incident",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="Notifications are not marked as needed for this incident.",
            )
        if not data_elements:
            await log_business_event(
                event_type="SEND_NOTIFICATION_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Data elements not specified"},
                message="Data elements are not specified in the incident for sending notifications",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="data_elements are not specified in the incident for sending notifications.",
            )
        if not mitigation_steps:
            await log_business_event(
                event_type="SEND_NOTIFICATION_FAILED",
                user_email=user_email,
                context={"user_id": user_id, "df_id": df_id, "incident_id": incident_id, "reason": "Mitigation steps not specified"},
                message="Mitigation steps are not specified in the incident for sending notifications",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
            )
            raise HTTPException(
                status_code=400,
                detail="mitigation_steps are not specified in the incident for sending notifications.",
            )

        affected_dps = await self.data_principal_service.get_dps_by_data_elements(data_elements, current_user)
        notification_docs = []
        for dp in affected_dps:
            existing_notification = await self.customer_notifications_collection.find_one(
                {
                    "dp_id": dp["dp_id"],
                    "incident_id": ObjectId(incident_id),
                    "type": "INCIDENT_MITIGATION",
                }
            )
            if not existing_notification:
                notification_docs.append(
                    {
                        "dp_id": dp["dp_id"],
                        "df_id": df_id,
                        "incident_id": incident_id,
                        "type": "INCIDENT_MITIGATION",
                        "title": f"Incident Alert: {incident_name}",
                        "message": f"An incident '{incident_name}' has occurred. Please follow these mitigation steps: {', '.join(mitigation_steps)}",
                        "status": "unread",
                        "created_at": datetime.now(UTC),
                        "incident_name": incident_name,
                        "mitigation_steps": mitigation_steps,
                        "data_elements": data_elements,
                    }
                )
        if notification_docs:
            await self.customer_notifications_collection.insert_many(notification_docs)

        update_incident_fields = {
            "notification_sent": True,
            "notification_sent_date": datetime.now(UTC),
        }
        await self.crud.update_incident(incident_id, update_incident_fields)

        await log_business_event(
            event_type="NOTIFICATIONS_SENT",
            user_email=user_email,
            context={
                "user_id": user_id,
                "df_id": df_id,
                "incident_id": incident_id,
                "affected_dps_count": len(affected_dps),
                "notifications_created_count": len(notification_docs),
            },
            message="Incident notifications sent successfully",
            business_logs_collection=self.business_logs_collection,
            log_level="INFO",
        )

        return {"incident_id": incident_id, "message": "Incident notifications sent successfully"}
