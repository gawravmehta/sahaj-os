import csv
from typing import Literal
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.api.v1.deps import get_current_user, get_notice_notification_service

from app.db.dependencies import get_notice_notification_collection
from app.db.session import get_postgres_pool, get_s3_client
from app.schemas.notice_notification_schema import NoticeNotification
from app.services.notice_notification_service import NoticeNotificationService
from app.utils.common import convert_objectid_to_str

import io
import json
import xml.etree.ElementTree as ET
from datetime import datetime, UTC
import uuid
from pymongo.errors import PyMongoError
from minio import Minio
from minio.error import S3Error

router = APIRouter()


consent_notification_table = "consent_notifications"


@router.post("/send-notice")
async def send_notice(
    notice_notification: NoticeNotification,
    current_user: dict = Depends(get_current_user),
    service: NoticeNotificationService = Depends(get_notice_notification_service),
):
    return await service.send_notice(notice_notification, current_user)


@router.get("/get-all-notice-notifications")
async def get_notifications_overview(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    service: NoticeNotificationService = Depends(get_notice_notification_service),
):
    return await service.get_notifications_overview(page, limit, current_user)


@router.get("/track/{event_id}.png")
async def track_pixel(event_id: str, service: NoticeNotificationService = Depends(get_notice_notification_service)):
    try:
        return await service.track_pixel(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/click/{event_id}/{token}/{url_type}")
async def track_click(event_id: str, token: str, url_type: str, service: NoticeNotificationService = Depends(get_notice_notification_service)):
    try:
        return await service.track_click(event_id, token, url_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def export_notifications_to_minio(
    notice_notification_id: str,
    type: Literal["json", "csv", "xml"],
    current_user: dict,
    object_name: str,
    notice_notification_collection,
    pool,
    s3_client,
):
    """Background task to process and upload data to MinIO."""
    try:

        notice_notification_docs = await notice_notification_collection.find_one({"_id": ObjectId(notice_notification_id)})
        if not notice_notification_docs:
            raise ValueError("Campaign not found")
        notice_notifications = convert_objectid_to_str(notice_notification_docs)

        query = """
            SELECT *
            FROM consent_notifications
            WHERE notice_notification_id = $1
        """

        async with pool.acquire() as connection:
            rows = await connection.fetch(query, notice_notification_id)

        if not rows:
            raise ValueError("No notifications found for this campaign")

        notifications = []
        for row in rows:
            notification = dict(row)
            notification = convert_objectid_to_str(notification)
            if "notification_id" in notification:
                notification["notification_id"] = str(notification["notification_id"])
            if "created_at" in notification:
                notification["created_at"] = str(notification["created_at"])
            if "sent_at" in notification:
                notification["sent_at"] = str(notification["sent_at"])
            notifications.append(notification)

        buffer = io.BytesIO()

        if type == "json":
            content = json.dumps(notifications, indent=2).encode("utf-8")
            media_type = "application/json"

        elif type == "csv":
            text_buffer = io.StringIO()
            writer = csv.DictWriter(text_buffer, fieldnames=notifications[0].keys())
            writer.writeheader()
            writer.writerows(notifications)
            content = text_buffer.getvalue().encode("utf-8")
            media_type = "text/csv"

        elif type == "xml":
            root = ET.Element("notifications")
            for item in notifications:
                notif_elem = ET.SubElement(root, "notification")
                for key, value in item.items():
                    ET.SubElement(notif_elem, key).text = str(value)
            ET.ElementTree(root).write(buffer, encoding="utf-8", xml_declaration=True)
            content = buffer.getvalue()
            media_type = "application/xml"

        buffer = io.BytesIO(content)
        s3_client.put_object(
            "campaign-notifications",
            object_name,
            buffer,
            length=len(content),
            content_type=media_type,
        )

        await notice_notification_collection.update_one(
            {
                "_id": ObjectId(notice_notification_id),
                "exports.type": type,
                "exports.object_name": object_name,
                "exports.status": "pending",
            },
            {
                "$set": {
                    "exports.$.status": "completed",
                    "exports.$.completed_at": datetime.now(UTC),
                }
            },
        )

    except Exception as e:
        await notice_notification_collection.update_one(
            {
                "_id": ObjectId(notice_notification_id),
                "exports.type": type,
                "exports.object_name": object_name,
                "exports.status": "pending",
            },
            {
                "$set": {
                    "exports.$.status": "failed",
                    "exports.$.error": str(e),
                    "exports.$.completed_at": datetime.now(UTC),
                }
            },
        )
        raise HTTPException(status_code=500, detail=f"Background task failed: {str(e)}")


@router.post("/trigger-download-notifications/{notice_notification_id}")
async def trigger_export(
    notice_notification_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    type: Literal["json", "csv", "xml"] = "json",
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_postgres_pool),
    notice_notification_collection=Depends(get_notice_notification_collection),
    s3_client: Minio = Depends(get_s3_client),
):
    """Trigger export as a background task and respond immediately."""
    try:
        user_id = current_user.get("_id")
        df_id = current_user.get("df_id")

        campaign = await notice_notification_collection.find_one({"_id": ObjectId(notice_notification_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if campaign.get("notification_status") not in ["fetched_dp", "completed"]:
            raise HTTPException(status_code=400, detail="Invalid notification status")

        object_name = f"campaigns/{notice_notification_id}/notifications_{uuid.uuid4()}.{type}"

        await notice_notification_collection.update_one(
            {"_id": ObjectId(notice_notification_id)},
            {
                "$push": {
                    "exports": {
                        "type": type,
                        "object_name": object_name,
                        "created_at": datetime.now(UTC),
                        "status": "pending",
                    }
                }
            },
        )

        background_tasks.add_task(
            export_notifications_to_minio,
            notice_notification_id=notice_notification_id,
            type=type,
            current_user=current_user,
            object_name=object_name,
            notice_notification_collection=notice_notification_collection,
            pool=pool,
            s3_client=s3_client,
        )

        return {
            "message": "Export started in the background",
            "status": "processing",
            "notice_notification_id": notice_notification_id,
            "format": type,
        }

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/download-campaign-notifications/{notice_notification_id}")
async def download_campaign_notifications(
    notice_notification_id: str,
    request: Request,
    object_name: str = None,
    type: Literal["json", "csv", "xml"] = "json",
    current_user: dict = Depends(get_current_user),
    notice_notification_collection=Depends(get_notice_notification_collection),
    s3_client: Minio = Depends(get_s3_client),
):
    try:

        user_id = str(current_user.get("_id"))
        df_id = current_user.get("df_id")
        campaign = await notice_notification_collection.find_one({"_id": ObjectId(notice_notification_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if not object_name:
            raise HTTPException(status_code=400, detail="Export object name not provided")

        content_type = {
            "json": "application/json",
            "csv": "text/csv",
            "xml": "application/xml",
        }.get(type, "application/octet-stream")

        response = s3_client.get_object("campaign-notifications", object_name)

        return StreamingResponse(
            response.stream(32 * 1024),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={object_name}",
                "Content-Type": content_type,
            },
        )

    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="File not found in MinIO")
        raise HTTPException(status_code=500, detail=f"MinIO error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-downloadable-notifications/{notice_notification_id}")
async def get_downloadable_notifications(
    notice_notification_id: str,
    type: Literal["json", "csv", "xml"] = "json",
    current_user: dict = Depends(get_current_user),
    notice_notification_collection=Depends(get_notice_notification_collection),
):
    try:

        campaign = await notice_notification_collection.find_one({"_id": ObjectId(notice_notification_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        data_to_return = []
        for export in campaign.get("exports", []):
            if export["type"] == type:
                data_to_return.append(
                    {
                        "object_name": export["object_name"],
                        "status": export["status"],
                        "created_at": str(export["created_at"]),
                    }
                )

        if not data_to_return:
            raise HTTPException(
                status_code=404,
                detail=f"No {type.upper()} exports found for this campaign",
            )

        return {
            "notice_notification_id": notice_notification_id,
            "exports": data_to_return,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-export/{notice_notification_id}")
async def delete_export(
    notice_notification_id: str,
    object_name: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    s3_client: Minio = Depends(get_s3_client),
    notice_notification_collection=Depends(get_notice_notification_collection),
):
    try:
        user_id = str(current_user.get("_id"))
        df_id = current_user.get("df_id")

        campaign = await notice_notification_collection.find_one({"_id": ObjectId(notice_notification_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        export = next(
            (export for export in campaign.get("exports", []) if export["object_name"] == object_name),
            None,
        )
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")

        s3_client.remove_object("campaign-notifications", object_name)

        await notice_notification_collection.update_one(
            {"_id": ObjectId(notice_notification_id)},
            {"$pull": {"exports": {"object_name": object_name}}},
        )

        return {"message": "Export deleted successfully"}

    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="File not found in MinIO")
        raise HTTPException(status_code=500, detail=f"MinIO error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
