import base64
import io
import json
from datetime import UTC, datetime


from fastapi import HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse

from app.crud.notice_notification_crud import NoticeNotificationCRUD
from app.core.config import settings
from app.db.rabbitmq import publish_message
from app.utils.business_logger import log_business_event


class NoticeNotificationService:
    def __init__(
        self,
        crud: NoticeNotificationCRUD,
        business_logs_collection: str,
    ):
        self.crud = crud
        self.business_logs_collection = business_logs_collection

    async def send_notice(
        self,
        notice_notification,
        current_user,
    ):
        try:
            current_user_df_id = current_user.get("df_id")
            current_user_id = str(current_user.get("_id"))
            notice_notification_data = notice_notification.model_dump()

            notice_notification_data.update(
                {
                    "df_id": current_user_df_id,
                    "created_by": current_user_id,
                    "notice_url": "",
                    "notification_status": "",
                    "created_at": datetime.now(UTC),
                    "dp_preferred_language": [],
                    "dp_state": "",
                    "dp_tags": notice_notification_data.get("dp_tags", []),
                    "dp_counter": 0,
                    "consent": [],
                }
            )

            result = await self.crud.insert_notice_notification(notice_notification_data)

            await publish_message(
                "notice_notification_queue",
                json.dumps({"notice_notification_id": str(result.inserted_id)}),
            )

            await log_business_event(
                event_type="NOTICE_SENT",
                user_email=current_user.get("email"),
                context={"notice_notification_id": str(result.inserted_id), "df_id": current_user_df_id},
                message=f"Notice triggered for DF {current_user_df_id}",
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "message": "Notice Sent Successfully",
                "notice_notification_id": str(result.inserted_id),
            }

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="NOTICE_SEND_FAILED",
                user_email=current_user.get("email"),
                context={},
                message=f"Failed to send notice",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
                error_details=str(e),
            )
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

    async def get_notifications_overview(self, page, limit, current_user):
        try:
            if page < 1 or limit < 1:

                raise HTTPException(status_code=400, detail="Page and limit must be greater than 0")

            df_id = current_user.get("df_id")
            if not df_id:
                raise HTTPException(status_code=400, detail="Invalid DF identity")

            skip = (page - 1) * limit

            total_notifications = await self.crud.get_total_notice_notifications_count(df_id)
            total_pages = (total_notifications + limit - 1) // limit
            notifications = await self.crud.get_notice_notifications(df_id, limit, skip)

            for n in notifications:
                n["is_notification_read"] = bool(n.get("is_notification_read", False))
                n["is_notification_clicked"] = bool(n.get("is_notification_clicked", False))

            await log_business_event(
                event_type="NOTICE_LIST_VIEWED",
                user_email=current_user.get("email"),
                context={"df_id": df_id, "page": page, "limit": limit},
                message="User viewed notice notifications overview",
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "notifications": notifications,
                "pagination": {
                    "total_notifications": total_notifications,
                    "total_pages": total_pages,
                    "current_page": page,
                    "limit": limit,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="NOTICE_LIST_FAILED",
                user_email=current_user.get("email") if isinstance(current_user, dict) else None,
                context={"page": page, "limit": limit},
                message="Failed to fetch notifications overview",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
                error_details=str(e),
            )
            raise HTTPException(status_code=500, detail=str(e))

    def _get_pixel_stream(self):
        pixel_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQImWNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
        return io.BytesIO(base64.b64decode(pixel_base64))

    async def track_pixel(self, event_id: str):
        try:
            await self.crud.mark_notification_as_read(event_id)

            await log_business_event(
                event_type="NOTICE_EMAIL_OPENED",
                user_email=None,
                context={"event_id": event_id},
                message=f"Notice email opened for event {event_id}",
                business_logs_collection=self.business_logs_collection,
            )

            return StreamingResponse(self._get_pixel_stream(), media_type="image/png")

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="NOTICE_EMAIL_OPEN_FAILED",
                user_email=None,
                context={"event_id": event_id},
                message="Failed to track email open",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
                error_details=str(e),
            )
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def track_click(self, event_id: str, token: str, url_type: str):
        try:
            await self.crud.mark_notification_as_clicked(event_id)

            if url_type == "ln":
                redirect_url = f"{settings.CMP_NOTICE_WORKER_URL}/api/v1/ln/{settings.SMS_SENDER_ID}?{token}"
            elif url_type == "mln":
                redirect_url = f"{settings.CMP_NOTICE_WORKER_URL}/api/v1/ln/mln/{token}"
            else:
                await log_business_event(
                    event_type="NOTICE_CLICK_FAILED",
                    user_email=None,
                    context={"event_id": event_id, "url_type": url_type},
                    message=f"Unknown url_type={url_type} for event {event_id}",
                    business_logs_collection=self.business_logs_collection,
                    log_level="ERROR",
                    error_details="Unknown url_type",
                )
                raise HTTPException(status_code=400, detail="Unknown url_type")

            await log_business_event(
                event_type="NOTICE_CLICKED",
                user_email=None,
                context={"event_id": event_id, "url_type": url_type},
                message=f"Notice clicked for event {event_id}",
                business_logs_collection=self.business_logs_collection,
            )

            return RedirectResponse(url=redirect_url)

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="NOTICE_CLICK_FAILED",
                user_email=None,
                context={"event_id": event_id},
                message="Failed to track notice click",
                business_logs_collection=self.business_logs_collection,
                log_level="ERROR",
                error_details=str(e),
            )
            raise HTTPException(status_code=500, detail="Internal Server Error")
