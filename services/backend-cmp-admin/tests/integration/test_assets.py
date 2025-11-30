import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from unittest.mock import patch


@pytest.mark.asyncio
async def test_create_asset(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    asset_data = {"asset_name": "Test Asset", "category": "Website", "description": "This is a test asset.", "usage_url": "https://example.com"}
    response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["asset_name"] == asset_data["asset_name"]
    assert response_data["description"] == asset_data["description"]
    assert "asset_id" in response_data

    asset_id = response_data["asset_id"]
    get_response = await client.get(f"/api/v1/assets/get-asset/{asset_id}")
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    assert get_response_data["asset_name"] == asset_data["asset_name"]
    assert get_response_data["description"] == asset_data["description"]


@pytest.mark.asyncio
async def test_create_asset_invalid_category(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    asset_data = {
        "asset_name": "Test Asset",
        "category": "Invalid Category",
        "description": "This is a test asset.",
        "usage_url": "https://example.com",
    }
    response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_asset_missing_usage_url(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    asset_data = {"asset_name": "Test Asset", "category": "Website", "description": "This is a test asset."}
    response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_asset_missing_name(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    asset_data = {"category": "Website", "description": "This is a test asset.", "usage_url": "https://example.com"}
    response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_asset_missing_category(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    asset_data = {"asset_name": "Test Asset", "description": "This is a test asset.", "usage_url": "https://example.com"}
    response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_asset(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # First, create an asset to update
    asset_data = {
        "asset_name": "Asset to Update",
        "category": "Website",
        "description": "Initial description.",
        "usage_url": "https://example-update.com",
    }
    create_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert create_response.status_code == 201
    asset_id = create_response.json()["asset_id"]

    # Now, update the asset
    update_data = {"description": "Updated description."}
    update_response = await client.patch(f"/api/v1/assets/update-asset/{asset_id}", json=update_data)
    assert update_response.status_code == 200
    updated_asset = update_response.json()
    assert updated_asset["description"] == update_data["description"]
    assert updated_asset["asset_name"] == asset_data["asset_name"]  # Ensure other fields are unchanged


@pytest.mark.asyncio
async def test_publish_asset(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # First, create a draft asset
    asset_data = {
        "asset_name": "Asset to Publish",
        "category": "Website",
        "description": "A draft asset.",
        "usage_url": "https://example-publish.com",
    }
    create_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert create_response.status_code == 201
    asset_id = create_response.json()["asset_id"]

    # Now, publish the asset
    publish_response = await client.patch(f"/api/v1/assets/publish-asset/{asset_id}")
    assert publish_response.status_code == 200
    published_asset = publish_response.json()
    assert published_asset["asset_status"] == "published"


@pytest.mark.asyncio
async def test_get_all_assets(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Create a couple of assets
    asset1_data = {"asset_name": "Asset One", "category": "Website", "description": "First asset.", "usage_url": "https://example-one.com"}
    asset2_data = {"asset_name": "Asset Two", "category": "Website", "description": "Second asset.", "usage_url": "https://example-two.com"}
    await client.post("/api/v1/assets/create-asset", json=asset1_data)
    await client.post("/api/v1/assets/create-asset", json=asset2_data)

    # Get all assets
    response = await client.get("/api/v1/assets/get-all-assets")
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total_items"] == 2
    assert len(paginated_response["assets"]) == 2
    assert paginated_response["assets"][0]["asset_name"] == asset1_data["asset_name"]
    assert paginated_response["assets"][1]["asset_name"] == asset2_data["asset_name"]


@pytest.mark.asyncio
async def test_delete_asset(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # First, create an asset to delete
    asset_data = {
        "asset_name": "Asset to Delete",
        "category": "Website",
        "description": "This asset will be deleted.",
        "usage_url": "https://example-delete.com",
    }
    create_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert create_response.status_code == 201
    asset_id = create_response.json()["asset_id"]

    # Delete the asset
    delete_response = await client.delete(f"/api/v1/assets/delete-asset/{asset_id}")
    assert delete_response.status_code == 200

    # Verify that the asset is no longer retrievable
    get_response = await client.get(f"/api/v1/assets/get-asset/{asset_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_asset_duplicate_name(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Create an asset
    asset_data = {
        "asset_name": "Duplicate Asset",
        "category": "Website",
        "description": "An asset to test duplication.",
        "usage_url": "https://example-duplicate.com",
    }
    first_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert first_response.status_code == 201

    # Attempt to create the same asset again
    second_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_update_asset_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Attempt to update an asset that does not exist
    update_data = {"description": "This will fail."}
    non_existent_asset_id = "615f8d9b8d9b8d9b8d9b8d9b"  # A valid but non-existent ObjectId
    update_response = await client.patch(f"/api/v1/assets/update-asset/{non_existent_asset_id}", json=update_data)
    assert update_response.status_code == 404


@pytest.mark.asyncio
async def test_publish_asset_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Attempt to publish an asset that does not exist
    non_existent_asset_id = "615f8d9b8d9b8d9b8d9b8d9b"
    publish_response = await client.patch(f"/api/v1/assets/publish-asset/{non_existent_asset_id}")
    assert publish_response.status_code == 404


@pytest.mark.parametrize(
    "service_method_to_patch, http_method, endpoint_url, request_data",
    [
        (
            "app.services.assets_service.AssetService.create_asset",
            "POST",
            "/api/v1/assets/create-asset",
            {"asset_name": "Test", "category": "Website", "usage_url": "http://test.com"},
        ),
        (
            "app.services.assets_service.AssetService.update_asset",
            "PATCH",
            "/api/v1/assets/update-asset/placeholder_id",
            {"description": "New description"},
        ),
        (
            "app.services.assets_service.AssetService.publish_asset",
            "PATCH",
            "/api/v1/assets/publish-asset/placeholder_id",
            None,
        ),
        ("app.services.assets_service.AssetService.get_all_assets", "GET", "/api/v1/assets/get-all-assets", None),
        ("app.services.assets_service.AssetService.get_asset", "GET", "/api/v1/assets/get-asset/placeholder_id", None),
        ("app.services.assets_service.AssetService.delete_asset", "DELETE", "/api/v1/assets/delete-asset/placeholder_id", None),
    ],
)
@pytest.mark.asyncio
async def test_asset_endpoints_internal_server_error(
    client: AsyncClient,
    test_db: AsyncIOMotorDatabase,
    service_method_to_patch,
    http_method,
    endpoint_url,
    request_data,
):
    asset_id = "615f8d9b8d9b8d9b8d9b8d9b"  # Dummy ID for GET/PATCH endpoints

    # Create a real asset for endpoints that need a valid ID
    if "placeholder_id" in endpoint_url and http_method in ["PATCH", "GET", "DELETE"]:
        create_response = await client.post(
            "/api/v1/assets/create-asset",
            json={"asset_name": "Error Test Asset", "category": "Website", "usage_url": "http://test.com"},
        )
        asset_id = create_response.json()["asset_id"]

    endpoint_url = endpoint_url.replace("placeholder_id", asset_id)

    with patch(service_method_to_patch, side_effect=Exception("A simulated internal error occurred")):
        if http_method == "GET":
            response = await client.get(endpoint_url)
        elif http_method == "POST":
            response = await client.post(endpoint_url, json=request_data)
        elif http_method == "PATCH":
            response = await client.patch(endpoint_url, json=request_data)
        elif http_method == "DELETE":
            response = await client.delete(endpoint_url)

        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_all_assets_http_exception(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Mock the service to raise an HTTPException
    from fastapi import HTTPException

    with patch(
        "app.services.assets_service.AssetService.get_all_assets",
        side_effect=HTTPException(status_code=400, detail="A simulated HTTP error"),
    ):
        response = await client.get("/api/v1/assets/get-all-assets")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_asset_not_found(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # Attempt to delete an asset that does not exist
    non_existent_asset_id = "615f8d9b8d9b8d9b8d9b8d9b"
    response = await client.delete(f"/api/v1/assets/delete-asset/{non_existent_asset_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_asset_no_changes(client: AsyncClient, test_db: AsyncIOMotorDatabase):
    # First, create an asset
    asset_data = {
        "asset_name": "No Change Asset",
        "category": "Website",
        "description": "Initial description.",
        "usage_url": "https://example-nochange.com",
    }
    create_response = await client.post("/api/v1/assets/create-asset", json=asset_data)
    assert create_response.status_code == 201
    asset_id = create_response.json()["asset_id"]

    # Mock the service to return None, simulating no changes being made
    with patch("app.services.assets_service.AssetService.update_asset", return_value=None):
        update_data = {"description": "This update will be mocked to do nothing."}
        update_response = await client.patch(f"/api/v1/assets/update-asset/{asset_id}", json=update_data)
        assert update_response.status_code == 404
        assert update_response.json()["detail"] == "Asset not found or no changes made"
