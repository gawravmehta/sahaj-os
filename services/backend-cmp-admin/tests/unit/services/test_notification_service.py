import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone
from app.services.notification_service import NotificationService


@pytest.fixture
def mock_crud():
    return AsyncMock()


@pytest.fixture
def service(mock_crud):
    return NotificationService(crud=mock_crud)


@pytest.fixture
def sample_user():
    return {"_id": "u123", "email": "test@example.com"}


def sample_notification(user_id="u123"):
    return {
        "_id": "notif1",
        "notification_title": "Welcome",
        "notification_message": "Hello!",
        "redirection_route": "/home",
        "cta_url": "https://example.com",
        "file_url": "",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "priority": "high",
        "icon_url": "icon.png",
        "category": "general",
        "users": {
            user_id: {
                "is_read": False,
                "is_deleted": False,
            }
        },
    }


# ------------------------------------------------------------
# TEST: get_notifications
# ------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_notifications_success(service, mock_crud, sample_user):
    mock_crud.count_notifications.return_value = 2
    mock_crud.get_notifications.return_value = [
        sample_notification("u123"),
        sample_notification("u123")
    ]

    result = await service.get_notifications(sample_user, page=1, limit=10)

    assert result["total_notifications"] == 2
    assert len(result["data"]) == 2
    assert result["unseen_notification_count"] == mock_crud.count_notifications.return_value
    mock_crud.count_notifications.assert_awaited()
    mock_crud.get_notifications.assert_awaited()


@pytest.mark.asyncio
async def test_get_notifications_handles_deleted_status(service, mock_crud, sample_user):
    notif = sample_notification("u123")
    notif["users"]["u123"]["is_deleted"] = True

    mock_crud.count_notifications.return_value = 1
    mock_crud.get_notifications.return_value = [notif]

    result = await service.get_notifications(sample_user)

    assert result["data"][0]["is_deleted"] is True
    assert result["data"][0]["is_read"] is False


@pytest.mark.asyncio
async def test_get_notifications_error_raises_500(service, mock_crud, sample_user):
    mock_crud.count_notifications.side_effect = Exception("DB error")

    with pytest.raises(HTTPException) as exc:
        await service.get_notifications(sample_user)

    assert exc.value.status_code == 500
    assert "DB error" in exc.value.detail


# ------------------------------------------------------------
# TEST: mark_notification_as_read
# ------------------------------------------------------------

@pytest.mark.asyncio
async def test_mark_notification_as_read_success(service, mock_crud, sample_user):
    mock_crud.mark_as_read.return_value.modified_count = 1

    result = await service.mark_notification_as_read("notif1", sample_user)

    assert result == {"message": "Notification marked as read."}
    mock_crud.mark_as_read.assert_awaited_with("notif1", "u123")


@pytest.mark.asyncio
async def test_mark_notification_as_read_not_found(service, mock_crud, sample_user):
    mock_crud.mark_as_read.return_value.modified_count = 0

    with pytest.raises(HTTPException) as exc:
        await service.mark_notification_as_read("notif1", sample_user)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_mark_notification_as_read_internal_error(service, mock_crud, sample_user):
    mock_crud.mark_as_read.side_effect = Exception("DB crashed")

    with pytest.raises(HTTPException) as exc:
        await service.mark_notification_as_read("notif1", sample_user)

    assert exc.value.status_code == 500
    assert "DB crashed" in exc.value.detail


# ------------------------------------------------------------
# TEST: mark_all_notifications_as_read
# ------------------------------------------------------------

@pytest.mark.asyncio
async def test_mark_all_notifications_as_read_success(service, mock_crud, sample_user):
    mock_crud.mark_all_as_read.return_value.modified_count = 3

    result = await service.mark_all_notifications_as_read(sample_user)

    assert result == {"message": "3 notifications marked as read."}
    mock_crud.mark_all_as_read.assert_awaited_with("u123")


@pytest.mark.asyncio
async def test_mark_all_notifications_as_read_internal_error(service, mock_crud, sample_user):
    mock_crud.mark_all_as_read.side_effect = Exception("DB failure")

    with pytest.raises(HTTPException) as exc:
        await service.mark_all_notifications_as_read(sample_user)

    assert exc.value.status_code == 500
    assert "DB failure" in exc.value.detail
