import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.consent_artifact_crud import ConsentArtifactCRUD


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
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return ConsentArtifactCRUD(mock_collection)


@pytest.fixture
def dummy_consent_artifact_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "cp_id": "cp123",
        "artifact": {
            "data_fiduciary": {"agreement_date": "2023-01-01T00:00:00Z"},
            "consent_scope": {
                "data_elements": [
                    {"de_id": "de1", "consents": [{"purpose_id": "p1"}]},
                    {"de_id": "de2", "consents": [{"purpose_id": "p2"}, {"purpose_id": "p3"}]},
                ]
            },
        },
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
async def test_get_filtered_consent_artifacts(crud, mock_collection, dummy_consent_artifact_data):
    mock_collection.find.return_value.__aiter__.return_value = iter([dummy_consent_artifact_data])
    
    query = {"some_field": "some_value"}
    sort_dir = 1
    skip = 0
    limit = 10

    result_cursor = crud.get_filtered_consent_artifacts(query, sort_dir, skip, limit)
    
    # Iterate through the cursor to trigger the async operation
    result_data = []
    async for doc in result_cursor:
        result_data.append(doc)

    mock_collection.find.assert_called_once_with(query)
    mock_collection.find.return_value.sort.assert_called_once_with("artifact.data_fiduciary.agreement_date", sort_dir)
    mock_collection.find.return_value.skip.assert_called_once_with(skip)
    mock_collection.find.return_value.limit.assert_called_once_with(limit)
    assert len(result_data) == 1
    assert str(result_data[0]["_id"]) == str(dummy_consent_artifact_data["_id"])


@pytest.mark.asyncio
async def test_count_filtered_consent_artifacts(crud, mock_collection):
    mock_collection.count_documents.return_value = 5
    query = {"some_field": "some_value"}

    result = await crud.count_filtered_consent_artifacts(query)

    mock_collection.count_documents.assert_called_once_with(query)
    assert result == 5


@pytest.mark.asyncio
async def test_get_one_consent_artifacts(crud, mock_collection, dummy_consent_artifact_data):
    mock_collection.find_one.return_value = dummy_consent_artifact_data
    query = {"_id": ObjectId("60d0fe4f3460595e63456789")}

    result = await crud.get_one_consent_artifacts(query)

    mock_collection.find_one.assert_called_once_with(query)
    assert result["_id"] == dummy_consent_artifact_data["_id"]


@pytest.mark.asyncio
async def test_get_expiring_consent_artifacts(crud, mock_collection, dummy_consent_artifact_data):
    mock_collection.find.return_value.__aiter__.return_value = iter([dummy_consent_artifact_data])
    query = {"expiration_date": {"$lt": "some_date"}}

    result_cursor = crud.get_expiring_consent_artifacts(query)

    # Iterate through the cursor to trigger the async operation
    result_data = []
    async for doc in result_cursor:
        result_data.append(doc)

    mock_collection.find.assert_called_once_with(query)
    assert len(result_data) == 1
    assert result_data[0]["_id"] == dummy_consent_artifact_data["_id"]


@pytest.mark.asyncio
async def test_count_collected_data_elements(crud, mock_collection, dummy_consent_artifact_data):
    mock_collection.find.return_value.__aiter__.return_value = iter([
        dummy_consent_artifact_data,
        {
            "_id": ObjectId(),
            "cp_id": "cp456",
            "artifact": {
                "consent_scope": {
                    "data_elements": [
                        {"de_id": "de1"}, # Duplicate de_id
                        {"de_id": "de3"},
                    ]
                }
            }
        },
        # Document with no artifact or malformed structure
        {"_id": ObjectId(), "cp_id": "cp789"},
        {"_id": ObjectId(), "cp_id": "cp101", "artifact": {"consent_scope": {}}}
    ])
    query = {"status": "active"}

    result = await crud.count_collected_data_elements(query)

    mock_collection.find.assert_called_once_with(query)
    # Expected unique de_ids: de1, de2, de3
    assert result == 3


@pytest.mark.asyncio
async def test_count_collected_purposes(crud, mock_collection, dummy_consent_artifact_data):
    mock_collection.find.return_value.__aiter__.return_value = iter([
        dummy_consent_artifact_data,
        {
            "_id": ObjectId(),
            "cp_id": "cp456",
            "artifact": {
                "consent_scope": {
                    "data_elements": [
                        {"de_id": "de4", "consents": [{"purpose_id": "p1"}, {"purpose_id": "p4"}]},
                    ]
                }
            }
        },
        # Document with no artifact or malformed structure
        {"_id": ObjectId(), "cp_id": "cp789"},
        {"_id": ObjectId(), "cp_id": "cp101", "artifact": {"consent_scope": {"data_elements": [{"de_id": "de5"}]}}}
    ])
    query = {"status": "active"}

    result = await crud.count_collected_purposes(query)

    mock_collection.find.assert_called_once_with(query)
    # Expected unique purpose_ids: p1, p2, p3, p4
    assert result == 4


@pytest.mark.asyncio
async def test_count_collected_collection_points(crud, mock_collection):
    mock_collection.distinct.return_value = ["cp123", "cp456", "cp789"]
    query = {"status": "active"}

    result = await crud.count_collected_collection_points(query)

    mock_collection.distinct.assert_called_once_with("cp_id", query)
    assert result == 3
