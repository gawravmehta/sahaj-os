import asyncio
import json
from jose import jwt
from fastapi import APIRouter, Depends, Query
from app.core.config import settings
from app.api.v1.deps import get_current_user, get_notification_service
from app.core.notifier import notifier
from app.services.notification_service import NotificationService
from sse_starlette.sse import EventSourceResponse
from fastapi import Request, Depends, HTTPException, status

router = APIRouter()


@router.get("/notifications")
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_notifications(current_user, page, limit)


@router.patch("/read-notification/{notification_id}")
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.mark_notification_as_read(notification_id, current_user)


@router.get("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.mark_all_notifications_as_read(current_user)




@router.get("/notifications/stream")
async def stream_notifications(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ")[1]
    try:
        current_user = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")


    async def event_generator(user_id: str):
        queue = await notifier.connect(user_id)
        try:
            while True:
                data = await queue.get()
                yield {
                    "event": "new_notification",
                    "id": str(data["_id"]),
                    "data": json.dumps(data),
                }
        except asyncio.CancelledError:
            notifier.disconnect(user_id, queue)
            raise

    return EventSourceResponse(event_generator(user_id))