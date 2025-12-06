import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, ANY
from fastapi import HTTPException, status


from app.main import app
from app.api.v1.deps import get_current_user, get_grievance_service

client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/grievances"


@pytest.fixture
def mock_user():

    return {"_id": "u1", "email": "admin@example.com", "df_id": "df123", "role": "admin"}


@pytest.fixture
def mock_grievance_id():

    return "60f7a2d81f1e9c001f8e1234"


def grievance_response(**kwargs):
    """Return a dictionary representing a grievance object."""
    base_grievance = {
        "_id": "60f7a2d81f1e9c001f8e1234",
        "title": "Data Access Issue",
        "description": "User reported unauthorized data access.",
        "status": "pending",
        "df_id": "df123",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
    }
    base_grievance.update(kwargs)
    return base_grievance


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_all_grievances = AsyncMock()
    service.view_grievance = AsyncMock()
    service.resolve_grievance = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_grievance_service] = lambda: mock_service

    yield
    app.dependency_overrides = {}


@pytest.mark.parametrize(
    "page, page_size, side_effect, return_value, expected_status",
    [
        (1, 10, None, {"grievances": [grievance_response()], "total": 1}, status.HTTP_200_OK),
        (2, 5, None, {"grievances": [], "total": 1}, status.HTTP_200_OK),
        (1, 10, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED), None, status.HTTP_401_UNAUTHORIZED),
        (1, 10, Exception("DB connection failure"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_grievances_success(mock_service, page, page_size, side_effect, return_value, expected_status):
    mock_service.get_all_grievances.side_effect = side_effect
    mock_service.get_all_grievances.return_value = return_value

    res = client.get(f"{BASE_URL}/view-all-grievances?page={page}&page_size={page_size}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "grievances" in res.json()
        mock_service.get_all_grievances.assert_called_once_with(page=page, page_size=page_size, current_user=ANY)


def test_get_all_grievances_validation_failure():

    res = client.get(f"{BASE_URL}/view-all-grievances", params={"page": 0})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res = client.get(f"{BASE_URL}/view-all-grievances", params={"page_size": 101})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res = client.get(f"{BASE_URL}/view-all-grievances", params={"page_size": "invalid"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, grievance_response(status="resolved"), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_403_FORBIDDEN), None, status.HTTP_403_FORBIDDEN),
        (Exception("Invalid ID"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_grievance_by_id(mock_service, mock_grievance_id, side_effect, return_value, expected_status):
    mock_service.view_grievance.side_effect = side_effect
    mock_service.view_grievance.return_value = return_value

    res = client.get(f"{BASE_URL}/view-grievance/{mock_grievance_id}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["_id"] == mock_grievance_id
        mock_service.view_grievance.assert_called_once_with(ANY, mock_grievance_id)


def test_get_grievance_by_id_invalid_path():

    res = client.get(f"{BASE_URL}/view-grievance/invalid_id_format")

    pass


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, grievance_response(status="resolved", updated_at="2025-01-02T00:00:00Z"), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_403_FORBIDDEN), None, status.HTTP_403_FORBIDDEN),
        (Exception("Database write failure"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_resolve_grievance(mock_service, mock_grievance_id, side_effect, return_value, expected_status):
    mock_service.resolve_grievance.side_effect = side_effect
    mock_service.resolve_grievance.return_value = return_value

    res = client.patch(f"{BASE_URL}/resolve-grievance/{mock_grievance_id}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["status"] == "resolved"
        mock_service.resolve_grievance.assert_called_once_with(ANY, mock_grievance_id)
