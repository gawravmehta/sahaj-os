from typing import Dict, Any
from fastapi import HTTPException
from datetime import datetime, UTC
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.grievance_crud import GrievanceCRUD
from app.utils.business_logger import log_business_event


class GrievanceService:
    def __init__(
        self,
        grievance_crud: GrievanceCRUD,
        business_logs_collection: str,
        customer_notification_collection: AsyncIOMotorCollection,
    ):
        self.grievance_crud = grievance_crud
        self.business_logs_collection = business_logs_collection
        self.customer_notification_collection = customer_notification_collection

    async def get_all_grievances(
        self,
        current_user: dict,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:

        skip = (page - 1) * page_size
        total_count = await self.grievance_crud.count_grievances()
        grievances = await self.grievance_crud.get_grievances(skip, page_size)

        await log_business_event(
            event_type="GRIEVANCE_LIST_VIEWED",
            user_email=current_user.get("email"),
            context={
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
            },
            message=f"User viewed grievance list (page={page}, size={page_size})",
            business_logs_collection=self.business_logs_collection,
        )

        return {
            "status": "success",
            "data": grievances,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "pages": (total_count + page_size - 1) // page_size,
            },
        }

    async def view_grievance(self, current_user: dict, grievance_id: str) -> Dict[str, Any]:

        grievance = await self.grievance_crud.get_by_id(grievance_id)
        if not grievance:

            await log_business_event(
                event_type="GRIEVANCE_NOT_FOUND",
                user_email=current_user.get("email"),
                context={"grievance_id": grievance_id},
                message=f"Grievance {grievance_id} not found",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Grievance not found")

        await log_business_event(
            event_type="GRIEVANCE_VIEWED",
            user_email=current_user.get("email"),
            context={"grievance_id": grievance_id},
            message=f"User viewed grievance {grievance_id}",
            business_logs_collection=self.business_logs_collection,
        )

        return {"status": "success", "data": grievance}

    async def resolve_grievance(self, current_user: dict, grievance_id: str) -> Dict[str, Any]:

        grievance = await self.grievance_crud.get_by_id(grievance_id)
        if not grievance:

            await log_business_event(
                event_type="GRIEVANCE_NOT_FOUND",
                user_email=current_user.get("email"),
                context={"grievance_id": grievance_id},
                message=f"Grievance {grievance_id} not found",
                business_logs_collection=self.business_logs_collection,
                log_level="WARNING",
            )
            raise HTTPException(status_code=404, detail="Grievance not found")

        await log_business_event(
            event_type="GRIEVANCE_RESOLVED",
            user_email=current_user.get("email"),
            context={"grievance_id": grievance_id},
            message=f"User resolved grievance {grievance_id}",
            business_logs_collection=self.business_logs_collection,
        )

        grievance["request_status"] = "resolved"
        await self.grievance_crud.resolve_grievance(grievance_id)

        # Create notification for DP
        dp_id = grievance.get("dp_id")
        if dp_id:
            print("Creating notification for DP")
            now = datetime.now(UTC)
            notification = {
                "dp_id": dp_id,
                "type": "GRIEVANCE_RESOLVED",
                "title": "Grievance Resolved",
                "message": f"Your grievance regarding {grievance.get('subject', 'issue')} has been resolved.",
                "status": "unread",
                "created_at": now,
                "grievance_id": grievance_id,
            }
            await self.customer_notification_collection.insert_one(notification)

        return {"status": "success", "data": grievance}
