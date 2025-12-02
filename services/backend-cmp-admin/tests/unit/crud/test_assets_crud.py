import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
from app.crud.assets_crud import AssetCrud


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock()
    collection.distinct = AsyncMock()

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


@pytest.mark.asyncio
async def test_create_asset(crud, mock_collection, dummy_data):
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    result = await crud.create_asset(dummy_data.copy())

    mock_collection.insert_one.assert_called_once()

    sent_data = mock_collection.insert_one.call_args[0][0]
    assert sent_data["asset_name"] == dummy_data["asset_name"]

    assert result["_id"] == "60d0fe4f3460595e63456789"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "asset_id, find_one_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", {"asset_name": "Test Asset", "_id": ObjectId("60d0fe4f3460595e63456789")}, True),
        ("60d0fe4f3460595e63456781", None, False),
    ],
)
async def test_get_asset(crud, mock_collection, dummy_data, asset_id, find_one_return, expected_result):
    if find_one_return:
        find_one_return = {**dummy_data, **find_one_return}

    mock_collection.find_one.return_value = find_one_return

    result = await crud.get_asset(asset_id, dummy_data["df_id"])

    if expected_result:
        assert result["_id"] == asset_id
        assert result["asset_name"] == dummy_data["asset_name"]
    else:
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "find_one_return, expected_result",
    [
        ({"_id": ObjectId()}, True),
        (None, False),
    ],
)
async def test_is_duplicate_name(crud, mock_collection, dummy_data, find_one_return, expected_result):
    mock_collection.find_one.return_value = find_one_return

    result = await crud.is_duplicate_name(dummy_data["asset_name"], dummy_data["df_id"])

    assert result is expected_result


@pytest.mark.asyncio
async def test_update_asset_by_id(crud, mock_collection, dummy_data):
    asset_id = "60d0fe4f3460595e63456789"

    mock_collection.find_one.return_value = {**dummy_data, "_id": ObjectId(asset_id)}

    result = await crud.update_asset_by_id(asset_id, dummy_data["df_id"], {"asset_name": "Updated"})

    mock_collection.update_one.assert_called_once()
    assert result["_id"] == asset_id
    assert result["asset_name"] == dummy_data["asset_name"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "category, expected_total, expected_data_len",
    [
        ("essential", 2, 2),
        (None, 1, 1),
    ],
)
async def test_get_all_assets(crud, mock_collection, dummy_data, category, expected_total, expected_data_len):
    if category:
        mock_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "asset_name": "Another"},
            ]
        )
    else:
        mock_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
            ]
        )

    mock_collection.count_documents.return_value = expected_total

    result = await crud.get_all_assets(dummy_data["df_id"], 0, 10, category)

    assert result["total"] == expected_total
    assert len(result["data"]) == expected_data_len


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
@pytest.mark.parametrize(
    "find_return, expected_total",
    [
        (
            [{"meta_cookies": {"cookies_count": 5}}, {"meta_cookies": {"cookies_count": 10}}, {"meta_cookies": None}, {}],
            15,
        ),
        (
            [
                {"meta_cookies": {"cookies_count": 5}},
                {"meta_cookies": {"cookies_count": "10"}},
                {"meta_cookies": 5},
                {"meta_cookies": []},
                {"meta_cookies": "random"},
                {},
            ],
            5,
        ),
    ],
)
async def test_get_total_cookie_count(crud, mock_collection, find_return, expected_total):
    mock_collection.find.return_value.__aiter__.return_value = iter(find_return)

    result = await crud.get_total_cookie_count("df123")

    assert result == expected_total


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name, method_args",
    [
        ("update_asset_by_id", ("not_valid_id", "df123", {})),
        ("get_asset", ("invalid_id", "df123")),
    ],
)
async def test_invalid_id_http_exception(crud, method_name, method_args):
    with pytest.raises(HTTPException) as exc:
        await getattr(crud, method_name)(*method_args)

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_asset_does_not_mutate_input(crud, mock_collection, dummy_data):
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    original = dummy_data.copy()

    await crud.create_asset(original)

    assert "_id" not in original
