import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from app.main import app
from app.api.v1.deps import get_current_user, get_role_service
from app.db.dependencies import get_system_admin_role_id

# FIX 1: set raise_server_exceptions=False to test 500 errors gracefully
client = TestClient(app, raise_server_exceptions=False)
BASE_URL = "/api/v1/roles"


# ---------------- FIXTURES ---------------- #

@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def role_response(**kwargs):
    """Return a complete schema-valid RoleResponse dict."""
    base_role = {
        "_id": "r1",
        "role_name": "Test Role",
        "role_description": "A test role",
        "routes_accessible": [],
        "role_users": [],
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "is_deleted": False,
        "version": 1
    }
    base_role.update(kwargs)
    return base_role


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.add_role = AsyncMock()
    service.get_all_roles = AsyncMock()
    service.get_one_role = AsyncMock()
    service.get_all_role_users = AsyncMock()
    service.update_role_users = AsyncMock()
    service.update_role_permissions = AsyncMock()
    service.search_role = AsyncMock()
    service.update_role = AsyncMock()
    service.soft_delete_role = AsyncMock()
    service.assign_roles_to_user = AsyncMock()
    service.get_all_frontend_routes = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_role_service] = lambda: mock_service
    app.dependency_overrides[get_system_admin_role_id] = lambda: "sysadmin_r1"
    yield
    app.dependency_overrides = {}


# ---------------- TEST ADD ROLE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, role_response(role_name="New Role"), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_409_CONFLICT, detail="duplicate"), None, status.HTTP_409_CONFLICT),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_add_role(mock_service, side_effect, return_value, expected_status):
    mock_service.add_role.side_effect = side_effect
    mock_service.add_role.return_value = return_value

    body = {"role_name": "New Role", "role_description": "Description of new role"}
    res = client.post(f"{BASE_URL}/add-role", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["role_name"] == "New Role"
        mock_service.add_role.assert_called_once()


def test_add_role_validation_error():
    res = client.post(f"{BASE_URL}/add-role", json={"wrong_field": "value"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST GET ALL ROLES ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (
            None,
            {
                "current_page": 1,
                "data_per_page": 10,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
                "roles": [role_response()],
            },
            status.HTTP_200_OK,
        ),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_roles(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_roles.side_effect = side_effect
    mock_service.get_all_roles.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-roles")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["roles"][0]["_id"] == "r1"
        mock_service.get_all_roles.assert_called_once()


def test_get_all_roles_invalid_query():
    # FIX 2: Send a non-integer string to force Pydantic validation error (422)
    # If we send "0" (int), validation passes, service is called, returning a Mock, causing RecursionError
    res = client.get(f"{BASE_URL}/get-all-roles?page=invalid")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST GET ONE ROLE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, role_response(), status.HTTP_200_OK),
        # FIX 3: To test 404, the service must RAISE the exception. 
        # Returning None results in 200 OK with null body unless controller handles it manually.
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_one_role(mock_service, side_effect, return_value, expected_status):
    mock_service.get_one_role.side_effect = side_effect
    mock_service.get_one_role.return_value = return_value

    res = client.get(f"{BASE_URL}/get-one-role/r1")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["_id"] == "r1"
        mock_service.get_one_role.assert_called_once()


# ---------------- TEST GET ALL ROLE USERS ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"user_id": "u1", "email": "test@example.com"}], status.HTTP_200_OK),
        (None, [], status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"), None, status.HTTP_404_NOT_FOUND),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_role_users(mock_service, mock_user, side_effect, return_value, expected_status):
    # Note: added mock_user to args above so we can use it
    mock_service.get_all_role_users.side_effect = side_effect
    mock_service.get_all_role_users.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-role-users?role_id=r1")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        # FIX 4: mock_user is a dict fixture, do not call it like a function mock_user()
        mock_service.get_all_role_users.assert_called_once_with("r1", mock_user)


# ---------------- TEST UPDATE ROLE USERS ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, role_response(role_users=["u1", "u2"]), status.HTTP_200_OK, {"users_list": ["u1", "u2"]}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"users_list": ["u1"]}),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST, {"users_list": ["u1"]}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"users_list": ["u1"]}),
    ],
)
def test_update_role_users(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_role_users.side_effect = side_effect
    mock_service.update_role_users.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-role-users/r1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["role_users"] == body["users_list"]
        mock_service.update_role_users.assert_called_once()


def test_update_role_users_invalid_body():
    res = client.patch(f"{BASE_URL}/update-role-users/r1", json={"users_list": "not a list"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST UPDATE ROLE PERMISSIONS ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, role_response(routes_accessible=[{"path": "/admin", "actions": ["read"]}]), status.HTTP_200_OK, {"routes_accessible": [{"path": "/admin", "actions": ["read"]}]}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"routes_accessible": []}),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST, {"routes_accessible": []}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"routes_accessible": []}),
    ],
)
def test_update_role_permissions(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_role_permissions.side_effect = side_effect
    mock_service.update_role_permissions.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-role-permissions/r1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["routes_accessible"] == body["routes_accessible"]
        mock_service.update_role_permissions.assert_called_once()


def test_update_role_permissions_invalid_body():
    res = client.patch(f"{BASE_URL}/update-role-permissions/r1", json={
        "routes_accessible": [{
            "path": "/admin",
            "actions": ["invalid_action"]
        }]
    })
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST SEARCH ROLE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [role_response(role_name="Search Role")], status.HTTP_200_OK),
        (None, [], status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_search_role(mock_service, side_effect, return_value, expected_status):
    mock_service.search_role.side_effect = side_effect
    mock_service.search_role.return_value = return_value

    res = client.get(f"{BASE_URL}/search-role?role_name=Search")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        if res.json():
            assert res.json()[0]["role_name"] == "Search Role"
        mock_service.search_role.assert_called_once()


def test_search_role_missing_query():
    res = client.get(f"{BASE_URL}/search-role")
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST UPDATE ROLE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, role_response(role_name="Updated Role Name"), status.HTTP_200_OK, {"role_name": "Updated Role Name"}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND, {"role_name": "Updated Role Name"}),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST, {"role_name": "Updated Role Name"}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"role_name": "Updated Role Name"}),
    ],
)
def test_update_role(mock_service, side_effect, return_value, expected_status, body):
    mock_service.update_role.side_effect = side_effect
    mock_service.update_role.return_value = return_value

    res = client.patch(f"{BASE_URL}/update-role/r1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["_id"] == "r1"
        mock_service.update_role.assert_called_once()


def test_update_role_invalid_body():
    # Sending a field that is NOT in UpdateRole schema. 
    # Note: By default Pydantic V2 ignores extra fields. 
    # To force 422, you need to send invalid TYPES for known fields (like role_name: 123) 
    # OR configure your Pydantic model with extra='forbid'.
    # Assuming extra='ignore' (default), this might actually pass with 200.
    # Changing test to send invalid type for a known field to guarantee 422:
    res = client.patch(f"{BASE_URL}/update-role/r1", json={"role_name": ["invalid_type"]}) 
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST DELETE ROLE ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, role_response(is_deleted=True), status.HTTP_200_OK),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND), None, status.HTTP_404_NOT_FOUND),
        (HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad"), None, status.HTTP_400_BAD_REQUEST),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_delete_role(mock_service, side_effect, return_value, expected_status):
    mock_service.soft_delete_role.side_effect = side_effect
    mock_service.soft_delete_role.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-role/r1")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json()["is_deleted"] is True
        mock_service.soft_delete_role.assert_called_once()


# ---------------- TEST ASSIGN ROLES TO USER ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, {"message": "Roles assigned successfully"}, status.HTTP_200_OK, {"roles_list": ["r1", "r2"]}),
        (HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found"), None, status.HTTP_404_NOT_FOUND, {"roles_list": ["r1"]}),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR, {"roles_list": ["r1"]}),
    ],
)
def test_assign_roles_to_user(mock_service, side_effect, return_value, expected_status, body):
    mock_service.assign_roles_to_user.side_effect = side_effect
    mock_service.assign_roles_to_user.return_value = return_value

    res = client.patch(f"{BASE_URL}/assign-roles-to-user/u1", json=body)

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert res.json() == {"message": "Roles assigned successfully"}
        mock_service.assign_roles_to_user.assert_called_once()


def test_assign_roles_to_user_invalid_body():
    res = client.patch(f"{BASE_URL}/assign-roles-to-user/u1", json={
        "roles_list": "not a list"
    })
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------- TEST GET ALL FRONTEND ROUTES ---------------- #

@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, [{"path": "/dashboard", "actions": ["read"]}], status.HTTP_200_OK),
        (None, [], status.HTTP_200_OK),
        (Exception("boom"), None, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_get_all_frontend_routes(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_frontend_routes.side_effect = side_effect
    mock_service.get_all_frontend_routes.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-frontend-routes")

    assert res.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert isinstance(res.json(), list)
        mock_service.get_all_frontend_routes.assert_called_once()