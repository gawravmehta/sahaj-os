import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_consent_artifact_service

client = TestClient(app)
BASE_URL = "/api/v1/consent-artifact"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_all_consent_artifact = AsyncMock()
    service.download_consent_artifact = AsyncMock()
    service.get_consent_artifact_by_id = AsyncMock()
    service.get_expiring_consents = AsyncMock()
    service.process_df_ack = AsyncMock()  # Add mock for process_df_ack
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_consent_artifact_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST GET ALL CONSENT ARTIFACTS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"data": [], "total_pages": 0, "current_page": 1, "total_items": 0, "available_filters": {}}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_all_consent_artifact(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_all_consent_artifact.side_effect = side_effect
    mock_service.get_all_consent_artifact.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-consent-artifact")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.get_all_consent_artifact.assert_called_once_with(1, 10, None, None, None, None, "desc", None, None, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_get_all_consent_artifact_invalid_query():
    # Attempt to send an invalid query parameter to trigger a validation error (422)
    # For example, 'page' parameter must be >= 1, so 'page=0' is invalid.
    res = client.get(f"{BASE_URL}/get-all-consent-artifact?page=0")
    assert res.status_code == 422


# ---------------- TEST DOWNLOAD CONSENT ARTIFACT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, "csv_data_here", 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_download_consent_artifact(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.download_consent_artifact.side_effect = side_effect
    mock_service.download_consent_artifact.return_value = return_value

    res = client.get(f"{BASE_URL}/export-csv")

    assert res.status_code == expected_status
    if expected_status == 200:
        mock_service.download_consent_artifact.assert_called_once_with(None, None, None, None, "desc", None, None, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST GET CONSENT ARTIFACT BY ID ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"consent_artifact_id": "ca123"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_consent_artifact_by_id(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_consent_artifact_by_id.side_effect = side_effect
    mock_service.get_consent_artifact_by_id.return_value = return_value

    consent_artifact_id = "ca123"
    res = client.get(f"{BASE_URL}/get-consent-artifact-by-id?id={consent_artifact_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.get_consent_artifact_by_id.assert_called_once_with(consent_artifact_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST GET EXPIRING CONSENTS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [], 200),
        (HTTPException(status_code=404, detail="User Not Found"), None, 404),
        (HTTPException(status_code=500, detail="Internal Server Error"), None, 500),
    ],
)
def test_get_expiring_consents(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_expiring_consents.side_effect = side_effect
    mock_service.get_expiring_consents.return_value = return_value

    res = client.get(f"{BASE_URL}/get-expiring-consents")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == return_value
        mock_service.get_expiring_consents.assert_called_once_with(mock_user["df_id"], None, None)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_get_expiring_consents_invalid_query():
    res = client.get(f"{BASE_URL}/get-expiring-consents?days_to_expire=invalid")
    assert res.status_code == 422


# ---------------- TEST CONSENT ACK ---------------- #


import hmac
import hashlib
from datetime import datetime, timezone, timedelta
import json


# Mock the actual verify_signature function from the endpoint
def mock_verify_signature(payload: dict, signature: str, CMP_WEBHOOK_SECRET: str) -> bool:
    if signature == "valid_signature":
        return True
    return False


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, ack_payload, signature, headers, has_secret",
    [
        (None, {"status": "received", "forwarded": True, "ack_id": "mock_ack_id"}, 200, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Processing halted as requested",
        }, "valid_signature", {"X-DF-Signature": "valid_signature"}, True),
        (HTTPException(status_code=401, detail="Missing X-DF-Signature header"), None, 401, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Processing halted as requested",
        }, None, {}, True),
        (HTTPException(status_code=401, detail="Invalid signature"), None, 401, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Processing halted as requested",
        }, "invalid_signature", {"X-DF-Signature": "invalid_signature"}, True),
        (HTTPException(status_code=400, detail="Request expired"), None, 400, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(), # Expired timestamp
            "message": "Processing halted as requested",
        }, "valid_signature", {"X-DF-Signature": "valid_signature"}, True),
        (HTTPException(status_code=400, detail="Invalid timestamp format"), None, 400, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": "invalid-timestamp",
            "message": "Processing halted as requested",
        }, "valid_signature", {"X-DF-Signature": "valid_signature"}, True),
        (HTTPException(status_code=500, detail="Server error processing acknowledgment"), None, 500, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Processing halted as requested",
        }, "valid_signature", {"X-DF-Signature": "valid_signature"}, True),
        (HTTPException(status_code=500, detail="Server error processing acknowledgment"), None, 500, {
            "dp_id": "dp123",
            "df_id": "df123",
            "de_id": "de1",
            "purpose_id": "p1",
            "original_event_type": "consent_revoked",
            "ack_status": "HALTED",
            "ack_timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Processing halted as requested",
        }, "valid_signature", {"X-DF-Signature": "valid_signature"}, False), # No secret found
    ],
)
async def test_consent_ack(
    mock_service,
    mock_user,
    side_effect,
    return_value,
    expected_status,
    ack_payload,
    signature,
    headers,
    has_secret,
    monkeypatch,
):
    mock_service.process_df_ack.side_effect = side_effect
    mock_service.process_df_ack.return_value = return_value

    # Mock the verify_signature function from the endpoint module
    monkeypatch.setattr("app.api.v1.endpoints.consent_artifact.verify_signature", mock_verify_signature)
    
    # Mock df_keys_collection.find_one to return a secret or None
    async def mock_find_one(*args, **kwargs):
        return {"cmp_webhook_secret": "test_secret"} if has_secret else None

    mock_df_keys_collection = MagicMock(find_one=AsyncMock(side_effect=mock_find_one))
    monkeypatch.setattr(
        "app.db.dependencies.get_df_keys_collection",
        lambda: mock_df_keys_collection,
    )

    # Mock get_df_ack_collection, get_customer_notifications_collection, get_consent_artifact_collection
    mock_df_ack_collection = MagicMock(insert_one=AsyncMock(return_value=MagicMock(inserted_id="mock_ack_id")))
    mock_customer_notifications_collection = MagicMock(insert_one=AsyncMock())
    mock_consent_artifact_collection = MagicMock(find_one=AsyncMock(return_value={"_id": "ca123", "artifact": {"cp_name": "test_cp", "consent_scope": {"data_elements": [{"de_id": "de1", "title": "Test Data Element", "consents": [{"purpose_id": "p1", "purpose_title": "Test Purpose"}]}]}}}))

    monkeypatch.setattr("app.db.dependencies.get_df_ack_collection", lambda: mock_df_ack_collection)
    monkeypatch.setattr("app.db.dependencies.get_customer_notifications_collection", lambda: mock_customer_notifications_collection)
    monkeypatch.setattr("app.db.dependencies.get_consent_artifact_collection", lambda: mock_consent_artifact_collection)


    res = client.post(f"{BASE_URL}/consent-ack", json=ack_payload, headers=headers)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["status"] == "received"
        assert res.json()["ack_id"] == "mock_ack_id"
        mock_service.process_df_ack.assert_called_once()
    elif expected_status == 500 and "Internal Server Error" in str(side_effect): # For generic exceptions
        assert res.json()["detail"] == "Server error processing acknowledgment"
    else:
        assert "detail" in res.json()


# ---------------- End of Tests ---------------- #
