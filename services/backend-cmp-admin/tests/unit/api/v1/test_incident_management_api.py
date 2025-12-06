import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, ANY
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

# Assuming 'app.main' and dependencies are correctly configured
from app.main import app 
from app.api.v1.deps import get_current_user, get_incident_service

client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/incidents"

# --- Simplified Schemas for Test Context (Only structure needed) ---
# Note: For real tests, these would be imported from the schema file.

class Step(BaseModel):
    step_name: str
    step_description: str

class WorkflowStage(BaseModel):
    stage_name: str
    steps: List[Step] = []

class IncidentCreate(BaseModel):
    incident_name: str = "Test Breach"
    incident_type: str = "Security"
    incident_sensitivity: Literal["low", "medium", "high"] = "high"
    description: str = "A test incident description."
    status: Optional[Literal["draft", "published", "in_progress", "closed"]] = "draft"
    current_stage: str = "Triage"
    workflow: List[WorkflowStage] = Field(default_factory=lambda: [WorkflowStage(stage_name="Triage")])
    
    # We will skip complex validators in the test file for brevity, 
    # focusing only on the structure needed for the API endpoint.

class AddStepRequest(BaseModel):
    stage_name: str = "Triage"
    step: Step = Field(default_factory=lambda: Step(step_name="Investigate", step_description="Check logs."))

class UpdateStageRequest(BaseModel):
    new_stage: str = "Remediation"
# -------------------------------------------------------------------


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "admin@example.com", "df_id": "df123"}


@pytest.fixture
def mock_incident_id():
    return "inc_12345"


def incident_response(**kwargs):
    """Return a dictionary representing a successful incident object."""
    base = {
        "_id": "inc_12345",
        "incident_name": "Test Incident",
        "status": "draft",
        "current_stage": "Triage",
        "df_id": "df123",
    }
    base.update(kwargs)
    return base


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_or_update_incident = AsyncMock()
    service.list_incidents = AsyncMock()
    service.get_incident = AsyncMock()
    service.publish_incident = AsyncMock()
    service.move_to_next_stage = AsyncMock()
    service.add_step_to_stage = AsyncMock()
    service.update_stage_manually = AsyncMock()
    service.send_incident_notifications = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_incident_service] = lambda: mock_service
    
    yield
    app.dependency_overrides = {}


# ---------------- 1. TEST POST /create-or-update ---------------- #


@pytest.mark.parametrize(
    "incident_id, side_effect, expected_status",
    [
        (None, None, status.HTTP_200_OK),  # Create
        ("inc_12345", None, status.HTTP_200_OK),  # Update
        (None, HTTPException(status_code=status.HTTP_400_BAD_REQUEST), status.HTTP_400_BAD_REQUEST),
    ],
)
def test_create_or_update_incident(mock_service, mock_user, incident_id, side_effect, expected_status):
    mock_service.create_or_update_incident.side_effect = side_effect
    mock_service.create_or_update_incident.return_value = incident_response()

    payload = IncidentCreate().model_dump(by_alias=True, exclude_none=True)
    
    url = f"{BASE_URL}/create-or-update"
    if incident_id:
        url += f"?incident_id={incident_id}"

    res = client.post(url, json=payload)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        mock_service.create_or_update_incident.assert_called_once_with(ANY, mock_user, incident_id)


# ---------------- 2. TEST GET /get-all-incidents ---------------- #


@pytest.mark.parametrize(
    "query_params, side_effect, expected_status",
    [
        ({}, None, status.HTTP_200_OK), # Default success
        ({"incident_sensitivity": "high", "sort_order": "asc"}, None, status.HTTP_200_OK), # Filtered
        ({"page": 2, "page_size": 50}, None, status.HTTP_200_OK), # Paged
        ({"status": "published"}, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED), status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_list_incidents_success(mock_service, mock_user, query_params, side_effect, expected_status):
    mock_service.list_incidents.side_effect = side_effect
    mock_service.list_incidents.return_value = {"incidents": [incident_response()], "total": 1}

    res = client.get(f"{BASE_URL}/get-all-incidents", params=query_params)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        mock_service.list_incidents.assert_called_once()
        # Check if the service was called with the right defaults/overrides
        call_kwargs = mock_service.list_incidents.call_args[1]
        
        # Check defaults if not provided in query_params
        assert call_kwargs.get("sort_order") == query_params.get("sort_order", "desc")
        assert call_kwargs.get("page") == query_params.get("page", 1)
        assert call_kwargs.get("current_user") == mock_user

def test_list_incidents_validation_failure():
    # Test case 1: invalid literal for incident_sensitivity
    res = client.get(f"{BASE_URL}/get-all-incidents", params={"incident_sensitivity": "very_high"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test case 2: page_size too large
    res = client.get(f"{BASE_URL}/get-all-incidents", params={"page_size": 101})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 3. TEST GET /get-incidents/{incident_id} ---------------- #


@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), status.HTTP_404_NOT_FOUND),
    ],
)
def test_get_incident(mock_service, mock_incident_id, side_effect, expected_status):
    mock_service.get_incident.side_effect = side_effect
    mock_service.get_incident.return_value = incident_response()

    res = client.get(f"{BASE_URL}/get-incidents/{mock_incident_id}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        mock_service.get_incident.assert_called_once_with(mock_incident_id, ANY)


# ---------------- 4. TEST POST /{incident_id}/publish ---------------- #


def test_publish_incident(mock_service, mock_incident_id):
    mock_service.publish_incident.return_value = incident_response(status="published")
    
    res = client.post(f"{BASE_URL}/{mock_incident_id}/publish")

    assert res.status_code == status.HTTP_200_OK
    assert res.json()["status"] == "published"
    mock_service.publish_incident.assert_called_once_with(mock_incident_id, ANY)


# ---------------- 5. TEST POST /{incident_id}/move-to-next-stage ---------------- #


def test_move_to_next_stage(mock_service, mock_incident_id):
    mock_service.move_to_next_stage.return_value = incident_response(current_stage="Remediation")
    
    res = client.post(f"{BASE_URL}/{mock_incident_id}/move-to-next-stage")

    assert res.status_code == status.HTTP_200_OK
    assert res.json()["current_stage"] == "Remediation"
    mock_service.move_to_next_stage.assert_called_once_with(mock_incident_id, ANY)


# ---------------- 6. TEST POST /{incident_id}/add-step ---------------- #


def test_add_step_to_stage(mock_service, mock_incident_id):
    mock_service.add_step_to_stage.return_value = incident_response()
    payload = AddStepRequest().model_dump(by_alias=True)
    
    res = client.post(f"{BASE_URL}/{mock_incident_id}/add-step", json=payload)

    assert res.status_code == status.HTTP_200_OK
    mock_service.add_step_to_stage.assert_called_once_with(mock_incident_id, ANY, ANY)


# ---------------- 7. TEST POST /{incident_id}/update-stage ---------------- #


def test_update_stage_manually(mock_service, mock_incident_id):
    mock_service.update_stage_manually.return_value = incident_response(current_stage="Post-Mortem")
    payload = UpdateStageRequest().model_dump(by_alias=True)
    
    res = client.post(f"{BASE_URL}/{mock_incident_id}/update-stage", json=payload)

    assert res.status_code == status.HTTP_200_OK
    assert res.json()["current_stage"] == "Post-Mortem"
    mock_service.update_stage_manually.assert_called_once_with(mock_incident_id, ANY, ANY)


# ---------------- 8. TEST POST /send-notification/{incident_id} ---------------- #


def test_send_incident_notification(mock_service, mock_incident_id):
    mock_service.send_incident_notifications.return_value = {"message": "Notification sent successfully"}
    
    res = client.post(f"{BASE_URL}/send-notification/{mock_incident_id}")

    assert res.status_code == status.HTTP_200_OK
    assert "successfully" in res.json()["message"]
    mock_service.send_incident_notifications.assert_called_once_with(mock_incident_id, ANY)