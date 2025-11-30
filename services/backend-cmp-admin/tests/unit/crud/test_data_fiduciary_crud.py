import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.data_fiduciary_crud import DataFiduciaryCRUD
from app.utils.common import convert_objectid_to_str


# ------------------ MOCK COLLECTION FIXTURE ------------------


@pytest.fixture
def mock_df_register_collection():
    """Mocked Mongo collection for data fiduciary registration with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.find_one = AsyncMock(return_value=None)
    collection.update_one = AsyncMock()

    return collection


@pytest.fixture
def crud(mock_df_register_collection):
    return DataFiduciaryCRUD(mock_df_register_collection)


@pytest.fixture
def dummy_data_fiduciary():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "df_id": "test_df_id",
        "name": "Test Data Fiduciary",
        "is_active": True,
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_get_data_fiduciary_found(crud, mock_df_register_collection, dummy_data_fiduciary):
    mock_df_register_collection.find_one.return_value = dummy_data_fiduciary.copy()
    df_id = dummy_data_fiduciary["df_id"]

    result = await crud.get_data_fiduciary(df_id)

    mock_df_register_collection.find_one.assert_called_once_with({"df_id": df_id})
    assert result == convert_objectid_to_str(dummy_data_fiduciary)


@pytest.mark.asyncio
async def test_get_data_fiduciary_not_found(crud, mock_df_register_collection):
    mock_df_register_collection.find_one.return_value = None
    df_id = "non_existent_df_id"

    result = await crud.get_data_fiduciary(df_id)

    mock_df_register_collection.find_one.assert_called_once_with({"df_id": df_id})
    assert result is None


@pytest.mark.asyncio
async def test_update_data_fiduciary_success(crud, mock_df_register_collection, dummy_data_fiduciary):
    df_id = dummy_data_fiduciary["df_id"]
    update_data = {"name": "Updated Data Fiduciary Name"}

    # Mock the update_one result
    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_df_register_collection.update_one.return_value = mock_update_result

    # Mock get_data_fiduciary for the subsequent call within update_data_fiduciary
    # We need to ensure that when get_data_fiduciary is called *after* update, it returns the updated doc
    updated_doc_data = {**dummy_data_fiduciary, **update_data}
    
    # We need to simulate the sequence of calls: update_one, then find_one for get_data_fiduciary
    mock_df_register_collection.find_one.side_effect = [
        updated_doc_data.copy() # This will be for the get_data_fiduciary call after update
    ]

    result = await crud.update_data_fiduciary(df_id, update_data)

    mock_df_register_collection.update_one.assert_called_once_with(
        {"df_id": df_id},
        {"$set": update_data},
        upsert=False,
    )
    # The get_data_fiduciary (which calls find_one) is called after update
    mock_df_register_collection.find_one.assert_called_once_with({"df_id": df_id})
    assert result == convert_objectid_to_str(updated_doc_data)


@pytest.mark.asyncio
async def test_update_data_fiduciary_not_found(crud, mock_df_register_collection):
    df_id = "non_existent_df_id"
    update_data = {"name": "Some Name"}

    # Mock the update_one result to show no document was matched
    mock_update_result = MagicMock(matched_count=0, modified_count=0)
    mock_df_register_collection.update_one.return_value = mock_update_result

    result = await crud.update_data_fiduciary(df_id, update_data)

    mock_df_register_collection.update_one.assert_called_once_with(
        {"df_id": df_id},
        {"$set": update_data},
        upsert=False,
    )
    # find_one (from get_data_fiduciary) should not be called if matched_count is 0
    mock_df_register_collection.find_one.assert_not_called()
    assert result is None
