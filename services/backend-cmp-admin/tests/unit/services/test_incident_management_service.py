import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from datetime import datetime, UTC
from bson import ObjectId

from app.services.incident_management_service import IncidentService
from app.crud.incident_management_crud import IncidentCRUD
from app.services.data_principal_service import DataPrincipalService

# FIXED IMPORTS → use WorkflowStage + Step
from app.schemas.incident_management_schema import (
    IncidentCreate,
    AddStepRequest,
    UpdateStageRequest,
    WorkflowStage,
    Step,
)


# -----------------------
# FIXTURES
# -----------------------


@pytest.fixture
def mock_incident_crud():
    return AsyncMock(spec=IncidentCRUD)


@pytest.fixture
def mock_user_collection():
    return AsyncMock()


@pytest.fixture
def mock_data_principal_service():
    return AsyncMock(spec=DataPrincipalService)


@pytest.fixture
def mock_customer_notifications_collection():
    mock = AsyncMock()
    mock.find_one = AsyncMock()
    mock.insert_many = AsyncMock()
    return mock


@pytest.fixture
def service(mock_incident_crud, mock_user_collection, mock_data_principal_service, mock_customer_notifications_collection):
    return IncidentService(
        mock_incident_crud,
        mock_user_collection,
        "test_business_logs",
        mock_data_principal_service,
        mock_customer_notifications_collection,
    )


@pytest.fixture
def mock_user():
    return {"_id": "user123", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_incident_create_data():
    return IncidentCreate(
        incident_name="Test Incident",
        incident_type="Data Breach",
        incident_sensitivity="high",
        description="A test incident",
        current_stage="Identification",
        workflow=[
            WorkflowStage(
                stage_name="Identification",
                steps=[Step(step_name="Identify", step_description="Identify breach")],
            ),
            WorkflowStage(stage_name="Containment", steps=[]),
        ],
        date_occurred=datetime.now(UTC),
        date_discovered=datetime.now(UTC),
        deadline=datetime.now(UTC),
    )


# -----------------------
# TESTS
# -----------------------


@pytest.mark.asyncio
async def test_create_incident_success(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    mock_incident_crud.find_duplicate.return_value = None
    mock_incident_crud.insert_incident.return_value = str(ObjectId())

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.create_or_update_incident(mock_incident_create_data, mock_user)

    mock_incident_crud.find_duplicate.assert_called_once()
    mock_incident_crud.insert_incident.assert_called_once()
    mock_log.assert_called_once()
    assert "incident_id" in result


@pytest.mark.asyncio
async def test_create_incident_duplicate_name(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    mock_incident_crud.find_duplicate.return_value = {"_id": ObjectId()}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    with pytest.raises(HTTPException):
        await service.create_or_update_incident(mock_incident_create_data, mock_user)

    mock_incident_crud.insert_incident.assert_not_called()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_incident_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {"_id": ObjectId(incident_id), "df_id": mock_user["df_id"]}
    mock_incident_crud.update_incident.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    update_data = IncidentCreate(
        incident_name="Updated Incident",
        incident_type="Data Breach",
        incident_sensitivity="high",
        description="Updated",
        current_stage="Identification",
        workflow=[WorkflowStage(stage_name="Identification", steps=[])],
    )

    result = await service.create_or_update_incident(update_data, mock_user, incident_id)

    mock_incident_crud.update_incident.assert_called_once()
    assert result["message"] == "Incident updated successfully"


@pytest.mark.asyncio
async def test_update_incident_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    update_data = IncidentCreate(
        incident_name="Updated",
        incident_type="Data Breach",
        incident_sensitivity="high",
        description="A",
        current_stage="Identification",
        workflow=[WorkflowStage(stage_name="Identification", steps=[])],
    )

    with pytest.raises(HTTPException):
        await service.create_or_update_incident(update_data, mock_user, incident_id)


@pytest.mark.asyncio
async def test_list_incidents_success(service, mock_incident_crud, mock_user, monkeypatch):
    mock_incident_crud.count_incidents.return_value = 1
    mock_incident_crud.get_incidents.return_value = [
        {
            "_id": ObjectId(),
            "incident_name": "Test",
            "incident_type": "Breach",
            "incident_sensitivity": "high",
            "status": "in_progress",
            "current_stage": "Identification",
            "workflow": [{"stage_name": "Identification"}],
            "date_discovered": datetime.now(UTC),
            "deadline": datetime.now(UTC),
            "created_at": datetime.now(UTC),
        }
    ]
    mock_incident_crud.get_filter_fields.return_value = {"incident_type": ["Breach"]}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.list_incidents(None, None, None, None, "asc", 1, 10, mock_user)

    assert result["pagination"]["total_incidents"] == 1
    assert len(result["incidents"]) == 1


@pytest.mark.asyncio
async def test_get_incident_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {"_id": ObjectId(incident_id), "incident_name": "Test Incident"}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.get_incident(incident_id, mock_user)

    assert result["_id"] == incident_id
    assert result["incident_name"] == "Test Incident"


@pytest.mark.asyncio
async def test_get_incident_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    with pytest.raises(HTTPException):
        await service.get_incident(incident_id, mock_user)


@pytest.mark.asyncio
async def test_publish_incident_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "status": "draft",
        "date_occurred": datetime.now(UTC),
        "date_discovered": datetime.now(UTC),
        "deadline": datetime.now(UTC),
    }

    mock_incident_crud.publish_incident.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.publish_incident(incident_id, mock_user)

    assert result["message"] == "Incident published successfully"


@pytest.mark.asyncio
async def test_publish_incident_not_draft(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {"status": "in_progress"}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    with pytest.raises(HTTPException):
        await service.publish_incident(incident_id, mock_user)


@pytest.mark.asyncio
async def test_move_to_next_stage_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())

    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "status": "in_progress",
        "current_stage": "Identification",
        "workflow": [
            {"stage_name": "Identification"},
            {"stage_name": "Containment"},
        ],
    }

    mock_incident_crud.update_incident.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    # FIX datetime
    mock_dt = MagicMock(wraps=datetime)
    mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=UTC)
    monkeypatch.setattr("app.services.incident_management_service.datetime", mock_dt)

    result = await service.move_to_next_stage(incident_id, mock_user)

    assert result["new_current_stage"] == "Containment"


@pytest.mark.asyncio
async def test_add_step_to_stage_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())

    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "workflow": [{"stage_name": "Identification", "steps": []}],
    }

    add_step = AddStepRequest(stage_name="Identification", step=Step(step_name="Check", step_description="Check issue"))

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.add_step_to_stage(incident_id, add_step, mock_user)

    assert result["message"] == "Step added successfully"


@pytest.mark.asyncio
async def test_update_stage_manually_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())

    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "current_stage": "Identification",
        "workflow": [{"stage_name": "Identification"}, {"stage_name": "Containment"}],
    }

    update_req = UpdateStageRequest(new_stage="Containment")

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.update_stage_manually(incident_id, update_req, mock_user)

    assert result["new_current_stage"] == "Containment"


@pytest.mark.asyncio
async def test_send_incident_notifications_success(
    service, mock_incident_crud, mock_data_principal_service, mock_customer_notifications_collection, mock_user, monkeypatch
):
    incident_id = str(ObjectId())

    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "notification_needed": True,
        "data_element": ["email"],
        "mitigation_steps": ["Step 1"],
        "incident_name": "Test Incident",
    }

    mock_data_principal_service.get_dps_by_data_elements.return_value = [{"dp_id": "dp1", "email": "dp1@example.com"}]

    mock_customer_notifications_collection.find_one.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log)

    result = await service.send_incident_notifications(incident_id, mock_user)

    assert result["message"] == "Incident notifications sent successfully"
