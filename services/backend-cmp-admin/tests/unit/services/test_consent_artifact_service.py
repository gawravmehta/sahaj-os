import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from io import StringIO
from datetime import datetime, timedelta
from bson import ObjectId

from app.services.consent_artifact_service import ConsentArtifactService
from app.crud.consent_artifact_crud import ConsentArtifactCRUD
from app.schemas.consent_artifact_schema import PurposeConsentExpiry, ExpiringConsentsByDpIdResponse
from app.utils.common import hash_shake256


@pytest.fixture
def mock_consent_artifact_crud():
    return MagicMock(spec=ConsentArtifactCRUD)


@pytest.fixture
def consent_artifact_service(mock_consent_artifact_crud):
    return ConsentArtifactService(crud=mock_consent_artifact_crud, business_logs_collection="test_logs")


@pytest.fixture
def current_user_data():
    return {"_id": "user1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def sample_consent_artifact():
    return {
        "_id": ObjectId(),
        "df_id": "df123",
        "dp_id": "dp1",  # Added top-level dp_id for query
        "artifact": {
            "agreement_id": "agr1",
            "cp_name": "CP1",
            "data_principal": {
                "dp_id": "dp1",
                "dp_e": hash_shake256("dp1@example.com"),
                "dp_m": hash_shake256("1234567890"),
            },
            "data_fiduciary": {"agreement_date": datetime(2023, 1, 1).isoformat()},
            "consent_scope": {
                "data_elements": [
                    {
                        "title": "DE1",
                        "consents": [
                            {
                                "purpose_id": "p1",
                                "purpose_title": "Purpose 1",
                                "consent_expiry_period": (datetime.now() + timedelta(days=5)).isoformat(),
                            },
                            {
                                "purpose_id": "p2",
                                "purpose_title": "Purpose 2",
                                "consent_expiry_period": (datetime.now() + timedelta(days=10)).isoformat(),
                            },
                        ],
                    }
                ]
            },
        },
    }


@pytest.mark.asyncio
async def test_get_all_consent_artifact_success(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor
    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 1

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    result = await consent_artifact_service.get_all_consent_artifact(
        page=1,
        limit=10,
        search=None,
        cp_names_query=None,
        purposes_query=None,
        data_elements_query=None,
        sort_order="desc",
        start_date=None,
        end_date=None,
        current_user=current_user_data,
    )

    mock_consent_artifact_crud.get_filtered_consent_artifacts.assert_called()
    mock_consent_artifact_crud.count_filtered_consent_artifacts.assert_called_once()
    mock_log.assert_called_once()
    assert result["total_count"] == 1
    assert len(result["consent_data"]) == 1
    assert result["consent_data"][0]["_id"] == str(sample_consent_artifact["_id"])


@pytest.mark.asyncio
async def test_get_all_consent_artifact_with_search(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor
    mock_consent_artifact_crud.count_filtered_consent_artifacts.return_value = 1

    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", AsyncMock())

    search_term = "dp1@example.com"
    result = await consent_artifact_service.get_all_consent_artifact(
        page=1,
        limit=10,
        search=search_term,
        cp_names_query=None,
        purposes_query=None,
        data_elements_query=None,
        sort_order="desc",
        start_date=None,
        end_date=None,
        current_user=current_user_data,
    )

    expected_hashed_search = hash_shake256(search_term)
    args, _ = mock_consent_artifact_crud.get_filtered_consent_artifacts.call_args
    assert "$or" in args[0]
    assert {"artifact.data_principal.dp_e": expected_hashed_search} in args[0]["$or"]
    assert result["total_count"] == 1


@pytest.mark.asyncio
async def test_get_all_consent_artifact_no_user_df_id(consent_artifact_service, current_user_data):
    user_without_df_id = {**current_user_data, "df_id": None}
    with pytest.raises(HTTPException) as exc:
        await consent_artifact_service.get_all_consent_artifact(
            page=1,
            limit=10,
            search=None,
            cp_names_query=None,
            purposes_query=None,
            data_elements_query=None,
            sort_order="desc",
            start_date=None,
            end_date=None,
            current_user=user_without_df_id,
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User Not Found"


@pytest.mark.asyncio
async def test_download_consent_artifact_success(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    response = await consent_artifact_service.download_consent_artifact(
        search=None,
        cp_names_query=None,
        purposes_query=None,
        data_elements_query=None,
        sort_order="asc",
        start_date=None,
        end_date=None,
        current_user=current_user_data,
    )

    mock_consent_artifact_crud.get_filtered_consent_artifacts.assert_called_once()
    mock_log.assert_called_once()
    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/csv"
    assert "consent_artifacts.csv" in response.headers["Content-Disposition"]

    content = ""
    async for chunk in response.body_iterator:
        content += chunk

    assert "Agreement ID,Agreement Timestamp,Collection Point,Data Elements,DP ID,DP Email,DP Mobile,Purposes" in content
    assert f"agr1,{datetime(2023, 1, 1).isoformat()},CP1,DE1,dp1,{hash_shake256('dp1@example.com')},{hash_shake256('1234567890')},Purpose 1|Purpose 2" in content


@pytest.mark.asyncio
async def test_download_consent_artifact_no_user_df_id(consent_artifact_service, current_user_data):
    user_without_df_id = {**current_user_data, "df_id": None}
    with pytest.raises(HTTPException) as exc:
        await consent_artifact_service.download_consent_artifact(
            search=None,
            cp_names_query=None,
            purposes_query=None,
            data_elements_query=None,
            sort_order="asc",
            start_date=None,
            end_date=None,
            current_user=user_without_df_id,
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User Not Found"


@pytest.mark.asyncio
async def test_get_consent_artifact_by_id_success(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_consent_artifact_crud.get_one_consent_artifacts.return_value = sample_consent_artifact

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    result = await consent_artifact_service.get_consent_artifact_by_id(
        str(sample_consent_artifact["_id"]), current_user_data
    )

    mock_consent_artifact_crud.get_one_consent_artifacts.assert_called_once_with(
        {"_id": ObjectId(str(sample_consent_artifact["_id"])), "df_id": current_user_data["df_id"]}
    )
    mock_log.assert_called_once()
    assert result["_id"] == str(sample_consent_artifact["_id"])


@pytest.mark.asyncio
async def test_get_consent_artifact_by_id_not_found(consent_artifact_service, mock_consent_artifact_crud, current_user_data, monkeypatch):
    mock_consent_artifact_crud.get_one_consent_artifacts.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        # Provide a valid-looking but non-existent ObjectId string
        await consent_artifact_service.get_consent_artifact_by_id(str(ObjectId()), current_user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Consent Artifact Not Found"
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_consent_artifact_by_id_no_user_df_id(consent_artifact_service, current_user_data):
    user_without_df_id = {**current_user_data, "df_id": None}
    with pytest.raises(HTTPException) as exc:
        await consent_artifact_service.get_consent_artifact_by_id("any_id", user_without_df_id)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User Not Found"


@pytest.mark.asyncio
async def test_get_expiring_consents_success(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_expiring_consent_artifacts.return_value = mock_cursor

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    result = await consent_artifact_service.get_expiring_consents(df_id=current_user_data["df_id"], days_to_expire="7")

    mock_consent_artifact_crud.get_expiring_consent_artifacts.assert_called_once()
    mock_log.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].dp_id == "dp1"
    assert len(result[0].expiring_purposes) == 1 # Only Purpose 1 (5 days) should expire in 7 days


@pytest.mark.asyncio
async def test_get_expiring_consents_no_matching_consents(consent_artifact_service, mock_consent_artifact_crud, current_user_data, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = []
    mock_consent_artifact_crud.get_expiring_consent_artifacts.return_value = mock_cursor

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    # For this test, log_business_event should still be called to log the query attempt, even if no results
    mock_log.reset_mock()
    result = await consent_artifact_service.get_expiring_consents(df_id=current_user_data["df_id"], days_to_expire="7")

    assert result == []
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_expiring_consents_with_dp_id_filter(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_expiring_consent_artifacts.return_value = mock_cursor

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    mock_log.reset_mock()
    result = await consent_artifact_service.get_expiring_consents(
        df_id=current_user_data["df_id"], dp_id="dp1", days_to_expire="15"
    )

    args, _ = mock_consent_artifact_crud.get_expiring_consent_artifacts.call_args
    assert args[0]["dp_id"] == "dp1"
    assert len(result) == 1
    assert result[0].dp_id == "dp1"
    assert len(result[0].expiring_purposes) == 2 # Both purposes expire within 15 days (5 and 10 days)
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_expiring_consents_default_30_days(consent_artifact_service, mock_consent_artifact_crud, current_user_data, sample_consent_artifact, monkeypatch):
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [sample_consent_artifact]
    mock_consent_artifact_crud.get_expiring_consent_artifacts.return_value = mock_cursor

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.consent_artifact_service.log_business_event", mock_log)

    mock_log.reset_mock()
    result = await consent_artifact_service.get_expiring_consents(df_id=current_user_data["df_id"], days_to_expire=None)

    args, _ = mock_consent_artifact_crud.get_expiring_consent_artifacts.call_args
    assert "$lte" in args[0]["artifact.consent_scope.data_elements.consents.consent_expiry_period"]
    assert len(result) == 1
    assert result[0].dp_id == "dp1"
    assert len(result[0].expiring_purposes) == 2 # Both purposes expire within 30 days (5 and 10 days)
    mock_log.assert_called_once()
