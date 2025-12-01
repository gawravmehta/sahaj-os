import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from datetime import datetime, UTC
from bson import ObjectId

from app.services.department_service import DepartmentService
from app.crud.department_crud import DepartmentCRUD
from app.crud.user_crud import UserCRUD
from app.schemas.department_schema import AddDepartment, UpdateDepartmentPermission, UpdateDepartmentRequest, UpdateDepartmentUsers, UserModel
from app.utils.business_logger import log_business_event


# --- Fixtures ---
@pytest.fixture
def mock_department_crud():
    return MagicMock(spec=DepartmentCRUD)


@pytest.fixture
def mock_user_crud():
    return MagicMock(spec=UserCRUD)


@pytest.fixture
def department_service(mock_department_crud, mock_user_crud):
    return DepartmentService(
        department_crud=mock_department_crud,
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
def department_data_add():
    return AddDepartment(
        department_name="test department",
        department_description="This is a test department.",
    )


@pytest.fixture
def sample_department_in_db(current_user_data):
    return {
        "_id": ObjectId(),
        "df_id": current_user_data["df_id"],
        "department_name": "existing department",
        "department_description": "An existing department.",
        "department_users": [],
        "department_admins": [],
        "created_at": datetime.now(UTC),
        "created_by": current_user_data["_id"],
        "modules_accessible": [],
        "routes_accessible": [],
        "apis_accessible": [],
        "is_deleted": False,
    }


@pytest.fixture
def sample_user_model(current_user_data):
    return UserModel(
        _id=current_user_data["_id"],  # Correctly map _id
        id=current_user_data["_id"],  # Keep 'id' for consistency if needed elsewhere
        first_name="Test",
        last_name="User",
        email=current_user_data["email"],
        designation="Software Engineer",  # Added required field
        contact=1234567890,  # Added required field
        df_id=current_user_data["df_id"],
        token="dummy_token",  # Added required field
        is_email_verified=True,
        user_roles=[],
        user_departments=[],
        user_plan=[],  # Added required field
        password="dummy_password",  # Added required field
        created_at=datetime.now(UTC),  # Added required field
    )


# --- Tests for add_department ---
@pytest.mark.asyncio
async def test_add_department_success(department_service, mock_department_crud, current_user_data, department_data_add, monkeypatch):
    mock_department_crud.find_by_name.return_value = None
    mock_department_crud.create.return_value = MagicMock(inserted_id=ObjectId())

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.add_department(department_data_add, current_user_data)

    mock_department_crud.find_by_name.assert_called_once_with(department_data_add.department_name, current_user_data["df_id"])
    mock_department_crud.create.assert_called_once()
    mock_log.assert_called_once_with(
        event_type="DEPARTMENT_CREATED",
        user_email=current_user_data["email"],
        context=pytest.approx(
            {
                "user_id": current_user_data["_id"],
                "df_id": current_user_data["df_id"],
                "department_id": str(mock_department_crud.create.return_value.inserted_id),
                "reason": "Department created successfully",
            }
        ),
        message="Department created successfully",
        business_logs_collection="test_logs",
    )
    assert result["message"] == "Department added successfully"
    assert "department_id" in result


@pytest.mark.asyncio
async def test_add_department_no_df_id(department_service, current_user_data, department_data_add, monkeypatch):
    user_no_df_id = {**current_user_data, "df_id": None}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.add_department(department_data_add, user_no_df_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "User does not have an associated df_id" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_add_department_duplicate_name(
    department_service, mock_department_crud, current_user_data, department_data_add, sample_department_in_db, monkeypatch
):
    mock_department_crud.find_by_name.return_value = sample_department_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.add_department(department_data_add, current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "A department with the same name already exists." in exc_info.value.detail
    mock_department_crud.find_by_name.assert_called_once()
    mock_department_crud.create.assert_not_called()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_add_department_db_error(department_service, mock_department_crud, current_user_data, department_data_add, monkeypatch):
    mock_department_crud.find_by_name.return_value = None
    mock_department_crud.create.side_effect = Exception("DB connection error")

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.add_department(department_data_add, current_user_data)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database insertion error" in exc_info.value.detail
    mock_log.assert_not_called()  # Log not called if exception is raised before log in service


# --- Tests for update_department_users ---
@pytest.mark.asyncio
async def test_update_department_users_success_add_new_user(
    department_service,
    mock_department_crud,
    mock_user_crud,
    current_user_data,
    sample_department_in_db,
    sample_user_model,
    system_admin_role_id,
    monkeypatch,
):
    department_id = str(sample_department_in_db["_id"])
    new_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[new_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],  # Make current_user a department admin
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model  # For validation of new_user_id
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]  # Ensure df_id matches
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)
    mock_user_crud.add_department_to_user.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_user_crud.get_user_by_id.assert_called_once_with(new_user_id)
    mock_department_crud.update_department.assert_called_once()
    mock_user_crud.add_department_to_user.assert_called_once_with(new_user_id, department_id)
    mock_log.assert_called_once()

    assert result["message"] == "Department users and admins updated successfully"
    assert new_user_id in result["department_users"]


@pytest.mark.asyncio
async def test_update_department_users_invalid_department_id(
    department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch
):
    update_data = UpdateDepartmentUsers(department_users=[str(ObjectId())])

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users("invalid_id", update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid department_id format" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_not_called()
    mock_log.assert_not_called()  # No log if id format is invalid


@pytest.mark.asyncio
async def test_update_department_users_department_not_found(
    department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch
):
    department_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[str(ObjectId())])

    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    assert "UnboundLocalError" in exc_info.value.detail  # Due to user_id/df_id not defined in log context
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_not_called()  # Log not called because UnboundLocalError occurs first


@pytest.mark.asyncio
async def test_update_department_users_unauthorized(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentUsers(department_users=[str(ObjectId())])

    # User is neither system admin nor department admin
    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [str(ObjectId())],  # Other admin
    }
    user_not_admin = {**current_user_data, "_id": str(ObjectId()), "user_roles": []}  # Not an admin

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, user_not_admin, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once()
    mock_log.assert_called_once()  # Log is called in this scenario


@pytest.mark.asyncio
async def test_update_department_users_invalid_user_id_format(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentUsers(department_users=["invalid_user_id_format"])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "InvalidId" in exc_info.value.detail  # Due to ObjectId('invalid_user_id_format')
    mock_user_crud.get_user_by_id.assert_not_called()
    mock_log.assert_not_called()  # No log before HTTPException due to InvalidId


@pytest.mark.asyncio
async def test_update_department_users_user_not_found(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    non_existent_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[non_existent_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_user_crud.get_user_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert f"User {non_existent_user_id} not found" in exc_info.value.detail
    mock_user_crud.get_user_by_id.assert_called_once_with(non_existent_user_id)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_user_df_id_mismatch(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    mismatch_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[mismatch_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    # Mock return value correctly as a UserModel object
    mismatch_user_model = UserModel(
        _id=mismatch_user_id,
        id=mismatch_user_id,
        first_name="Mismatch",
        last_name="User",
        email="mismatch@example.com",
        designation="Software Engineer",
        contact=9876543210,
        df_id="other_df",  # Mismatch df_id
        token="mismatch_token",
        is_email_verified=True,
        user_roles=[],
        user_departments=[],
        user_plan=[],
        password="mismatch_password",
        created_at=datetime.now(UTC),
    )
    mock_user_crud.get_user_by_id.return_value = mismatch_user_model

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "does not belong to the same df_id as the department" in exc_info.value.detail
    mock_user_crud.get_user_by_id.assert_called_once_with(mismatch_user_id)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_overlap_users_admins(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    overlapping_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[overlapping_user_id], department_admins=[overlapping_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "cannot be both admins and users" in exc_info.value.detail  # Message from original HTTPException
    mock_log.assert_called_once()  # The error happens in validate_users, but the outer try-except means the log event might still be triggered or not depending on where user_id/df_id are set.


@pytest.mark.asyncio
async def test_update_department_users_duplicate_existing_user(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    existing_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[existing_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_users": [existing_user_id],  # User already exists
        "department_admins": [current_user_data["_id"]],
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.id = existing_user_id  # Match the ID
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "already exist in the department" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_duplicate_existing_admin(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    existing_admin_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_admins=[existing_admin_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"], existing_admin_id],  # Admin already exists
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.id = existing_admin_id
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "already exist in the department" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_promote_user_to_admin(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    promoted_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_admins=[promoted_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_users": [promoted_user_id],  # User is currently a regular user
        "department_admins": [current_user_data["_id"]],  # Current user is an admin
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.id = promoted_user_id
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)
    mock_user_crud.add_department_to_user.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    mock_department_crud.update_department.assert_called_once()
    assert promoted_user_id in result["department_admins"]
    assert promoted_user_id not in result["department_users"]
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_demote_admin_to_user(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    demoted_admin_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[demoted_admin_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_users": [],
        "department_admins": [current_user_data["_id"], demoted_admin_id],  # Admin is currently an admin
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.id = demoted_admin_id
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)
    mock_user_crud.add_department_to_user.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    mock_department_crud.update_department.assert_called_once()
    assert demoted_admin_id in result["department_users"]
    assert demoted_admin_id not in result["department_admins"]
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_users_db_update_error(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    new_user_id = str(ObjectId())
    update_data = UpdateDepartmentUsers(department_users=[new_user_id])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_user_crud.get_user_by_id.return_value = sample_user_model
    mock_user_crud.get_user_by_id.return_value.df_id = current_user_data["df_id"]
    mock_department_crud.update_department.side_effect = Exception("DB update error")

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_users(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database update error" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_permissions_success(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentPermission(modules_accessible=["module1"], routes_accessible=["/route1"], apis_accessible=["/api/v1/test"])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department_permissions(department_id, update_data, current_user_data, system_admin_role_id)

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_department_crud.update_department.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Department permissions updated successfully"
    assert "module1" in result["modules_accessible"]


@pytest.mark.asyncio
async def test_update_department_permissions_invalid_department_id(
    department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch
):
    update_data = UpdateDepartmentPermission(modules_accessible=["module1"])

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_permissions("invalid_id", update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid department_id format" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_not_called()
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_update_department_permissions_department_not_found(
    department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch
):
    department_id = str(ObjectId())
    update_data = UpdateDepartmentPermission(modules_accessible=["module1"])

    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_permissions(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "UnboundLocalError" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_update_department_permissions_unauthorized(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentPermission(modules_accessible=["module1"])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [str(ObjectId())],  # Other admin
    }
    user_not_admin = {**current_user_data, "_id": str(ObjectId()), "user_roles": []}  # Not an admin

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_permissions(department_id, update_data, user_not_admin, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once()
    mock_log.assert_called_once()  # Log is called in this scenario


@pytest.mark.asyncio
async def test_update_department_permissions_db_update_error(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentPermission(modules_accessible=["module1"])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_department_crud.update_department.side_effect = Exception("DB update error")

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department_permissions(department_id, update_data, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database update error" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for search_department ---
@pytest.mark.asyncio
async def test_search_department_success(department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch):
    search_name = "existing department"
    mock_department_crud.search_by_name.return_value = [{**sample_department_in_db, "_id": str(sample_department_in_db["_id"])}]

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.search_department(search_name, current_user_data)

    mock_department_crud.search_by_name.assert_called_once_with(search_name, current_user_data["df_id"])
    mock_log.assert_called_once()
    assert len(result) == 1
    assert result[0]["department_name"] == search_name
    assert result[0]["_id"] == str(sample_department_in_db["_id"])


@pytest.mark.asyncio
async def test_search_department_not_found(department_service, mock_department_crud, current_user_data, monkeypatch):
    search_name = "non-existent"
    mock_department_crud.search_by_name.return_value = []

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.search_department(search_name, current_user_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "No matching departments found" in exc_info.value.detail
    mock_department_crud.search_by_name.assert_called_once_with(search_name, current_user_data["df_id"])
    mock_log.assert_called_once()


# --- Tests for get_all_departments ---
@pytest.mark.asyncio
async def test_get_all_departments_success(department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch):
    mock_department_crud.get_all.return_value = [sample_department_in_db]
    mock_department_crud.count_departments.return_value = 1

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.get_all_departments(page=1, limit=10, current_user=current_user_data)

    mock_department_crud.get_all.assert_called_once_with(current_user_data["df_id"], skip=0, limit=10)
    mock_department_crud.count_departments.assert_called_once_with(current_user_data["df_id"])
    mock_log.assert_called_once()
    assert result["total_departments"] == 1
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == str(sample_department_in_db["_id"])


@pytest.mark.asyncio
async def test_get_all_departments_invalid_pagination(department_service, current_user_data, monkeypatch):
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.get_all_departments(page=0, limit=10, current_user=current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Page and limit must be positive integers" in exc_info.value.detail
    mock_log.assert_called_once()


# --- Tests for get_one_department ---
@pytest.mark.asyncio
async def test_get_one_department_success(
    department_service, mock_department_crud, mock_user_crud, current_user_data, sample_department_in_db, sample_user_model, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    sample_department_in_db_with_users = {
        **sample_department_in_db,
        "department_users": [current_user_data["_id"]],
        "department_admins": [current_user_data["_id"]],
    }
    mock_department_crud.find_by_id.return_value = sample_department_in_db_with_users
    mock_user_crud.find_by_ids.side_effect = [[sample_user_model], [sample_user_model]]  # For users and admins

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.get_one_department(department_id, current_user_data)

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_user_crud.find_by_ids.assert_called()  # Called for users and admins
    mock_log.assert_called_once()
    assert result["_id"] == department_id
    assert len(result["department_users_data"]) == 1
    assert len(result["department_admins_data"]) == 1
    assert result["department_users_data"][0]["id"] == current_user_data["_id"]


@pytest.mark.asyncio
async def test_get_one_department_invalid_department_id(department_service, current_user_data, monkeypatch):
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.get_one_department("invalid_id", current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid department_id format" in exc_info.value.detail
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_get_one_department_not_found(department_service, mock_department_crud, current_user_data, monkeypatch):
    department_id = str(ObjectId())
    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.get_one_department(department_id, current_user_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    assert "UnboundLocalError" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_get_one_department_unauthorized_df_id(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    department_other_df = {**sample_department_in_db, "df_id": "other_df"}
    mock_department_crud.find_by_id.return_value = department_other_df

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.get_one_department(department_id, current_user_data)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized access to department" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_called_once()


# --- Tests for update_department ---
@pytest.mark.asyncio
async def test_update_department_success(department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentRequest(department_description="New description.")

    mock_department_crud.find_by_id.return_value = sample_department_in_db
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department(department_id, update_data, current_user_data)

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_department_crud.update_department.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Department updated successfully"
    assert result["id"] == department_id


@pytest.mark.asyncio
async def test_update_department_invalid_department_id(department_service, current_user_data, monkeypatch):
    update_data = UpdateDepartmentRequest(department_description="New description.")

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department("invalid_id", update_data, current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid department_id format" in exc_info.value.detail
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_update_department_not_found(department_service, mock_department_crud, current_user_data, monkeypatch):
    department_id = str(ObjectId())
    update_data = UpdateDepartmentRequest(department_description="New description.")

    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department(department_id, update_data, current_user_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Department not found" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_no_fields_to_update(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentRequest()  # Empty update data

    mock_department_crud.find_by_id.return_value = sample_department_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.update_department(department_id, update_data, current_user_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "No fields provided to update" in exc_info.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_department_no_changes_made(department_service, mock_department_crud, current_user_data, sample_department_in_db, monkeypatch):
    department_id = str(sample_department_in_db["_id"])
    update_data = UpdateDepartmentRequest(department_description=sample_department_in_db["department_description"])  # Same description

    mock_department_crud.find_by_id.return_value = sample_department_in_db
    mock_department_crud.update_department.return_value = MagicMock(modified_count=0)  # No changes

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.update_department(department_id, update_data, current_user_data)

    assert result["message"] == "No changes made"
    mock_log.assert_called_once()


# --- Tests for soft_delete_department ---
@pytest.mark.asyncio
async def test_soft_delete_department_success(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"]],
    }
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.soft_delete_department(department_id, current_user_data, system_admin_role_id)

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_department_crud.update_department.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Department soft deleted successfully"
    assert result["department_id"] == department_id


@pytest.mark.asyncio
async def test_soft_delete_department_invalid_id(department_service, current_user_data, system_admin_role_id, monkeypatch):
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.soft_delete_department("invalid_id", current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid department_id format" in exc_info.value.detail
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_soft_delete_department_not_found(department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch):
    department_id = str(ObjectId())
    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.soft_delete_department(department_id, current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Department not found" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_soft_delete_department_unauthorized(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [str(ObjectId())],  # Other admin
    }
    user_not_admin = {**current_user_data, "_id": str(ObjectId()), "user_roles": []}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.soft_delete_department(department_id, user_not_admin, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Unauthorized" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once()
    mock_log.assert_not_called()  # user_id/df_id not defined yet, would cause UnboundLocalError


# --- Tests for remove_department_members ---
@pytest.mark.asyncio
async def test_remove_department_members_success(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    admin_to_remove = str(ObjectId())
    user_to_remove = str(ObjectId())

    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [current_user_data["_id"], admin_to_remove],
        "department_users": [user_to_remove, str(ObjectId())],  # Existing user
    }
    mock_department_crud.update_department.return_value = MagicMock(modified_count=1)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    result = await department_service.remove_department_members(
        department_id, [admin_to_remove], [user_to_remove], current_user_data, system_admin_role_id
    )

    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_department_crud.update_department.assert_called_once()
    mock_log.assert_called_once()
    assert result["message"] == "Members removed successfully"
    assert admin_to_remove in result["removed_admins"]
    assert user_to_remove in result["removed_users"]
    updated_admins_call = mock_department_crud.update_department.call_args[0][1]["department_admins"]
    updated_users_call = mock_department_crud.update_department.call_args[0][1]["department_users"]
    assert admin_to_remove not in updated_admins_call
    assert user_to_remove not in updated_users_call


@pytest.mark.asyncio
async def test_remove_department_members_department_not_found(
    department_service, mock_department_crud, current_user_data, system_admin_role_id, monkeypatch
):
    department_id = str(ObjectId())
    mock_department_crud.find_by_id.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.remove_department_members(department_id, [], [], current_user_data, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Department not found" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once_with(department_id)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_remove_department_members_unauthorized(
    department_service, mock_department_crud, current_user_data, sample_department_in_db, system_admin_role_id, monkeypatch
):
    department_id = str(sample_department_in_db["_id"])
    mock_department_crud.find_by_id.return_value = {
        **sample_department_in_db,
        "department_admins": [str(ObjectId())],  # Other admin
    }
    user_not_admin = {**current_user_data, "_id": str(ObjectId()), "user_roles": []}  # Not an admin

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.department_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc_info:
        await department_service.remove_department_members(department_id, [], [], user_not_admin, system_admin_role_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Only admins can remove members" in exc_info.value.detail
    mock_department_crud.find_by_id.assert_called_once()
    mock_log.assert_called_once()
