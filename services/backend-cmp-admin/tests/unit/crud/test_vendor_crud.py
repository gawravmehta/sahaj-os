import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.vendor_crud import VendorCRUD
from pymongo import ASCENDING, DESCENDING


@pytest.fixture
def mock_vendor_collection():
    """Mocked Mongo collection for vendors with correct async behavior."""
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
    cursor.__aiter__.return_value = iter([])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def mock_purpose_collection():
    """Mocked Mongo collection for purposes with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)
    collection.update_one = AsyncMock()
    return collection


@pytest.fixture
def crud(mock_vendor_collection, mock_purpose_collection):
    return VendorCRUD(mock_vendor_collection, mock_purpose_collection)


@pytest.fixture
def dummy_vendor_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "name": "Test Vendor",
        "df_id": "df123",
        "status": "active",
        "dpr_country": "USA",
        "dpr_country_risk": "low",
        "industry": "IT",
        "processing_category": ["marketing", "analytics"],
        "cross_border": True,
        "sub_processor": False,
        "audit_status": {"audit_result": "pass"},
        "created_at": "2023-01-01T00:00:00Z",
    }


@pytest.mark.asyncio
async def test_get_vendor_by_id(crud, mock_vendor_collection, dummy_vendor_data):
    mock_vendor_collection.find_one.return_value = dummy_vendor_data.copy()
    vendor_id = str(dummy_vendor_data["_id"])

    result = await crud.get_vendor_by_id(vendor_id)

    mock_vendor_collection.find_one.assert_called_once_with({"_id": ObjectId(vendor_id), "status": {"$ne": "archived"}})
    assert result == dummy_vendor_data


@pytest.mark.asyncio
async def test_create_vendor(crud, mock_vendor_collection, dummy_vendor_data):
    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_vendor_data["_id"]
    mock_vendor_collection.insert_one.return_value = mock_insert_one_result

    vendor_data_to_create = dummy_vendor_data.copy()
    del vendor_data_to_create["_id"]

    result = await crud.create_vendor(vendor_data_to_create)

    mock_vendor_collection.insert_one.assert_called_once_with(vendor_data_to_create)
    assert result == mock_insert_one_result


@pytest.mark.asyncio
async def test_update_vendor(crud, mock_vendor_collection, dummy_vendor_data):
    vendor_id = str(dummy_vendor_data["_id"])
    update_data = {"name": "Updated Vendor Name"}

    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_vendor_collection.update_one.return_value = mock_update_result

    result = await crud.update_vendor(vendor_id, update_data)

    mock_vendor_collection.update_one.assert_called_once_with({"_id": ObjectId(vendor_id)}, {"$set": update_data})
    assert result == mock_update_result


@pytest.mark.asyncio
async def test_count_vendors(crud, mock_vendor_collection):
    mock_vendor_collection.count_documents.return_value = 10
    query = {"df_id": "df123"}

    result = await crud.count_vendors(query)

    mock_vendor_collection.count_documents.assert_called_once_with(query)
    assert result == 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_order, expected_sort_dir",
    [
        ("asc", ASCENDING),
        ("desc", DESCENDING),
        ("any_other", DESCENDING),
    ],
)
async def test_get_vendors(crud, mock_vendor_collection, dummy_vendor_data, sort_order, expected_sort_dir):
    mock_vendor_collection.find.return_value.__aiter__.return_value = iter([dummy_vendor_data.copy()])

    query = {"df_id": dummy_vendor_data["df_id"]}
    page = 1
    page_size = 10

    result = await crud.get_vendors(query, sort_order, page, page_size)

    mock_vendor_collection.find.assert_called_once_with(query)
    mock_vendor_collection.find.return_value.sort.assert_called_once_with("created_at", expected_sort_dir)
    mock_vendor_collection.find.return_value.skip.assert_called_once_with((page - 1) * page_size)
    mock_vendor_collection.find.return_value.limit.assert_called_once_with(page_size)
    assert len(result) == 1
    assert result[0]["_id"] == str(dummy_vendor_data["_id"])


@pytest.mark.asyncio
async def test_get_filter_fields(crud, mock_vendor_collection, dummy_vendor_data):
    df_id = dummy_vendor_data["df_id"]
    query = {"df_id": df_id, "status": {"$ne": "archived"}}

    mock_vendor_collection.distinct.side_effect = [
        ["USA", "IND"],
        ["low", "medium"],
        ["IT", "Finance"],
        ["pass", "fail"],
    ]
    mock_vendor_collection.find.return_value.__aiter__.return_value = iter(
        [
            {"processing_category": ["marketing", "analytics"]},
            {"processing_category": ["finance", "marketing"]},
            {"processing_category": ["hr"]},
            {},
            {"processing_category": "invalid_type"},
            {"processing_category": None},
        ]
    )

    result = await crud.get_filter_fields(df_id)

    mock_vendor_collection.distinct.assert_any_call("dpr_country", query)
    mock_vendor_collection.distinct.assert_any_call("dpr_country_risk", query)
    mock_vendor_collection.distinct.assert_any_call("industry", query)
    mock_vendor_collection.distinct.assert_any_call("audit_status.audit_result", query)

    mock_vendor_collection.find.assert_called_with(query, {"processing_category": 1})

    assert result == {
        "dpr_country": ["IND", "USA"],
        "dpr_country_risk": ["low", "medium"],
        "industry": ["Finance", "IT"],
        "processing_category": ["analytics", "finance", "hr", "marketing"],
        "cross_border": [True, False],
        "sub_processor": [True, False],
        "audit_result": ["fail", "pass"],
    }


@pytest.mark.asyncio
async def test_archive_vendor(crud, mock_vendor_collection, dummy_vendor_data):
    vendor_id = str(dummy_vendor_data["_id"])
    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_vendor_collection.update_one.return_value = mock_update_result

    result = await crud.archive_vendor(vendor_id)

    mock_vendor_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(vendor_id)},
        {"$set": {"status": "archived"}},
    )
    assert result == mock_update_result


@pytest.mark.asyncio
async def test_update_purpose_with_vendor(crud, mock_purpose_collection, dummy_vendor_data):
    purpose_id = "60d0fe4f3460595e6345678a"
    vendor_details = {
        "vendor_id": str(dummy_vendor_data["_id"]),
        "vendor_name": dummy_vendor_data["name"],
        "cross_border": dummy_vendor_data["cross_border"],
    }

    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_purpose_collection.update_one.return_value = mock_update_result

    result = await crud.update_purpose_with_vendor(purpose_id, vendor_details)

    mock_purpose_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(purpose_id)},
        {
            "$addToSet": {
                "data_processor_details": {
                    "data_processor_id": vendor_details["vendor_id"],
                    "data_processor_name": vendor_details["vendor_name"],
                    "cross_border_data_transfer": vendor_details["cross_border"],
                }
            }
        },
    )
    assert result == mock_update_result
