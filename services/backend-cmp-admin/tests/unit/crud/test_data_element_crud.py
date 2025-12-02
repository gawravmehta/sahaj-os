import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException
import httpx
from app.crud.data_element_crud import DataElementCRUD


@pytest.fixture
def mock_de_template_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def mock_de_master_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock()

    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def mock_de_master_translated_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)
    return collection


@pytest.fixture
def crud(
    mock_de_template_collection,
    mock_de_master_collection,
    mock_de_master_translated_collection,
):
    return DataElementCRUD(
        mock_de_template_collection,
        mock_de_master_collection,
        mock_de_master_translated_collection,
    )


@pytest.fixture
def dummy_data():
    return {
        "de_name": "Test Data Element",
        "df_id": "test_df_id",
        "de_status": "draft",
    }


@pytest.mark.asyncio
async def test_create_de(crud, mock_de_master_collection, dummy_data):
    mock_de_master_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d0fe4f3460595e63456789"))

    result = await crud.create_de(dummy_data.copy())

    mock_de_master_collection.insert_one.assert_called_once()

    sent_data = mock_de_master_collection.insert_one.call_args[0][0]
    assert sent_data["de_name"] == dummy_data["de_name"]

    assert result["_id"] == "60d0fe4f3460595e63456789"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "de_id, find_one_return, expected_result",
    [
        ("60d0fe4f3460595e63456789", {"de_name": "Test Data Element", "_id": ObjectId("60d0fe4f3460595e63456789")}, True),
        ("60d0fe4f3460595e63456781", None, False),
    ],
)
async def test_get_de_master(crud, mock_de_master_collection, dummy_data, de_id, find_one_return, expected_result):
    if find_one_return:
        find_one_return = {**dummy_data, **find_one_return}

    mock_de_master_collection.find_one.return_value = find_one_return

    result = await crud.get_de_master(de_id, dummy_data["df_id"])

    if expected_result:
        assert result["_id"] == de_id
        assert result["de_name"] == dummy_data["de_name"]
    else:
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "de_title, find_one_return, expected_result",
    [
        ("Test Data Element", {"de_name": "Test Data Element", "_id": ObjectId("60d0fe4f3460595e63456789")}, True),
        ("Non Existent Element", None, False),
    ],
)
async def test_get_de_master_by_name(crud, mock_de_master_collection, dummy_data, de_title, find_one_return, expected_result):
    if find_one_return:
        find_one_return = {**dummy_data, **find_one_return}

    mock_de_master_collection.find_one.return_value = find_one_return

    result = await crud.get_de_master_by_name(de_title, dummy_data["df_id"])

    if expected_result:
        assert result["de_name"] == de_title
    else:
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_core_identifier, expected_total, expected_data_len",
    [
        (True, 1, 1),
        (False, 1, 1),
        (None, 2, 2),
    ],
)
async def test_get_all_de_master(crud, mock_de_master_collection, dummy_data, is_core_identifier, expected_total, expected_data_len):
    if is_core_identifier is True:
        mock_de_master_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789"), "is_core_identifier": True},
            ]
        )
    elif is_core_identifier is False:
        mock_de_master_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "is_core_identifier": False},
            ]
        )
    else:
        mock_de_master_collection.find.return_value.__aiter__.return_value = iter(
            [
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e63456789"), "is_core_identifier": True},
                {**dummy_data, "_id": ObjectId("60d0fe4f3460595e6345678a"), "is_core_identifier": False},
            ]
        )

    mock_de_master_collection.count_documents.return_value = expected_total

    result = await crud.get_all_de_master(dummy_data["df_id"], 0, 10, is_core_identifier)

    assert result["total"] == expected_total
    assert len(result["data"]) == expected_data_len


@pytest.mark.asyncio
async def test_update_data_element_by_id(crud, mock_de_master_collection, dummy_data):
    de_id = "60d0fe4f3460595e63456789"

    mock_de_master_collection.find_one.return_value = {**dummy_data, "_id": ObjectId(de_id)}

    result = await crud.update_data_element_by_id(de_id, dummy_data["df_id"], {"de_name": "Updated"})

    mock_de_master_collection.update_one.assert_called_once()
    assert result["_id"] == de_id
    assert result["de_name"] == dummy_data["de_name"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "find_one_return, expected_result",
    [
        ({"_id": ObjectId()}, True),
        (None, False),
    ],
)
async def test_is_duplicate_name(crud, mock_de_master_collection, dummy_data, find_one_return, expected_result):
    mock_de_master_collection.find_one.return_value = find_one_return

    result = await crud.is_duplicate_name(dummy_data["de_name"], dummy_data["df_id"])

    assert result is expected_result


@pytest.mark.asyncio
async def test_count_data_elements(crud, mock_de_master_collection):
    mock_de_master_collection.count_documents.return_value = 5

    result = await crud.count_data_elements("df123")

    assert result == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name, method_args",
    [
        ("update_data_element_by_id", ("not_valid_id", "df123", {})),
        ("get_de_master", ("invalid_id", "df123")),
    ],
)
async def test_invalid_id_http_exception(crud, method_name, method_args):
    with pytest.raises(HTTPException) as exc:
        await getattr(crud, method_name)(*method_args)

    assert exc.value.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        ({"domain": "test_domain"}),
        ({"title": "test_title"}),
        ({"id": "test_id"}),
        ({"domain": "test_domain", "title": "test_title", "id": "test_id"}),
        ({}),
    ],
)
async def test_get_all_de_templates(crud, monkeypatch, params):
    mock_async_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [], "total": 0}
    mock_response.raise_for_status = MagicMock()

    mock_async_client.get = AsyncMock(return_value=mock_response)

    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_async_client

    monkeypatch.setattr(httpx, "AsyncClient", MagicMock(return_value=async_context_manager))

    result = await crud.get_all_de_templates(**params)

    httpx.AsyncClient.assert_called_once()

    mock_async_client.get.assert_called_once()
    call_args, call_kwargs = mock_async_client.get.call_args
    assert call_args[0] == f"{crud.external_base_url}/data-elements"

    expected_params = {"offset": 0, "limit": 20, **params}
    assert call_kwargs["params"] == expected_params

    mock_response.raise_for_status.assert_called_once()
    assert result == {"data": [], "total": 0}


@pytest.mark.asyncio
async def test_get_all_de_templates_http_error(crud, monkeypatch):
    mock_async_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())

    mock_async_client.get = AsyncMock(return_value=mock_response)

    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_async_client

    monkeypatch.setattr(httpx, "AsyncClient", MagicMock(return_value=async_context_manager))

    with pytest.raises(httpx.HTTPStatusError):
        await crud.get_all_de_templates()
