import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
from app.crud.assets_crud import AssetCrud


# ------------------ MOCK COLLECTION FIXTURE ------------------


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock()
    collection.distinct = AsyncMock()

    # Cursor mock for find()
    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return AssetCrud(mock_collection)


@pytest.fixture
def dummy_data():
    return {
        "asset_name": "Test Asset",
        "df_id": "test_df_id",
        "category": "essential",
        "asset_status": "draft",
        "meta_cookies": {"cookies_count": 5},
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_create_asset(crud, mock_collection, dummy_data):
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    result = await crud.create_asset(dummy_data.copy())

    mock_collection.insert_one.assert_called_once()

    sent_data = mock_collection.insert_one.call_args[0][0]
    assert sent_data["asset_name"] == dummy_data["asset_name"]

    assert result["_id"] == "60d0fe4f3460595e63456789"


@pytest.mark.asyncio
async def test_get_asset_found(crud, mock_collection, dummy_data):
    asset_id = "60d0fe4f3460595e63456789"

    mock_collection.find_one.return_value = {**dummy_data, "_id": ObjectId(asset_id)}

    result = await crud.get_asset(asset_id, dummy_data["df_id"])

    assert result["_id"] == asset_id
    assert result["asset_name"] == dummy_data["asset_name"]


@pytest.mark.asyncio
async def test_get_asset_not_found(crud, mock_collection):
    mock_collection.find_one.return_value = None

    result = await crud.get_asset("60d0fe4f3460595e63456781", "test_df_id")

    assert result is None


@pytest.mark.asyncio
async def test_is_duplicate_name_true(crud, mock_collection, dummy_data):
    mock_collection.find_one.return_value = {"_id": ObjectId()}

    result = await crud.is_duplicate_name(dummy_data["asset_name"], dummy_data["df_id"])

    assert result is True


@pytest.mark.asyncio
async def test_is_duplicate_name_false(crud, mock_collection, dummy_data):
    mock_collection.find_one.return_value = None

    result = await crud.is_duplicate_name(dummy_data["asset_name"], dummy_data["df_id"])

    assert result is False


@pytest.mark.asyncio
async def test_update_asset_by_id(crud, mock_collection, dummy_data):
    asset_id = "60d0fe4f3460595e63456789"

    mock_collection.find_one.return_value = {**dummy_data, "_id": ObjectId(asset_id)}

    result = await crud.update_asset_by_id(asset_id, dummy_data["df_id"], {"asset_name": "Updated"})

    mock_collection.update_one.assert_called_once()
    assert result["_id"] == asset_id
    assert result["asset_name"] == dummy_data["asset_name"]  # find_one returns dummy_data


@pytest.mark.asyncio
async def test_get_all_assets(crud, mock_collection, dummy_data):
    # Mock cursor __aiter__
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [
            {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
            {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "asset_name": "Another"},
        ]
    )

    mock_collection.count_documents.return_value = 2

    result = await crud.get_all_assets(dummy_data["df_id"], 0, 10, "essential")

    assert result["total"] == 2
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_count_assets(crud, mock_collection):
    mock_collection.count_documents.return_value = 5

    result = await crud.count_assets("df123")

    assert result == 5


@pytest.mark.asyncio
async def test_get_assets_categories(crud, mock_collection):
    mock_collection.distinct.return_value = ["essential", "functional"]

    result = await crud.get_assets_categories("df123")

    assert result == ["essential", "functional"]


@pytest.mark.asyncio
async def test_get_total_cookie_count(crud, mock_collection):
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [{"meta_cookies": {"cookies_count": 5}}, {"meta_cookies": {"cookies_count": 10}}, {"meta_cookies": None}, {}]
    )

    result = await crud.get_total_cookie_count("df123")

    assert result == 15


@pytest.mark.asyncio
async def test_update_asset_invalid_id(crud):
    with pytest.raises(HTTPException) as exc:
        await crud.update_asset_by_id("not_valid_id", "df123", {})

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_get_asset_invalid_id(crud):
    with pytest.raises(HTTPException) as exc:
        await crud.get_asset("invalid_id", "df123")

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_asset_does_not_mutate_input(crud, mock_collection, dummy_data):
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    original = dummy_data.copy()

    await crud.create_asset(original)

    # Ensure original data is untouched
    assert "_id" not in original


@pytest.mark.asyncio
async def test_get_all_assets_without_category(crud, mock_collection, dummy_data):
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [
            {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
        ]
    )
    mock_collection.count_documents.return_value = 1

    result = await crud.get_all_assets(dummy_data["df_id"], 0, 10, None)

    # Ensure category filter was NOT added
    called_query = mock_collection.find.call_args[0][0]
    assert "category" not in called_query

    assert result["total"] == 1
    assert len(result["data"]) == 1


@pytest.mark.asyncio
async def test_get_total_cookie_count_with_invalid_values(crud, mock_collection):
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [
            {"meta_cookies": {"cookies_count": 5}},
            {"meta_cookies": {"cookies_count": "10"}},
            {"meta_cookies": 5},
            {"meta_cookies": []},
            {"meta_cookies": "random"},
            {},
        ]
    )

    result = await crud.get_total_cookie_count("df123")

    assert result == 5
