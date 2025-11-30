import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.crud.invite_crud import InviteCRUD


@pytest.fixture
def mock_collection():
    """Mocked Mongo collection with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.find_one = AsyncMock(return_value=None)
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()

    cursor = MagicMock()
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_collection):
    return InviteCRUD(mock_collection)


@pytest.fixture
def dummy_invite_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "invited_user_email": "test@example.com",
        "invite_status": "pending",
        "invite_token": "some_token_123",
        "invited_df": "df123",
        "is_deleted": False,
        "role_id": "role456",
    }


@pytest.mark.asyncio
async def test_get_pending_invite(crud, mock_collection, dummy_invite_data):
    mock_collection.find_one.return_value = dummy_invite_data.copy()
    email = dummy_invite_data["invited_user_email"]

    result = await crud.get_pending_invite(email)

    mock_collection.find_one.assert_called_once_with(
        {
            "invited_user_email": email,
            "invite_status": "pending",
            "is_deleted": False,
        }
    )
    assert result == dummy_invite_data


@pytest.mark.asyncio
async def test_get_invite_by_token(crud, mock_collection, dummy_invite_data):
    mock_collection.find_one.return_value = dummy_invite_data.copy()
    token = dummy_invite_data["invite_token"]

    result = await crud.get_invite_by_token(token)

    mock_collection.find_one.assert_called_once_with({"invite_token": token, "is_deleted": False})
    assert result == dummy_invite_data


@pytest.mark.asyncio
async def test_get_invite_by_id(crud, mock_collection, dummy_invite_data):
    mock_collection.find_one.return_value = dummy_invite_data.copy()
    invite_id = str(dummy_invite_data["_id"])

    result = await crud.get_invite_by_id(invite_id)

    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(invite_id), "is_deleted": False})
    assert result == dummy_invite_data


@pytest.mark.asyncio
async def test_create_invite(crud, mock_collection, dummy_invite_data):
    mock_insert_one_result = MagicMock()
    mock_insert_one_result.inserted_id = dummy_invite_data["_id"]
    mock_collection.insert_one.return_value = mock_insert_one_result

    invite_data_to_create = dummy_invite_data.copy()
    del invite_data_to_create["_id"]

    result = await crud.create_invite(invite_data_to_create)

    mock_collection.insert_one.assert_called_once_with(invite_data_to_create)
    assert result == mock_insert_one_result


@pytest.mark.asyncio
async def test_update_invite_data(crud, mock_collection, dummy_invite_data):
    invite_id = str(dummy_invite_data["_id"])
    update_data = {"invite_status": "accepted"}

    mock_collection.update_one.return_value = MagicMock(matched_count=1, modified_count=1)

    result = await crud.update_invite_data(invite_id, update_data)

    mock_collection.update_one.assert_called_once_with({"_id": ObjectId(invite_id)}, {"$set": update_data})
    assert result.matched_count == 1
    assert result.modified_count == 1


@pytest.mark.asyncio
async def test_get_invites(crud, mock_collection, dummy_invite_data):
    mock_collection.find.return_value.to_list.return_value = [dummy_invite_data.copy()]
    df_id = dummy_invite_data["invited_df"]
    page = 1
    page_size = 10

    result = await crud.get_invites(df_id, page, page_size)

    mock_collection.find.assert_called_once_with({"invited_df": df_id, "is_deleted": False})
    mock_collection.find.return_value.skip.assert_called_once_with((page - 1) * page_size)
    mock_collection.find.return_value.limit.assert_called_once_with(page_size)
    mock_collection.find.return_value.to_list.assert_called_once_with(length=None)
    assert result == [dummy_invite_data]


@pytest.mark.asyncio
async def test_soft_delete_invite(crud, mock_collection, dummy_invite_data):
    invite_id = str(dummy_invite_data["_id"])
    mock_collection.update_one.return_value = MagicMock(matched_count=1, modified_count=1)

    result = await crud.soft_delete_invite(invite_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(invite_id)},
        {"$set": {"is_deleted": True}},
    )
    assert result.matched_count == 1
    assert result.modified_count == 1
