import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from app.main import app
from app.api.v1.deps import get_current_user, get_data_element_service
from app.schemas.data_element_schema import LanguageCodes

client = TestClient(app)
BASE_URL = "/api/v1/data-elements"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def de_response(de_id="de1"):
    """Return a complete schema-valid DataElementResponse dict."""
    return {
        "_id": de_id,
        "de_name": "Test Data Element",
        "de_description": "Test Description",
        "de_original_name": "Test Data Element",
        "de_data_type": "string",
        "de_sensitivity": "low",
        "is_core_identifier": False,
        "de_retention_period": 30,
        "de_status": "draft",
        "translations": {code.name: f"Translated {code.name}" for code in LanguageCodes},
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "de_hash_id": None,
    }


def de_create_body():
    return {
        "de_name": "Test",
        "de_description": "D",
        "de_original_name": "O",
        "de_data_type": "string",
        "de_sensitivity": "low",
        "is_core_identifier": False,
        "de_retention_period": 30,
        "translations": {"eng": "Test"},
    }


def de_template_response(template_id="t1"):
    """Return a schema-valid DataElementTemplateResponse dict."""
    return {
        "id": template_id,
        "title": "Template Title",
        "description": "Template Description",
        "aliases": ["test_alias"],
        "domain": "Template Domain",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "category": "personal",
        "keywords": ["test"],
        "translations": {"eng": "English title"},
    }


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_all_data_element_templates = AsyncMock()
    service.create_data_element = AsyncMock()
    service.copy_data_element = AsyncMock()
    service.update_data_element = AsyncMock()
    service.publish_data_element = AsyncMock()
    service.get_all_data_element = AsyncMock()
    service.get_data_element = AsyncMock()
    service.delete_data_element = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_data_element_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST LIST DATA ELEMENT TEMPLATES ---------------- #


@pytest.mark.parametrize(
    "service_return_value, expected_status_code, query_params",
    [
        (
            {"data": [de_template_response()], "total_items": 1, "total_pages": 1, "current_page": 1, "data_per_page": 20},
            200,
            {},
        ),
        (
            {"data": [], "total_items": 0, "total_pages": 0, "current_page": 1, "data_per_page": 20},
            200,
            {"domain": "test", "title": "test", "id": "t1"},
        ),
        (HTTPException(status_code=400, detail="Bad request"), 400, {}),
        (Exception("Internal error"), 500, {}),
    ],
)
def test_list_data_element_templates_endpoint(mock_service, service_return_value, expected_status_code, query_params):
    if isinstance(service_return_value, HTTPException):
        mock_service.get_all_data_element_templates.side_effect = service_return_value
    elif isinstance(service_return_value, Exception):
        mock_service.get_all_data_element_templates.side_effect = service_return_value
    else:
        mock_service.get_all_data_element_templates.return_value = service_return_value

    res = client.get(f"{BASE_URL}/templates", params=query_params)

    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["total_items"] == service_return_value["total_items"]
        if query_params:
            mock_service.get_all_data_element_templates.assert_called_once_with(
                user=mock_service.get_all_data_element_templates.call_args.kwargs["user"],
                current_page=1,
                data_per_page=20,
                **query_params,
            )
        else:
            mock_service.get_all_data_element_templates.assert_called_once_with(
                user=mock_service.get_all_data_element_templates.call_args.kwargs["user"],
                current_page=1,
                data_per_page=20,
                domain=None,
                title=None,
                id=None,
            )


# ---------------- TEST CREATE DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_data_body",
    [
        (None, de_response(), 201, de_create_body()),  # Success
        (HTTPException(status_code=409, detail="duplicate"), None, 409, de_create_body()),  # Duplicate
        (Exception("Internal error"), None, 500, de_create_body()),  # Internal error
        (None, None, 422, {"de_name": "Missing Fields"}),  # Validation error (FastAPI handles)
    ],
)
def test_create_data_element_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_data_body):
    mock_service.create_data_element.side_effect = service_side_effect
    mock_service.create_data_element.return_value = service_return_value

    res = client.post(f"{BASE_URL}/create-data-element", json=de_data_body)
    assert res.status_code == expected_status_code
    if expected_status_code == 201:
        assert res.json()["de_id"] == service_return_value["_id"]


# ---------------- TEST COPY DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_id",
    [
        (None, de_response("new_de_id"), 201, "template_id"),  # Success
        (HTTPException(status_code=404, detail="not found"), None, 404, "non_existent_id"),  # Not found
        (HTTPException(status_code=409, detail="duplicate"), None, 409, "duplicate_template_id"),  # Duplicate
        (Exception("Internal error"), None, 500, "error_id"),  # Internal error
    ],
)
def test_copy_data_element_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_id):
    mock_service.copy_data_element.side_effect = service_side_effect
    mock_service.copy_data_element.return_value = service_return_value

    res = client.post(f"{BASE_URL}/copy-data-element", params={"de_id": de_id})
    assert res.status_code == expected_status_code
    if expected_status_code == 201:
        assert res.json()["de_id"] == service_return_value["_id"]


# ---------------- TEST UPDATE DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_id, update_data_body",
    [
        (None, de_response(de_id="de1"), 200, "de1", {"de_name": "Updated"}),  # Success
        (None, None, 404, "de_not_found", {"de_name": "Updated"}),  # Not found (service returns None)
        (HTTPException(status_code=400, detail="bad request"), None, 400, "de1", {"de_name": "Dupe"}),  # Bad request from service
        (Exception("Internal error"), None, 500, "de1", {"de_name": "Error"}),  # Internal error
    ],
)
def test_update_data_element_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_id, update_data_body):
    mock_service.update_data_element.side_effect = service_side_effect
    mock_service.update_data_element.return_value = service_return_value

    res = client.patch(f"{BASE_URL}/update-data-element/{de_id}", json=update_data_body)
    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["de_id"] == de_id


# ---------------- TEST PUBLISH DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_id",
    [
        (None, de_response(de_id="de1"), 200, "de1"),  # Success
        (HTTPException(status_code=404, detail="not found"), None, 404, "de_not_found"),  # Not found
        (HTTPException(status_code=400, detail="bad request"), None, 400, "de1"),  # Bad request
        (Exception("Internal error"), None, 500, "de1"),  # Internal error
    ],
)
def test_publish_de_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_id):
    mock_service.publish_data_element.side_effect = service_side_effect
    mock_service.publish_data_element.return_value = service_return_value

    res = client.patch(f"{BASE_URL}/publish-data-element/{de_id}")
    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["de_id"] == service_return_value["_id"]


# ---------------- TEST GET ALL DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, query_params",
    [
        (None, {"data_elements": [de_response()], "total_items": 1, "total_pages": 1, "current_page": 1, "data_per_page": 20}, 200, {}),  # Success
        (
            None,
            {"data_elements": [], "total_items": 0, "total_pages": 0, "current_page": 1, "data_per_page": 20},
            200,
            {"is_core_identifier": True},
        ),  # Success with filter
        (HTTPException(status_code=400, detail="Bad request"), None, 400, {}),  # Bad request
        (Exception("Internal error"), None, 500, {}),  # Internal error
    ],
)
def test_get_all_de_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, query_params):
    mock_service.get_all_data_element.side_effect = service_side_effect
    mock_service.get_all_data_element.return_value = service_return_value

    res = client.get(f"{BASE_URL}/get-all-data-element", params=query_params)
    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["total_items"] == service_return_value["total_items"]
        if query_params:
            mock_service.get_all_data_element.assert_called_once_with(
                user=mock_service.get_all_data_element.call_args.kwargs["user"],
                current_page=1,
                data_per_page=20,
                **query_params,
            )
        else:
            mock_service.get_all_data_element.assert_called_once_with(
                user=mock_service.get_all_data_element.call_args.kwargs["user"],
                current_page=1,
                data_per_page=20,
                is_core_identifier=None,
            )


# ---------------- TEST GET DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_id",
    [
        (None, de_response(de_id="de1"), 200, "de1"),  # Success
        (None, None, 404, "de_not_found"),  # Not found
        (HTTPException(status_code=400, detail="bad request"), None, 400, "de1"),  # Bad request
        (Exception("Internal error"), None, 500, "de1"),  # Internal error
    ],
)
def test_get_data_element_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_id):
    mock_service.get_data_element.side_effect = service_side_effect
    mock_service.get_data_element.return_value = service_return_value

    res = client.get(f"{BASE_URL}/get-data-element/{de_id}")
    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["de_id"] == service_return_value["_id"]


# ---------------- TEST DELETE DATA ELEMENT ---------------- #


@pytest.mark.parametrize(
    "service_side_effect, service_return_value, expected_status_code, de_id",
    [
        (None, de_response(de_id="de1"), 200, "de1"),  # Success
        (None, None, 404, "de_not_found"),  # Not found
        (HTTPException(status_code=400, detail="bad request"), None, 400, "de1"),  # Bad request
        (Exception("Internal error"), None, 500, "de1"),  # Internal error
    ],
)
def test_delete_data_element_endpoint(mock_service, service_side_effect, service_return_value, expected_status_code, de_id):
    mock_service.delete_data_element.side_effect = service_side_effect
    mock_service.delete_data_element.return_value = service_return_value

    res = client.delete(f"{BASE_URL}/delete-data-element/{de_id}")
    assert res.status_code == expected_status_code
    if expected_status_code == 200:
        assert res.json()["de_id"] == service_return_value["_id"]
