import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_notification_service

client = TestClient(app)
BASE_URL = "/api/v1/notifications"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_notifications = AsyncMock()
    service.mark_notification_as_read = AsyncMock()
    service.mark_all_notifications_as_read = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_notification_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST GET NOTIFICATIONS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"notifications": [], "total": 0}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_notifications(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_notifications.side_effect = side_effect
    mock_service.get_notifications.return_value = return_value

    res = client.get(f"{BASE_URL}/notifications")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.get_notifications.assert_called_once_with(mock_user, 1, 10)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_get_notifications_invalid_query():
    res = client.get(f"{BASE_URL}/notifications?page=0")
    assert res.status_code == 422


# ---------------- TEST MARK NOTIFICATION AS READ ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"message": "Notification marked as read"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_mark_notification_as_read(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.mark_notification_as_read.side_effect = side_effect
    mock_service.mark_notification_as_read.return_value = return_value

    notification_id = "notif123"
    res = client.patch(f"{BASE_URL}/read-notification/{notification_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.mark_notification_as_read.assert_called_once_with(notification_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST MARK ALL NOTIFICATIONS AS READ ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"message": "All notifications marked as read"}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_mark_all_notifications_as_read(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.mark_all_notifications_as_read.side_effect = side_effect
    mock_service.mark_all_notifications_as_read.return_value = return_value

    res = client.get(f"{BASE_URL}/mark-all-read")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.mark_all_notifications_as_read.assert_called_once_with(mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST ENDPOINTS ---------------- #
