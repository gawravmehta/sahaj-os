import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_asset_service

client = TestClient(app)
BASE_URL = "/api/v1/assets"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def asset_response():
    """Return a complete schema-valid AssetResponse dict."""
    return {
        "_id": "a1",
        "asset_name": "Asset1",
        "category": "Website",
        "description": None,
        "image": None,
        "asset_status": "draft",
        "usage_url": "x.com",
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "meta_cookies": None,
    }


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_asset = AsyncMock()
    service.update_asset = AsyncMock()
    service.publish_asset = AsyncMock()
    service.get_all_assets = AsyncMock()
    service.get_asset = AsyncMock()
    service.delete_asset = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_asset_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST CREATE ASSET ---------------- #


def test_create_asset_success(mock_service):
    mock_service.create_asset.return_value = asset_response()

    body = {"asset_name": "Asset1", "category": "Website", "usage_url": "x.com"}

    res = client.post(f"{BASE_URL}/create-asset", json=body)

    assert res.status_code == 201
    data = res.json()
    assert data["asset_id"] == "a1"
    mock_service.create_asset.assert_called_once()


def test_create_asset_http_exception(mock_service):
    mock_service.create_asset.side_effect = HTTPException(status_code=409, detail="duplicate")

    body = {"asset_name": "Asset1", "category": "Website", "usage_url": "x.com"}
    res = client.post(f"{BASE_URL}/create-asset", json=body)
    assert res.status_code == 409


def test_create_asset_internal_error(mock_service):
    mock_service.create_asset.side_effect = Exception("boom")

    body = {"asset_name": "Asset1", "category": "Website", "usage_url": "x.com"}
    res = client.post(f"{BASE_URL}/create-asset", json=body)
    assert res.status_code == 500


def test_create_asset_validation_error():
    res = client.post(f"{BASE_URL}/create-asset", json={"wrong_field": "value"})
    assert res.status_code == 422


# ---------------- TEST UPDATE ASSET ---------------- #


def test_update_asset_success(mock_service):
    data = asset_response()
    data["asset_name"] = "Updated"
    mock_service.update_asset.return_value = data

    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"asset_name": "Updated"})

    assert res.status_code == 200
    assert res.json()["asset_id"] == "a1"
    mock_service.update_asset.assert_called_once()


def test_update_asset_not_found(mock_service):
    mock_service.update_asset.return_value = None

    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"asset_name": "NewName"})
    assert res.status_code == 404


def test_update_asset_http_exception(mock_service):
    mock_service.update_asset.side_effect = HTTPException(status_code=400, detail="bad")

    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"asset_name": "NewName"})
    assert res.status_code == 400


def test_update_asset_internal_error(mock_service):
    mock_service.update_asset.side_effect = Exception("boom")

    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"asset_name": "NewName"})
    assert res.status_code == 500


def test_update_asset_invalid_body():
    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"usage_url": 12345})
    assert res.status_code == 422


# ---------------- TEST PUBLISH ASSET ---------------- #


def test_publish_asset_success(mock_service):
    data = asset_response()
    data["asset_status"] = "published"
    mock_service.publish_asset.return_value = data

    res = client.patch(f"{BASE_URL}/publish-asset/a1")
    assert res.status_code == 200
    assert res.json()["asset_status"] == "published"


def test_publish_asset_http_exception(mock_service):
    mock_service.publish_asset.side_effect = HTTPException(status_code=404, detail="not found")

    res = client.patch(f"{BASE_URL}/publish-asset/a1")
    assert res.status_code == 404


def test_publish_asset_internal_error(mock_service):
    mock_service.publish_asset.side_effect = Exception("boom")

    res = client.patch(f"{BASE_URL}/publish-asset/a1")
    assert res.status_code == 500


# ---------------- TEST GET ALL ASSETS ---------------- #


def test_get_all_assets_success(mock_service):
    mock_service.get_all_assets.return_value = {
        "current_page": 1,
        "data_per_page": 20,
        "total_items": 1,
        "total_pages": 1,
        "has_next": False,
        "has_previous": False,
        "assets": [asset_response()],
    }

    res = client.get(f"{BASE_URL}/get-all-assets")

    assert res.status_code == 200
    assert res.json()["assets"][0]["asset_id"] == "a1"


def test_get_all_assets_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-assets?current_page=0")
    assert res.status_code == 422


# ---------------- TEST GET ASSET ---------------- #


def test_get_asset_success(mock_service):
    mock_service.get_asset.return_value = asset_response()

    res = client.get(f"{BASE_URL}/get-asset/a1")
    assert res.status_code == 200
    assert res.json()["asset_id"] == "a1"


def test_get_asset_not_found(mock_service):
    mock_service.get_asset.return_value = None

    res = client.get(f"{BASE_URL}/get-asset/a1")
    assert res.status_code == 404


def test_get_asset_http_exception(mock_service):
    mock_service.get_asset.side_effect = HTTPException(status_code=400, detail="bad")

    res = client.get(f"{BASE_URL}/get-asset/a1")
    assert res.status_code == 400


def test_get_asset_internal_error(mock_service):
    mock_service.get_asset.side_effect = Exception("boom")

    res = client.get(f"{BASE_URL}/get-asset/a1")
    assert res.status_code == 500


# ---------------- TEST DELETE ASSET ---------------- #


def test_delete_asset_success(mock_service):
    data = asset_response()
    data["asset_status"] = "archived"
    mock_service.delete_asset.return_value = data

    res = client.delete(f"{BASE_URL}/delete-asset/a1")

    assert res.status_code == 200
    assert res.json()["asset_status"] == "archived"


def test_delete_asset_not_found(mock_service):
    mock_service.delete_asset.return_value = None

    res = client.delete(f"{BASE_URL}/delete-asset/a1")
    assert res.status_code == 404


def test_delete_asset_http_exception(mock_service):
    mock_service.delete_asset.side_effect = HTTPException(status_code=400, detail="bad")

    res = client.delete(f"{BASE_URL}/delete-asset/a1")
    assert res.status_code == 400


def test_delete_asset_internal_error(mock_service):
    mock_service.delete_asset.side_effect = Exception("boom")

    res = client.delete(f"{BASE_URL}/delete-asset/a1")
    assert res.status_code == 500
