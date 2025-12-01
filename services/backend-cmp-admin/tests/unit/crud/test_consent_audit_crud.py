import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.consent_audit_crud import ConsentAuditCRUD


# ------------------ MOCK COLLECTION FIXTURE ------------------


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection for consent audit logs with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    # Mock cursor for find()
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.__aiter__.return_value = iter([]) # Default to empty iterator for async for loops

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return ConsentAuditCRUD(mock_collection)


@pytest.fixture
def dummy_audit_log_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "dp_id": "dp123",
        "df_id": "df123",
        "action": "consent_given",
        "timestamp": "2023-01-01T10:00:00Z",
    }


# ------------------ TESTS ------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "df_id, expected_query_df_id, expected_call_df_id",
    [
        ("df123", {"df_id": "df123"}, "df123"),  # With df_id
        (None, {}, None),  # Without df_id
    ],
)
async def test_get_logs(crud, mock_collection, dummy_audit_log_data, df_id, expected_query_df_id, expected_call_df_id):
    # Prepare dummy data for the iterator
    if df_id:
        mock_collection.find.return_value.__aiter__.return_value = iter([dummy_audit_log_data.copy()])
    else:
        # If df_id is None, the data should not include df_id in the query, so return all for dp_id
        log_data_no_df = dummy_audit_log_data.copy()
        del log_data_no_df["df_id"]
        mock_collection.find.return_value.__aiter__.return_value = iter([log_data_no_df])


    dp_id = dummy_audit_log_data["dp_id"]
    query = {"dp_id": dp_id}
    query.update(expected_query_df_id)

    result_cursor = crud.get_logs(dp_id, df_id)

    # Iterate through the cursor to trigger the async operation and retrieve results
    result_data = []
    async for doc in result_cursor:
        result_data.append(doc)

    mock_collection.find.assert_called_once_with(query)
    mock_collection.find.return_value.sort.assert_called_once_with("timestamp", 1)
    
    if expected_query_df_id:
        assert len(result_data) == 1
        assert result_data[0]["dp_id"] == dummy_audit_log_data["dp_id"]
        assert result_data[0]["df_id"] == dummy_audit_log_data["df_id"]
    else:
        assert len(result_data) == 1
        assert result_data[0]["dp_id"] == dummy_audit_log_data["dp_id"]
        assert "df_id" not in result_data[0] # Ensure df_id is not present when not filtered
