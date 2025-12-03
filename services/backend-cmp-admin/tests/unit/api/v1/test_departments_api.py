import pytest
from fastapi.testclient import TestClient
# Fix 1: Import ANY for use in assertions
from unittest.mock import AsyncMock, MagicMock, ANY
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from app.main import app
from app.api.v1.deps import get_current_user, get_department_service
from app.db.dependencies import (
    get_system_admin_role_id,
    get_departments_collection,
    get_roles_collection,
    get_user_collection,
    get_user_invites_collection,
)

# Use raise_server_exceptions=False to test 500 status codes properly
client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/departments"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def department_response(**kwargs):
    """Return a complete schema-valid Department response dict."""
    base_dept = {
        "_id": "d1",
        "department_name": "Test Dept",
        "department_description": "A test department",
        "department_admins": ["u1"],
        "department_users": ["u1", "u2"],
        "routes_accessible": [],
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "is_deleted": False,
        "version": 1
    }
    base_dept.update(kwargs)
    return base_dept


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.add_department = AsyncMock()
    service.get_all_departments = AsyncMock()
    service.get_one_department = AsyncMock()
    service.update_department_users = AsyncMock()
    service.update_department_permissions = AsyncMock()
    service.search_department = AsyncMock()
    service.update_department = AsyncMock()
    service.soft_delete_department = AsyncMock()
    service.remove_department_members = AsyncMock()
    return service


@pytest.fixture
def mock_mongo_collection():
    """Mock a PyMongo collection with a count_documents method for the general override."""
    mock_collection = MagicMock()
    mock_collection.count_documents = AsyncMock(return_value=1)
    return mock_collection


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service, mock_mongo_collection):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_department_service] = lambda: mock_service
    app.dependency_overrides[get_system_admin_role_id] = lambda: "sysadmin_r1"
    
    # Dependencies for the /dashboard endpoint (set to a basic mock by default)
    app.dependency_overrides[get_departments_collection] = lambda: mock_mongo_collection
    app.dependency_overrides[get_roles_collection] = lambda: mock_mongo_collection
    app.dependency_overrides[get_user_collection] = lambda: mock_mongo_collection
    app.dependency_overrides[get_user_invites_collection] = lambda: mock_mongo_collection
    
    yield
    app.dependency_overrides = {}


# ---------------- 1. TEST ADD DEPARTMENT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, department_response(department_name="New Dept"), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_409_CONFLICT, detail="duplicate"), None, status.HTTP_409_CONFLICT),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_add_department(mock_service, side_effect, return_value, expected_status):
    mock_service.add_department.side_effect = side_effect
    mock_service.add_department.return_value = return_value

    body = {"department_name": "New Dept", "department_description": "Description"}
    res = client.post(f"{BASE_URL}/add-department", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["department_name"] == "New Dept"
        mock_service.add_department.assert_called_once()


def test_add_department_validation_error():
    res = client.post(f"{BASE_URL}/add-department", json={"department_name": 123})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 2. TEST UPDATE DEPARTMENT MEMBERS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, department_response(department_users=["u1", "u3"]), status.HTTP_200_OK, {"users_list": ["u1", "u3"], "admins_list": ["u1"]}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"users_list": ["u1"], "admins_list": []}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"users_list": ["u1"], "admins_list": []}),
    ],
)
def test_update_department_users(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_department_users.side_effect = side_effect
    mock_service.update_department_users.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-department-members/d1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "u3" in res.json()["department_users"]
        mock_service.update_department_users.assert_called_once()


# ---------------- 3. TEST UPDATE DEPARTMENT PERMISSIONS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        # Fix 2: Changed "read" to "view" in the actions list to pass Pydantic validation (422 error was likely here)
        (
            None, 
            department_response(routes_accessible=[{"path": "/home", "actions": ["view"]}]), 
            status.HTTP_200_OK, 
            {"routes_accessible": [{"path": "/home", "actions": ["view"]}]}
        ),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"routes_accessible": []}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"routes_accessible": []}),
    ],
)
def test_update_department_permissions(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_department_permissions.side_effect = side_effect
    mock_service.update_department_permissions.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-department-permissions/d1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["routes_accessible"] == body["routes_accessible"]
        mock_service.update_department_permissions.assert_called_once()


# ---------------- 4. TEST SEARCH DEPARTMENT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [department_response(department_name="Finance")], status.HTTP_200_OK),
        (None, [], status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_search_department(mock_service, side_effect, return_value, expected_status):
    mock_service.search_department.side_effect = side_effect
    mock_service.search_department.return_value = return_value

    res = client.get(f"{BASE_URL}/search-department?department_name=Fin")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        mock_service.search_department.assert_called_once()


def test_search_department_missing_query():
    res = client.get(f"{BASE_URL}/search-department")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 5. TEST GET ALL DEPARTMENTS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {"departments": [department_response()], "total_items": 1}, status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_departments(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_departments.side_effect = side_effect
    mock_service.get_all_departments.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-departments?page=1&limit=5")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "departments" in res.json()
        # Fix 1: Use ANY to assert the current_user argument
        mock_service.get_all_departments.assert_called_once_with(1, 5, ANY)


def test_get_all_departments_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-departments?page=invalid")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 6. TEST GET ONE DEPARTMENT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, department_response(), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_one_department(mock_service, side_effect, return_value, expected_status):
    mock_service.get_one_department.side_effect = side_effect
    mock_service.get_one_department.return_value = return_value

    res = client.get(f"{BASE_URL}/get-one-department/d1")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["_id"] == "d1"
        mock_service.get_one_department.assert_called_once()


# ---------------- 7. TEST UPDATE DEPARTMENT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, department_response(department_name="Updated Name"), status.HTTP_200_OK, {"department_name": "Updated Name"}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"department_name": "New Name"}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"department_name": "New Name"}),
    ],
)
def test_update_department(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_department.side_effect = side_effect
    mock_service.update_department.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-department/d1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["department_name"] == body["department_name"]
        mock_service.update_department.assert_called_once()


def test_update_department_invalid_body():
    res = client.patch(f"{BASE_URL}/update-department/d1", json={"department_name": 123})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- 8. TEST SOFT DELETE DEPARTMENT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, department_response(is_deleted=True), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_soft_delete_department(mock_service, side_effect, return_value, expected_status):
    mock_service.soft_delete_department.side_effect = side_effect
    mock_service.soft_delete_department.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-department/d1")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["is_deleted"] is True
        mock_service.soft_delete_department.assert_called_once()


# ---------------- 9. TEST GET DEPARTMENT DASHBOARD ---------------- #


# Fix 3 & 4: Refactored test to set up the sequential mock returns explicitly inside the function
# This ensures the AsyncMock handles the sequence correctly for all five database calls.
@pytest.mark.parametrize(
    "counts, expected_body",
    [
        (
            [10, 5, 3, 2, 1], # user_count, department_count, role_count, accepted, pending
            {"user_count": 10, "department_count": 5, "role_count": 3, "invitations": {"accepted": 2, "pending": 1}},
        ),
        (
            [0, 0, 0, 0, 0],
            {"user_count": 0, "department_count": 0, "role_count": 0, "invitations": {"accepted": 0, "pending": 0}},
        ),
    ],
)
def test_get_department_dashboard_success(counts, expected_body):
    # Create one mock object that will be used for all collection dependencies
    mock_coll = MagicMock()
    # Set the side_effect sequence for the count_documents method
    mock_coll.count_documents = AsyncMock(side_effect=counts)

    # Override dependencies locally
    app.dependency_overrides[get_departments_collection] = lambda: mock_coll
    app.dependency_overrides[get_roles_collection] = lambda: mock_coll
    app.dependency_overrides[get_user_collection] = lambda: mock_coll
    app.dependency_overrides[get_user_invites_collection] = lambda: mock_coll
    
    try:
        res = client.get(f"{BASE_URL}/dashboard")
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == expected_body
    finally:
        # Clean up overrides
        app.dependency_overrides.pop(get_departments_collection, None)
        app.dependency_overrides.pop(get_roles_collection, None)
        app.dependency_overrides.pop(get_user_collection, None)
        app.dependency_overrides.pop(get_user_invites_collection, None)


def test_get_department_dashboard_exception():
    # Simulate a database error on the first call
    mock_coll = MagicMock()
    mock_coll.count_documents = AsyncMock(side_effect=Exception("DB boom"))
    
    app.dependency_overrides[get_departments_collection] = lambda: mock_coll
    app.dependency_overrides[get_roles_collection] = lambda: mock_coll
    app.dependency_overrides[get_user_collection] = lambda: mock_coll
    app.dependency_overrides[get_user_invites_collection] = lambda: mock_coll

    try:
        res = client.get(f"{BASE_URL}/dashboard")
        # Since the router has no try/except block, it will return a 500
        assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    finally:
        app.dependency_overrides.pop(get_departments_collection, None)
        app.dependency_overrides.pop(get_roles_collection, None)
        app.dependency_overrides.pop(get_user_collection, None)
        app.dependency_overrides.pop(get_user_invites_collection, None)


# ---------------- 10. TEST REMOVE DEPARTMENT MEMBERS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, query_params",
    [
        (None, {"message": "Members removed"}, status.HTTP_200_OK, "admin_ids=a1&user_ids=u5"),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, "admin_ids=a1"),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, "user_ids=u5"),
    ],
)
def test_remove_department_members(mock_service, side_effect, return_value, expected_status, query_params):
    mock_service.remove_department_members.side_effect = side_effect
    mock_service.remove_department_members.return_value = return_value

    res = client.delete(f"{BASE_URL}/remove-members?department_id=d1&{query_params}")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["message"] == "Members removed"
        mock_service.remove_department_members.assert_called_once()


def test_remove_department_members_missing_dept_id():
    res = client.delete(f"{BASE_URL}/remove-members?admin_ids=a1")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY