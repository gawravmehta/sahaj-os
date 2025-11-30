import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.consent_validation_crud import ConsentValidationCRUD
from pymongo import ASCENDING, DESCENDING


@pytest.fixture
def mock_consent_validation_collection():
    """Mocked Mongo collection for consent validation logs with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock(return_value=None)
    collection.count_documents = AsyncMock(return_value=0)
    collection.distinct = AsyncMock(return_value=[])

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def mock_consent_validation_files_collection():
    """Mocked Mongo collection for consent validation files with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)
    collection.insert_one = AsyncMock()

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_consent_validation_collection, mock_consent_validation_files_collection):
    return ConsentValidationCRUD(mock_consent_validation_collection, mock_consent_validation_files_collection)


@pytest.fixture
def dummy_log_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "timestamp": "2023-01-01T12:00:00Z",
        "df_id": "df123",
        "status": "success",
        "file_name": "test_file.csv",
        "error_count": 0,
    }


@pytest.fixture
def dummy_file_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e6345678a"),
        "file_name": "uploaded_file.csv",
        "df_id": "df123",
        "created_at": "2023-01-01T10:00:00Z",
        "status": "processed",
    }


@pytest.mark.asyncio
async def test_insert_verification_log(crud, mock_consent_validation_collection, dummy_log_data):
    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_log_data["_id"]
    mock_consent_validation_collection.insert_one.return_value = mock_insert_one_result

    log_data_to_insert = dummy_log_data.copy()
    del log_data_to_insert["_id"]

    result = await crud.insert_verification_log(log_data_to_insert)

    mock_consent_validation_collection.insert_one.assert_called_once_with(log_data_to_insert)
    assert result == mock_insert_one_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_dir_input, expected_sort_dir",
    [
        (ASCENDING, ASCENDING),
        (DESCENDING, DESCENDING),
        (1, 1),
        (-1, -1),
    ],
)
async def test_find_logs(crud, mock_consent_validation_collection, dummy_log_data, sort_dir_input, expected_sort_dir):
    mock_consent_validation_collection.find.return_value.__aiter__.return_value = iter([dummy_log_data.copy()])

    query = {"df_id": dummy_log_data["df_id"]}
    skip = 0
    limit = 10

    result_cursor = crud.find_logs(query, sort_dir_input, skip, limit)

    result_data = []
    async for doc in result_cursor:
        result_data.append(doc)

    mock_consent_validation_collection.find.assert_called_once_with(query)
    mock_consent_validation_collection.find.return_value.sort.assert_called_once_with("timestamp", expected_sort_dir)
    mock_consent_validation_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_consent_validation_collection.find.return_value.limit.assert_called_once_with(limit)
    assert len(result_data) == 1
    assert result_data[0]["_id"] == dummy_log_data["_id"]


@pytest.mark.asyncio
async def test_count_total_logs(crud, mock_consent_validation_collection):
    mock_consent_validation_collection.count_documents.return_value = 5
    query = {"df_id": "df123"}

    result = await crud.count_total_logs(query)

    mock_consent_validation_collection.count_documents.assert_called_once_with(query)
    assert result == 5


@pytest.mark.asyncio
async def test_find_one_log(crud, mock_consent_validation_collection, dummy_log_data):
    mock_consent_validation_collection.find_one.return_value = dummy_log_data.copy()
    query = {"_id": dummy_log_data["_id"]}

    result = await crud.find_one_log(query)

    mock_consent_validation_collection.find_one.assert_called_once_with(query)
    assert result == dummy_log_data


@pytest.mark.asyncio
async def test_count_logs(crud, mock_consent_validation_collection):
    mock_consent_validation_collection.count_documents.return_value = 10
    query = {"status": "failed"}

    result = await crud.count_logs(query)

    mock_consent_validation_collection.count_documents.assert_called_once_with(query)
    assert result == 10


@pytest.mark.asyncio
async def test_find_distinct_logs(crud, mock_consent_validation_collection):
    mock_consent_validation_collection.distinct.return_value = ["file1.csv", "file2.csv"]
    field = "file_name"
    query = {"df_id": "df123"}

    result = await crud.find_distinct_logs(field, query)

    mock_consent_validation_collection.distinct.assert_called_once_with(field, query)
    assert result == ["file1.csv", "file2.csv"]


@pytest.mark.asyncio
async def test_insert_validation_file_details(crud, mock_consent_validation_files_collection, dummy_file_data):
    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_file_data["_id"]
    mock_consent_validation_files_collection.insert_one.return_value = mock_insert_one_result

    file_data_to_insert = dummy_file_data.copy()
    del file_data_to_insert["_id"]

    result = await crud.insert_validation_file_details(file_data_to_insert)

    mock_consent_validation_files_collection.insert_one.assert_called_once_with(file_data_to_insert)
    assert result == mock_insert_one_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_dir_input, expected_sort_dir",
    [
        (ASCENDING, ASCENDING),
        (DESCENDING, DESCENDING),
        (1, 1),
        (-1, -1),
    ],
)
async def test_get_all_uploaded_files(crud, mock_consent_validation_files_collection, dummy_file_data, sort_dir_input, expected_sort_dir):
    mock_consent_validation_files_collection.find.return_value.to_list.return_value = [dummy_file_data.copy()]

    query = {"df_id": dummy_file_data["df_id"]}
    skip = 0
    limit = 10

    result = await crud.get_all_uploaded_files(query, sort_dir_input, skip, limit)

    mock_consent_validation_files_collection.find.assert_called_once_with(query)
    mock_consent_validation_files_collection.find.return_value.sort.assert_called_once_with("created_at", expected_sort_dir)
    mock_consent_validation_files_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_consent_validation_files_collection.find.return_value.limit.assert_called_once_with(limit)
    mock_consent_validation_files_collection.find.return_value.to_list.assert_called_once_with(length=limit)
    assert len(result) == 1
    assert result[0]["_id"] == dummy_file_data["_id"]
