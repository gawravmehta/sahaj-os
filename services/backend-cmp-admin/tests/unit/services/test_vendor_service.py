import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from bson import ObjectId

from app.services.vendor_service import VendorService
from app.crud.vendor_crud import VendorCRUD
from app.schemas.vendor_schema import CreateMyVendor


# -------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------
@pytest.fixture
def mock_vendor_crud():
    """CRUD layer mock."""
    crud = MagicMock(spec=VendorCRUD)
    crud.update_purpose_with_vendor = AsyncMock()  # required in make_it_publish
    return crud


@pytest.fixture
def vendor_service(mock_vendor_crud):
    """VendorService with mocked CRUD + mocked user collection."""
    mock_user_collection = AsyncMock()
    mock_user_collection.find_one.return_value = {"first_name": "John", "last_name": "Doe"}

    return VendorService(
        crud=mock_vendor_crud,
        user_collection=mock_user_collection,
        business_logs_collection="test_logs",
    )


@pytest.fixture
def current_user_data():
    return {"_id": str(ObjectId()), "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def add_vendor_data():
    return CreateMyVendor(
        dpr_name="Test Vendor",
        dpr_country="USA",
    )


# -------------------------------------------------------------------
# CREATE / UPDATE VENDOR
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_vendor_success(vendor_service, mock_vendor_crud, current_user_data, add_vendor_data, monkeypatch):
    mock_vendor_crud.create_vendor.return_value = MagicMock(inserted_id=ObjectId())

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.create_or_update_vendor(
        vendor_id=None,
        add_vendor=add_vendor_data,
        current_user=current_user_data,
    )

    mock_vendor_crud.create_vendor.assert_called_once()
    assert result["message"] == "Vendor created successfully"
    assert "vendor_id" in result

    mock_log.assert_awaited()  # FIX


@pytest.mark.asyncio
async def test_update_vendor_success(vendor_service, mock_vendor_crud, current_user_data, add_vendor_data, monkeypatch):
    vendor_id = str(ObjectId())
    mock_vendor_crud.get_vendor_by_id.return_value = {"_id": vendor_id, "dpr_name": "Old Name"}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.create_or_update_vendor(
        vendor_id=vendor_id,
        add_vendor=add_vendor_data,
        current_user=current_user_data,
    )

    mock_vendor_crud.update_vendor.assert_called_once()
    assert result["message"] == "Vendor updated successfully"
    assert result["vendor_id"] == vendor_id

    mock_log.assert_awaited()


# -------------------------------------------------------------------
# GET ALL MY VENDORS
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_all_my_vendors_success(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    mock_vendor_crud.count_vendors.return_value = 0
    mock_vendor_crud.get_vendors.return_value = []
    mock_vendor_crud.get_filter_fields.return_value = {}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.get_all_my_vendors(
        current_user=current_user_data,
        dpr_country=None,
        dpr_country_risk=None,
        industry=None,
        processing_category=None,
        cross_border=None,
        sub_processor=None,
        audit_result=None,
        search=None,
        sort_order="asc",
        page=1,
        page_size=10,
    )

    assert "pagination" in result
    mock_log.assert_awaited()


# -------------------------------------------------------------------
# GET ONE VENDOR
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_one_vendor_success(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    vendor_id = str(ObjectId())
    mock_vendor_crud.get_vendor_by_id.return_value = {"_id": vendor_id, "created_by": ObjectId()}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.get_one_vendor(vendor_id, current_user_data)

    assert result["_id"] == vendor_id
    assert "created_by_name" in result

    mock_log.assert_awaited()


@pytest.mark.asyncio
async def test_get_one_vendor_not_found(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    vendor_id = str(ObjectId())
    mock_vendor_crud.get_vendor_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await vendor_service.get_one_vendor(vendor_id, current_user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "vendor not found" in exc.value.detail

    mock_log.assert_awaited()


# -------------------------------------------------------------------
# DELETE VENDOR
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_vendor_success(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    vendor_id = str(ObjectId())

    mock_vendor_crud.get_vendor_by_id.return_value = {"status": "active"}

    # FIXED: archive_vendor must be AsyncMock
    mock_vendor_crud.archive_vendor = AsyncMock(
        return_value=MagicMock(modified_count=1)
    )

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.delete_vendor(vendor_id, current_user_data)

    assert result["message"] == "Vendor archived successfully"
    mock_log.assert_awaited()



@pytest.mark.asyncio
async def test_delete_vendor_not_found(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    vendor_id = str(ObjectId())
    mock_vendor_crud.get_vendor_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await vendor_service.delete_vendor(vendor_id, current_user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Vendor not present" in exc.value.detail

    mock_log.assert_awaited()


# -------------------------------------------------------------------
# MAKE IT PUBLISH
# -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_make_it_publish_success(vendor_service, mock_vendor_crud, current_user_data, monkeypatch):
    vendor_id = str(ObjectId())
    mock_vendor_crud.get_vendor_by_id.return_value = {
        "_id": vendor_id,
        "dpr_name": "TestVendor",
        "cross_border": False,
        "data_processing_activity": [],
    }

    mock_vendor_crud.update_vendor.return_value = MagicMock(modified_count=1)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.vendor_service.log_business_event", mock_log)

    result = await vendor_service.make_it_publish(vendor_id, current_user_data)

    assert result["message"] == "Vendor published successfully"
    assert "api_key" in result

    mock_log.assert_awaited()
