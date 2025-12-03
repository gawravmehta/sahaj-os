import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.grievance_service import GrievanceService
from app.crud.grievance_crud import GrievanceCRUD
from datetime import datetime, UTC
from bson import ObjectId

@pytest.fixture
def mock_grievance_crud():
    return AsyncMock(spec=GrievanceCRUD)

@pytest.fixture
def mock_customer_notification_collection():
    return AsyncMock()

@pytest.fixture
def service(mock_grievance_crud, mock_customer_notification_collection):
    return GrievanceService(mock_grievance_crud, "test_business_logs", mock_customer_notification_collection)

@pytest.fixture
def mock_user():
    return {"_id": "user123", "email": "test@example.com", "df_id": "df123"}

@pytest.mark.asyncio
async def test_get_all_grievances_success(service, mock_grievance_crud, mock_user, monkeypatch):
    mock_grievance_crud.count_grievances.return_value = 2
    mock_grievance_crud.get_grievances.return_value = [
        {"_id": ObjectId(), "subject": "Grievance 1"},
        {"_id": ObjectId(), "subject": "Grievance 2"},
    ]
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)

    result = await service.get_all_grievances(mock_user, page=1, page_size=2)

    mock_grievance_crud.count_grievances.assert_called_once()
    mock_grievance_crud.get_grievances.assert_called_once_with(0, 2)
    mock_log_business_event.assert_called_once()
    assert result["status"] == "success"
    assert len(result["data"]) == 2
    assert result["pagination"]["total"] == 2

@pytest.mark.asyncio
async def test_view_grievance_success(service, mock_grievance_crud, mock_user, monkeypatch):
    grievance_id = str(ObjectId())
    mock_grievance_crud.get_by_id.return_value = {"_id": ObjectId(grievance_id), "subject": "Test Grievance"}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)

    result = await service.view_grievance(mock_user, grievance_id)

    mock_grievance_crud.get_by_id.assert_called_once_with(grievance_id)
    mock_log_business_event.assert_called_once()
    assert result["status"] == "success"
    assert result["data"]["subject"] == "Test Grievance"

@pytest.mark.asyncio
async def test_view_grievance_not_found(service, mock_grievance_crud, mock_user, monkeypatch):
    grievance_id = str(ObjectId())
    mock_grievance_crud.get_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.view_grievance(mock_user, grievance_id)

    mock_grievance_crud.get_by_id.assert_called_once_with(grievance_id)
    mock_log_business_event.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Grievance not found"

@pytest.mark.asyncio
async def test_resolve_grievance_success_with_dp_notification(service, mock_grievance_crud, mock_customer_notification_collection, mock_user, monkeypatch):
    grievance_id = str(ObjectId())
    mock_grievance_crud.get_by_id.return_value = {
        "_id": ObjectId(grievance_id),
        "subject": "Test Grievance",
        "request_status": "pending",
        "dp_id": "dp123",
    }
    mock_grievance_crud.resolve_grievance.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)
    
    mock_datetime = MagicMock(wraps=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("app.services.grievance_service.datetime", mock_datetime)

    result = await service.resolve_grievance(mock_user, grievance_id)

    mock_grievance_crud.get_by_id.assert_called_once_with(grievance_id)
    mock_grievance_crud.resolve_grievance.assert_called_once_with(grievance_id)
    mock_log_business_event.assert_called_once()
    mock_customer_notification_collection.insert_one.assert_called_once()
    assert result["status"] == "success"
    assert result["data"]["request_status"] == "resolved"

@pytest.mark.asyncio
async def test_resolve_grievance_success_no_dp_notification(service, mock_grievance_crud, mock_customer_notification_collection, mock_user, monkeypatch):
    grievance_id = str(ObjectId())
    mock_grievance_crud.get_by_id.return_value = {
        "_id": ObjectId(grievance_id),
        "subject": "Test Grievance",
        "request_status": "pending",
        "dp_id": None,
    }
    mock_grievance_crud.resolve_grievance.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)

    result = await service.resolve_grievance(mock_user, grievance_id)

    mock_grievance_crud.get_by_id.assert_called_once_with(grievance_id)
    mock_grievance_crud.resolve_grievance.assert_called_once_with(grievance_id)
    mock_log_business_event.assert_called_once()
    mock_customer_notification_collection.insert_one.assert_not_called()
    assert result["status"] == "success"
    assert result["data"]["request_status"] == "resolved"

@pytest.mark.asyncio
async def test_resolve_grievance_not_found(service, mock_grievance_crud, mock_user, monkeypatch):
    grievance_id = str(ObjectId())
    mock_grievance_crud.get_by_id.return_value = None
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.grievance_service.log_business_event", mock_log_business_event)

    with pytest.raises(HTTPException) as exc_info:
        await service.resolve_grievance(mock_user, grievance_id)

    mock_grievance_crud.get_by_id.assert_called_once_with(grievance_id)
    mock_log_business_event.assert_called_once()
    mock_grievance_crud.resolve_grievance.assert_not_called()
    mock_customer_notification_collection.insert_one.assert_not_called()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Grievance not found"
