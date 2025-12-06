import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_dashboard_service

client = TestClient(app)
BASE_URL = "/api/v1/dashboard"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.get_dashboard_detail = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_dashboard_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST GET DASHBOARD DETAILS ---------------- #


# Example test structure:
@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (
            None,
            {
                "total_purpose": 1,
                "total_data_element": 1,
                "total_assets": 1,
                "total_data_fiduciary": 1,
                "total_data_processor": 1,
                "total_data_principal": 1,
                "collection_point": 1,
                "total_consent": 1,
                "total_requests": 1,
                "total_notice": 1,
            },
            200,
        ),
        (HTTPException(status_code=400, detail="bad"), None, 400),
    ],
)
def test_get_dashboard_details(mock_service, side_effect, return_value, expected_status):
    mock_service.get_dashboard_detail.side_effect = side_effect
    mock_service.get_dashboard_detail.return_value = return_value

    res = client.get(f"{BASE_URL}/dashboard-details")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["total_purpose"] == 1
        mock_service.get_dashboard_detail.assert_called_once()
    elif expected_status == 500:  # Catching generic exceptions
        assert res.json()["detail"] == "Internal Server Error"
    else:
        assert "detail" in res.json()
