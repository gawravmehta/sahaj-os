from bson import ObjectId
from typing import List, Optional
from datetime import datetime, UTC, timedelta, timezone
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.notifier import notifier

from app.db.dependencies import get_df_register_collection, get_notifications_collection, get_user_collection


async def create_user_notification(
    df_id: Optional[str],
    users_list: Optional[List[str]],
    notification_title: Optional[str],
    notification_message: Optional[str] = None,
    redirection_route: Optional[str] = None,
    cta_url: Optional[str] = None,
    file_url: Optional[str] = None,
    priority: Optional[str] = "normal",
    icon_url: Optional[str] = None,
    category: Optional[str] = None,
    df_register_collection: AsyncIOMotorCollection = Depends(get_df_register_collection),
    user_collection: AsyncIOMotorCollection = Depends(get_user_collection),
    notification_collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
):
    """
    Creates a notification document in the database.

    Args:
        df_id (str): The ID of the data fiduciary (mandatory).
        users_list (List[str]): List of user IDs (mandatory, at least one user).
        notification_title (str): Title of the notification.
        notification_message (str): Message content of the notification.
        redirection_route (str): Route to redirect the user when the notification is clicked.
        cta_url (str): Call-to-action URL for the notification.
        file_url (str): URL of any associated file.
        priority (str): Priority of the notification (default: "normal").
        icon_url (str): URL of the notification icon (optional).
        category (str): Category of the notification (optional).

    Returns:
        dict: The created notification document.
    """

    df_checker = await df_register_collection.find_one({"df_id": df_id})
    if not df_checker:
        raise ValueError("df_id is mandatory")
    if not users_list or len(users_list) == 0:
        raise ValueError("users_list must contain at least one user ID")

    for user_id in users_list:
        user_checker = await user_collection.find_one({"_id": ObjectId(user_id)})
        if not user_checker:
            raise ValueError(f"Invalid user ID: {user_id}")

    users_status = {user_id: {"is_read": False, "is_deleted": False} for user_id in users_list}

    notification_doc = {
        "df_id": df_id,
        "users": users_status,
        "notification_title": notification_title,
        "notification_message": notification_message,
        "redirection_route": redirection_route,
        "cta_url": cta_url,
        "file_url": file_url,
        "priority": priority,
        "icon_url": icon_url,
        "category": category,
        "created_at": datetime.now(timezone.utc),
    }

    for uid in users_list:
        await notifier.push(uid, notification_doc)

    try:
        await notification_collection.insert_one(notification_doc)
    except Exception as e:
        raise Exception(f"Failed to create notification: {str(e)}")
