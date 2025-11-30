import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.incident_management_crud import IncidentCRUD
from pymongo import ASCENDING, DESCENDING
from datetime import datetime, UTC
from fastapi import HTTPException


@pytest.fixture
def mock_incident_collection():
    """Mocked Mongo collection for incidents with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.find_one = AsyncMock(return_value=None)
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock(return_value=0)
    collection.distinct = AsyncMock(return_value=[])

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_incident_collection):
    return IncidentCRUD(mock_incident_collection)


@pytest.fixture
def dummy_incident_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "df_id": "df123",
        "incident_name": "Test Incident",
        "incident_type": "Data Breach",
        "incident_sensitivity": "High",
        "status": "draft",
        "current_stage": "Identification",
        "created_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        "updated_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
    }


@pytest.mark.asyncio
async def test_find_duplicate(crud, mock_incident_collection, dummy_incident_data):
    mock_incident_collection.find_one.return_value = dummy_incident_data.copy()
    df_id = dummy_incident_data["df_id"]
    incident_name = dummy_incident_data["incident_name"]

    result = await crud.find_duplicate(df_id, incident_name)

    mock_incident_collection.find_one.assert_called_once_with({"df_id": df_id, "incident_name": incident_name, "status": "draft"})
    assert result == dummy_incident_data


@pytest.mark.asyncio
async def test_insert_incident(crud, mock_incident_collection, dummy_incident_data):
    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_incident_data["_id"]
    mock_incident_collection.insert_one.return_value = mock_insert_one_result

    incident_data_to_insert = dummy_incident_data.copy()
    del incident_data_to_insert["_id"]
    incident_data_to_insert["created_at"] = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    incident_data_to_insert["updated_at"] = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)

    result = await crud.insert_incident(incident_data_to_insert)

    mock_incident_collection.insert_one.assert_called_once_with(incident_data_to_insert)
    assert result == str(dummy_incident_data["_id"])


@pytest.mark.asyncio
async def test_update_incident(crud, mock_incident_collection, dummy_incident_data):
    incident_id = str(dummy_incident_data["_id"])
    update_data = {"incident_name": "Updated Incident Name"}

    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_incident_collection.update_one.return_value = mock_update_result

    await crud.update_incident(incident_id, update_data)

    mock_incident_collection.update_one.assert_called_once_with({"_id": ObjectId(incident_id)}, {"$set": update_data})


@pytest.mark.asyncio
async def test_get_incident_by_id(crud, mock_incident_collection, dummy_incident_data):
    mock_incident_collection.find_one.return_value = dummy_incident_data.copy()
    incident_id = str(dummy_incident_data["_id"])

    result = await crud.get_incident_by_id(incident_id)

    mock_incident_collection.find_one.assert_called_once_with({"_id": ObjectId(incident_id)})
    assert result == dummy_incident_data


@pytest.mark.asyncio
async def test_count_incidents(crud, mock_incident_collection):
    mock_incident_collection.count_documents.return_value = 5
    query = {"df_id": "df123"}

    result = await crud.count_incidents(query)

    mock_incident_collection.count_documents.assert_called_once_with(query)
    assert result == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_order, expected_sort_dir",
    [
        ("asc", ASCENDING),
        ("desc", DESCENDING),
        ("any_other", DESCENDING),
    ],
)
async def test_get_incidents(crud, mock_incident_collection, dummy_incident_data, sort_order, expected_sort_dir):
    mock_incident_collection.find.return_value.to_list.return_value = [dummy_incident_data.copy()]

    query = {"df_id": dummy_incident_data["df_id"]}
    skip = 0
    limit = 10

    result = await crud.get_incidents(query, sort_order, skip, limit)

    mock_incident_collection.find.assert_called_once_with(query)
    mock_incident_collection.find.return_value.sort.assert_called_once_with("created_at", expected_sort_dir)
    mock_incident_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_incident_collection.find.return_value.limit.assert_called_once_with(limit)
    assert len(result) == 1
    assert result[0] == dummy_incident_data


@pytest.mark.asyncio
async def test_get_filter_fields(crud, mock_incident_collection, dummy_incident_data):
    df_id = dummy_incident_data["df_id"]
    query = {"df_id": df_id}

    mock_incident_collection.distinct.side_effect = [
        ["Data Breach", "Security Incident"],
        ["High", "Medium", "Low"],
        ["draft", "published", "resolved"],
        ["Identification", "Containment", "Eradication"],
    ]

    result = await crud.get_filter_fields(df_id)

    mock_incident_collection.distinct.assert_any_call("incident_type", query)
    mock_incident_collection.distinct.assert_any_call("incident_sensitivity", query)
    mock_incident_collection.distinct.assert_any_call("status", query)
    mock_incident_collection.distinct.assert_any_call("current_stage", query)

    assert result == {
        "incident_type": sorted(["Data Breach", "Security Incident"]),
        "incident_sensitivity": sorted(["High", "Medium", "Low"]),
        "status": sorted(["draft", "published", "resolved"]),
        "current_stage": sorted(["Containment", "Eradication", "Identification"]),
    }


@pytest.mark.asyncio
async def test_publish_incident_success(crud, mock_incident_collection, dummy_incident_data):
    incident_id = str(dummy_incident_data["_id"])
    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_incident_collection.update_one.return_value = mock_update_result

    result = await crud.publish_incident(incident_id)

    mock_incident_collection.update_one.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_publish_incident_failure(crud, mock_incident_collection, dummy_incident_data):
    incident_id = str(dummy_incident_data["_id"])
    mock_update_result = MagicMock(matched_count=1, modified_count=0)
    mock_incident_collection.update_one.return_value = mock_update_result

    with pytest.raises(HTTPException) as exc_info:
        await crud.publish_incident(incident_id)

    assert exc_info.value.status_code == 500
    assert "Failed to publish incident" in exc_info.value.detail
    mock_incident_collection.update_one.assert_called_once()
