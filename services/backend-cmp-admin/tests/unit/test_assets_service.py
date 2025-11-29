import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC
from fastapi import HTTPException, status
from bson import ObjectId

from app.services.assets_service import AssetService
from app.crud.assets_crud import AssetCrud
from app.schemas.assets_schema import AssetInDB, MetaCookies


@pytest.fixture
def mock_asset_crud():
    """Fixture for a mock AssetCrud instance."""
    return AsyncMock(spec=AssetCrud)

@pytest.fixture
def mock_business_logs_collection():
    """Fixture for a mock business logs collection name."""
    return "mock_business_logs"

@pytest.fixture
def asset_service(mock_asset_crud, mock_business_logs_collection):
    """Fixture for an AssetService instance."""
    return AssetService(mock_asset_crud, mock_business_logs_collection)

@pytest.fixture
def dummy_user():
    """Fixture for dummy user data."""
    return {"_id": "user_123", "email": "testuser@example.com", "df_id": "test_df_id"}

@pytest.fixture
def dummy_asset_data_create():
    """Fixture for dummy asset data for creation."""
    return {
        "asset_name": "New Test Asset",
        "category": "website",
        "description": "A new asset for testing",
    }

@pytest.fixture
def dummy_asset_in_db(dummy_user):
    """Fixture for a dummy asset as it would appear in the database."""
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "asset_name": "Existing Test Asset",
        "df_id": dummy_user["df_id"],
        "created_by": dummy_user["_id"],
        "asset_status": "draft",
        "category": "website",
        "meta_cookies": {"cookies_count": 0},
        "created_at": datetime.now(UTC),
    }

@pytest.mark.asyncio
@patch("app.utils.business_logger.log_business_event", AsyncMock())
async def test_create_asset_success(
    mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_data_create, dummy_asset_in_db
):
    """Test successful asset creation."""
    mock_asset_crud.is_duplicate_name.return_value = False
    mock_asset_crud.create_asset.return_value = {
        **dummy_asset_data_create,
        "_id": str(dummy_asset_in_db["_id"]),
        "df_id": dummy_user["df_id"],
        "created_by": dummy_user["_id"],
        "asset_status": "draft",
    }

    created_asset = await asset_service.create_asset(dummy_asset_data_create.copy(), dummy_user)

    mock_asset_crud.is_duplicate_name.assert_called_once_with(
        asset_name=dummy_asset_data_create["asset_name"], df_id=dummy_user["df_id"]
    )
    mock_asset_crud.create_asset.assert_called_once()
    assert created_asset["asset_name"] == dummy_asset_data_create["asset_name"]
    assert created_asset["df_id"] == dummy_user["df_id"]
    assert created_asset["asset_status"] == "draft"
    mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_create_asset_duplicate_name(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_data_create
# ):
#     """Test asset creation with a duplicate name."""
#     mock_asset_crud.is_duplicate_name.return_value = True

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.create_asset(dummy_asset_data_create, dummy_user)

#     assert exc_info.value.status_code == status.HTTP_409_CONFLICT
#     assert "An Asset with the same name already exists." in exc_info.value.detail
#     mock_asset_crud.create_asset.assert_not_called()
#     mock_log_business_event.assert_not_called()

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_update_asset_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful asset update."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     update_data = {"asset_name": "Revised Asset Name"}

#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id} # Simulate conversion to str
#     mock_asset_crud.is_duplicate_name.return_value = False
#     mock_asset_crud.update_asset_by_id.return_value = {
#         **dummy_asset_in_db,
#         "_id": asset_id,
#         "asset_name": update_data["asset_name"],
#         "updated_by": dummy_user["_id"],
#     }

#     updated_asset = await asset_service.update_asset(asset_id, update_data, dummy_user)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     mock_asset_crud.is_duplicate_name.assert_called_once_with(
#         asset_name=update_data["asset_name"], df_id=dummy_user["df_id"]
#     )
#     mock_asset_crud.update_asset_by_id.assert_called_once()
#     assert updated_asset["asset_name"] == update_data["asset_name"]
#     assert updated_asset["updated_by"] == dummy_user["_id"]
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# async def test_update_asset_not_found(asset_service, mock_asset_crud, dummy_user):
#     """Test updating a non-existent asset."""
#     asset_id = "60d0fe4f3460595e63456789"
#     update_data = {"asset_name": "Non-existent Asset"}

#     mock_asset_crud.get_asset.return_value = None

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.update_asset(asset_id, update_data, dummy_user)

#     assert exc_info.value.status_code == 404
#     assert "Asset not found." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_update_asset_not_draft(asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db):
#     """Test updating an asset that is not in 'draft' status."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     update_data = {"asset_name": "Updated Name"}
#     published_asset = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "published"}

#     mock_asset_crud.get_asset.return_value = published_asset

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.update_asset(asset_id, update_data, dummy_user)

#     assert exc_info.value.status_code == 400
#     assert "Only Assets in draft status can be updated." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_update_asset_duplicate_name_on_update(
#     asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test updating an asset to a name that already exists."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     update_data = {"asset_name": "Existing Asset Name"}

#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id}
#     mock_asset_crud.is_duplicate_name.return_value = True

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.update_asset(asset_id, update_data, dummy_user)

#     assert exc_info.value.status_code == 400
#     assert "An Asset with name 'Existing Asset Name' already exists." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_update_asset_cookie_fields_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful update of asset cookie fields for a 'website' category asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     meta_cookies_update = MetaCookies(cookies_count=10, scripts=["script1.js"])

#     # Ensure the asset is a "website" category
#     website_asset = {
#         **dummy_asset_in_db,
#         "_id": asset_id,
#         "category": "website",
#         "meta_cookies": {"cookies_count": 5, "scripts": ["old_script.js"]},
#     }
#     mock_asset_crud.get_asset.return_value = website_asset

#     updated_asset_data = {
#         **website_asset,
#         "meta_cookies": {"cookies_count": 10, "scripts": ["script1.js"]},
#         "updated_by": dummy_user["_id"],
#     }
#     mock_asset_crud.update_asset_by_id.return_value = updated_asset_data

#     updated = await asset_service.update_asset_cookie_fields(asset_id, dummy_user, meta_cookies_update)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     mock_asset_crud.update_asset_by_id.assert_called_once()
#     assert updated["meta_cookies"]["cookies_count"] == 10
#     assert "script1.js" in updated["meta_cookies"]["scripts"]
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# async def test_update_asset_cookie_fields_not_found(asset_service, mock_asset_crud, dummy_user):
#     """Test updating cookie fields for a non-existent asset."""
#     asset_id = "60d0fe4f3460595e63456789"
#     meta_cookies_update = MetaCookies(cookies_count=1)
#     mock_asset_crud.get_asset.return_value = None

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.update_asset_cookie_fields(asset_id, dummy_user, meta_cookies_update)

#     assert exc_info.value.status_code == 404
#     assert "Asset not found" in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_update_asset_cookie_fields_not_website_category(
#     asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test updating cookie fields for a non-'website' category asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     meta_cookies_update = MetaCookies(cookies_count=1)
#     non_website_asset = {**dummy_asset_in_db, "_id": asset_id, "category": "mobile_app"}
#     mock_asset_crud.get_asset.return_value = non_website_asset

#     updated = await asset_service.update_asset_cookie_fields(asset_id, dummy_user, meta_cookies_update)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     mock_asset_crud.update_asset_by_id.assert_not_called()
#     assert updated is None

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_publish_asset_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful publishing of a draft asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "draft"}
#     mock_asset_crud.update_asset_by_id.return_value = {
#         **dummy_asset_in_db,
#         "_id": asset_id,
#         "asset_status": "published",
#         "updated_by": dummy_user["_id"],
#     }

#     published_asset = await asset_service.publish_asset(asset_id, dummy_user)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     mock_asset_crud.update_asset_by_id.assert_called_once()
#     assert published_asset["asset_status"] == "published"
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# async def test_publish_asset_not_found(asset_service, mock_asset_crud, dummy_user):
#     """Test publishing a non-existent asset."""
#     asset_id = "60d0fe4f3460595e63456789"
#     mock_asset_crud.get_asset.return_value = None

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.publish_asset(asset_id, dummy_user)

#     assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
#     assert "Asset not found or does not belong to the current domain." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_publish_asset_already_published(asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db):
#     """Test publishing an asset that is already published."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "published"}

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.publish_asset(asset_id, dummy_user)

#     assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Asset is already published." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_publish_asset_archived(asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db):
#     """Test publishing an archived asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "archived"}

#     with pytest.raises(HTTPException) as exc_info:
#         await asset_service.publish_asset(asset_id, dummy_user)

#     assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Cannot publish an archived Asset." in exc_info.value.detail
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_get_all_assets_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful retrieval of all assets with pagination."""
#     df_id = dummy_user["df_id"]
#     current_page = 1
#     data_per_page = 20
#     category = None

#     mock_asset_crud.get_all_assets.return_value = {
#         "data": [{**dummy_asset_in_db, "_id": str(dummy_asset_in_db["_id"])}],
#         "total": 1,
#     }

#     result = await asset_service.get_all_assets(dummy_user, current_page, data_per_page, category)

#     mock_asset_crud.get_all_assets.assert_called_once_with(
#         df_id=df_id, offset=0, limit=data_per_page, category=category
#     )
#     assert result["total_items"] == 1
#     assert result["current_page"] == current_page
#     assert len(result["assets"]) == 1
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_get_asset_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful retrieval of a single asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id}

#     fetched_asset = await asset_service.get_asset(asset_id, dummy_user)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     assert fetched_asset["_id"] == asset_id
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# async def test_get_asset_not_found_service(asset_service, mock_asset_crud, dummy_user):
#     """Test retrieving a non-existent asset at the service layer."""
#     asset_id = "60d0fe4f3460595e63456789"
#     mock_asset_crud.get_asset.return_value = None

#     fetched_asset = await asset_service.get_asset(asset_id, dummy_user)

#     assert fetched_asset is None

# @pytest.mark.asyncio
# @patch("app.utils.business_logger.log_business_event", AsyncMock())
# async def test_delete_asset_success(
#     mock_log_business_event, asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db
# ):
#     """Test successful soft deletion (archiving) of an asset."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "draft"}
#     mock_asset_crud.update_asset_by_id.return_value = {
#         **dummy_asset_in_db,
#         "_id": asset_id,
#         "asset_status": "archived",
#         "updated_by": dummy_user["_id"],
#     }

#     deleted_asset = await asset_service.delete_asset(asset_id, dummy_user)

#     mock_asset_crud.get_asset.assert_called_once_with(asset_id, dummy_user["df_id"])
#     mock_asset_crud.update_asset_by_id.assert_called_once()
#     assert deleted_asset["asset_status"] == "archived"
#     mock_log_business_event.assert_called_once()

# @pytest.mark.asyncio
# async def test_delete_asset_not_found(asset_service, mock_asset_crud, dummy_user):
#     """Test deleting a non-existent asset."""
#     asset_id = "60d0fe4f3460595e63456789"
#     mock_asset_crud.get_asset.return_value = None

#     deleted_asset = await asset_service.delete_asset(asset_id, dummy_user)

#     assert deleted_asset is None
#     mock_asset_crud.update_asset_by_id.assert_not_called()

# @pytest.mark.asyncio
# async def test_delete_asset_already_archived(asset_service, mock_asset_crud, dummy_user, dummy_asset_in_db):
#     """Test deleting an asset that is already archived."""
#     asset_id = str(dummy_asset_in_db["_id"])
#     mock_asset_crud.get_asset.return_value = {**dummy_asset_in_db, "_id": asset_id, "asset_status": "archived"}

#     deleted_asset = await asset_service.delete_asset(asset_id, dummy_user)

#     assert deleted_asset is None
#     mock_asset_crud.update_asset_by_id.assert_not_called()
