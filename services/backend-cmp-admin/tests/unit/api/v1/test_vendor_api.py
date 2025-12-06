from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.deps import get_current_user, get_vendor_service
from app.main import app
from app.schemas.vendor_schema import (
    AuditStatus,
    ContactPerson,
    ContractDocument,
    CreateMyVendor,
    DataProcessingActivity,
    DPDPAComplianceStatus,
    SecurityMeasure,
)

client = TestClient(app)
BASE_URL = "/api/v1/vendor"

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def vendor_response():
    """Return a complete schema-valid vendor response dict."""
    return {
        "_id": "v1",
        "dpr_name": "Test Vendor",
        "dpr_legal_name": "Test Vendor Inc.",
        "description": "A test vendor for data processing.",
        "dpr_address": "123 Test St",
        "dpr_country": "USA",
        "dpr_country_risk": "Low",
        "dpr_privacy_policy": "http://example.com/privacy",
        "dpr_data_policy": "http://example.com/data",
        "dpr_security_policy": "http://example.com/security",
        "industry": "Software",
        "processing_category": ["Marketing"],
        "data_categories": ["Personal Data"],
        "data_processing_activity": [
            {
                "activity_name": "Email Marketing",
                "purpose_id": "p1",
                "purpose": "Marketing",
                "lawful_basis": "Consent",
                "data_elements": ["email"],
                "frequency": "Monthly",
                "storage_location": "Cloud",
            }
        ],
        "data_retention_policy": "1 year",
        "data_location": ["USA"],
        "cross_border": False,
        "sub_processor": False,
        "sub_processors": [],
        "legal_basis_of_processing": "Consent",
        "dpdpa_compliance_status": {
            "signed_dpa": True,
            "transfer_outside_india": False,
            "cross_border_mechanism": "None",
            "breach_notification_time": "72 hours",
        },
        "security_measures": [],
        "audit_status": {
            "last_audit_date": "2024-01-01T00:00:00Z",
            "next_audit_due": "2025-01-01T00:00:00Z",
            "audit_result": "Pass",
        },
        "contact_person": {
            "name": "John Doe",
            "designation": "Manager",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
        },
        "contract_documents": [],
        "df_id": "df123",
        "created_by": "u1",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None,
        "updated_by": None,
        "dpr_status": "draft",
    }


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_or_update_vendor = AsyncMock()
    service.edit_data_processing_activities = AsyncMock()
    service.get_all_my_vendors = AsyncMock()
    service.get_one_vendor = AsyncMock()
    service.delete_vendor = AsyncMock()
    service.make_it_publish = AsyncMock()
    return service


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_vendor_service] = lambda: mock_service
    yield
    app.dependency_overrides = {}


# ---------------- TEST CREATE OR UPDATE VENDOR ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, vendor_id_query",
    [
        (None, vendor_response(), 200, None),  # Create
        (
            None,
            {**vendor_response(), "dpr_name": "Updated Vendor"},
            200,
            "v1",
        ),
        (Exception("boom"), None, 500, None),
    ],
)
def test_create_or_update_vendor(mock_service, side_effect, return_value, expected_status, vendor_id_query):
    mock_service.create_or_update_vendor.side_effect = side_effect
    mock_service.create_or_update_vendor.return_value = return_value

    body = {
        "dpr_name": "New Vendor",
        "dpr_legal_name": "New Vendor Inc.",
        "industry": "IT",
    }

    url = f"{BASE_URL}/create-or-update-vendor"
    if vendor_id_query:
        url += f"?vendor_id={vendor_id_query}"

    res = client.post(url, json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["_id"] == "v1"
        if vendor_id_query:
            assert res.json()["dpr_name"] == return_value["dpr_name"]
        mock_service.create_or_update_vendor.assert_called_once()


# ---------------- TEST EDIT DATA PROCESSING ACTIVITIES ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, vendor_response(), 200),
        (HTTPException(status_code=404, detail="Vendor not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_edit_data_processing_activities(mock_service, side_effect, return_value, expected_status):
    mock_service.edit_data_processing_activities.side_effect = side_effect
    mock_service.edit_data_processing_activities.return_value = return_value

    body = [
        {
            "activity_name": "New Activity",
            "purpose_id": "p2",
            "purpose": "Analytics",
            "lawful_basis": "Legitimate Interest",
            "data_elements": ["cookies"],
            "frequency": "Daily",
            "storage_location": "EU",
        }
    ]
    res = client.patch(f"{BASE_URL}/edit-data-processing-activities/v1", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["_id"] == "v1"
        mock_service.edit_data_processing_activities.assert_called_once()


def test_edit_data_processing_activities_validation_error():
    res = client.patch(f"{BASE_URL}/edit-data-processing-activities/v1", json=[{"activity_name": 123}])
    assert res.status_code == 422


# ---------------- TEST GET ALL VENDORS ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (
            None,
            {
                "current_page": 1,
                "data_per_page": 20,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
                "vendors": [vendor_response()],
            },
            200,
        ),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_vendors(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_my_vendors.side_effect = side_effect
    mock_service.get_all_my_vendors.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-vendors")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["vendors"][0]["_id"] == "v1"
        mock_service.get_all_my_vendors.assert_called_once()


def test_get_all_vendors_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-vendors?page=0")
    assert res.status_code == 422


# ---------------- TEST GET ONE VENDOR ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, vendor_response(), 200),
        (None, None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_get_one_vendor(mock_service, side_effect, return_value, expected_status):
    mock_service.get_one_vendor.side_effect = side_effect
    mock_service.get_one_vendor.return_value = return_value

    res = client.get(f"{BASE_URL}/get-one-vendor?vendor_id=v1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["_id"] == "v1"
        mock_service.get_one_vendor.assert_called_once()


def test_get_one_vendor_missing_id():
    res = client.get(f"{BASE_URL}/get-one-vendor")
    assert res.status_code == 422


# ---------------- TEST DELETE VENDOR ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**vendor_response(), "dpr_status": "archived"}, 200),
        (None, None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_vendor(mock_service, side_effect, return_value, expected_status):
    mock_service.delete_vendor.side_effect = side_effect
    mock_service.delete_vendor.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-my-vendor/v1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["dpr_status"] == "archived"
        mock_service.delete_vendor.assert_called_once()


# ---------------- TEST MAKE IT PUBLISH ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**vendor_response(), "dpr_status": "published"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_make_it_publish(mock_service, side_effect, return_value, expected_status):
    mock_service.make_it_publish.side_effect = side_effect
    mock_service.make_it_publish.return_value = return_value

    res = client.post(f"{BASE_URL}/make-it-publish/v1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["dpr_status"] == "published"
        mock_service.make_it_publish.assert_called_once()
