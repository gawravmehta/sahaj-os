import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_consent_audit_service

client = TestClient(app)
BASE_URL = "/api/v1/consent_audit"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_dp_audit_history = AsyncMock()
    service.get_dp_audit_history_internal = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_consent_audit_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST GET DP AUDIT HISTORY ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"id": "log1", "event": "consent_given"}], 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_dp_audit_history(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_dp_audit_history.side_effect = side_effect
    mock_service.get_dp_audit_history.return_value = return_value

    dp_id = "dp123"
    res = client.get(f"{BASE_URL}/consents/{dp_id}/audit")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["dp_id"] == dp_id
        assert res.json()["df_id"] == mock_user["df_id"]
        assert len(res.json()["logs"]) == 1
        mock_service.get_dp_audit_history.assert_called_once_with(dp_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST GET DP AUDIT HISTORY INTERNAL ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"id": "log2", "event": "consent_withdrawn"}], 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_dp_audit_history_internal(mock_service, side_effect, return_value, expected_status):
    mock_service.get_dp_audit_history_internal.side_effect = side_effect
    mock_service.get_dp_audit_history_internal.return_value = return_value

    dp_id = "dp456"
    df_id = "df456"
    res = client.get(f"{BASE_URL}/consent-timeline/{dp_id}/audit?df_id={df_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["dp_id"] == dp_id
        assert res.json()["df_id"] == df_id
        assert len(res.json()["logs"]) == 1
        mock_service.get_dp_audit_history_internal.assert_called_once_with(dp_id, df_id)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()
