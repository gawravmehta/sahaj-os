import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, ANY
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, UTC

# Assuming 'app.main' and dependencies are correctly configured
from app.main import app 
from app.api.v1.deps import get_current_user, get_data_fiduciary_service

# Import the router-specific schema for the test body
# Since the schemas were provided in the prompt, we redefine them here for context
# In a real project, we would import them from app.schemas.data_fiduciary_schema

# --- Redefining necessary Schemas for Test Context ---
# (Using simplified definitions since full Pydantic models are complex)

class UpdateDataFiduciary(BaseModel):
    # Just need one field to make a valid body
    org_info: Optional[Dict] = None

# --- End Schema Redefinition ---


client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/data-fiduciary"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_update_payload():
    return UpdateDataFiduciary(org_info={"name": "NewOrg"})


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.setup = AsyncMock()
    service.get_details = AsyncMock()
    service.get_sms_templates = AsyncMock()
    service.get_in_app_notification_templates = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_data_fiduciary_service] = lambda: mock_service
    
    yield
    app.dependency_overrides = {}


# ---------------- 1. TEST POST /setup-data-fiduciary ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"message": "Setup complete"}, status.HTTP_200_OK),
        # Expected failure from within the service layer (e.g., DF not found or validation)
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DF not found"), None, status.HTTP_404_NOT_FOUND),
        # Unexpected error caught by generic 'except Exception' block
        (Exception("Database error"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_setup_data_fiduciary(mock_service, mock_update_payload, side_effect, return_value, expected_status):
    mock_service.setup.side_effect = side_effect
    mock_service.setup.return_value = return_value

    res = client.post(
        f"{BASE_URL}/setup-data-fiduciary", 
        json=mock_update_payload.model_dump(by_alias=True, exclude_none=True)
    )

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["message"] == "Setup complete"
        mock_service.setup.assert_called_once()
        # Ensure service is called with the correct df_id, payload, and user
        mock_service.setup.assert_called_once_with("df123", ANY, ANY)

    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Database error" in res.json()["detail"]


def test_setup_data_fiduciary_validation_error():
    # Send invalid data to trigger Pydantic validation error (422)
    res = client.post(f"{BASE_URL}/setup-data-fiduciary", json={"org_info": 123})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 2. TEST GET /data-fiduciary-details ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"df_id": "df123", "org_info": {"name": "TestCorp"}}, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (Exception("Network timeout"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_data_fiduciary_details(mock_service, side_effect, return_value, expected_status):
    mock_service.get_details.side_effect = side_effect
    mock_service.get_details.return_value = return_value

    res = client.get(f"{BASE_URL}/data-fiduciary-details")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["df_id"] == "df123"
        mock_service.get_details.assert_called_once_with("df123", ANY)

    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Network timeout" in res.json()["detail"]


# ---------------- 3. TEST GET /get-all-sms-templates ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"name": "OTP", "content": "Your OTP is {code}"}], status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_401_UNAUTHORIZED), None, status.HTTP_401_UNAUTHORIZED),
        (Exception("Config missing"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_sms_templates(mock_service, side_effect, return_value, expected_status):
    mock_service.get_sms_templates.side_effect = side_effect
    mock_service.get_sms_templates.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-sms-templates")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        mock_service.get_sms_templates.assert_called_once_with("df123", ANY)

    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Config missing" in res.json()["detail"]


# ---------------- 4. TEST GET /get-all-in-app-notification-templates ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"name": "Welcome", "content": "Welcome to the app!"}], status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_403_FORBIDDEN), None, status.HTTP_403_FORBIDDEN),
        (Exception("Template parsing error"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_in_app_notification_templates(mock_service, side_effect, return_value, expected_status):
    mock_service.get_in_app_notification_templates.side_effect = side_effect
    mock_service.get_in_app_notification_templates.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-in-app-notification-templates")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        assert res.json()[0]["name"] == "Welcome"
        mock_service.get_in_app_notification_templates.assert_called_once_with("df123", ANY)

    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Template parsing error" in res.json()["detail"]