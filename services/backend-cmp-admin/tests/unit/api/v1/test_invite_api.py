import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, ANY
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Assuming 'app.main' and dependencies are correctly configured
from app.main import app 
from app.api.v1.deps import get_current_user, get_invites_service
# Dependency from app.db.dependencies
from app.db.dependencies import get_system_admin_role_id

client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/invite"

# --- Schema for Test Context ---
class InviteModel(BaseModel):
    invited_user_id: Optional[str] = None
    invited_user_email: EmailStr
    invited_user_name: Optional[str] = None
    invited_user_roles: Optional[List[str]] = []
# -------------------------------


# ---------------- FIXTURES ---------------- #

@pytest.fixture
def mock_user():
    # User who is initiating the invite
    return {"_id": "u1", "email": "admin@example.com", "df_id": "df123"}

@pytest.fixture
def mock_invite_id():
    return "inv_12345"

@pytest.fixture
def mock_token():
    return "sometokenstring12345"

@pytest.fixture
def mock_system_admin_role_id():
    return "r_sys_admin"

def invite_response(**kwargs):
    """Return a dictionary representing a successful invite object."""
    base_invite = {
        "_id": "inv_12345",
        "invited_user_email": "newuser@example.com",
        "token": "sometokenstring12345",
        "status": "pending",
        "created_by": "u1",
        "created_at": datetime.now().isoformat(),
        "df_id": "df123"
    }
    base_invite.update(kwargs)
    return base_invite

@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_invite = AsyncMock()
    service.verify_token = AsyncMock()
    service.get_all_invites = AsyncMock()
    service.resend_invites = AsyncMock()
    service.cancel_invite = AsyncMock()
    return service

@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service, mock_system_admin_role_id):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_invites_service] = lambda: mock_service
    app.dependency_overrides[get_system_admin_role_id] = lambda: mock_system_admin_role_id
    
    yield
    app.dependency_overrides = {}


# ---------------- 1. TEST POST /new ---------------- #

@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already invited"), status.HTTP_409_CONFLICT),
        (Exception("Service error"), status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_invite_new_user(mock_service, mock_user, mock_system_admin_role_id, side_effect, expected_status):
    mock_service.create_invite.side_effect = side_effect
    mock_service.create_invite.return_value = invite_response()

    payload = InviteModel(
        invited_user_email="newuser@example.com", 
        invited_user_roles=["r_manager"]
    ).model_dump(by_alias=True)

    res = client.post(f"{BASE_URL}/new", json=payload)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        mock_service.create_invite.assert_called_once()
        # Ensure service is called with the correct dependencies
        mock_service.create_invite.assert_called_once_with(ANY, mock_user, mock_system_admin_role_id)
    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Service error" in res.json()["detail"]


def test_invite_new_user_validation_failure():
    # Missing required 'invited_user_email'
    res = client.post(f"{BASE_URL}/new", json={})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 2. TEST GET /accept/{token} ---------------- #

@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token"), status.HTTP_404_NOT_FOUND),
        (Exception("Token processing error"), status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_verify_token(mock_service, mock_token, side_effect, expected_status):
    mock_service.verify_token.side_effect = side_effect
    mock_service.verify_token.return_value = {"email": "verified@example.com"}

    res = client.get(f"{BASE_URL}/accept/{mock_token}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["email"] == "verified@example.com"
        mock_service.verify_token.assert_called_once_with(mock_token)
    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Token processing error" in res.json()["detail"]


# ---------------- 3. TEST GET /view-all-invites ---------------- #

@pytest.mark.parametrize(
    "page, page_size, side_effect, expected_status",
    [
        (1, 10, None, status.HTTP_200_OK), # Default success
        (2, 50, None, status.HTTP_200_OK), # Custom pagination
        (1, 10, HTTPException(status_code=status.HTTP_403_FORBIDDEN), status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_all_invites_success(mock_service, mock_user, page, page_size, side_effect, expected_status):
    mock_service.get_all_invites.side_effect = side_effect
    mock_service.get_all_invites.return_value = {"invites": [invite_response()], "total": 1}

    res = client.get(f"{BASE_URL}/view-all-invites?page={page}&page_size={page_size}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "invites" in res.json()
        mock_service.get_all_invites.assert_called_once_with(mock_user, page, page_size)


def test_get_all_invites_validation_failure():
    # page must be >= 1
    res = client.get(f"{BASE_URL}/view-all-invites?page=0")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # page_size must be <= 100
    res = client.get(f"{BASE_URL}/view-all-invites?page_size=101")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 4. TEST PATCH /resend-invitation/{invite_id} ---------------- #

@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), status.HTTP_404_NOT_FOUND),
        (Exception("Email send failed"), status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_resend_invites(mock_service, mock_invite_id, mock_user, side_effect, expected_status):
    mock_service.resend_invites.side_effect = side_effect
    mock_service.resend_invites.return_value = {"message": "Invite resent successfully"}

    res = client.patch(f"{BASE_URL}/resend-invitation/{mock_invite_id}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "successfully" in res.json()["message"]
        mock_service.resend_invites.assert_called_once_with(mock_invite_id, mock_user)
    elif expected_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
        assert "Email send failed" in res.json()["detail"]


# ---------------- 5. TEST DELETE /cancel-invite/{invite_id} ---------------- #

@pytest.mark.parametrize(
    "side_effect, expected_status",
    [
        (None, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel"), status.HTTP_403_FORBIDDEN),
    ],
)
def test_cancel_invite(mock_service, mock_invite_id, mock_user, side_effect, expected_status):
    mock_service.cancel_invite.side_effect = side_effect
    mock_service.cancel_invite.return_value = {"message": "Invite cancelled"}

    res = client.delete(f"{BASE_URL}/cancel-invite/{mock_invite_id}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "cancelled" in res.json()["message"]
        mock_service.cancel_invite.assert_called_once_with(mock_invite_id)