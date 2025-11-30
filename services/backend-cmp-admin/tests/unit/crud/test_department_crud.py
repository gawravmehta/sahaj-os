import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.department_crud import DepartmentCRUD


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock()

    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return DepartmentCRUD(mock_collection)


@pytest.fixture
def dummy_department_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "department_name": "Test Department",
        "df_id": "test_df_id",
        "is_deleted": False,
    }


@pytest.mark.asyncio
async def test_find_by_name(crud, mock_collection, dummy_department_data):
    mock_collection.find_one.return_value = dummy_department_data.copy()

    result = await crud.find_by_name(dummy_department_data["department_name"], dummy_department_data["df_id"])

    mock_collection.find_one.assert_called_once_with(
        {"department_name": dummy_department_data["department_name"], "df_id": dummy_department_data["df_id"]}
    )
    assert result == dummy_department_data


@pytest.mark.asyncio
async def test_find_by_id(crud, mock_collection, dummy_department_data):
    mock_collection.find_one.return_value = dummy_department_data.copy()
    department_id = str(dummy_department_data["_id"])

    result = await crud.find_by_id(department_id)

    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(department_id)})
    assert result == dummy_department_data


@pytest.mark.asyncio
async def test_search_by_name(crud, mock_collection, dummy_department_data):
    mock_collection.find.return_value.to_list.return_value = [dummy_department_data.copy()]
    department_name_part = "test"
    df_id = dummy_department_data["df_id"]

    result = await crud.search_by_name(department_name_part, df_id)

    regex = f".*{department_name_part}.*"
    mock_collection.find.assert_called_once_with({"department_name": {"$regex": regex, "$options": "i"}, "df_id": df_id})
    mock_collection.find.return_value.to_list.assert_called_once_with(length=100)
    assert result == [dummy_department_data]


@pytest.mark.asyncio
async def test_get_all(crud, mock_collection, dummy_department_data):
    mock_collection.find.return_value.to_list.return_value = [dummy_department_data.copy()]
    df_id = dummy_department_data["df_id"]
    skip = 0
    limit = 10

    result = await crud.get_all(df_id, skip, limit)

    mock_collection.find.assert_called_once_with({"df_id": df_id, "is_deleted": False})
    mock_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_collection.find.return_value.limit.assert_called_once_with(limit)
    mock_collection.find.return_value.to_list.assert_called_once_with(length=limit)
    assert result == [dummy_department_data]


@pytest.mark.asyncio
async def test_create_department(crud, mock_collection, dummy_department_data):

    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_department_data["_id"]
    mock_collection.insert_one.return_value = mock_insert_one_result

    department_data_to_create = dummy_department_data.copy()

    del department_data_to_create["_id"]

    result = await crud.create(department_data_to_create)

    mock_collection.insert_one.assert_called_once_with(department_data_to_create)
    assert result == mock_insert_one_result


@pytest.mark.asyncio
async def test_update_department(crud, mock_collection, dummy_department_data):
    department_id = str(dummy_department_data["_id"])
    update_data = {"department_name": "Updated Department"}

    mock_collection.update_one.return_value = MagicMock(matched_count=1, modified_count=1)

    result = await crud.update_department(department_id, update_data)

    mock_collection.update_one.assert_called_once_with({"_id": ObjectId(department_id)}, {"$set": update_data})
    assert result.matched_count == 1
    assert result.modified_count == 1


@pytest.mark.asyncio
async def test_count_departments(crud, mock_collection, dummy_department_data):
    mock_collection.count_documents.return_value = 5
    df_id = dummy_department_data["df_id"]

    result = await crud.count_departments(df_id)

    mock_collection.count_documents.assert_called_once_with({"df_id": df_id, "is_deleted": False})
    assert result == 5
