import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from bson import ObjectId

from app.main import app
from app.api.v1.deps import get_current_user, get_purpose_service
from app.schemas.purpose_schema import PurposeResponse, PurposePaginatedResponse

client = TestClient(app)
BASE_URL = "/api/v1/purposes"

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}

def purpose_response(purpose_id="p1", title="Test Purpose"):
    """Return a complete schema-valid PurposeResponse dict."""
    return {
        "_id": purpose_id,
        "purpose_title": title,
        "purpose_description": "Description of Test Purpose",
        "purpose_priority": "low",
        "review_frequency": "quarterly",
        "consent_time_period": 30,
        "reconsent": False,
        "data_elements": [],
        "translations": {"eng": "English Test Purpose"},
        "collection_points": [],
        "purpose_status": "draft",
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "purpose_hash_id": None,
        "data_processor_details": [],
    }

def purpose_template_response(purpose_id="p1_template"):
    """Return a complete schema-valid PurposeTemplate dict for templates endpoint."""
    return {
        "purpose_id": purpose_id,
        "industry": "Finance",
        "sub_category": "Loans",
        "data_elements": [],
        "translations": {"eng": "Template Purpose"},
    }

@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_purpose = AsyncMock()
    service.copy_purpose = AsyncMock()
    service.delete_purpose = AsyncMock()
    service.get_all_purpose_templates = AsyncMock()
    service.publish_purpose = AsyncMock()
    service.get_all_purpose = AsyncMock()
    service.get_purpose = AsyncMock()
    service.update_purpose_data = AsyncMock()
    return service

@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_purpose_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}

# ---------------- TEST LIST PURPOSE TEMPLATES ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"data": [purpose_template_response()], "total": 1, "total_items": 1, "current_page": 1, "data_per_page": 10, "total_pages": 1}, 200),
        (HTTPException(status_code=400, detail="bad request"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_list_purpose_templates(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_purpose_templates.side_effect = side_effect
    mock_service.get_all_purpose_templates.return_value = return_value

    res = client.get(f"{BASE_URL}/templates?current_page=1&data_per_page=10&title=Test")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["purposes"][0]["purpose_id"] == "p1_template"
        mock_service.get_all_purpose_templates.assert_called_once()

def test_list_purpose_templates_validation_error():
    res = client.get(f"{BASE_URL}/templates?current_page=0")
    assert res.status_code == 422

# ---------------- TEST CREATE PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, purpose_response(), 201),
        (HTTPException(status_code=400, detail="Purpose title already exists."), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_create_purpose(mock_service, side_effect, return_value, expected_status):
    mock_service.create_purpose.side_effect = side_effect
    mock_service.create_purpose.return_value = return_value

    body = {
        "purpose_title": "New Purpose",
        "purpose_description": "Desc",
        "purpose_priority": "low",
        "review_frequency": "quarterly",
        "consent_time_period": 30,
        "reconsent": False,
        "translations": {"eng": "New Purpose"},
    }
    res = client.post(f"{BASE_URL}/create-purpose", json=body)

    assert res.status_code == expected_status
    if expected_status == 201:
        assert res.json()["purpose_id"] == "p1"
        mock_service.create_purpose.assert_called_once()

def test_create_purpose_validation_error():
    res = client.post(f"{BASE_URL}/create-purpose", json={"purpose_title": "A"}) # Min length 4
    assert res.status_code == 422

# ---------------- TEST COPY PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, purpose_response(title="Copied Purpose"), 201),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_copy_purpose(mock_service, side_effect, return_value, expected_status):
    mock_service.copy_purpose.side_effect = side_effect
    mock_service.copy_purpose.return_value = return_value

    res = client.post(f"{BASE_URL}/copy-purpose?purpose_id=p1", json=["DE1", "DE2"])

    assert res.status_code == expected_status
    if expected_status == 201:
        assert res.json()["purpose_title"] == "Copied Purpose"
        mock_service.copy_purpose.assert_called_once()

def test_copy_purpose_validation_error():
    res = client.post(f"{BASE_URL}/copy-purpose?purpose_id=p1", json="not a list")
    assert res.status_code == 422

# ---------------- TEST UPDATE PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, purpose_response(title="Updated Title"), 200, {"purpose_title": "Updated Title"}),
        (None, None, 404, {"purpose_title": "NotFound"}), # 404 from service
        (HTTPException(status_code=400, detail="bad request"), None, 400, {"purpose_title": "Valid Bad"}), # Valid input for Pydantic, triggers 400 from service
        (Exception("boom"), None, 500, {"purpose_title": "Boom Test"}), # Valid input, triggers 500
        (HTTPException(status_code=400, detail="Purpose title 'Existing' already exists."), None, 400, {"purpose_title": "Existing"}), # Service-level HTTPException for duplicate name
    ],
)
def test_update_purpose(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_purpose_data.side_effect = side_effect
    mock_service.update_purpose_data.return_value = return_value

    res = client.put(f"{BASE_URL}/update-purpose/p1", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["purpose_title"] == body["purpose_title"]
        mock_service.update_purpose_data.assert_called_once()

def test_update_purpose_validation_error():
    res = client.put(f"{BASE_URL}/update-purpose/p1", json={"purpose_title": "A"})
    assert res.status_code == 422

# ---------------- TEST PUBLISH PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**purpose_response(purpose_id="p1"), "purpose_status": "published"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_publish_purpose(mock_service, side_effect, return_value, expected_status):
    mock_service.publish_purpose.side_effect = side_effect
    mock_service.publish_purpose.return_value = return_value

    res = client.patch(f"{BASE_URL}/publish-purpose/p1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["purpose_status"] == "published"
        mock_service.publish_purpose.assert_called_once()

# ---------------- TEST GET ALL PURPOSES ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"purposes": [purpose_response()], "total_items": 1, "current_page": 1, "data_per_page": 10, "total_pages": 1}, 200),
        (None, {"purposes": [], "total_items": 0, "current_page": 1, "data_per_page": 10, "total_pages": 0}, 404),
        (HTTPException(status_code=400, detail="bad request"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_purposes(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_purpose.side_effect = side_effect
    mock_service.get_all_purpose.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-purposes?current_page=1&data_per_page=10")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["purposes"][0]["purpose_id"] == "p1"
        mock_service.get_all_purpose.assert_called_once()

def test_get_all_purposes_validation_error():
    res = client.get(f"{BASE_URL}/get-all-purposes?current_page=0")
    assert res.status_code == 422

# ---------------- TEST GET PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, purpose_response(), 200),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad request"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_purpose(mock_service, side_effect, return_value, expected_status):
    mock_service.get_purpose.side_effect = side_effect
    mock_service.get_purpose.return_value = return_value

    res = client.get(f"{BASE_URL}/get-purpose/p1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["purpose_id"] == "p1"
        mock_service.get_purpose.assert_called_once()

# ---------------- TEST DELETE PURPOSE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"_id": "p1", "purpose_status": "archived"}, 204),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad request"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_purpose(mock_service, side_effect, return_value, expected_status):
    mock_service.delete_purpose.side_effect = side_effect
    mock_service.delete_purpose.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-purpose/p1")

    assert res.status_code == expected_status
    if expected_status == 204:
        mock_service.delete_purpose.assert_called_once()
