import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from app.services.consent_validation_service import ConsentValidationService
from app.schemas.consent_validation_schema import VerificationRequest


pytestmark = pytest.mark.asyncio


def make_cursor(return_value):
    """
    Helper: returns an AsyncMock that behaves like a Motor cursor with an async to_list().
    """
    cursor = AsyncMock()
    cursor.to_list = AsyncMock(return_value=return_value)
    return cursor


@pytest.fixture
def mock_cruds():
    return {
        "consent_validation": AsyncMock(),
        "consent_artifact": AsyncMock(),
        "vendor_crud": AsyncMock(),
    }


@pytest.fixture
def mock_notifications_collection():
    return AsyncMock()


@pytest.fixture
def service(mock_cruds, mock_notifications_collection):
    return ConsentValidationService(
        consent_validation_crud=mock_cruds["consent_validation"],
        consent_artifact_crud=mock_cruds["consent_artifact"],
        vendor_crud=mock_cruds["vendor_crud"],
        business_logs_collection="business_logs",
        customer_notifications_collection=mock_notifications_collection,
    )


@pytest.fixture
def sample_user():
    return {"_id": "user123", "df_id": "df123", "email": "user@test.com"}


@pytest.fixture
def sample_verification_request():
    return VerificationRequest(
        dp_id="dp123",
        dp_system_id=None,
        dp_e="email@test.com",
        dp_m=None,
        data_elements_hash=["hash1", "hash2"],
        purpose_hash="purpose123",
    )


# ---------------------------------------------------------------------
#   TESTS — verify_consent_internal
# ---------------------------------------------------------------------


async def test_verify_consent_no_df(service, sample_verification_request):
    with pytest.raises(HTTPException) as excinfo:
        await service.verify_consent_internal(sample_verification_request, current_user={"email": "a@b.com"})
    assert excinfo.value.status_code == 404


async def test_verify_consent_missing_dp_identifiers(service, sample_user):
    req = VerificationRequest(
        dp_id=None,
        dp_system_id=None,
        dp_e=None,
        dp_m=None,
        data_elements_hash=["h1"],
        purpose_hash="p1",
    )

    with pytest.raises(HTTPException) as excinfo:
        await service.verify_consent_internal(req, current_user=sample_user)
    assert excinfo.value.status_code == 400


async def test_verify_consent_missing_purpose_hash(service, sample_user):
    req = VerificationRequest(
        dp_id="dp1",
        dp_system_id=None,
        dp_e=None,
        dp_m=None,
        data_elements_hash=["h1"],
        purpose_hash=None,
    )
    with pytest.raises(HTTPException) as excinfo:
        await service.verify_consent_internal(req, current_user=sample_user)
    assert excinfo.value.status_code == 400


async def test_verify_consent_missing_data_element_hash(service, sample_user):
    req = VerificationRequest(
        dp_id="dp1",
        dp_system_id=None,
        dp_e=None,
        dp_m=None,
        data_elements_hash=[],
        purpose_hash="p1",
    )
    with pytest.raises(HTTPException) as excinfo:
        await service.verify_consent_internal(req, current_user=sample_user)
    assert excinfo.value.status_code == 400


# ---------------------------------------------------------------------
# Tests for get_all_verification_logs
# ---------------------------------------------------------------------
async def test_get_all_logs_missing_df(service):
    with pytest.raises(HTTPException) as excinfo:
        await service.get_all_verification_logs(
            page=1,
            limit=10,
            sort_order="asc",
            search=None,
            internal_external=None,
            status=None,
            from_date=None,
            to_date=None,
            purpose_hashes=None,
            data_element_hashes=None,
            current_user={"email": "test@test.com"},
        )
    assert excinfo.value.status_code == 404


# ---------------------------------------------------------------------
# Tests — download_verification_logs
# ---------------------------------------------------------------------


async def test_download_logs_invalid_df(service):
    with pytest.raises(HTTPException):
        await service.download_verification_logs(
            sort_order="asc",
            search=None,
            internal_external=None,
            status=None,
            from_date=None,
            to_date=None,
            purpose_hashes=None,
            data_element_hashes=None,
            current_user={"email": "a@b.com"},
        )


async def test_download_logs_invalid_from_date(service, sample_user):
    with pytest.raises(HTTPException) as excinfo:
        await service.download_verification_logs("asc", None, None, None, "INVALID_DATE", None, None, None, sample_user)
    assert excinfo.value.status_code == 400


# ---------------------------------------------------------------------
# Test get_one_verification_log
# ---------------------------------------------------------------------


async def test_get_one_verification_log_not_found(service, sample_user, mock_cruds):
    mock_cruds["consent_validation"].find_one_log.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await service.get_one_verification_log("req1", sample_user)
    assert excinfo.value.status_code == 404


async def test_get_one_verification_log_success(service, sample_user, mock_cruds):
    mock_cruds["consent_validation"].find_one_log.return_value = {"_id": ObjectId(), "request_id": "req1"}

    result = await service.get_one_verification_log("req1", sample_user)
    assert result["request_id"] == "req1"


# ---------------------------------------------------------------------
# Test get_verification_dashboard_stats
# ---------------------------------------------------------------------


async def test_verification_dashboard_stats_missing_df(service):
    # The service uses current_user["df_id"] which raises KeyError if missing.
    with pytest.raises(KeyError):
        await service.get_verification_dashboard_stats({"email": "a@b.com"})


async def test_verification_dashboard_stats_success(service, sample_user, mock_cruds):
    # vendor_crud.count_vendors returns a value when awaited
    mock_cruds["vendor_crud"].count_vendors.return_value = 5

    # count_total_logs is called multiple times in the implementation;
    # provide enough values to the side_effect so StopAsyncIteration won't occur.
    mock_cruds["consent_validation"].count_total_logs.side_effect = [10, 6, 4, 6, 4, 2]

    result = await service.get_verification_dashboard_stats(sample_user)

    assert result["total_requests"] == 10
    assert result["valid_results"] == 6
    assert result["invalid_results"] == 4
    assert result["data_processors"] == 5
