import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.cookie_crud import CookieCrud
from app.schemas.cookie_schema import CookieCreate


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()

    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return CookieCrud(mock_collection)


@pytest.fixture
def dummy_cookie_data():
    return {
        "cookie_name": "test_cookie",
        "website_id": "web123",
        "df_id": "df123",
        "hostname": "example.com",
        "path": "/",
        "cookie_status": "draft",
        "category": "necessary",
        "cookie_type": "first_party",
        "expires_after_days": 30,
        "description": "A test cookie",
    }


@pytest.mark.asyncio
async def test_create_cookie(crud, mock_collection, dummy_cookie_data):
    inserted_id = ObjectId("60d0fe4f3460595e63456789")
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    cookie_to_create = dummy_cookie_data.copy()
    result = await crud.create_cookie(cookie_to_create)

    mock_collection.insert_one.assert_called_once()

    actual_args_passed_to_insert = mock_collection.insert_one.call_args.args[0].copy()

    if "_id" in actual_args_passed_to_insert:
        del actual_args_passed_to_insert["_id"]

    assert actual_args_passed_to_insert == dummy_cookie_data

    assert result is not None
    assert result["_id"] == str(inserted_id)
    assert result["cookie_name"] == dummy_cookie_data["cookie_name"]


@pytest.mark.asyncio
async def test_create_cookie_insert_failed_returns_none(crud, mock_collection, dummy_cookie_data):
    """If Mongo returns inserted_id=None, function should return None."""

    mock_collection.insert_one.return_value = MagicMock(inserted_id=None)

    result = await crud.create_cookie(dummy_cookie_data.copy())

    mock_collection.insert_one.assert_called_once()
    assert result is None


@pytest.mark.asyncio
async def test_get_cookies_for_website(crud, mock_collection, dummy_cookie_data):
    cookie_id = ObjectId("60d0fe4f3460595e63456789")
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [
            {**dummy_cookie_data, "_id": cookie_id},
        ]
    )
    mock_collection.count_documents.return_value = 1

    website_id = dummy_cookie_data["website_id"]
    df_id = dummy_cookie_data["df_id"]
    offset = 0
    limit = 10

    result = await crud.get_cookies_for_website(website_id, df_id, offset, limit)

    query = {"website_id": website_id, "df_id": df_id, "cookie_status": {"$in": ["draft", "published"]}}
    mock_collection.find.assert_called_once_with(query)
    mock_collection.find.return_value.skip.assert_called_once_with(offset)
    mock_collection.find.return_value.limit.assert_called_once_with(limit)
    mock_collection.count_documents.assert_called_once_with(query)

    assert result["total"] == 1
    assert len(result["data"]) == 1
    assert result["data"][0]["_id"] == str(cookie_id)


@pytest.mark.asyncio
async def test_get_published_cookies_for_website(crud, mock_collection, dummy_cookie_data):
    cookie_id_1 = ObjectId("60d0fe4f3460595e63456789")
    cookie_id_2 = ObjectId("60d0fe4f3460595e6345678a")
    mock_collection.find.return_value.__aiter__.return_value = iter(
        [
            {**dummy_cookie_data, "_id": cookie_id_1, "cookie_status": "published"},
            {**dummy_cookie_data, "_id": cookie_id_2, "cookie_status": "published", "cookie_name": "another_cookie"},
        ]
    )

    website_id = dummy_cookie_data["website_id"]
    df_id = dummy_cookie_data["df_id"]

    result = await crud._get_published_cookies_for_website(website_id, df_id)

    query = {"website_id": website_id, "df_id": df_id, "cookie_status": "published"}
    mock_collection.find.assert_called_once_with(query)

    assert result["total"] == 2
    assert len(result["data"]) == 2
    assert result["data"][0]["_id"] == str(cookie_id_1)
    assert result["data"][1]["_id"] == str(cookie_id_2)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cookie_id, find_one_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", {"cookie_name": "test_cookie", "_id": ObjectId("60d0fe4f3460595e63456789")}, True),
        ("60d0fe4f3460595e63456781", None, False),
    ],
)
async def test_get_cookie_master(crud, mock_collection, dummy_cookie_data, cookie_id, find_one_return, expected_result):
    if find_one_return:
        find_one_return = {**dummy_cookie_data, **find_one_return}

    mock_collection.find_one.return_value = find_one_return

    result = await crud.get_cookie_master(cookie_id, dummy_cookie_data["df_id"])

    if expected_result:
        assert result["_id"] == cookie_id
        assert result["cookie_name"] == dummy_cookie_data["cookie_name"]
    else:
        assert result is None


@pytest.mark.asyncio
async def test_update_cookie_master(crud, mock_collection, dummy_cookie_data):
    cookie_id = "60d0fe4f3460595e63456789"
    updated_name = "Updated Cookie Name"

    mock_collection.find_one.return_value = {**dummy_cookie_data, "_id": ObjectId(cookie_id), "cookie_name": updated_name}

    update_data = {"cookie_name": updated_name}
    result = await crud.update_cookie_master(cookie_id, dummy_cookie_data["df_id"], update_data)

    query = {"_id": ObjectId(cookie_id), "df_id": dummy_cookie_data["df_id"]}
    mock_collection.update_one.assert_called_once_with(query, {"$set": update_data})
    mock_collection.find_one.assert_called_with({"_id": ObjectId(cookie_id)})

    assert result["_id"] == cookie_id
    assert result["cookie_name"] == updated_name


@pytest.mark.asyncio
async def test_delete_cookie_master(crud, mock_collection):
    cookie_id = "60d0fe4f3460595e63456789"
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

    result = await crud.delete_cookie_master(cookie_id)

    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(cookie_id)})
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "count_documents_return, expected_result",
    [
        (1, True),
        (0, False),
    ],
)
async def test_is_duplicate(crud, mock_collection, dummy_cookie_data, count_documents_return, expected_result):
    mock_collection.count_documents.return_value = count_documents_return

    cookie_data_for_check = {
        "cookie_name": dummy_cookie_data["cookie_name"],
        "hostname": dummy_cookie_data["hostname"],
        "path": dummy_cookie_data["path"],
    }
    result = await crud.is_duplicate(cookie_data_for_check, dummy_cookie_data["website_id"])

    query = {
        "website_id": dummy_cookie_data["website_id"],
        "cookie_name": cookie_data_for_check["cookie_name"],
        "hostname": cookie_data_for_check["hostname"],
        "path": cookie_data_for_check.get("path", "/"),
        "cookie_status": {"$in": ["draft", "published"]},
    }
    mock_collection.count_documents.assert_called_once_with(query)
    assert result is expected_result
