import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
from app.crud.collection_point_crud import CollectionPointCrud


# ------------------ MOCK COLLECTION FIXTURE ------------------


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock()

    # Cursor mock for find()
    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return CollectionPointCrud(mock_collection)


@pytest.fixture
def dummy_data():
    return {
        "cp_name": "Test Collection Point",
        "df_id": "test_df_id",
        "asset_id": "test_asset_id",
        "cp_status": "draft",
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_create_cp(crud, mock_collection, dummy_data):
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    result = await crud.create_cp(dummy_data.copy())

    mock_collection.insert_one.assert_called_once()

    sent_data = mock_collection.insert_one.call_args[0][0]
    assert sent_data["cp_name"] == dummy_data["cp_name"]

    assert result["_id"] == "60d0fe4f3460595e63456789"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cp_id, find_one_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", {"cp_name": "Test Collection Point", "_id": ObjectId("60d0fe4f3460595e63456789")}, True),
        ("60d0fe4f3460595e63456781", None, False),
    ],
)
async def test_get_cp_master(crud, mock_collection, dummy_data, cp_id, find_one_return, expected_result):
    if find_one_return:
        find_one_return = {**dummy_data, **find_one_return}

    mock_collection.find_one.return_value = find_one_return

    result = await crud.get_cp_master(cp_id, dummy_data["df_id"])

    if expected_result:
        assert result["_id"] == cp_id
        assert result["cp_name"] == dummy_data["cp_name"]
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

    result = await crud.is_duplicate_name(dummy_data["cp_name"], dummy_data["asset_id"], dummy_data["df_id"])

    assert result is expected_result


@pytest.mark.asyncio
async def test_update_cp_by_id(crud, mock_collection, dummy_data):
    cp_id = "60d0fe4f3460595e63456789"

    mock_collection.find_one.return_value = {**dummy_data, "_id": ObjectId(cp_id)}

    result = await crud.update_cp_by_id(cp_id, dummy_data["df_id"], {"cp_name": "Updated"})

    mock_collection.update_one.assert_called_once()
    assert result["_id"] == cp_id
    assert result["cp_name"] == dummy_data["cp_name"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "additional_filters, expected_total, expected_data_len",
    [
        (None, 2, 2),
        ({"cp_status": "published"}, 1, 1),
    ],
)
async def test_get_all_cps(crud, mock_collection, dummy_data, additional_filters, expected_total, expected_data_len):
    if additional_filters:
        mock_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "cp_status": "published"},
            ]
        )
    else:
        mock_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789")},
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "cp_name": "Another"},
            ]
        )

    mock_collection.count_documents.return_value = expected_total

    result = await crud.get_all_cps(dummy_data["df_id"], 0, 10, additional_filters)

    assert result["total"] == expected_total
    assert len(result["data"]) == expected_data_len


@pytest.mark.asyncio
async def test_count_collection_points(crud, mock_collection):
    mock_collection.count_documents.return_value = 5

    result = await crud.count_collection_points("df123")

    assert result == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name, method_args",
    [
        ("update_cp_by_id", ("not_valid_id", "df123", {})),
        ("get_cp_master", ("invalid_id", "df123")),
    ],
)
async def test_invalid_id_http_exception(crud, method_name, method_args):
    with pytest.raises(HTTPException) as exc:
        await getattr(crud, method_name)(*method_args)

    assert exc.value.status_code == 422
