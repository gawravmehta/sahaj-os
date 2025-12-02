import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC
from bson import ObjectId

from app.services.invite_service import InviteService
from app.crud.user_crud import UserCRUD
from app.crud.role_crud import RoleCRUD
from app.crud.invite_crud import InviteCRUD
from app.crud.data_fiduciary_crud import DataFiduciaryCRUD
from app.schemas.invite_schema import InviteModel


# --- Fixtures ---
@pytest.fixture
def mock_user_crud():
    return MagicMock(spec=UserCRUD)


@pytest.fixture
def mock_role_crud():
    return MagicMock(spec=RoleCRUD)


@pytest.fixture
def mock_invite_crud():
    return MagicMock(spec=InviteCRUD)


@pytest.fixture
def mock_df_crud():
    return MagicMock(spec=DataFiduciaryCRUD)


@pytest.fixture
def invite_service(mock_user_crud, mock_role_crud, mock_invite_crud, mock_df_crud):
    return InviteService(
        user_crud=mock_user_crud,
        role_crud=mock_role_crud,
        invite_crud=mock_invite_crud,
        df_crud=mock_df_crud,
        business_logs_collection="test_logs",
        df_register_collection=MagicMock(),
    )


@pytest.fixture
def current_user_data():
    return {"_id": str(ObjectId()), "email": "test@example.com", "df_id": "df123", "user_roles": []}


@pytest.fixture
def system_admin_role_id():
    return "system_admin_role_id"


@pytest.fixture
def invite_data():
    return InviteModel(
        invited_user_email="newuser@example.com",
        invited_user_name="New User",
        invited_user_roles=[],
    )


# --- Tests for create_invite ---
@pytest.mark.asyncio
async def test_create_invite_success(invite_service, mock_user_crud, mock_invite_crud, current_user_data, invite_data, monkeypatch):
    mock_user_crud.get_user_by_email.return_value = None
    mock_invite_crud.get_pending_invite.return_value = None
    mock_invite_crud.get_invite_by_token.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)
    mock_mail_sender = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.mail_sender", mock_mail_sender)

    result = await invite_service.create_invite(invite_data, current_user_data, "system_admin_role_id")

    mock_user_crud.get_user_by_email.assert_called_once_with(invite_data.invited_user_email)
    mock_invite_crud.get_pending_invite.assert_called_once_with(invite_data.invited_user_email)
    mock_mail_sender.assert_called_once()
    mock_invite_crud.create_invite.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Invite sent successfully!"


@pytest.mark.asyncio
async def test_create_invite_user_already_exists(invite_service, mock_user_crud, current_user_data, invite_data, monkeypatch):
    mock_user_crud.get_user_by_email.return_value = {"email": invite_data.invited_user_email}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await invite_service.create_invite(invite_data, current_user_data, "system_admin_role_id")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already exists in the system" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_create_invite_pending_invite_exists(invite_service, mock_user_crud, mock_invite_crud, current_user_data, invite_data, monkeypatch):
    mock_user_crud.get_user_by_email.return_value = None
    mock_invite_crud.get_pending_invite.return_value = {"email": invite_data.invited_user_email}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await invite_service.create_invite(invite_data, current_user_data, "system_admin_role_id")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "An invitation is already pending for this email" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for verify_token ---
@pytest.mark.asyncio
async def test_verify_token_success(invite_service, mock_invite_crud, mock_user_crud, mock_df_crud, mock_role_crud, monkeypatch):
    token = "valid_token"
    invite = {
        "_id": ObjectId(),
        "invited_user_email": "test@example.com",
        "expiry_at": datetime.now(UTC) + timedelta(days=1),
        "invite_status": "pending",
        "invited_df": "df123",
        "invited_user_roles": [],
    }
    mock_invite_crud.get_invite_by_token.return_value = invite
    mock_user_crud.get_user_by_email.return_value = None
    mock_df_crud.get_data_fiduciary.return_value = {"_id": "df123"}
    mock_user_crud.insert_user_data.return_value = str(ObjectId())

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    result = await invite_service.verify_token(token)

    assert result["message"] == "Invite accepted successfully!"
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_verify_token_invalid(invite_service, mock_invite_crud, monkeypatch):
    token = "invalid_token"
    mock_invite_crud.get_invite_by_token.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await invite_service.verify_token(token)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Invalid invite token" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_verify_token_expired(invite_service, mock_invite_crud, mock_user_crud, monkeypatch):
    token = "expired_token"
    invite = {
        "invited_user_email": "test@example.com",
        "expiry_at": datetime.now(UTC) - timedelta(days=1),
        "invite_status": "pending",
    }
    mock_invite_crud.get_invite_by_token.return_value = invite
    mock_user_crud.get_user_by_email.return_value = None  # Ensure user does not exist

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await invite_service.verify_token(token)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invite has expired" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for get_all_invites ---
@pytest.mark.asyncio
async def test_get_all_invites_success(invite_service, mock_invite_crud, current_user_data, monkeypatch):
    mock_invite_crud.get_invites.return_value = []

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    result = await invite_service.get_all_invites(current_user_data)

    assert result == {"pending": [], "accepted": [], "expired": []}
    mock_log.assert_called_once()


# --- Tests for resend_invites ---
@pytest.mark.asyncio
async def test_resend_invites_success(invite_service, mock_invite_crud, current_user_data, monkeypatch):
    invite_id = str(ObjectId())
    invite = {
        "_id": invite_id,
        "invited_user_email": "test@example.com",
        "invite_status": "pending",
        "is_deleted": False,
    }
    mock_invite_crud.get_invite_by_id.return_value = invite
    mock_invite_crud.get_invite_by_token.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)
    mock_mail_sender = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.mail_sender", mock_mail_sender)

    result = await invite_service.resend_invites(invite_id, current_user_data)

    assert result["message"] == "Invite resent successfully!"
    mock_mail_sender.assert_called_once()
    mock_log.assert_called_once()


# --- Tests for cancel_invite ---
@pytest.mark.asyncio
async def test_cancel_invite_success(invite_service, mock_invite_crud, current_user_data, monkeypatch):
    invite_id = str(ObjectId())
    invite = {
        "_id": invite_id,
        "invited_user_email": "test@example.com",
        "is_deleted": False,
    }
    mock_invite_crud.get_invite_by_id.return_value = invite

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.invite_service.log_business_event", mock_log)

    result = await invite_service.cancel_invite(invite_id, current_user_data)

    assert result["message"] == "Invite deleted successfully!"
    mock_invite_crud.soft_delete_invite.assert_called_once_with(invite_id)
    mock_log.assert_called_once()
