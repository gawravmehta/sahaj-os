import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone


from app.main import app
from app.api.v1.deps import get_current_user, get_webhooks_service

client = TestClient(app)
BASE_URL = "/api/v1/webhooks"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_webhook = AsyncMock()
    service.list_paginated_webhooks = AsyncMock()
    service.get_webhook = AsyncMock()
    service.update_webhook = AsyncMock()
    service.delete_webhook = AsyncMock()
    service.test_webhook = AsyncMock()
    return service


def webhook_response_data():
    return {
        "_id": "wh123",
        "webhook_id": "wh123",
        "url": "https://example.com/webhook",
        "subscribed_events": ["consent_given", "consent_revoked"],
        "webhook_for": "df",
        "environment": "testing",
        "df_id": "df123",
        "status": "active",
        "auth": {
            "type": "none",
            "key": "X-Consent-Signature",
            "secret": None
        },
        "retry_policy": {
            "max_retries": 3,
            "retry_interval_sec": 10,
            "backoff_strategy": "exponential"
        },
        "metrics": {
            "delivered": 0,
            "failed": 0,
            "last_success": None,
            "last_failure": None
        },
        "created_by": "u1",
        "updated_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_webhooks_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST CREATE WEBHOOK ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, webhook_data",
    [
        (None, {"webhook_id": "wh123", "message": "Webhook created successfully"}, 201, {"url": "https://example.com/webhook", "webhook_for": "df", "environment": "testing"}),
        (HTTPException(status_code=400, detail="bad request"), None, 400, {"url": "https://example.com/webhook", "webhook_for": "df", "environment": "testing"}),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500, {"url": "https://example.com/webhook", "webhook_for": "df", "environment": "testing"}),
    ],
)
def test_create_webhook(mock_service, mock_user, side_effect, return_value, expected_status, webhook_data):
    mock_service.create_webhook.side_effect = side_effect
    mock_service.create_webhook.return_value = return_value

    res = client.post(f"{BASE_URL}/create-webhook", json=webhook_data)

    assert res.status_code == expected_status
    if expected_status == 201:
        assert res.json()["message"] == "Webhook created successfully"
        mock_service.create_webhook.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_create_webhook_validation_error():
    res = client.post(f"{BASE_URL}/create-webhook", json={"url": "invalid-url", "webhook_for": "df"})
    assert res.status_code == 422


# ---------------- TEST GET ALL WEBHOOKS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"current_page": 1, "data_per_page": 20, "total_items": 0, "total_pages": 0, "webhooks": []}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_all_webhooks(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.list_paginated_webhooks.side_effect = side_effect
    mock_service.list_paginated_webhooks.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-webhooks")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.list_paginated_webhooks.assert_called_once_with(mock_user, 1, 20)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_get_all_webhooks_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-webhooks?current_page=0")
    assert res.status_code == 422


# ---------------- TEST GET ONE WEBHOOK BY ID ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, webhook_response_data(), 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_one_webhook(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_webhook.side_effect = side_effect
    mock_service.get_webhook.return_value = return_value

    webhook_id = "wh123"
    res = client.get(f"{BASE_URL}/get-one-webhook/{webhook_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["webhook_id"] == "wh123"
        assert res.json()["url"] == return_value["url"]
        assert res.json()["df_id"] == return_value["df_id"]
        mock_service.get_webhook.assert_called_once_with(webhook_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST UPDATE WEBHOOK ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, update_data",
    [
        (None, webhook_response_data(), 200, {"url": "https://updated.com/webhook"}),
        (HTTPException(status_code=404, detail="not found"), None, 404, {"url": "https://updated.com/webhook"}),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500, {"url": "https://updated.com/webhook"}),
    ],
)
def test_update_webhook(mock_service, mock_user, side_effect, return_value, expected_status, update_data):
    mock_service.update_webhook.side_effect = side_effect
    mock_service.update_webhook.return_value = return_value

    webhook_id = "wh123"
    res = client.put(f"{BASE_URL}/update-webhook/{webhook_id}", json=update_data)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["webhook_id"] == "wh123"
        assert res.json()["url"] == return_value["url"]
        mock_service.update_webhook.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_update_webhook_validation_error():
    res = client.put(f"{BASE_URL}/update-webhook/wh123", json={"url": "invalid-url"})
    assert res.status_code == 422


# ---------------- TEST DELETE WEBHOOK ---------------- #


@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, 204),
        (HTTPException(status_code=404, detail="not found"), 404),
        (HTTPException(status_code=500, detail="Internal Server Error"), 500),
    ],
)
def test_delete_webhook(mock_service, mock_user, side_effect, expected_status):
    mock_service.delete_webhook.side_effect = side_effect

    webhook_id = "wh123"
    res = client.delete(f"{BASE_URL}/delete-webhook/{webhook_id}")

    assert res.status_code == expected_status
    if expected_status == 204:
        mock_service.delete_webhook.assert_called_once_with(webhook_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- End of Tests ---------------- #
