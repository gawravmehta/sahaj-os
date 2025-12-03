import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from datetime import datetime, UTC
from bson import ObjectId

from app.services.data_fiduciary_service import DataFiduciaryService
from app.crud.data_fiduciary_crud import DataFiduciaryCRUD

# Correct imports (matching your schema)
from app.schemas.data_fiduciary_schema import (
    UpdateDataFiduciary,
    CommunicationConfig,
    SMTPConfig,
    SMTPCredentials,
    SMSConfig,
    SMSCredentials,
    AIConfig,
    UserBasicInfo,
)

from app.core.config import settings


# ---------------- FIXTURES -----------------

@pytest.fixture
def mock_data_fiduciary_crud():
    return AsyncMock(spec=DataFiduciaryCRUD)


@pytest.fixture
def mock_user_collection():
    return AsyncMock()


@pytest.fixture
def mock_df_keys_collection():
    return AsyncMock()


@pytest.fixture
def service(mock_data_fiduciary_crud, mock_user_collection, mock_df_keys_collection):
    return DataFiduciaryService(
        mock_data_fiduciary_crud,
        "test_business_logs",
        mock_user_collection,
        mock_df_keys_collection,
    )


@pytest.fixture
def mock_user():
    return {"_id": "user123", "email": "test@example.com", "df_id": "df123"}


# -------- Corrected Payload Fixtures --------

@pytest.fixture
def mock_update_payload_full():
    return UpdateDataFiduciary(
        communication=CommunicationConfig(
            smtp=SMTPConfig(
                credentials=SMTPCredentials(
                    host="smtp.host.com",
                    port=587,
                    username="smtp@example.com",
                    password="password",
                    from_email="smtp@example.com",
                ),
                system=None,
            ),
            sms=SMSConfig(
                credentials=SMSCredentials(
                    api_key="sms_key",
                    sender_id="sender",
                )
            ),
        ),
        ai=AIConfig(
            openrouter_api_key="ai_key"
        ),
        user_basic_info=UserBasicInfo(
            first_name="Test",
            last_name="User",
            phone="1234567890",
        ),
    )


@pytest.fixture
def mock_update_payload_partial():
    return UpdateDataFiduciary(
        communication=CommunicationConfig(
            smtp=SMTPConfig(
                credentials=SMTPCredentials(
                    host="smtp.host.com",
                    port=587,
                    username="smtp@example.com",
                    password="password",
                    from_email="smtp@example.com",
                )
            )
        )
    )


# ---------------- TESTS -----------------

@pytest.mark.asyncio
async def test_setup_success_full_payload(
    service, mock_data_fiduciary_crud, mock_user_collection, mock_user,
    mock_update_payload_full, monkeypatch
):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {"_id": ObjectId(), "df_id": df_id}
    mock_data_fiduciary_crud.update_data_fiduciary.return_value = True

    mock_user_collection.update_one.return_value = MagicMock(matched_count=1)

    mock_log_event = AsyncMock()
    monkeypatch.setattr(
        "app.services.data_fiduciary_service.log_business_event", mock_log_event
    )

    monkeypatch.setattr(
        "app.core.config.settings.SUPERADMIN_EMAIL", "admin@example.com"
    )

    mock_dt = MagicMock(wraps=datetime)
    mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    monkeypatch.setattr("app.services.data_fiduciary_service.datetime", mock_dt)

    result = await service.setup(df_id, mock_update_payload_full, mock_user)

    assert result["msg"] == "Data fiduciary setup successfully"
    assert result["df_id"] == df_id
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_setup_success_partial_payload(
    service, mock_data_fiduciary_crud, mock_user_collection, mock_user,
    mock_update_payload_partial, monkeypatch
):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {"_id": ObjectId(), "df_id": df_id}
    mock_data_fiduciary_crud.update_data_fiduciary.return_value = True

    mock_user_collection.update_one.return_value = MagicMock(matched_count=1)

    mock_log_event = AsyncMock()
    monkeypatch.setattr(
        "app.services.data_fiduciary_service.log_business_event", mock_log_event
    )

    monkeypatch.setattr(
        "app.core.config.settings.SUPERADMIN_EMAIL", "admin@example.com"
    )

    result = await service.setup(df_id, mock_update_payload_partial, mock_user)

    assert result["msg"] == "Data fiduciary setup successfully"
    assert result["df_id"] == df_id
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_setup_data_fiduciary_not_found(service, mock_data_fiduciary_crud, mock_user, mock_update_payload_full, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = None

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    with pytest.raises(HTTPException) as exc:
        await service.setup(df_id, mock_update_payload_full, mock_user)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Data fiduciary not found"
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_setup_no_updates_applied(service, mock_data_fiduciary_crud, mock_user, mock_update_payload_full, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {"_id": ObjectId(), "df_id": df_id}
    mock_data_fiduciary_crud.update_data_fiduciary.return_value = False

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    monkeypatch.setattr("app.core.config.settings.SUPERADMIN_EMAIL", "admin@example.com")

    with pytest.raises(HTTPException) as exc:
        await service.setup(df_id, mock_update_payload_full, mock_user)

    assert exc.value.status_code == 400
    assert exc.value.detail == "No updates were applied"
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_details_success(service, mock_data_fiduciary_crud, mock_df_keys_collection, mock_user, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {"_id": ObjectId(), "name": "Test DF"}
    mock_df_keys_collection.find_one.return_value = {"_id": ObjectId(), "df_id": df_id, "key": "value"}

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    res = await service.get_details(df_id, mock_user)

    assert res["df"]["name"] == "Test DF"
    assert res["df_keys"]["key"] == "value"
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_details_df_not_found(service, mock_data_fiduciary_crud, mock_df_keys_collection, mock_user, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = None
    mock_df_keys_collection.find_one.return_value = {"_id": ObjectId(), "df_id": df_id}

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    with pytest.raises(HTTPException) as exc:
        await service.get_details(df_id, mock_user)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Data fiduciary not found"
    mock_log_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_df_name_success(service, mock_data_fiduciary_crud, mock_user, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {
        "_id": ObjectId(),
        "org_info": {"name": "Test Org"}
    }

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    assert await service.get_df_name(df_id, mock_user) == "Test Org"


@pytest.mark.asyncio
async def test_get_df_name_not_found(service, mock_data_fiduciary_crud, mock_user, monkeypatch):
    df_id = "df123"
    mock_data_fiduciary_crud.get_data_fiduciary.return_value = None

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    with pytest.raises(HTTPException) as exc:
        await service.get_df_name(df_id, mock_user)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_sms_templates_success(service, mock_data_fiduciary_crud, mock_user, monkeypatch):
    df_id = "df123"

    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {
        "_id": ObjectId(),
        "communication": {
            "sms": {"templates": [{"id": "t1", "content": "Hello"}]}
        }
    }

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    result = await service.get_sms_templates(df_id, mock_user)

    assert len(result) == 1
    assert result[0]["id"] == "t1"


@pytest.mark.asyncio
async def test_get_in_app_notification_templates_success(service, mock_data_fiduciary_crud, mock_user, monkeypatch):
    df_id = "df123"

    mock_data_fiduciary_crud.get_data_fiduciary.return_value = {
        "_id": ObjectId(),
        "communication": {
            "in_app": [{"id": "n1", "content": "Hi"}]
        }
    }

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.data_fiduciary_service.log_business_event", mock_log_event)

    result = await service.get_in_app_notification_templates(df_id, mock_user)

    assert len(result) == 1
    assert result[0]["id"] == "n1"
