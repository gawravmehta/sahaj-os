import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, UTC, timedelta
from bson import ObjectId

from app.services.auth_service import AuthService
from app.schemas.auth_schema import UserInDB, Token


# -----------------------------------------------------
# FIXTURES
# -----------------------------------------------------


@pytest.fixture
def mock_user_crud():
    return AsyncMock()


@pytest.fixture
def mock_user_collection():
    mock = AsyncMock()
    mock.update_one = AsyncMock()
    return mock


@pytest.fixture
def mock_df_register_collection():
    mock = AsyncMock()
    mock.insert_one = AsyncMock()
    return mock


@pytest.fixture
def service(mock_user_crud, mock_user_collection, mock_df_register_collection):
    return AuthService(
        user_crud=mock_user_crud,
        business_logs_collection="business_logs",
        user_collection=mock_user_collection,
        df_register_collection=mock_df_register_collection,
    )


@pytest.fixture
def mock_user_data():
    # Matches UserInDB schema fields
    return UserInDB(
        _id=str(ObjectId()),
        email="test@example.com",
        password="$2b$12$abcdefghijklmnopqrstuv",  # fake hashed pwd
        df_id="df123",
        user_roles=["admin"],
        is_password_reseted=False,
        is_org_configured=True,
        is_invited_user=False,
    )


# -----------------------------------------------------
# TEST CASES
# -----------------------------------------------------


@pytest.mark.asyncio
async def test_authenticate_user_success(service, mock_user_crud, mock_user_data, monkeypatch):
    """User exists + password is correct = success"""

    # Mock DB user
    mock_user_crud.get_user_by_email.return_value = mock_user_data

    # Mock password verification
    monkeypatch.setattr("app.services.auth_service.pwd_context.verify", lambda pwd, hashed: True)

    # Mock business logger
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.log_business_event", mock_log)

    result = await service.authenticate_user("test@example.com", "correctpassword")

    assert result.email == "test@example.com"
    assert result.df_id == "df123"
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_not_found(service, mock_user_crud, monkeypatch):
    """Raise 401 when user does not exist"""

    mock_user_crud.get_user_by_email.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await service.authenticate_user("missing@example.com", "password")

    assert exc.value.status_code == 401
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(service, mock_user_crud, mock_user_data, monkeypatch):
    """Raise 401 when password is wrong"""

    mock_user_crud.get_user_by_email.return_value = mock_user_data

    monkeypatch.setattr("app.services.auth_service.pwd_context.verify", lambda pwd, hashed: False)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await service.authenticate_user("test@example.com", "wrongpassword")

    assert exc.value.status_code == 401
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_creates_df_if_missing(
    service, mock_user_crud, mock_user_collection, mock_df_register_collection, monkeypatch
):
    """DF auto-registration should happen if df_id is None"""

    # Create a fake user object with attributes, not a pydantic model
    user_mock = MagicMock()
    user_mock.id = ObjectId()
    user_mock.email = "new@example.com"
    user_mock.password = "$2b$12$abcdefghijklmnopqrstuv"
    user_mock.df_id = None
    user_mock.user_roles = []
    user_mock.is_password_reseted = False
    user_mock.is_org_configured = False
    user_mock.is_invited_user = False

    # CRUD mock returns this user object
    mock_user_crud.get_user_by_email.return_value = user_mock

    # Password verification should pass
    monkeypatch.setattr("app.services.auth_service.pwd_context.verify", lambda pwd, hashed: True)

    # Mock logging
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.log_business_event", mock_log)

    result = await service.authenticate_user("new@example.com", "password")

    # Assertions
    mock_df_register_collection.insert_one.assert_called_once()
    mock_user_collection.update_one.assert_called_once()

    assert result.df_id is not None  # df_id auto-created

    mock_log.assert_called()


@pytest.mark.asyncio
async def test_create_access_token_for_user(service, monkeypatch):
    """Token creation should return Token schema"""

    mock_user = UserInDB(
        _id=str(ObjectId()),
        email="test@example.com",
        password=None,
        df_id="df123",
        user_roles=["admin"],
    )

    # Mock JWT token
    monkeypatch.setattr("app.services.auth_service.create_access_token", lambda data, expires_delta: "FAKE_TOKEN")

    # Mock logger
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.log_business_event", mock_log)

    token: Token = await service.create_access_token_for_user(mock_user)

    assert token.access_token == "FAKE_TOKEN"
    assert token.token_type == "bearer"
    mock_log.assert_called_once()
