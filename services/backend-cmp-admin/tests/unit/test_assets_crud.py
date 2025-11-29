import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.assets_crud import AssetCrud
from app.schemas.assets_schema import AssetCreate, AssetUpdate


# Helper function to create an async generator for mocking cursors
def _async_generator_helper(items):
    async def _generator():
        for item in items:
            yield item
    return _generator()


@pytest.fixture
def mock_assets_master_collection():
    """Fixture for a mock AsyncIOMotorCollection that correctly simulates MongoDB operations."""
    # Use MagicMock for the collection itself to allow flexible attribute assignment,
    # and spec=AsyncIOMotorCollection for method signature validation.
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)

    # Explicitly mock asynchronous methods to return awaitable objects
    mock_collection.insert_one = AsyncMock()
    mock_collection.find_one = AsyncMock()
    mock_collection.update_one = AsyncMock()
    mock_collection.count_documents = AsyncMock()
    mock_collection.distinct = AsyncMock()

    # Create a mock cursor that behaves like AsyncIOMotorCursor
    mock_cursor_instance = MagicMock()
    mock_cursor_instance.skip.return_value = mock_cursor_instance
    mock_cursor_instance.limit.return_value = mock_cursor_instance
    # Configure __aiter__ for the mock cursor to use our helper
    mock_cursor_instance.__aiter__ = lambda: _async_generator_helper([]) # Default to empty

    # Configure the 'find' method of the collection to return our configured mock cursor
    mock_collection.find.return_value = mock_cursor_instance

    # Set default return values for the mocked methods
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))
    mock_collection.find_one.return_value = None # Default for find_one
    mock_collection.update_one.return_value = MagicMock(matched_count=1, modified_count=1) # Generic update success
    mock_collection.count_documents.return_value = 0
    mock_collection.distinct.return_value = []

    return mock_collection


@pytest.fixture
def asset_crud(mock_assets_master_collection):
    """Fixture for an AssetCrud instance with a mocked collection."""
    return AssetCrud(mock_assets_master_collection)

@pytest.fixture
def dummy_asset_data() -> dict:
    """Fixture for dummy asset data."""
    return {
        "asset_name": "Test Asset",
        "df_id": "test_df_id",
        "category": "essential",
        "asset_status": "draft",
        "meta_cookies": {"cookies_count": 5},
    }

@pytest.mark.asyncio
async def test_create_asset(asset_crud, mock_assets_master_collection, dummy_asset_data: dict):
    """Test creating a new asset."""
    # The insert_one return_value is already set in the fixture for mock_assets_master_collection
    # We can override it here if specific behavior is needed for this test.

    # Pass a copy to the CRUD method to ensure the original dummy_asset_data is not mutated.
    created_asset = await asset_crud.create_asset(dummy_asset_data.copy())

    # The mock.insert_one should have been called with the data *before* the _id was added by the CRUD method.
    mock_assets_master_collection.insert_one.assert_called_once_with(dummy_asset_data.copy())
    assert created_asset["_id"] == "60d0fe4f3460595e63456789"
    assert created_asset["asset_name"] == dummy_asset_data["asset_name"]

@pytest.mark.asyncio
async def test_get_asset_found(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test fetching an existing asset."""
    asset_id = "60d0fe4f3460595e63456789"
    df_id = dummy_asset_data["df_id"]
    mock_assets_master_collection.find_one.return_value = {
        **dummy_asset_data,
        "_id": ObjectId(asset_id),
    }

    fetched_asset = await asset_crud.get_asset(asset_id, df_id)

    mock_assets_master_collection.find_one.assert_called_once_with(
        {"_id": ObjectId(asset_id), "df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
    )
    assert fetched_asset["_id"] == asset_id
    assert fetched_asset["asset_name"] == dummy_asset_data["asset_name"]

@pytest.mark.asyncio
async def test_get_asset_not_found(asset_crud, mock_assets_master_collection):
    """Test fetching a non-existent asset."""
    asset_id = "60d0fe4f3460595e63456789"
    df_id = "non_existent_df"
    mock_assets_master_collection.find_one.return_value = None

    fetched_asset = await asset_crud.get_asset(asset_id, df_id)

    assert fetched_asset is None

@pytest.mark.asyncio
async def test_update_asset_by_id(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test updating an existing asset."""
    asset_id = "60d0fe4f3460595e63456789"
    df_id = dummy_asset_data["df_id"]
    update_data = {"asset_name": "Updated Asset Name", "asset_status": "published"}

    mock_assets_master_collection.find_one.return_value = {
        **dummy_asset_data,
        "_id": ObjectId(asset_id),
        **update_data,
    }

    updated_asset = await asset_crud.update_asset_by_id(asset_id, df_id, update_data)

    mock_assets_master_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(asset_id), "df_id": df_id},
        {"$set": update_data},
    )
    mock_assets_master_collection.find_one.assert_called_once_with({"_id": ObjectId(asset_id)})
    assert updated_asset["_id"] == asset_id
    assert updated_asset["asset_name"] == "Updated Asset Name"
    assert updated_asset["asset_status"] == "published"

@pytest.mark.asyncio
async def test_is_duplicate_name_true(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test checking for a duplicate asset name when one exists."""
    mock_assets_master_collection.find_one.return_value = {"_id": ObjectId()}

    is_duplicate = await asset_crud.is_duplicate_name(dummy_asset_data["asset_name"], dummy_asset_data["df_id"])

    mock_assets_master_collection.find_one.assert_called_once_with(
        {
            "asset_name": dummy_asset_data["asset_name"],
            "df_id": dummy_asset_data["df_id"],
            "asset_status": {"$in": ["draft", "published"]},
        }
    )
    assert is_duplicate is True

@pytest.mark.asyncio
async def test_is_duplicate_name_false(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test checking for a duplicate asset name when none exists."""
    mock_assets_master_collection.find_one.return_value = None

    is_duplicate = await asset_crud.is_duplicate_name(dummy_asset_data["asset_name"], dummy_asset_data["df_id"])

    assert is_duplicate is False

@pytest.mark.asyncio
async def test_get_all_assets(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test getting all assets with pagination and optional category filter."""
    df_id = dummy_asset_data["df_id"]
    offset = 0
    limit = 10
    category = "essential"

    # Configure the mock cursor's async iteration for this specific test
    mock_assets_master_collection.find.return_value.skip.return_value.limit.return_value.__aiter__ = \
        lambda: _async_generator_helper([
            {**dummy_asset_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
            {**dummy_asset_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "asset_name": "Another Asset"}
        ])
    mock_assets_master_collection.count_documents.return_value = 2

    result = await asset_crud.get_all_assets(df_id, offset, limit, category)

    query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}, "category": category}
    mock_assets_master_collection.find.assert_called_once_with(query)
    mock_assets_master_collection.count_documents.assert_called_once_with(query)
    assert result["total"] == 2
    assert len(result["data"]) == 2
    assert result["data"][0]["_id"] == "60d0fe4f3460595e63456789"
    assert result["data"][1]["asset_name"] == "Another Asset"

@pytest.mark.asyncio
async def test_count_assets(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test counting assets."""
    df_id = dummy_asset_data["df_id"]
    mock_assets_master_collection.count_documents.return_value = 5

    count = await asset_crud.count_assets(df_id)

    query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
    mock_assets_master_collection.count_documents.assert_called_once_with(query)
    assert count == 5

@pytest.mark.asyncio
async def test_get_assets_categories(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test getting unique asset categories."""
    df_id = dummy_asset_data["df_id"]
    mock_assets_master_collection.distinct.return_value = ["essential", "functional"]

    categories = await asset_crud.get_assets_categories(df_id)

    query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
    mock_assets_master_collection.distinct.assert_called_once_with("category", query)
    assert categories == ["essential", "functional"]

@pytest.mark.asyncio
async def test_get_total_cookie_count(asset_crud, mock_assets_master_collection, dummy_asset_data):
    """Test getting total cookie count from meta_cookies."""
    df_id = dummy_asset_data["df_id"]

    # Configure the mock cursor's async iteration for this specific test
    mock_assets_master_collection.find.return_value.__aiter__ = \
        lambda: _async_generator_helper([
            {"meta_cookies": {"cookies_count": 5}},
            {"meta_cookies": {"cookies_count": 10}},
            {"meta_cookies": None}, # Should be ignored
            {}, # Should be ignored
            {"meta_cookies": {"cookies_count": "invalid"}}, # Should be ignored
        ])

    total_cookies = await asset_crud.get_total_cookie_count(df_id)

    query = {"df_id": df_id, "asset_status": {"$in": ["draft", "published"]}}
    projection = {"meta_cookies": 1, "_id": 0}
    mock_assets_master_collection.find.assert_called_once_with(query, projection)
    assert total_cookies == 15 # 5 + 10
