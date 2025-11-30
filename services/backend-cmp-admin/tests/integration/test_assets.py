import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase


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
