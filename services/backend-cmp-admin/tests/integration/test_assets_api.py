import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, UTC
from app.core.config import settings

@pytest.fixture(autouse=True)
async def clean_db(concur_master_db: AsyncIOMotorDatabase):
    """Clean up the database before each test."""
    await concur_master_db[settings.DB_NAME_CONCUR_MASTER].drop()
    yield
    await concur_master_db[settings.DB_NAME_CONCUR_MASTER].drop()

@pytest.fixture
def test_asset_data():
    """Dummy asset data for API requests."""
    return {
        "asset_name": "Integration Test Asset",
        "category": "website",
        "description": "An asset for integration testing purposes.",
        "meta_cookies": {"cookies_count": 0, "scripts": []},
    }

@pytest.fixture
async def create_test_asset(concur_master_db: AsyncIOMotorDatabase, test_asset_data: dict):
    """Fixture to create an asset directly in the database."""
    collection = concur_master_db["assets_master"]
    asset_to_insert = {
        **test_asset_data,
        "df_id": "test_df_id",
        "created_by": "user_123",
        "asset_status": "draft",
        "created_at": datetime.now(UTC),
    }
    result = await collection.insert_one(asset_to_insert)
    asset_to_insert["_id"] = str(result.inserted_id)
    return asset_to_insert


def test_create_asset_success(client: TestClient, test_asset_data: dict):
    """Test creating an asset successfully via the API."""
    response = client.post(
        "/api/v1/assets/create-asset",
        json=test_asset_data,
        headers={"Authorization": "Bearer dummy_token"},
    )
    assert response.status_code == 201
    created_asset = response.json()
    assert created_asset["asset_name"] == test_asset_data["asset_name"]
    assert created_asset["df_id"] == "test_df_id"
    assert created_asset["asset_status"] == "draft"
    assert "_id" in created_asset

# def test_create_asset_duplicate_name(client: TestClient, create_test_asset: dict, test_asset_data: dict):
#     """Test creating an asset with a duplicate name."""
#     response = client.post(
#         "/api/v1/assets/create-asset",
#         json=test_asset_data,
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 409
#     assert "An Asset with the same name already exists." in response.json()["detail"]

# def test_update_asset_success(client: TestClient, create_test_asset: dict):
#     """Test updating an existing asset."""
#     asset_id = create_test_asset["_id"]
#     update_data = {"asset_name": "Updated Integration Test Asset", "description": "Updated description"}
#     response = client.patch(
#         f"/api/v1/assets/update-asset/{asset_id}",
#         json=update_data,
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 200
#     updated_asset = response.json()
#     assert updated_asset["_id"] == asset_id
#     assert updated_asset["asset_name"] == update_data["asset_name"]
#     assert updated_asset["description"] == update_data["description"]

# def test_update_asset_not_found(client: TestClient):
#     """Test updating a non-existent asset."""
#     non_existent_id = str(ObjectId())
#     update_data = {"asset_name": "Non Existent"}
#     response = client.patch(
#         f"/api/v1/assets/update-asset/{non_existent_id}",
#         json=update_data,
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 404
#     assert "Asset not found or no changes made" in response.json()["detail"]

# @pytest.mark.asyncio
# async def test_update_asset_not_draft(client: TestClient, concur_master_db: AsyncIOMotorDatabase, test_asset_data: dict):
#     """Test updating a published asset."""
#     collection = concur_master_db["assets_master"]
#     asset_to_insert = {
#         **test_asset_data,
#         "df_id": "test_df_id",
#         "created_by": "user_123",
#         "asset_status": "published", # Set to published
#         "created_at": datetime.now(UTC),
#     }
#     result = await collection.insert_one(asset_to_insert)
#     asset_id = str(result.inserted_id)

#     update_data = {"asset_name": "Attempt Update Published"}
#     response = client.patch(
#         f"/api/v1/assets/update-asset/{asset_id}",
#         json=update_data,
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 400
#     assert "Only Assets in draft status can be updated." in response.json()["detail"]


# def test_publish_asset_success(client: TestClient, create_test_asset: dict):
#     """Test publishing a draft asset."""
#     asset_id = create_test_asset["_id"]
#     response = client.patch(
#         f"/api/v1/assets/publish-asset/{asset_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 200
#     published_asset = response.json()
#     assert published_asset["_id"] == asset_id
#     assert published_asset["asset_status"] == "published"

# def test_publish_asset_not_found(client: TestClient):
#     """Test publishing a non-existent asset."""
#     non_existent_id = str(ObjectId())
#     response = client.patch(
#         f"/api/v1/assets/publish-asset/{non_existent_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 404
#     assert "Asset not found or does not belong to the current domain." in response.json()["detail"]

# @pytest.mark.asyncio
# async def test_publish_asset_already_published(client: TestClient, concur_master_db: AsyncIOMotorDatabase, test_asset_data: dict):
#     """Test publishing an asset that is already published."""
#     collection = concur_master_db["assets_master"]
#     asset_to_insert = {
#         **test_asset_data,
#         "df_id": "test_df_id",
#         "created_by": "user_123",
#         "asset_status": "published",
#         "created_at": datetime.now(UTC),
#     }
#     result = await collection.insert_one(asset_to_insert)
#     asset_id = str(result.inserted_id)

#     response = client.patch(
#         f"/api/v1/assets/publish-asset/{asset_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 400
#     assert "Asset is already published." in response.json()["detail"]

# def test_get_all_assets_success(client: TestClient, create_test_asset: dict):
#     """Test retrieving all assets."""
#     response = client.get(
#         "/api/v1/assets/get-all-assets",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 200
#     assets_response = response.json()
#     assert assets_response["total_items"] >= 1
#     assert any(asset["_id"] == create_test_asset["_id"] for asset in assets_response["assets"])

# def test_get_asset_by_id_success(client: TestClient, create_test_asset: dict):
#     """Test retrieving a single asset by ID."""
#     asset_id = create_test_asset["_id"]
#     response = client.get(
#         f"/api/v1/assets/get-asset/{asset_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 200
#     asset = response.json()
#     assert asset["_id"] == asset_id
#     assert asset["asset_name"] == create_test_asset["asset_name"]

# def test_get_asset_by_id_not_found(client: TestClient):
#     """Test retrieving a non-existent asset by ID."""
#     non_existent_id = str(ObjectId())
#     response = client.get(
#         f"/api/v1/assets/get-asset/{non_existent_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 404
#     assert "Asset not found" in response.json()["detail"]

# def test_delete_asset_success(client: TestClient, create_test_asset: dict):
#     """Test soft deleting an asset."""
#     asset_id = create_test_asset["_id"]
#     response = client.delete(
#         f"/api/v1/assets/delete-asset/{asset_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 200
#     deleted_asset = response.json()
#     assert deleted_asset["_id"] == asset_id
#     assert deleted_asset["asset_status"] == "archived"

# def test_delete_asset_not_found(client: TestClient):
#     """Test soft deleting a non-existent asset."""
#     non_existent_id = str(ObjectId())
#     response = client.delete(
#         f"/api/v1/assets/delete-asset/{non_existent_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 404
#     assert "Asset not found or already deleted." in response.json()["detail"]

# @pytest.mark.asyncio
# async def test_delete_asset_already_archived(client: TestClient, concur_master_db: AsyncIOMotorDatabase, test_asset_data: dict):
#     """Test soft deleting an asset that is already archived."""
#     collection = concur_master_db["assets_master"]
#     asset_to_insert = {
#         **test_asset_data,
#         "df_id": "test_df_id",
#         "created_by": "user_123",
#         "asset_status": "archived",
#         "created_at": datetime.now(UTC),
#     }
#     result = await collection.insert_one(asset_to_insert)
#     asset_id = str(result.inserted_id)

#     response = client.delete(
#         f"/api/v1/assets/delete-asset/{asset_id}",
#         headers={"Authorization": "Bearer dummy_token"},
#     )
#     assert response.status_code == 404
#     assert "Asset not found or already deleted." in response.json()["detail"]
