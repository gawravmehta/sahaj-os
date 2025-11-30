import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime, UTC

from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud.webhook_events_crud import WebhookEventCRUD
from app.schemas.webhook_events_schema import WebhookEventInDB


@pytest.fixture
def mock_collection():
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()

    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[])
    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return WebhookEventCRUD(mock_collection)


@pytest.fixture
def dummy_event():
    """Fixture returning a valid WebhookEventInDB object."""
    return WebhookEventInDB(
        webhook_id=str(ObjectId()),
        df_id=str(ObjectId()),
        dp_id=str(ObjectId()),
        id=ObjectId(),
        event_type="user.created",
        payload={"user_id": "123"},
        status="pending",
        attempts=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_create_event(crud, mock_collection, dummy_event):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    result = await crud.create_event(dummy_event)

    mock_collection.insert_one.assert_called_once()
    assert result == str(inserted_id)


@pytest.mark.asyncio
async def test_get_event_found(crud, mock_collection):
    event_id = str(ObjectId())
    fake_doc = {"_id": ObjectId(event_id), "status": "pending"}

    mock_collection.find_one.return_value = fake_doc

    result = await crud.get_event(event_id)

    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(event_id)})
    assert result == fake_doc


@pytest.mark.asyncio
async def test_get_event_not_found(crud, mock_collection):
    event_id = str(ObjectId())

    mock_collection.find_one.return_value = None

    result = await crud.get_event(event_id)

    mock_collection.find_one.assert_called_once()
    assert result is None


@pytest.mark.asyncio
async def test_update_event_status_success(crud, mock_collection):
    event_id = str(ObjectId())
    mock_collection.update_one.return_value = MagicMock(modified_count=1)

    result = await crud.update_event_status(
        event_id,
        status="sent",
        attempts=3,
        last_error=None,
    )

    mock_collection.update_one.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_update_event_status_with_error(crud, mock_collection):
    event_id = str(ObjectId())
    mock_collection.update_one.return_value = MagicMock(modified_count=1)

    result = await crud.update_event_status(
        event_id,
        status="failed",
        attempts=2,
        last_error="Timeout error",
    )

    update_call = mock_collection.update_one.call_args[0][1]["$set"]

    assert update_call["status"] == "failed"
    assert update_call["attempts"] == 2
    assert update_call["last_error"] == "Timeout error"
    assert result is True


@pytest.mark.asyncio
async def test_update_event_status_not_modified(crud, mock_collection):
    event_id = str(ObjectId())
    mock_collection.update_one.return_value = MagicMock(modified_count=0)

    result = await crud.update_event_status(
        event_id,
        status="sent",
        attempts=1,
    )

    assert result is False


@pytest.mark.asyncio
async def test_list_pending_events(crud, mock_collection):
    fake_events = [
        {"_id": ObjectId(), "status": "pending"},
        {"_id": ObjectId(), "status": "failed"},
    ]

    mock_collection.find.return_value.to_list.return_value = fake_events

    result = await crud.list_pending_events()

    mock_collection.find.assert_called_once_with({"status": {"$ne": "sent"}})
    assert result == fake_events


@pytest.mark.asyncio
async def test_list_pending_events_empty(crud, mock_collection):
    mock_collection.find.return_value.to_list.return_value = []

    result = await crud.list_pending_events()

    assert result == []
