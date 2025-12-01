import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
import httpx
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud.purpose_crud import PurposeCRUD


def dummy_object_id():
    return str(ObjectId())


@pytest.fixture
def mock_purpose_master_collection():
    """A mock for the purpose_master_collection that allows for chained calls."""
    collection = MagicMock(spec=AsyncIOMotorCollection)
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()

    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor

    async def async_iterator(docs):
        for doc in docs:
            yield doc

    cursor.__aiter__ = MagicMock(return_value=async_iterator([]))

    collection.find.return_value = cursor
    return collection


@pytest.fixture
def mock_purpose_template_collection(mock_purpose_master_collection):

    return AsyncMock()


@pytest.fixture
def mock_purpose_master_translated_collection(mock_purpose_master_collection):
    return AsyncMock()


@pytest.fixture
def purpose_crud(
    mock_purpose_template_collection,
    mock_purpose_master_collection,
    mock_purpose_master_translated_collection,
):
    return PurposeCRUD(
        purpose_template_collection=mock_purpose_template_collection,
        purpose_master_collection=mock_purpose_master_collection,
        purpose_master_translated_collection=mock_purpose_master_translated_collection,
    )


@pytest.mark.asyncio
async def test_create_purpose(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    purpose_data = {"purpose_title": "Test"}
    mock_purpose_master_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId(purpose_id))

    result = await purpose_crud.create_purpose(purpose_data)

    mock_purpose_master_collection.insert_one.assert_called_once_with(purpose_data)
    assert result["_id"] == purpose_id


@pytest.mark.asyncio
async def test_get_purpose_template(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    doc = {"_id": ObjectId(purpose_id)}
    mock_purpose_master_collection.find_one.return_value = doc

    result = await purpose_crud.get_purpose_template(purpose_id)

    assert result["_id"] == purpose_id
    mock_purpose_master_collection.find_one.assert_called_once_with({"_id": ObjectId(purpose_id)})


@pytest.mark.asyncio
async def test_update_purpose(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    df_id = "test-df"
    update_data = {"purpose_title": "Updated"}
    updated_doc = {"_id": ObjectId(purpose_id), **update_data}

    mock_purpose_master_collection.find_one.return_value = updated_doc

    result = await purpose_crud.update_purpose(purpose_id, df_id, update_data)

    mock_purpose_master_collection.update_one.assert_called_once_with({"_id": ObjectId(purpose_id), "df_id": df_id}, {"$set": update_data})
    assert result["_id"] == purpose_id


@pytest.mark.asyncio
async def test_delete_purpose_template(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    mock_purpose_master_collection.delete_one.return_value = MagicMock(deleted_count=1)

    result = await purpose_crud.delete_purpose_template(purpose_id)

    assert result is True
    mock_purpose_master_collection.delete_one.assert_called_once_with({"_id": ObjectId(purpose_id)})


@pytest.mark.asyncio
async def test_get_all_purpose_master(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    df_id = "test-df"
    docs = [{"_id": ObjectId(), "purpose_title": "P1"}, {"_id": ObjectId(), "purpose_title": "P2"}]

    async def async_iterator(items):
        for item in items:
            yield item

    mock_purpose_master_collection.find.return_value.__aiter__.return_value = async_iterator(docs)
    mock_purpose_master_collection.count_documents.return_value = len(docs)

    result = await purpose_crud.get_all_purpose_master(df_id, 0, 10)

    assert len(result["data"]) == 2
    assert result["total"] == 2
    mock_purpose_master_collection.find.assert_called_once_with({"df_id": df_id, "purpose_status": {"$in": ["draft", "published"]}})
    mock_purpose_master_collection.count_documents.assert_called_once()


@pytest.mark.asyncio
async def test_get_purpose_master(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    df_id = "test-df"
    doc = {"_id": ObjectId(purpose_id)}
    mock_purpose_master_collection.find_one.return_value = doc

    result = await purpose_crud.get_purpose_master(purpose_id, df_id)

    assert result["_id"] == purpose_id
    mock_purpose_master_collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_create_purpose_master(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    purpose_id = dummy_object_id()
    purpose_data = {"purpose_title": "Test"}
    mock_purpose_master_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId(purpose_id))

    result = await purpose_crud.create_purpose_master(purpose_data)

    assert result["_id"] == purpose_id


@pytest.mark.asyncio
async def test_is_duplicate_name(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    mock_purpose_master_collection.find_one.return_value = {"_id": ObjectId()}
    result = await purpose_crud.is_duplicate_name("title", "df_id")
    assert result is True


@pytest.mark.asyncio
async def test_is_not_duplicate_name(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    mock_purpose_master_collection.find_one.return_value = None
    result = await purpose_crud.is_duplicate_name("title", "df_id")
    assert result is False


@pytest.mark.asyncio
async def test_count_consent_purposes(purpose_crud: PurposeCRUD, mock_purpose_master_collection: MagicMock):
    mock_purpose_master_collection.count_documents.return_value = 10
    result = await purpose_crud.count_consent_purposes("df_id")
    assert result == 10


@pytest.mark.asyncio
async def test_get_all_purpose_templates(purpose_crud: PurposeCRUD, monkeypatch):
    mock_response_json = {"data": "test"}

    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_json
    mock_response.raise_for_status = MagicMock()

    mock_async_client = MagicMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)

    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_async_client

    monkeypatch.setattr(httpx, "AsyncClient", MagicMock(return_value=async_context_manager))

    result = await purpose_crud.get_all_purpose_templates()

    mock_async_client.get.assert_called_once()
    assert result == mock_response_json


@pytest.mark.asyncio
async def test_get_all_purpose_templates_with_all_params(purpose_crud: PurposeCRUD, monkeypatch):
    mock_response_json = {"data": "test"}

    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_json
    mock_response.raise_for_status = MagicMock()

    captured_params = {}

    async def mock_get(url, params=None):
        nonlocal captured_params
        captured_params = params
        return mock_response

    mock_async_client = MagicMock()
    mock_async_client.get = AsyncMock(side_effect=mock_get)

    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_async_client

    monkeypatch.setattr(httpx, "AsyncClient", MagicMock(return_value=async_context_manager))

    result = await purpose_crud.get_all_purpose_templates(
        offset=5, limit=25, id="abc123", industry="finance", sub_category="loan", title="Personal Loan"
    )

    assert result == mock_response_json
    mock_async_client.get.assert_called_once()

    assert captured_params == {
        "offset": 5,
        "limit": 25,
        "id": "abc123",
        "industry": "finance",
        "sub_category": "loan",
        "title": "Personal Loan",
    }
