import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from datetime import datetime, UTC
from bson import ObjectId

from app.services.role_service import RoleService
from app.crud.role_crud import RoleCRUD
from app.crud.user_crud import UserCRUD
from app.schemas.role_schema import AddRole, UpdateRole, UpdateRolePermissions, UpdateRoleUser
from app.schemas.auth_schema import UserInDB as User

# --- Fixtures ---
@pytest.fixture
def mock_role_crud():
    return MagicMock(spec=RoleCRUD)


@pytest.fixture
def mock_user_crud():
    return MagicMock(spec=UserCRUD)


@pytest.fixture
def role_service(mock_role_crud, mock_user_crud):
    return RoleService(
        role_crud=mock_role_crud,
        user_crud=mock_user_crud,
        business_logs_collection="test_logs",
    )


@pytest.fixture
def current_user_data():
    return {"_id": str(ObjectId()), "email": "test@example.com", "df_id": "df123", "user_roles": []}


@pytest.fixture
def system_admin_role_id():
    return "system_admin_role_id"


@pytest.fixture
def role_data_add():
    return AddRole(
        role_name="test role",
        role_description="This is a test role.",
    )


@pytest.fixture
def sample_role_in_db(current_user_data):
    return {
        "_id": ObjectId(),
        "df_id": current_user_data["df_id"],
        "role_name": "existing role",
        "role_description": "An existing role.",
        "role_users": [],
        "created_at": datetime.now(UTC),
        "created_by": current_user_data["_id"],
        "modules_accessible": [],
        "routes_accessible": [],
        "apis_accessible": [],
        "is_deleted": False,
    }


@pytest.fixture
def sample_user_in_db(current_user_data):
    return User(
        id=str(ObjectId()),
        email="test@example.com",
        df_id=current_user_data["df_id"],
        user_roles=[],
    )


# --- Tests for add_role ---
@pytest.mark.asyncio
async def test_add_role_success(role_service, mock_role_crud, current_user_data, role_data_add, monkeypatch):
    mock_role_crud.find_by_name.return_value = None
    mock_role_crud.insert.return_value = MagicMock(inserted_id=ObjectId())

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.add_role(role_data_add, current_user_data)

    mock_role_crud.find_by_name.assert_called_once_with(role_data_add.role_name, current_user_data["df_id"])
    mock_role_crud.insert.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Role added successfully"
    assert "role_id" in result


@pytest.mark.asyncio
async def test_add_role_duplicate_name(role_service, mock_role_crud, current_user_data, role_data_add, sample_role_in_db, monkeypatch):
    mock_role_crud.find_by_name.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await role_service.add_role(role_data_add, current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Role with this name already exists" in exc_info.value.detail
    mock_role_crud.find_by_name.assert_called_once()
    mock_role_crud.insert.assert_not_called()
    mock_log.assert_called_once()


# --- Tests for get_all_roles ---
@pytest.mark.asyncio
async def test_get_all_roles_success(role_service, mock_role_crud, current_user_data, sample_role_in_db):
    mock_role_crud.get_roles_paginated.return_value = [sample_role_in_db]
    mock_role_crud.count_roles.return_value = 1

    result = await role_service.get_all_roles(current_user_data, page=1, limit=10)

    mock_role_crud.get_roles_paginated.assert_called_once_with(current_user_data["df_id"], 0, 10)
    mock_role_crud.count_roles.assert_called_once_with(current_user_data["df_id"])
    assert result["total_roles"] == 1
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == str(sample_role_in_db["_id"])


@pytest.mark.asyncio
async def test_get_all_roles_invalid_pagination(role_service, current_user_data):
    with pytest.raises(HTTPException) as exc_info:
        await role_service.get_all_roles(current_user_data, page=0, limit=10)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Page and limit must be positive integers" in exc_info.value.detail


# --- Tests for get_one_role ---
@pytest.mark.asyncio
async def test_get_one_role_success(role_service, mock_role_crud, current_user_data, sample_role_in_db):
    role_id = str(sample_role_in_db["_id"])
    mock_role_crud.find_by_id.return_value = sample_role_in_db

    result = await role_service.get_one_role(role_id, current_user_data)

    mock_role_crud.find_by_id.assert_called_once_with(role_id)
    assert result["_id"] == role_id


@pytest.mark.asyncio
async def test_get_one_role_not_found(role_service, mock_role_crud, current_user_data):
    role_id = str(ObjectId())
    mock_role_crud.find_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await role_service.get_one_role(role_id, current_user_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Role not found" in exc_info.value.detail
    mock_role_crud.find_by_id.assert_called_once_with(role_id)


# --- Tests for update_role_users ---
@pytest.mark.asyncio
async def test_update_role_users_success(
    role_service, mock_role_crud, mock_user_crud, current_user_data, sample_role_in_db, sample_user_in_db, system_admin_role_id, monkeypatch
):
    role_id = str(sample_role_in_db["_id"])
    user_id = sample_user_in_db.id
    update_data = UpdateRoleUser(users_list=[user_id])
    sample_role_in_db["created_by"] = current_user_data["_id"]

    mock_role_crud.find_by_id.return_value = sample_role_in_db
    mock_user_crud.get_user_by_id.return_value = sample_user_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.update_role_users(role_id, update_data, current_user_data, system_admin_role_id)

    mock_role_crud.find_by_id.assert_called_once_with(role_id)
    mock_user_crud.get_user_by_id.assert_called_once_with(user_id)
    mock_role_crud.update_role_users.assert_called_once_with(role_id, [user_id])
    mock_user_crud.add_role_to_user.assert_called_once_with(user_id, role_id)
    assert result["message"] == "Users added to role successfully"
    assert user_id in result["updated_users"]
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_role_users_unauthorized(role_service, mock_role_crud, current_user_data, sample_role_in_db, system_admin_role_id, monkeypatch):
    role_id = str(sample_role_in_db["_id"])
    update_data = UpdateRoleUser(users_list=[str(ObjectId())])
    sample_role_in_db["created_by"] = str(ObjectId())  # Different user

    mock_role_crud.find_by_id.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await role_service.update_role_users(role_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for update_role_permissions ---
@pytest.mark.asyncio
async def test_update_role_permissions_success(role_service, mock_role_crud, current_user_data, sample_role_in_db, system_admin_role_id, monkeypatch):
    role_id = str(sample_role_in_db["_id"])
    update_data = UpdateRolePermissions(routes_accessible=[])
    sample_role_in_db["created_by"] = current_user_data["_id"]

    mock_role_crud.find_by_id.return_value = sample_role_in_db
    mock_reset_role_policies = MagicMock()
    monkeypatch.setattr("app.services.role_service.reset_role_policies", mock_reset_role_policies)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.update_role_permissions(role_id, update_data, current_user_data, system_admin_role_id)

    mock_role_crud.find_by_id.assert_called_once_with(role_id)
    mock_role_crud.update_role_permissions.assert_called_once()
    mock_reset_role_policies.assert_called_once()
    assert result["message"] == "Role permissions updated successfully"
    mock_log.assert_called_once()


# --- Tests for search_role ---
@pytest.mark.asyncio
async def test_search_role_success(role_service, mock_role_crud, current_user_data, sample_role_in_db):
    mock_role_crud.search_roles.return_value = [sample_role_in_db]

    result = await role_service.search_role("existing", current_user_data)

    mock_role_crud.search_roles.assert_called_once_with(current_user_data["df_id"], "existing")
    assert len(result["data"]) == 1
    assert result["data"][0]["role_name"] == "existing role"


@pytest.mark.asyncio
async def test_search_role_not_found(role_service, mock_role_crud, current_user_data):
    mock_role_crud.search_roles.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await role_service.search_role("non_existent", current_user_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "No matching roles found" in exc_info.value.detail


# --- Tests for update_role ---
@pytest.mark.asyncio
async def test_update_role_success(role_service, mock_role_crud, current_user_data, sample_role_in_db, system_admin_role_id, monkeypatch):
    role_id = str(sample_role_in_db["_id"])
    update_data = UpdateRole(role_name="new name")
    sample_role_in_db["created_by"] = current_user_data["_id"]
    mock_role_crud.find_by_id.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.update_role(role_id, update_data, current_user_data, system_admin_role_id)

    mock_role_crud.update_role.assert_called_once_with(role_id, {"role_name": "new name"})
    assert result["message"] == "Role updated successfully"
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_role_unauthorized(role_service, mock_role_crud, current_user_data, sample_role_in_db, system_admin_role_id, monkeypatch):
    role_id = str(sample_role_in_db["_id"])
    update_data = UpdateRole(role_name="new name")
    sample_role_in_db["created_by"] = str(ObjectId())  # Different user
    mock_role_crud.find_by_id.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await role_service.update_role(role_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for soft_delete_role ---
@pytest.mark.asyncio
async def test_soft_delete_role_success(role_service, mock_role_crud, current_user_data, sample_role_in_db, system_admin_role_id, monkeypatch):
    role_id = str(sample_role_in_db["_id"])
    sample_role_in_db["created_by"] = current_user_data["_id"]
    mock_role_crud.find_by_id.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.soft_delete_role(role_id, current_user_data, system_admin_role_id)

    mock_role_crud.soft_delete_role.assert_called_once()
    assert result["message"] == "Role soft deleted successfully"
    mock_log.assert_called_once()


# --- Tests for assign_roles_to_user ---
@pytest.mark.asyncio
async def test_assign_roles_to_user_success(
    role_service, mock_role_crud, mock_user_crud, current_user_data, sample_role_in_db, sample_user_in_db, system_admin_role_id, monkeypatch
):
    user_id = sample_user_in_db.id
    role_id = str(sample_role_in_db["_id"])
    mock_user_crud.get_user_by_id.return_value = sample_user_in_db
    mock_role_crud.find_by_id.return_value = sample_role_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.role_service.log_business_event", mock_log)

    result = await role_service.assign_roles_to_user(user_id, [role_id], current_user_data, system_admin_role_id)

    mock_user_crud.add_role_to_user.assert_called_once_with(user_id, role_id)
    mock_role_crud.add_user_to_role.assert_called_once_with(role_id, user_id)
    assert result["message"] == "Roles assigned to user successfully"
    mock_log.assert_called_once()


# --- Tests for get_all_frontend_routes ---
@pytest.mark.asyncio
async def test_get_all_frontend_routes_success(role_service, current_user_data):
    result = await role_service.get_all_frontend_routes(current_user_data)

    assert "data" in result
    assert isinstance(result["data"], list)
