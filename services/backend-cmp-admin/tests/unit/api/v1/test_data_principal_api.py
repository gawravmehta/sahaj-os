import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_data_principal_service
from datetime import datetime, timezone
import uuid

client = TestClient(app)
BASE_URL = "/api/v1/data-principal"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def data_principal_response():
    return {
        "dp_id": "dp123",  # Use a fixed dp_id for consistent testing
        "dp_system_id": "system123",
        "dp_identifiers": ["email"],
        "dp_email": ["test@example.com"],
        "dp_mobile": [],
        "dp_other_identifier": [],
        "dp_preferred_lang": "eng",
        "dp_country": "india",
        "dp_state": "karnataka",
        "dp_tags": ["customer"],
        "dp_active_devices": ["mobile"],
        "is_active": True,
        "is_legacy": True,
        "added_by": "u1",
        "added_with": "manual",
        "df_id": "df123",
        "created_at_df": datetime.now(timezone.utc).isoformat(),
        "last_activity": datetime.now(timezone.utc).isoformat(),
        "consent_count": 0,
        "consent_status": "unsent",
    }


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_dps_by_data_elements = AsyncMock()
    service.add_data_principal = AsyncMock()
    service.get_data_principal = AsyncMock()
    service.delete_data_principal = AsyncMock()
    service.get_all_data_principals = AsyncMock()
    service.update_data_principal = AsyncMock()
    service.get_all_dp_tags = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_data_principal_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST SEARCH DATA PRINCIPALS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [data_principal_response()], 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_search_data_principals(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_dps_by_data_elements.side_effect = side_effect
    mock_service.get_dps_by_data_elements.return_value = return_value

    body = {"filter": {"data_elements": ["de1"]}}
    res = client.post(f"{BASE_URL}/search-data-principals", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["count"] == len(return_value)
        assert res.json()["data_principals"][0]["dp_system_id"] == "system123"
        mock_service.get_dps_by_data_elements.assert_called_once_with(["de1"], mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_search_data_principals_validation_error():
    res = client.post(f"{BASE_URL}/search-data-principals", json={"wrong_field": "value"})
    assert res.status_code == 422


# ---------------- TEST ADD DATA PRINCIPAL ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"message": "Data Principal Added Successfully", "principal_ids": ["dp1"]}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_add_data_principal(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.add_data_principal.side_effect = side_effect
    mock_service.add_data_principal.return_value = return_value

    body = [
        {
            "dp_system_id": "system123",
            "dp_identifiers": ["email"],
            "dp_email": ["test@example.com"],
            "created_at_df": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }
    ]
    res = client.post(f"{BASE_URL}/add-data-principal", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["message"] == "Data Principal Added Successfully"
        mock_service.add_data_principal.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_add_data_principal_validation_error():
    res = client.post(f"{BASE_URL}/add-data-principal", json=[{"wrong_field": "value"}])
    assert res.status_code == 422


# ---------------- TEST GET DATA PRINCIPAL ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, data_principal_response(), 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_get_data_principal(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_data_principal.side_effect = side_effect
    mock_service.get_data_principal.return_value = return_value

    dp_id = "dp123"
    res = client.get(f"{BASE_URL}/view-data-principal/{dp_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["dp_id"] == return_value["dp_id"]
        mock_service.get_data_principal.assert_called_once_with(dp_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST DELETE DATA PRINCIPAL ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"message": "Data Principal deleted successfully"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_data_principal(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.delete_data_principal.side_effect = side_effect
    mock_service.delete_data_principal.return_value = return_value

    dp_id = "dp123"
    res = client.delete(f"{BASE_URL}/delete-data-principal/{dp_id}")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["message"] == "Data Principal deleted successfully"
        mock_service.delete_data_principal.assert_called_once_with(dp_id, mock_user)
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


# ---------------- TEST GET ALL DATA PRINCIPALS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (
            None,
            {
                "currentPage": 1,
                "totalPages": 1,
                "totalPrincipals": 1,
                "dataPrincipals": [data_principal_response()],
                "available_options": {
                    "dp_country": ["india"],
                    "dp_preferred_lang": ["eng"],
                    "is_legacy": [True],
                    "consent_status": ["unsent"],
                    "added_with": ["manual"],
                    "dp_tags": ["customer"],
                },
            },
            200,
        ),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_data_principals(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_all_data_principals.side_effect = side_effect
    mock_service.get_all_data_principals.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-data-principals")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["totalPrincipals"] == 1
        mock_service.get_all_data_principals.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_get_all_data_principals_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-data-principals?page=0")
    assert res.status_code == 422


# ---------------- TEST UPDATE DATA PRINCIPAL ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, {"message": "Data Principal updated successfully", "principal_id": "dp123"}, 200, {"dp_preferred_lang": "hindi"}),
        (HTTPException(status_code=404, detail="not found"), None, 404, {"dp_preferred_lang": "hindi"}),
        (Exception("boom"), None, 500, {"dp_preferred_lang": "hindi"}),
    ],
)
def test_update_data_principal(mock_service, mock_user, side_effect, return_value, expected_status, body):
    mock_service.update_data_principal.side_effect = side_effect
    mock_service.update_data_principal.return_value = return_value

    dp_id = "dp123"
    res = client.put(f"{BASE_URL}/update-data-principal/{dp_id}", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["message"] == "Data Principal updated successfully"
        mock_service.update_data_principal.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()


def test_update_data_principal_validation_error():
    res = client.put(f"{BASE_URL}/update-data-principal/dp123", json={"dp_email": ["invalid-email"]})
    assert res.status_code == 422


# ---------------- TEST GET ALL DP TAGS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"dp_tags": ["tag1", "tag2"]}, 200),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_dp_tags(mock_service, mock_user, side_effect, return_value, expected_status):
    mock_service.get_all_dp_tags.side_effect = side_effect
    mock_service.get_all_dp_tags.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-dp-tags")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert "dp_tags" in res.json()
        mock_service.get_all_dp_tags.assert_called_once()
    elif expected_status == 500:
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()
