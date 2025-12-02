import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.notification_crud import NotificationCRUD
from pymongo import ASCENDING, DESCENDING


# ------------------ MOCK COLLECTION FIXTURE ------------------


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection for notifications with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.count_documents = AsyncMock(return_value=0)
    collection.update_one = AsyncMock()
    collection.update_many = AsyncMock()

    # Mock cursor for find()
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return NotificationCRUD(mock_collection)


@pytest.fixture
def dummy_notification_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "title": "Test Notification",
        "message": "This is a test notification.",
        "created_at": "2023-01-01T10:00:00Z",
        "users": {
            "user123": {"is_read": False, "is_deleted": False},
            "user456": {"is_read": True, "is_deleted": False},
        },
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_count_notifications(crud, mock_collection):
    mock_collection.count_documents.return_value = 5
    filter_query = {"df_id": "df123"}

    result = await crud.count_notifications(filter_query)

    mock_collection.count_documents.assert_called_once_with(filter_query)
    assert result == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_field, sort_order, page, limit, expected_skip",
    [
        ("created_at", ASCENDING, 1, 10, 0),
        ("created_at", DESCENDING, 2, 5, 5),
    ],
)
async def test_get_notifications(crud, mock_collection, dummy_notification_data, sort_field, sort_order, page, limit, expected_skip):
    mock_collection.find.return_value.to_list.return_value = [dummy_notification_data.copy()]
    filter_query = {"users.user123.is_deleted": False}

    result = await crud.get_notifications(filter_query, sort_field, sort_order, page, limit)

    mock_collection.find.assert_called_once_with(filter_query)
    mock_collection.find.return_value.sort.assert_called_once_with(sort_field, sort_order)
    mock_collection.find.return_value.skip.assert_called_once_with(expected_skip)
    mock_collection.find.return_value.limit.assert_called_once_with(limit)
    mock_collection.find.return_value.to_list.assert_called_once_with(length=limit)
    assert len(result) == 1
    assert result[0] == dummy_notification_data


@pytest.mark.asyncio
async def test_mark_as_read_success(crud, mock_collection):
    notification_id = "60d0fe4f3460595e63456789"
    user_id = "user123"

    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_collection.update_one.return_value = mock_update_result

    result = await crud.mark_as_read(notification_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(notification_id), f"users.{user_id}.is_deleted": False},
        {"$set": {f"users.{user_id}.is_read": True}},
    )
    assert result == mock_update_result


@pytest.mark.asyncio
async def test_mark_as_read_not_found(crud, mock_collection):
    notification_id = "60d0fe4f3460595e63456789"
    user_id = "user123"

    mock_update_result = MagicMock(matched_count=0, modified_count=0)
    mock_collection.update_one.return_value = mock_update_result

    result = await crud.mark_as_read(notification_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(notification_id), f"users.{user_id}.is_deleted": False},
        {"$set": {f"users.{user_id}.is_read": True}},
    )
    assert result == mock_update_result # Should return the mock result even if not found


@pytest.mark.asyncio
async def test_mark_all_as_read_success(crud, mock_collection):
    user_id = "user123"

    mock_update_result = MagicMock(matched_count=2, modified_count=2)
    mock_collection.update_many.return_value = mock_update_result

    result = await crud.mark_all_as_read(user_id)

    mock_collection.update_many.assert_called_once_with(
        {f"users.{user_id}.is_deleted": False, f"users.{user_id}.is_read": False},
        {"$set": {f"users.{user_id}.is_read": True}},
    )
    assert result == mock_update_result


@pytest.mark.asyncio
async def test_mark_all_as_read_no_unreads(crud, mock_collection):
    user_id = "user123"

    mock_update_result = MagicMock(matched_count=0, modified_count=0)
    mock_collection.update_many.return_value = mock_update_result

    result = await crud.mark_all_as_read(user_id)

    mock_collection.update_many.assert_called_once_with(
        {f"users.{user_id}.is_deleted": False, f"users.{user_id}.is_read": False},
        {"$set": {f"users.{user_id}.is_read": True}},
    )
    assert result == mock_update_result
