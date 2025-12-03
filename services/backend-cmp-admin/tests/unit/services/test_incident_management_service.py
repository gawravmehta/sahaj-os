import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.incident_management_service import IncidentService
from app.crud.incident_management_crud import IncidentCRUD
from app.services.data_principal_service import DataPrincipalService
from app.schemas.incident_management_schema import IncidentCreate, AddStepRequest, UpdateStageRequest, IncidentWorkflowStage, IncidentWorkflowStep
from datetime import datetime, UTC
from bson import ObjectId

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
    return AsyncMock()

@pytest.fixture
def service(
    mock_incident_crud,
    mock_user_collection,
    mock_data_principal_service,
    mock_customer_notifications_collection,
):
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
        description="A test incident",
        incident_type="Data Breach",
        incident_sensitivity="high",
        date_occurred=datetime.now(UTC),
        date_discovered=datetime.now(UTC),
        deadline=datetime.now(UTC),
        workflow=[
            IncidentWorkflowStage(stage_name="Identification", steps=[IncidentWorkflowStep(step_description="Identify breach")]),
            IncidentWorkflowStage(stage_name="Containment", steps=[]),
        ],
    )

@pytest.mark.asyncio
async def test_create_incident_success(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    mock_incident_crud.find_duplicate.return_value = None
    mock_incident_crud.insert_incident.return_value = str(ObjectId())
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    result = await service.create_or_update_incident(mock_incident_create_data, mock_user)

    mock_incident_crud.find_duplicate.assert_called_once()
    mock_incident_crud.insert_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert "incident_id" in result
    assert result["message"] == "Incident created successfully"

@pytest.mark.asyncio
async def test_create_incident_duplicate_name(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    mock_incident_crud.find_duplicate.return_value = {"_id": ObjectId()}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_or_update_incident(mock_incident_create_data, mock_user)

    mock_incident_crud.find_duplicate.assert_called_once()
    mock_incident_crud.insert_incident.assert_not_called()
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert "Stage already open for incident" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_incident_success(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {"_id": ObjectId(incident_id), "df_id": mock_user["df_id"], "status": "draft"}
    mock_incident_crud.update_incident.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    update_data = IncidentCreate(
        incident_name="Updated Incident Name",
        workflow=[
            IncidentWorkflowStage(stage_name="Identification", steps=[IncidentWorkflowStep(step_description="Identify breach")]),
        ],
    )

    result = await service.create_or_update_incident(update_data, mock_user, incident_id=incident_id)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["incident_id"] == incident_id
    assert result["message"] == "Incident updated successfully"

@pytest.mark.asyncio
async def test_update_incident_not_found(service, mock_incident_crud, mock_user, mock_incident_create_data, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    update_data = IncidentCreate(incident_name="Updated Incident Name")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_or_update_incident(update_data, mock_user, incident_id=incident_id)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_not_called()
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_list_incidents_success(service, mock_incident_crud, mock_user, monkeypatch):
    mock_incident_crud.count_incidents.return_value = 1
    mock_incident_crud.get_incidents.return_value = [
        {
            "_id": ObjectId(),
            "incident_name": "Test Incident",
            "incident_type": "Data Breach",
            "incident_sensitivity": "high",
            "status": "in_progress",
            "current_stage": "Identification",
            "workflow": [{"stage_name": "Identification"}, {"stage_name": "Containment"}],
            "date_discovered": datetime.now(UTC),
            "deadline": datetime.now(UTC),
            "created_at": datetime.now(UTC),
        }
    ]
    mock_incident_crud.get_filter_fields.return_value = {"type": ["Data Breach"]}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    result = await service.list_incidents(None, None, None, None, "asc", 1, 10, mock_user)

    mock_incident_crud.count_incidents.assert_called_once()
    mock_incident_crud.get_incidents.assert_called_once()
    mock_incident_crud.get_filter_fields.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["pagination"]["total_incidents"] == 1
    assert len(result["incidents"]) == 1
    assert result["incidents"][0]["incident_name"] == "Test Incident"

@pytest.mark.asyncio
async def test_get_incident_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {"_id": ObjectId(incident_id), "incident_name": "Test Incident"}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    result = await service.get_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert result["_id"] == incident_id
    assert result["incident_name"] == "Test Incident"

@pytest.mark.asyncio
async def test_get_incident_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

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
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    result = await service.publish_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.publish_incident.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Incident published successfully"

@pytest.mark.asyncio
async def test_publish_incident_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.publish_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_publish_incident_not_draft(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "status": "in_progress",
        "date_occurred": datetime.now(UTC),
        "date_discovered": datetime.now(UTC),
        "deadline": datetime.now(UTC),
    }
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.publish_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Incident is not in draft state"

@pytest.mark.asyncio
async def test_publish_incident_missing_fields(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = {
        "_id": ObjectId(incident_id),
        "status": "draft",
        "date_occurred": datetime.now(UTC),
        "date_discovered": datetime.now(UTC),
        "deadline": None,
    }
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.publish_incident(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert "deadline" in exc_info.value.detail

@pytest.mark.asyncio
async def test_move_to_next_stage_success_mid_workflow(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "status": "in_progress",
        "current_stage": "Identification",
        "workflow": [
            {"stage_name": "Identification"},
            {"stage_name": "Containment"},
            {"stage_name": "Eradication"},
        ],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident
    mock_incident_crud.update_incident.return_value = None

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    mock_datetime = MagicMock(wraps=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("app.services.incident_management_service.datetime", mock_datetime)

    result = await service.move_to_next_stage(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Stage updated successfully"
    assert result["new_current_stage"] == "Containment"
    assert result["new_status"] == "in_progress"

@pytest.mark.asyncio
async def test_move_to_next_stage_success_last_stage(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "status": "in_progress",
        "current_stage": "Eradication",
        "workflow": [
            {"stage_name": "Identification"},
            {"stage_name": "Containment"},
            {"stage_name": "Eradication"},
        ],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident
    mock_incident_crud.update_incident.return_value = None

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    mock_datetime = MagicMock(wraps=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("app.services.incident_management_service.datetime", mock_datetime)

    result = await service.move_to_next_stage(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Stage updated successfully"
    assert result["new_current_stage"] == "Eradication" # Stays the same as it's the last stage
    assert result["new_status"] == "closed"

@pytest.mark.asyncio
async def test_move_to_next_stage_incident_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.move_to_next_stage(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_add_step_to_stage_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "workflow": [
            {"stage_name": "Identification", "steps": []},
        ],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident
    mock_incident_crud.update_incident.return_value = None

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    add_step_request = AddStepRequest(stage_name="Identification", step=IncidentWorkflowStep(step_description="New Step"))

    result = await service.add_step_to_stage(incident_id, add_step_request, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Step added successfully"

@pytest.mark.asyncio
async def test_add_step_to_stage_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    add_step_request = AddStepRequest(stage_name="Identification", step=IncidentWorkflowStep(step_description="New Step"))

    with pytest.raises(HTTPException) as exc_info:
        await service.add_step_to_stage(incident_id, add_step_request, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_update_stage_manually_success(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "current_stage": "Identification",
        "workflow": [
            {"stage_name": "Identification"},
            {"stage_name": "Containment"},
        ],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident
    mock_incident_crud.update_incident.return_value = None

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    update_stage_request = UpdateStageRequest(new_stage="Containment")

    result = await service.update_stage_manually(incident_id, update_stage_request, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Current stage updated successfully"
    assert result["new_current_stage"] == "Containment"

@pytest.mark.asyncio
async def test_update_stage_manually_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    update_stage_request = UpdateStageRequest(new_stage="Containment")

    with pytest.raises(HTTPException) as exc_info:
        await service.update_stage_manually(incident_id, update_stage_request, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_send_incident_notifications_success(service, mock_incident_crud, mock_data_principal_service, mock_customer_notifications_collection, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "notification_needed": True,
        "data_element": ["email"],
        "mitigation_steps": ["Step 1"],
        "incident_name": "Test Incident",
    }
    mock_incident_crud.get_incident_by_id.return_value = incident
    mock_data_principal_service.get_dps_by_data_elements.return_value = [{
        "dp_id": "dp1", "email": "dp1@example.com"
    }]
    mock_customer_notifications_collection.find_one.return_value = None
    mock_customer_notifications_collection.insert_many.return_value = None
    mock_incident_crud.update_incident.return_value = None

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    mock_datetime = MagicMock(wraps=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("app.services.incident_management_service.datetime", mock_datetime)

    result = await service.send_incident_notifications(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_data_principal_service.get_dps_by_data_elements.assert_called_once()
    mock_customer_notifications_collection.find_one.assert_called_once()
    mock_customer_notifications_collection.insert_many.assert_called_once()
    mock_incident_crud.update_incident.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["message"] == "Incident notifications sent successfully"

@pytest.mark.asyncio
async def test_send_incident_notifications_not_found(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    mock_incident_crud.get_incident_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.send_incident_notifications(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Incident not found"

@pytest.mark.asyncio
async def test_send_incident_notifications_not_needed(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "notification_needed": False,
    }
    mock_incident_crud.get_incident_by_id.return_value = incident

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.send_incident_notifications(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Notifications are not marked as needed for this incident."

@pytest.mark.asyncio
async def test_send_incident_notifications_no_data_elements(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "notification_needed": True,
        "data_element": [],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.send_incident_notifications(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "data_elements are not specified in the incident for sending notifications."

@pytest.mark.asyncio
async def test_send_incident_notifications_no_mitigation_steps(service, mock_incident_crud, mock_user, monkeypatch):
    incident_id = str(ObjectId())
    incident = {
        "_id": ObjectId(incident_id),
        "df_id": mock_user["df_id"],
        "notification_needed": True,
        "data_element": ["email"],
        "mitigation_steps": [],
    }
    mock_incident_crud.get_incident_by_id.return_value = incident

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.incident_management_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.send_incident_notifications(incident_id, mock_user)

    mock_incident_crud.get_incident_by_id.assert_called_once_with(incident_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "mitigation_steps are not specified in the incident for sending notifications."
