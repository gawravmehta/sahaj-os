import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.dashboard_service import DashboardService


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_departments_crud():
    """Mock DepartmentCRUD"""
    crud = MagicMock()
    crud.count_departments = AsyncMock()
    return crud


@pytest.fixture
def mock_roles_crud():
    """Mock RoleCRUD"""
    crud = MagicMock()
    crud.count_roles = AsyncMock()
    return crud


@pytest.fixture
def mock_users_crud():
    """Mock UserCRUD"""
    crud = MagicMock()
    crud.count_users = AsyncMock()
    return crud


@pytest.fixture
def mock_assets_crud():
    """Mock AssetCrud"""
    crud = MagicMock()
    crud.count_assets = AsyncMock()
    crud.get_assets_categories = AsyncMock()
    crud.get_total_cookie_count = AsyncMock()
    return crud


@pytest.fixture
def mock_data_principal_crud():
    """Mock DataPrincipalCRUD"""
    crud = MagicMock()
    crud.count = AsyncMock()
    return crud


@pytest.fixture
def mock_data_elements_crud():
    """Mock DataElementCRUD"""
    crud = MagicMock()
    crud.count_data_elements = AsyncMock()
    return crud


@pytest.fixture
def mock_purposes_crud():
    """Mock PurposeCRUD"""
    crud = MagicMock()
    crud.count_consent_purposes = AsyncMock()
    return crud


@pytest.fixture
def mock_collection_points_crud():
    """Mock CollectionPointCrud"""
    crud = MagicMock()
    crud.count_collection_points = AsyncMock()
    return crud


@pytest.fixture
def mock_grievance_crud():
    """Mock GrievanceCRUD"""
    crud = MagicMock()
    crud.count_grievances = AsyncMock()
    return crud


@pytest.fixture
def mock_dpar_crud():
    """Mock DparCRUD"""
    crud = MagicMock()
    crud.count_requests = AsyncMock()
    return crud


@pytest.fixture
def mock_vendor_crud():
    """Mock VendorCRUD"""
    crud = MagicMock()
    crud.count_vendors = AsyncMock()
    return crud


@pytest.fixture
def mock_consent_artifact_crud():
    """Mock ConsentArtifactCRUD"""
    crud = MagicMock()
    crud.count_collected_data_elements = AsyncMock()
    crud.count_collected_purposes = AsyncMock()
    crud.count_collected_collection_points = AsyncMock()
    crud.count_filtered_consent_artifacts = AsyncMock()
    return crud


@pytest.fixture
def mock_consent_artifact_service():
    """Mock ConsentArtifactService"""
    service = MagicMock()
    service.get_expiring_consents = AsyncMock()
    return service


@pytest.fixture
def dashboard_service(
    mock_departments_crud,
    mock_roles_crud,
    mock_users_crud,
    mock_assets_crud,
    mock_data_principal_crud,
    mock_data_elements_crud,
    mock_purposes_crud,
    mock_collection_points_crud,
    mock_grievance_crud,
    mock_dpar_crud,
    mock_vendor_crud,
    mock_consent_artifact_crud,
    mock_consent_artifact_service,
):
    """Create DashboardService instance with all mocked dependencies"""
    return DashboardService(
        departments_crud=mock_departments_crud,
        roles_crud=mock_roles_crud,
        users_crud=mock_users_crud,
        assets_crud=mock_assets_crud,
        data_principal_crud=mock_data_principal_crud,
        data_elements_crud=mock_data_elements_crud,
        purposes_crud=mock_purposes_crud,
        collection_points_crud=mock_collection_points_crud,
        grievance_crud=mock_grievance_crud,
        dpar_crud=mock_dpar_crud,
        vendor_crud=mock_vendor_crud,
        consent_artifact_crud=mock_consent_artifact_crud,
        consent_artifact_service=mock_consent_artifact_service,
    )


@pytest.fixture
def mock_user():
    """Mock user object"""
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


# ---------------- TEST get_dashboard_detail ---------------- #


@pytest.mark.asyncio
async def test_get_dashboard_detail_success(
    dashboard_service,
    mock_user,
    mock_departments_crud,
    mock_roles_crud,
    mock_users_crud,
    mock_assets_crud,
    mock_data_principal_crud,
    mock_data_elements_crud,
    mock_purposes_crud,
    mock_collection_points_crud,
    mock_grievance_crud,
    mock_dpar_crud,
    mock_vendor_crud,
    mock_consent_artifact_crud,
    mock_consent_artifact_service,
):
    """Test successful dashboard detail retrieval with all stats"""
    # Mock all CRUD return values
    mock_departments_crud.count_departments.return_value = 5
    mock_roles_crud.count_roles.return_value = 10
    mock_users_crud.count_users.return_value = 25

    mock_assets_crud.count_assets.return_value = 15
    mock_assets_crud.get_assets_categories.return_value = ["website", "mobile_app", "api"]
    mock_assets_crud.get_total_cookie_count.return_value = 50

    mock_data_principal_crud.count.side_effect = [100, 200]  # legacy, new

    mock_data_elements_crud.count_data_elements.return_value = 30
    mock_consent_artifact_crud.count_collected_data_elements.return_value = 20

    mock_purposes_crud.count_consent_purposes.return_value = 12
    mock_consent_artifact_crud.count_collected_purposes.return_value = 8

    mock_collection_points_crud.count_collection_points.return_value = 7
    mock_consent_artifact_crud.count_collected_collection_points.return_value = 5

    mock_grievance_crud.count_grievances.return_value = 3

    mock_dpar_crud.count_requests.side_effect = [15, 35]  # active, closed

    mock_vendor_crud.count_vendors.return_value = 8

    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 500

    mock_consent_artifact_service.get_expiring_consents.side_effect = [
        [{"id": "1"}, {"id": "2"}],  # 7 days - 2 items
        [{"id": "1"}, {"id": "2"}, {"id": "3"}],  # 15 days - 3 items
        [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}],  # 30 days - 4 items
    ]

    # Call the method
    result = await dashboard_service.get_dashboard_detail(mock_user)

    # Verify structure and values
    assert result["total_departments"] == 5
    assert result["total_roles"] == 10
    assert result["total_users"] == 25

    assert result["total_assets"] == 15
    assert result["list_of_assets_categories"] == ["website", "mobile_app", "api"]
    assert result["total_cookies"] == 50

    assert result["total_legacy_data_principals"] == 100
    assert result["total_new_data_principals"] == 200

    assert result["total_data_elements"] == 30
    assert result["total_collected_data_elements"] == 20

    assert result["total_purposes"] == 12
    assert result["total_collected_purposes"] == 8

    assert result["total_collection_points"] == 7
    assert result["total_collected_collection_points"] == 5

    assert result["active_grievances"] == 3
    assert result["closed_grievances"] == 0

    assert result["active_dpar_requests"] == 15
    assert result["closed_dpar_requests"] == 35

    assert result["total_data_processors"] == 8

    assert result["total_consent_artifacts"] == 500

    assert result["total_expiring_consent_in_seven_days"] == 2
    assert result["total_expiring_consent_in_fifteen_days"] == 3
    assert result["total_expiring_consent_in_thirty_days"] == 4

    # Verify all CRUD methods were called with correct parameters
    mock_departments_crud.count_departments.assert_called_once_with("df123")
    mock_roles_crud.count_roles.assert_called_once_with("df123")
    mock_users_crud.count_users.assert_called_once_with("df123")

    mock_assets_crud.count_assets.assert_called_once_with("df123")
    mock_assets_crud.get_assets_categories.assert_called_once_with("df123")
    mock_assets_crud.get_total_cookie_count.assert_called_once_with("df123")

    # Check data principal counts were called twice (legacy and new)
    assert mock_data_principal_crud.count.call_count == 2
    mock_data_principal_crud.count.assert_any_call(table_name="dpd", where_clause="is_legacy = $1", values=[True])
    mock_data_principal_crud.count.assert_any_call(table_name="dpd", where_clause="is_legacy = $1", values=[False])

    mock_data_elements_crud.count_data_elements.assert_called_once_with("df123")
    mock_purposes_crud.count_consent_purposes.assert_called_once_with("df123")
    mock_collection_points_crud.count_collection_points.assert_called_once_with("df123")

    mock_grievance_crud.count_grievances.assert_called_once()

    # Check DPAR counts
    assert mock_dpar_crud.count_requests.call_count == 2

    mock_vendor_crud.count_vendors.assert_called_once_with({"df_id": "df123", "status": {"$ne": "archived"}})

    # Check expiring consents
    assert mock_consent_artifact_service.get_expiring_consents.call_count == 3
    mock_consent_artifact_service.get_expiring_consents.assert_any_call(df_id="df123", days_to_expire="7")
    mock_consent_artifact_service.get_expiring_consents.assert_any_call(df_id="df123", days_to_expire="15")
    mock_consent_artifact_service.get_expiring_consents.assert_any_call(df_id="df123", days_to_expire="30")


@pytest.mark.asyncio
async def test_get_dashboard_detail_with_zeros(
    dashboard_service,
    mock_user,
    mock_departments_crud,
    mock_roles_crud,
    mock_users_crud,
    mock_assets_crud,
    mock_data_principal_crud,
    mock_data_elements_crud,
    mock_purposes_crud,
    mock_collection_points_crud,
    mock_grievance_crud,
    mock_dpar_crud,
    mock_vendor_crud,
    mock_consent_artifact_crud,
    mock_consent_artifact_service,
):
    """Test dashboard detail with all zero counts"""
    # Mock all CRUD return values to 0 or empty
    mock_departments_crud.count_departments.return_value = 0
    mock_roles_crud.count_roles.return_value = 0
    mock_users_crud.count_users.return_value = 0

    mock_assets_crud.count_assets.return_value = 0
    mock_assets_crud.get_assets_categories.return_value = []
    mock_assets_crud.get_total_cookie_count.return_value = 0

    mock_data_principal_crud.count.return_value = 0

    mock_data_elements_crud.count_data_elements.return_value = 0
    mock_consent_artifact_crud.count_collected_data_elements.return_value = 0

    mock_purposes_crud.count_consent_purposes.return_value = 0
    mock_consent_artifact_crud.count_collected_purposes.return_value = 0

    mock_collection_points_crud.count_collection_points.return_value = 0
    mock_consent_artifact_crud.count_collected_collection_points.return_value = 0

    mock_grievance_crud.count_grievances.return_value = 0
    mock_dpar_crud.count_requests.return_value = 0
    mock_vendor_crud.count_vendors.return_value = 0

    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 0
    mock_consent_artifact_service.get_expiring_consents.return_value = []

    result = await dashboard_service.get_dashboard_detail(mock_user)

    # Verify all counts are 0
    assert result["total_departments"] == 0
    assert result["total_roles"] == 0
    assert result["total_users"] == 0
    assert result["total_assets"] == 0
    assert result["list_of_assets_categories"] == []
    assert result["total_cookies"] == 0
    assert result["total_legacy_data_principals"] == 0
    assert result["total_new_data_principals"] == 0
    assert result["total_data_elements"] == 0
    assert result["total_collected_data_elements"] == 0
    assert result["total_purposes"] == 0
    assert result["total_collected_purposes"] == 0
    assert result["total_collection_points"] == 0
    assert result["total_collected_collection_points"] == 0
    assert result["active_grievances"] == 0
    assert result["closed_grievances"] == 0
    assert result["active_dpar_requests"] == 0
    assert result["closed_dpar_requests"] == 0
    assert result["total_data_processors"] == 0
    assert result["total_consent_artifacts"] == 0
    assert result["total_expiring_consent_in_seven_days"] == 0
    assert result["total_expiring_consent_in_fifteen_days"] == 0
    assert result["total_expiring_consent_in_thirty_days"] == 0


@pytest.mark.asyncio
async def test_get_dashboard_detail_crud_exception(dashboard_service, mock_user, mock_departments_crud):
    """Test dashboard detail when a CRUD method raises exception"""
    # Mock first CRUD to raise exception
    mock_departments_crud.count_departments.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        await dashboard_service.get_dashboard_detail(mock_user)

    assert "Database error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_dashboard_detail_response_structure(
    dashboard_service,
    mock_user,
    mock_departments_crud,
    mock_roles_crud,
    mock_users_crud,
    mock_assets_crud,
    mock_data_principal_crud,
    mock_data_elements_crud,
    mock_purposes_crud,
    mock_collection_points_crud,
    mock_grievance_crud,
    mock_dpar_crud,
    mock_vendor_crud,
    mock_consent_artifact_crud,
    mock_consent_artifact_service,
):
    """Test that response contains all expected keys"""
    # Mock minimal returns
    mock_departments_crud.count_departments.return_value = 1
    mock_roles_crud.count_roles.return_value = 1
    mock_users_crud.count_users.return_value = 1
    mock_assets_crud.count_assets.return_value = 1
    mock_assets_crud.get_assets_categories.return_value = []
    mock_assets_crud.get_total_cookie_count.return_value = 1
    mock_data_principal_crud.count.return_value = 1
    mock_data_elements_crud.count_data_elements.return_value = 1
    mock_consent_artifact_crud.count_collected_data_elements.return_value = 1
    mock_purposes_crud.count_consent_purposes.return_value = 1
    mock_consent_artifact_crud.count_collected_purposes.return_value = 1
    mock_collection_points_crud.count_collection_points.return_value = 1
    mock_consent_artifact_crud.count_collected_collection_points.return_value = 1
    mock_grievance_crud.count_grievances.return_value = 1
    mock_dpar_crud.count_requests.return_value = 1
    mock_vendor_crud.count_vendors.return_value = 1
    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 1
    mock_consent_artifact_service.get_expiring_consents.return_value = []

    result = await dashboard_service.get_dashboard_detail(mock_user)

    # Verify all expected keys are present
    expected_keys = [
        "total_departments",
        "total_roles",
        "total_users",
        "total_assets",
        "list_of_assets_categories",
        "total_cookies",
        "total_legacy_data_principals",
        "total_new_data_principals",
        "total_data_elements",
        "total_collected_data_elements",
        "total_purposes",
        "total_collected_purposes",
        "total_collection_points",
        "total_collected_collection_points",
        "active_grievances",
        "closed_grievances",
        "active_dpar_requests",
        "closed_dpar_requests",
        "total_data_processors",
        "total_consent_artifacts",
        "total_expiring_consent_in_seven_days",
        "total_expiring_consent_in_fifteen_days",
        "total_expiring_consent_in_thirty_days",
    ]

    for key in expected_keys:
        assert key in result, f"Missing key: {key}"

    # Verify no extra keys
    assert len(result.keys()) == len(expected_keys)


@pytest.mark.asyncio
async def test_get_dashboard_detail_data_types(
    dashboard_service,
    mock_user,
    mock_departments_crud,
    mock_roles_crud,
    mock_users_crud,
    mock_assets_crud,
    mock_data_principal_crud,
    mock_data_elements_crud,
    mock_purposes_crud,
    mock_collection_points_crud,
    mock_grievance_crud,
    mock_dpar_crud,
    mock_vendor_crud,
    mock_consent_artifact_crud,
    mock_consent_artifact_service,
):
    """Test that response values have correct data types"""
    mock_departments_crud.count_departments.return_value = 5
    mock_roles_crud.count_roles.return_value = 10
    mock_users_crud.count_users.return_value = 25
    mock_assets_crud.count_assets.return_value = 15
    mock_assets_crud.get_assets_categories.return_value = ["website", "mobile_app"]
    mock_assets_crud.get_total_cookie_count.return_value = 50
    mock_data_principal_crud.count.return_value = 100
    mock_data_elements_crud.count_data_elements.return_value = 30
    mock_consent_artifact_crud.count_collected_data_elements.return_value = 20
    mock_purposes_crud.count_consent_purposes.return_value = 12
    mock_consent_artifact_crud.count_collected_purposes.return_value = 8
    mock_collection_points_crud.count_collection_points.return_value = 7
    mock_consent_artifact_crud.count_collected_collection_points.return_value = 5
    mock_grievance_crud.count_grievances.return_value = 3
    mock_dpar_crud.count_requests.return_value = 15
    mock_vendor_crud.count_vendors.return_value = 8
    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 500
    mock_consent_artifact_service.get_expiring_consents.return_value = [{"id": "1"}]

    result = await dashboard_service.get_dashboard_detail(mock_user)

    # Verify data types
    assert isinstance(result["total_departments"], int)
    assert isinstance(result["total_roles"], int)
    assert isinstance(result["total_users"], int)
    assert isinstance(result["total_assets"], int)
    assert isinstance(result["list_of_assets_categories"], list)
    assert isinstance(result["total_cookies"], int)
    assert isinstance(result["total_legacy_data_principals"], int)
    assert isinstance(result["total_new_data_principals"], int)
    assert isinstance(result["total_data_elements"], int)
    assert isinstance(result["total_collected_data_elements"], int)
    assert isinstance(result["total_purposes"], int)
    assert isinstance(result["total_collected_purposes"], int)
    assert isinstance(result["total_collection_points"], int)
    assert isinstance(result["total_collected_collection_points"], int)
    assert isinstance(result["active_grievances"], int)
    assert isinstance(result["closed_grievances"], int)
    assert isinstance(result["active_dpar_requests"], int)
    assert isinstance(result["closed_dpar_requests"], int)
    assert isinstance(result["total_data_processors"], int)
    assert isinstance(result["total_consent_artifacts"], int)
    assert isinstance(result["total_expiring_consent_in_seven_days"], int)
    assert isinstance(result["total_expiring_consent_in_fifteen_days"], int)
    assert isinstance(result["total_expiring_consent_in_thirty_days"], int)
