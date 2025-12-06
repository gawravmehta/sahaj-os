import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from fastapi import HTTPException

from app.services.user_notification_service import create_user_notification


@pytest.fixture
def mock_df_collection():
    return AsyncMock()


@pytest.fixture
def mock_user_collection():
    return AsyncMock()


@pytest.fixture
def mock_notification_collection():
    return AsyncMock()


@pytest.fixture
def valid_df():
    return {"df_id": "df123"}


@pytest.fixture
def valid_user():
    return {"_id": ObjectId(), "email": "abc@example.com"}


# --------------------------------------------------------------------------
# TEST: df_id validation
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_user_notification_invalid_df(
    mock_df_collection, mock_user_collection, mock_notification_collection
):
    mock_df_collection.find_one.return_value = None

    with pytest.raises(ValueError) as exc:
        await create_user_notification(
            df_id="df999",
            users_list=["u1"],
            notification_title="Hello",
            df_register_collection=mock_df_collection,
            user_collection=mock_user_collection,
            notification_collection=mock_notification_collection,
        )
    assert "df_id is mandatory" in str(exc.value)


# --------------------------------------------------------------------------
# TEST: empty users_list
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_user_notification_empty_users_list(
    mock_df_collection, mock_user_collection, mock_notification_collection, valid_df
):
    mock_df_collection.find_one.return_value = valid_df

    with pytest.raises(ValueError) as exc:
        await create_user_notification(
            df_id="df123",
            users_list=[],
            notification_title="Hello",
            df_register_collection=mock_df_collection,
            user_collection=mock_user_collection,
            notification_collection=mock_notification_collection,
        )
    assert "users_list must contain at least one" in str(exc.value)


# --------------------------------------------------------------------------
# TEST: invalid user in users_list
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_user_notification_invalid_user(
    mock_df_collection, mock_user_collection, mock_notification_collection, valid_df
):
    mock_df_collection.find_one.return_value = valid_df

    mock_user_collection.find_one.return_value = None  # invalid user

    with pytest.raises(ValueError) as exc:
        await create_user_notification(
            df_id="df123",
            users_list=[str(ObjectId())],
            notification_title="Hello",
            df_register_collection=mock_df_collection,
            user_collection=mock_user_collection,
            notification_collection=mock_notification_collection,
        )
    assert "Invalid user ID" in str(exc.value)


# --------------------------------------------------------------------------
# TEST: success case
# --------------------------------------------------------------------------

@pytest.mark.asyncio
@patch("app.services.user_notification_service.notifier.push", new_callable=AsyncMock)
async def test_create_user_notification_success(
    mock_push,
    mock_df_collection,
    mock_user_collection,
    mock_notification_collection,
    valid_df,
    valid_user,
):
    mock_df_collection.find_one.return_value = valid_df
    mock_user_collection.find_one.return_value = valid_user
    mock_notification_collection.insert_one.return_value = None

    user_id = str(valid_user["_id"])

    result = await create_user_notification(
        df_id="df123",
        users_list=[user_id],
        notification_title="Test Notification",
        notification_message="Hello world!",
        df_register_collection=mock_df_collection,
        user_collection=mock_user_collection,
        notification_collection=mock_notification_collection,
    )

    # notifier.push must be awaited
    mock_push.assert_awaited()

    # DB insert must be called
    mock_notification_collection.insert_one.assert_awaited()

    # Validate document sent to push()
    args, kwargs = mock_push.call_args
    assert args[0] == user_id
    assert args[1]["notification_title"] == "Test Notification"
    assert args[1]["notification_message"] == "Hello world!"


# --------------------------------------------------------------------------
# TEST: DB insert failure
# --------------------------------------------------------------------------

@pytest.mark.asyncio
@patch("app.services.user_notification_service.notifier.push", new_callable=AsyncMock)
async def test_create_user_notification_insert_failure(
    mock_push,
    mock_df_collection,
    mock_user_collection,
    mock_notification_collection,
    valid_df,
    valid_user,
):
    mock_df_collection.find_one.return_value = valid_df
    mock_user_collection.find_one.return_value = valid_user

    # Simulate DB insertion error
    mock_notification_collection.insert_one.side_effect = Exception("DB crashed")

    with pytest.raises(Exception) as exc:
        await create_user_notification(
            df_id="df123",
            users_list=[str(valid_user["_id"])],
            notification_title="Break me",
            df_register_collection=mock_df_collection,
            user_collection=mock_user_collection,
            notification_collection=mock_notification_collection,
        )

    assert "Failed to create notification: DB crashed" in str(exc.value)
