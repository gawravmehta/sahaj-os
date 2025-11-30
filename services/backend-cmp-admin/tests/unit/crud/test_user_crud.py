import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException

from app.crud.user_crud import UserCRUD
from app.schemas.auth_schema import UserInDB
from app.utils.common import convert_objectid_to_str


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_users_collection():
    """Mocked Mongo collection for users with correct async behavior."""
    collection = MagicMock(spec=AsyncIOMotorCollection)

    collection.find_one = AsyncMock(return_value=None)
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.count_documents = AsyncMock(return_value=0)

    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[])
    collection.find.return_value = cursor

    return collection


@pytest.fixture
def crud(mock_users_collection):
    return UserCRUD(mock_users_collection)


@pytest.fixture
def dummy_user_data():
    return {
        "_id": ObjectId("60d0fe4f3460595e63456789"),
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "df_id": "df123",
        "user_roles": [],
        "user_departments": [],
        "is_active": True,
        "is_superuser": False,
    }


# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_user_by_email_found(crud, mock_users_collection, dummy_user_data):
    mock_users_collection.find_one.return_value = dummy_user_data.copy()

    result = await crud.get_user_by_email(dummy_user_data["email"])

    mock_users_collection.find_one.assert_called_once_with({"email": dummy_user_data["email"]})
    assert isinstance(result, UserInDB)
    assert result.email == dummy_user_data["email"]


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(crud, mock_users_collection):
    mock_users_collection.find_one.return_value = None

    result = await crud.get_user_by_email("unknown@example.com")

    mock_users_collection.find_one.assert_called_once()
    assert result is None


# ---------------- Test get_user_by_id --------------------

@pytest.mark.asyncio
@patch("app.crud.user_crud.validate_object_id")
async def test_get_user_by_id_success(mock_validate_object_id, crud, mock_users_collection, dummy_user_data):
    uid = str(dummy_user_data["_id"])
    mock_validate_object_id.return_value = ObjectId(uid)
    mock_users_collection.find_one.return_value = dummy_user_data.copy()

    result = await crud.get_user_by_id(uid)

    mock_validate_object_id.assert_called_once_with(uid)
    mock_users_collection.find_one.assert_called_once_with({"_id": ObjectId(uid)})
    assert isinstance(result, UserInDB)
    assert result.email == dummy_user_data["email"]


@pytest.mark.asyncio
@patch("app.crud.user_crud.validate_object_id")
async def test_get_user_by_id_invalid(mock_validate_object_id, crud, mock_users_collection):
    mock_validate_object_id.side_effect = HTTPException(422, "Invalid ObjectId format")

    with pytest.raises(HTTPException):
        await crud.get_user_by_id("invalid")

    mock_users_collection.find_one.assert_not_called()


@pytest.mark.asyncio
@patch("app.crud.user_crud.validate_object_id")
async def test_get_user_by_id_not_found(mock_validate_object_id, crud, mock_users_collection):
    uid = "60d0fe4f3460595e63456781"
    mock_validate_object_id.return_value = ObjectId(uid)
    mock_users_collection.find_one.return_value = None

    result = await crud.get_user_by_id(uid)

    assert result is None


# ---------------- Test find_by_ids --------------------

@pytest.mark.asyncio
@patch("app.crud.user_crud.validate_object_id")
async def test_find_by_ids(mock_validate_object_id, crud, mock_users_collection, dummy_user_data):

    user_ids = [
        "60d0fe4f3460595e63456789",
        "60d0fe4f3460595e6345678a",
        "invalid_id"
    ]

    valid_obj_ids = [
        ObjectId("60d0fe4f3460595e63456789"),
        ObjectId("60d0fe4f3460595e6345678a")
    ]

    # Valid → True (truthy) ; Invalid → False (skip)
    mock_validate_object_id.side_effect = (
        lambda uid: True if ObjectId.is_valid(uid) else False
    )

    user_doc_1 = {**dummy_user_data, "_id": valid_obj_ids[0], "email": "user1@example.com"}
    user_doc_2 = {**dummy_user_data, "_id": valid_obj_ids[1], "email": "user2@example.com"}

    mock_users_collection.find.return_value.to_list.return_value = [
        user_doc_1.copy(),
        user_doc_2.copy(),
    ]

    result = await crud.find_by_ids(user_ids)

    assert mock_validate_object_id.call_count == 3
    mock_users_collection.find.assert_called_once_with({"_id": {"$in": valid_obj_ids}})
    assert len(result) == 2
    assert result[0]["_id"] == str(valid_obj_ids[0])
    assert result[1]["_id"] == str(valid_obj_ids[1])


# ---------------- Insert user --------------------

@pytest.mark.asyncio
async def test_insert_user_data(crud, mock_users_collection, dummy_user_data):

    inserted_id = ObjectId("60d0fe4f3460595e6345678b")
    mock_users_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    to_insert = dummy_user_data.copy()
    del to_insert["_id"]
    to_insert["email"] = "new@example.com"

    result = await crud.insert_user_data(to_insert)

    mock_users_collection.insert_one.assert_called_once_with(to_insert)
    assert result == inserted_id


# ---------------- Update role --------------------

@pytest.mark.asyncio
async def test_add_role_to_user(crud, mock_users_collection, dummy_user_data):
    user_id = str(dummy_user_data["_id"])
    role_id = "role123"

    mock_update = MagicMock(matched_count=1, modified_count=1)
    mock_users_collection.update_one.return_value = mock_update

    result = await crud.add_role_to_user(user_id, role_id)

    mock_users_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"user_roles": role_id}},
    )
    assert result == mock_update


# ---------------- Update department --------------------

@pytest.mark.asyncio
async def test_add_department_to_user(crud, mock_users_collection, dummy_user_data):

    user_id = str(dummy_user_data["_id"])
    dept_id = "dept123"

    mock_update = MagicMock(matched_count=1, modified_count=1)
    mock_users_collection.update_one.return_value = mock_update

    result = await crud.add_department_to_user(user_id, dept_id)

    mock_users_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"user_departments": dept_id}},
    )
    assert result == mock_update


# ---------------- Count users --------------------

@pytest.mark.asyncio
async def test_count_users(crud, mock_users_collection, dummy_user_data):

    df_id = dummy_user_data["df_id"]
    mock_users_collection.count_documents.return_value = 5

    result = await crud.count_users(df_id)

    mock_users_collection.count_documents.assert_called_once_with({"df_id": df_id})
    assert result == 5
