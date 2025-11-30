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


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, asset_response(), 201),
        (HTTPException(status_code=409, detail="duplicate"), None, 409),
        (Exception("boom"), None, 500),
    ],
)
def test_create_asset(mock_service, side_effect, return_value, expected_status):
    mock_service.create_asset.side_effect = side_effect
    mock_service.create_asset.return_value = return_value

    body = {"asset_name": "Asset1", "category": "Website", "usage_url": "x.com"}
    res = client.post(f"{BASE_URL}/create-asset", json=body)

    assert res.status_code == expected_status
    if expected_status == 201:
        assert res.json()["asset_id"] == "a1"
        mock_service.create_asset.assert_called_once()


def test_create_asset_validation_error():
    res = client.post(f"{BASE_URL}/create-asset", json={"wrong_field": "value"})
    assert res.status_code == 422


# ---------------- TEST UPDATE ASSET ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, asset_response(), 200, {"asset_name": "Updated"}),
        (None, None, 404, {"asset_name": "NewName"}),
        (HTTPException(status_code=400, detail="bad"), None, 400, {"asset_name": "NewName"}),
        (Exception("boom"), None, 500, {"asset_name": "NewName"}),
    ],
)
def test_update_asset(mock_service, side_effect, return_value, expected_status, body):
    if return_value:
        return_value["asset_name"] = body.get("asset_name", "Asset1")

    mock_service.update_asset.side_effect = side_effect
    mock_service.update_asset.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-asset/a1", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["asset_id"] == "a1"
        mock_service.update_asset.assert_called_once()


def test_update_asset_invalid_body():
    res = client.patch(f"{BASE_URL}/update-asset/a1", json={"usage_url": 12345})
    assert res.status_code == 422


# ---------------- TEST PUBLISH ASSET ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**asset_response(), "asset_status": "published"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_publish_asset(mock_service, side_effect, return_value, expected_status):
    mock_service.publish_asset.side_effect = side_effect
    mock_service.publish_asset.return_value = return_value

    res = client.patch(f"{BASE_URL}/publish-asset/a1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["asset_status"] == "published"


# ---------------- TEST GET ALL ASSETS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (
            None,
            {
                "current_page": 1,
                "data_per_page": 20,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
                "assets": [asset_response()],
            },
            200,
        ),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_assets(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_assets.side_effect = side_effect
    mock_service.get_all_assets.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-assets")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["assets"][0]["asset_id"] == "a1"


def test_get_all_assets_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-assets?current_page=0")
    assert res.status_code == 422


# ---------------- TEST GET ASSET ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, asset_response(), 200),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_asset(mock_service, side_effect, return_value, expected_status):
    mock_service.get_asset.side_effect = side_effect
    mock_service.get_asset.return_value = return_value

    res = client.get(f"{BASE_URL}/get-asset/a1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["asset_id"] == "a1"


# ---------------- TEST DELETE ASSET ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**asset_response(), "asset_status": "archived"}, 200),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_asset(mock_service, side_effect, return_value, expected_status):
    mock_service.delete_asset.side_effect = side_effect
    mock_service.delete_asset.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-asset/a1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["asset_status"] == "archived"
