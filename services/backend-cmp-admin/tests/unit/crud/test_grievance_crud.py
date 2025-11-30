import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.grievance_crud import GrievanceCRUD


# ------------------ MOCK COLLECTIONS FIXTURE ------------------


@pytest.fixture
def mock_grievance_collection():
    """Mocked Mongo collection for grievances with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.count_documents = AsyncMock(return_value=0)
    collection.find_one = AsyncMock(return_value=None)
    collection.find_one_and_update = AsyncMock(return_value=None)

    # Mock cursor for find()
    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_grievance_collection):
    return GrievanceCRUD(mock_grievance_collection)


@pytest.fixture
def dummy_grievance_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "subject": "Test Grievance",
        "request_status": "pending",
        "created_at": "2023-01-01T12:00:00Z",
        "last_updated_at": "2023-01-01T12:00:00Z",
        "is_verified": False,
        "is_registered_user": False,
        "email": "test@example.com",
        "mobile_number": "1234567890",
        "dp_type": "Data Principal",
        "business_entity": "Test Entity",
        "data_processor": "Test Processor",
        "ticket_allocated": "ticket123",
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_count_grievances(crud, mock_grievance_collection):
    mock_grievance_collection.count_documents.return_value = 5

    result = await crud.count_grievances()

    mock_grievance_collection.count_documents.assert_called_once_with({})
    assert result == 5


@pytest.mark.asyncio
async def test_get_grievances(crud, mock_grievance_collection, dummy_grievance_data):
    mock_grievance_collection.find.return_value.to_list.return_value = [dummy_grievance_data.copy()]
    skip = 0
    limit = 10
    projection = {
        "_id": 1,
        "subject": 1,
        "request_status": 1,
        "created_at": 1,
        "last_updated_at": 1,
        "is_verified": 1,
        "is_registered_user": 1,
        "email": 1,
        "mobile_number": 1,
        "dp_type": 1,
        "business_entity": 1,
        "data_processor": 1,
        "ticket_allocated": 1,
    }

    result = await crud.get_grievances(skip, limit)

    mock_grievance_collection.find.assert_called_once_with({}, projection)
    mock_grievance_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_grievance_collection.find.return_value.limit.assert_called_once_with(limit)
    mock_grievance_collection.find.return_value.to_list.assert_called_once_with(length=limit)
    assert len(result) == 1
    assert result[0]["_id"] == str(dummy_grievance_data["_id"])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "grievance_id_input, is_valid_objectid, find_one_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", True, {"_id": ObjectId("60d0fe4f3460595e63456789"), "subject": "Test"}, True),
        ("invalid_id", False, None, False),
        ("60d0fe4f3460595e63456781", True, None, False),
    ],
)
async def test_get_by_id(crud, mock_grievance_collection, dummy_grievance_data, grievance_id_input, is_valid_objectid, find_one_return, expected_result):
    if is_valid_objectid:
        mock_grievance_collection.find_one.return_value = find_one_return
        
    result = await crud.get_by_id(grievance_id_input)

    if is_valid_objectid:
        mock_grievance_collection.find_one.assert_called_once_with({"_id": ObjectId(grievance_id_input)})
        if expected_result:
            expected_dict = find_one_return.copy()
            expected_dict["_id"] = str(expected_dict["_id"])
            assert result == expected_dict
        else:
            assert result is None
    else:
        mock_grievance_collection.find_one.assert_not_called()
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "grievance_id_input, is_valid_objectid, find_one_and_update_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", True, {"_id": ObjectId("60d0fe4f3460595e63456789"), "request_status": "pending"}, True),
        ("invalid_id", False, None, False),
        ("60d0fe4f3460595e63456781", True, None, False),
    ],
)
async def test_resolve_grievance(crud, mock_grievance_collection, dummy_grievance_data, grievance_id_input, is_valid_objectid, find_one_and_update_return, expected_result):
    if is_valid_objectid:
        mock_grievance_collection.find_one_and_update.return_value = find_one_and_update_return
        
    result = await crud.resolve_grievance(grievance_id_input)

    if is_valid_objectid:
        mock_grievance_collection.find_one_and_update.assert_called_once_with(
            {"_id": ObjectId(grievance_id_input)},
            {"$set": {"request_status": "resolved"}},
        )
        if expected_result:
            expected_dict = find_one_and_update_return.copy()
            expected_dict["_id"] = str(expected_dict["_id"])
            assert result == expected_dict
        else:
            assert result is None
    else:
        mock_grievance_collection.find_one_and_update.assert_not_called()
        assert result is None
