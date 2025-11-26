from bson import ObjectId
from fastapi import HTTPException
from app.crud.notification_crud import NotificationCRUD
from datetime import timezone
import math


class NotificationService:
    def __init__(
        self,
        crud: NotificationCRUD,
    ):
        self.crud = crud

    async def get_notifications(self, current_user: dict, page: int = 1, limit: int = 10):
        try:
            user_id = str(current_user["_id"])

            total_notifications = await self.crud.count_notifications({f"users.{user_id}.is_deleted": False})

            notifications = await self.crud.get_notifications(
                {f"users.{user_id}.is_deleted": False}, sort_field="created_at", sort_order=-1, page=page, limit=limit
            )

            result = []
            for notification in notifications:
                user_status = notification["users"].get(user_id, {})
                result.append(
                    {
                        "_id": str(notification["_id"]),
                        "notification_title": notification["notification_title"],
                        "notification_message": notification["notification_message"],
                        "redirection_route": notification["redirection_route"],
                        "cta_url": notification["cta_url"],
                        "file_url": notification["file_url"],
                        "created_at": notification["created_at"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "is_read": user_status.get("is_read", False),
                        "is_deleted": user_status.get("is_deleted", False),
                        "priority": notification["priority"],
                        "icon_url": notification.get("icon_url", ""),
                        "category": notification["category"],
                    }
                )

            total_pages = math.ceil(total_notifications / limit)

            unseen_notification_count = await self.crud.count_notifications(
                {
                    f"users.{user_id}.is_read": False,
                    f"users.{user_id}.is_deleted": False,
                }
            )

            return {
                "page": page,
                "limit": limit,
                "total_notifications": total_notifications,
                "total_pages": total_pages,
                "data": result,
                "unseen_notification_count": unseen_notification_count,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving notifications: {str(e)}",
            )

    async def mark_notification_as_read(self, notification_id: str, current_user: dict):
        try:
            user_id = str(current_user["_id"])

            update_result = await self.crud.mark_as_read(notification_id, user_id)

            if update_result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Notification not found or already marked as read.")

            return {"message": "Notification marked as read."}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error marking notification as read: {str(e)}",
            )

    async def mark_all_notifications_as_read(self, current_user: dict):
        try:
            user_id = str(current_user["_id"])

            update_result = await self.crud.mark_all_as_read(user_id)

            return {"message": f"{update_result.modified_count} notifications marked as read."}

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error marking all notifications as read: {str(e)}",
            )
