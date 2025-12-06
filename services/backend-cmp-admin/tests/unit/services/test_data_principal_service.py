import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.data_principal_service import DataPrincipalService
from app.schemas.data_principal_schema import AddDP, UpdateDP
from datetime import datetime, UTC
import uuid


class AnyDictContaining(object):
    def __init__(self, expected_dict):
        self.expected_dict = expected_dict

    def __eq__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        for key, value in self.expected_dict.items():
            if key not in other or other[key] != value:
                return False
        return True

    def __repr__(self):
        return f"<AnyDictContaining {self.expected_dict!r}>"


# Mock for business_logger
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_data_principal_crud():
    return AsyncMock()


@pytest.fixture
def mock_consent_latest_artifacts_collection():
    return AsyncMock()


@pytest.fixture
def business_logs_collection():
    return "business_logs"


@pytest.fixture
def data_principal_service(mock_data_principal_crud, mock_consent_latest_artifacts_collection, business_logs_collection):
    return DataPrincipalService(
        data_principal_crud=mock_data_principal_crud,
        consent_latest_artifacts=mock_consent_latest_artifacts_collection,
        business_logs_collection=business_logs_collection,
    )


@pytest.fixture
def sample_user():
    return {"email": "test@example.com", "df_id": "df_id_123", "_id": "user_id_123"}


@pytest.fixture
def sample_add_dp_payload_1():
    return AddDP(
        dp_system_id="system123",
        dp_identifiers=["email", "mobile"],
        dp_email=["test1@example.com"],
        dp_mobile=[1234567890],
        dp_preferred_lang="eng",
        dp_country="india",
        dp_state="karnataka",
        created_at_df=datetime.now(UTC),
        last_activity=datetime.now(UTC),
    )


@pytest.fixture
def sample_add_dp_payload_2():
    return AddDP(
        dp_system_id="system456",
        dp_identifiers=["email"],
        dp_email=["test2@example.com"],
        dp_preferred_lang="eng",
        dp_country="usa",
        dp_state="ca",
        created_at_df=datetime.now(UTC),
        last_activity=datetime.now(UTC),
    )


@pytest.fixture
def sample_update_dp_payload():
    return UpdateDP(
        dp_email=["updated@example.com"],
        dp_preferred_lang="hin",
    )


@pytest.fixture
def sample_principal_id():
    return str(uuid.uuid4())


class TestAddDataPrincipal:
    async def test_add_data_principal_success_new_dp(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_add_dp_payload_1,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_system_id.return_value = None
        mock_data_principal_crud.insert.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.add_data_principal([sample_add_dp_payload_1], sample_user)

        mock_data_principal_crud.ensure_table.assert_called_once_with("dpd")
        mock_data_principal_crud.get_by_system_id.assert_called_once_with("dpd", sample_add_dp_payload_1.dp_system_id)
        mock_data_principal_crud.insert.assert_called_once()
        assert "principal_ids" in result
        assert len(result["principal_ids"]) == 1
        mock_log_business_event.assert_called_with(
            event_type="ADD_DP_SUCCESS",
            user_email=sample_user["email"],
            message=f"Data Principal added successfully for system_id={sample_add_dp_payload_1.dp_system_id}",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_system_id": sample_add_dp_payload_1.dp_system_id,
                    "df_id": sample_user["df_id"],
                    "added_by": sample_user["email"],
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_add_data_principal_success_reactivate_dp(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_add_dp_payload_1,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_system_id.return_value = (["old@example.com"], [9876543210], True)
        mock_data_principal_crud.insert_or_update_deleted.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.add_data_principal([sample_add_dp_payload_1], sample_user)

        mock_data_principal_crud.ensure_table.assert_called_once_with("dpd")
        mock_data_principal_crud.get_by_system_id.assert_called_once_with("dpd", sample_add_dp_payload_1.dp_system_id)
        mock_data_principal_crud.insert_or_update_deleted.assert_called_once()
        assert result == {"message": "Data Principal re-activated", "principal_id": None}
        mock_log_business_event.assert_called_with(
            event_type="ADD_DP_REACTIVATED",
            user_email=sample_user["email"],
            message=f"Re-activated deleted Data Principal for system_id={sample_add_dp_payload_1.dp_system_id}",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_system_id": sample_add_dp_payload_1.dp_system_id,
                    "df_id": sample_user["df_id"],
                    "added_by": sample_user["email"],
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_add_data_principal_failure_duplicate_system_id(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_add_dp_payload_1,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_system_id.return_value = ([], [], False)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.add_data_principal([sample_add_dp_payload_1], sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "System ID already exists."
        mock_log_business_event.assert_called_with(
            event_type="ADD_DP_FAILURE",
            user_email=sample_user["email"],
            message=f"Duplicate system_id detected: {sample_add_dp_payload_1.dp_system_id}",
            log_level="ERROR",
            context=AnyDictContaining(
                {
                    "dp_system_id": sample_add_dp_payload_1.dp_system_id,
                    "df_id": sample_user["df_id"],
                    "added_by": sample_user["email"],
                    "reason": "System ID already exists",
                }
            ),
            business_logs_collection="business_logs",
        )

    @pytest.mark.parametrize(
        "field, value, error_detail",
        [
            ("dp_system_id", None, "System ID is required."),
            ("dp_system_id", "", "System ID is required."),
        ],
    )
    async def test_add_data_principal_validation_system_id_failure(
        self, data_principal_service, sample_add_dp_payload_1, sample_user, field, value, error_detail
    ):
        setattr(sample_add_dp_payload_1, field, value)
        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.add_data_principal([sample_add_dp_payload_1], sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_detail

    @pytest.mark.parametrize(
        "identifiers, emails, mobiles, error_detail",
        [
            (["email"], [], [], "At least one email is required."),
            (["email"], ["a@a.com", "a@a.com"], [], "Duplicate emails found."),
            (["email"], ["invalid-email"], [], "Invalid email address"),
            (["mobile"], [], [], "At least one mobile is required."),
            (["mobile"], [], [1234567890, 1234567890], "Duplicate mobile numbers found."),
            (["mobile"], [], [123], "Invalid mobile number"),
            (["mobile"], [], [0], "Invalid mobile number"),
        ],
    )
    async def test_add_data_principal_validation_identifier_failure(
        self,
        data_principal_service,
        sample_add_dp_payload_1,
        sample_user,
        identifiers,
        emails,
        mobiles,
        error_detail,
    ):
        sample_add_dp_payload_1.dp_identifiers = identifiers
        sample_add_dp_payload_1.dp_email = emails
        sample_add_dp_payload_1.dp_mobile = mobiles

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.add_data_principal([sample_add_dp_payload_1], sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_detail

    async def test_add_data_principal_multiple_dps_success(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_add_dp_payload_1,
        sample_add_dp_payload_2,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_system_id.return_value = None
        mock_data_principal_crud.insert.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.add_data_principal([sample_add_dp_payload_1, sample_add_dp_payload_2], sample_user)

        assert "principal_ids" in result
        assert len(result["principal_ids"]) == 2
        assert mock_data_principal_crud.insert.call_count == 2
        assert mock_log_business_event.call_count == 2


class TestGetDataPrincipal:
    async def test_get_data_principal_success(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_dp_id.return_value = {
            "dp_id": sample_principal_id,
            "dp_system_id": "system123",
            "dp_identifiers": ["email"],
            "dp_email": ["test@example.com"],
            "dp_mobile": ["1234567890"],
            "dp_other_identifier": [],
            "dp_preferred_lang": "eng",
            "dp_country": "india",
            "dp_state": "karnataka",
            "dp_active_devices": [],
            "dp_tags": [],
            "is_active": True,
            "is_legacy": False,
            "added_by": "user_id_123",
            "added_with": "manual",
            "created_at_df": datetime.now(UTC),
            "last_activity": datetime.now(UTC),
            "consent_count": 0,
            "consent_status": "unsent",
            "is_deleted": False,
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)
        monkeypatch.setattr("app.services.data_principal_service.mask_email", lambda e: f"{e[0]}**@e")

        monkeypatch.setattr("app.services.data_principal_service.mask_mobile", lambda m: f"{str(m)[0]}**")

        result = await data_principal_service.get_data_principal(sample_principal_id, sample_user)

        mock_data_principal_crud.get_by_dp_id.assert_called_once_with("dpd", sample_principal_id)
        assert result["dp_id"] == sample_principal_id
        assert result["dp_email"][0].startswith("t**@e")  # masked email
        assert result["dp_mobile"][0].startswith("1**")  # masked mobile
        mock_log_business_event.assert_called_with(
            event_type="GET_DP_SUCCESS",
            user_email=sample_user["email"],
            message=f"Data Principal fetched successfully for principal_id={sample_principal_id}",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "action": "get",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_get_data_principal_failure_not_found(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_dp_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.get_data_principal(sample_principal_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Data Principal not found"
        mock_log_business_event.assert_called_with(
            event_type="GET_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Data Principal not found (principal_id={sample_principal_id})",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Data Principal not found",
                    "action": "get",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_get_data_principal_failure_is_deleted(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_by_dp_id.return_value = {"is_deleted": True}

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.get_data_principal(sample_principal_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Data Principal is deleted"
        mock_log_business_event.assert_called_with(
            event_type="GET_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Data Principal is deleted (principal_id={sample_principal_id})",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Data Principal is deleted",
                    "action": "get",
                }
            ),
            business_logs_collection="business_logs",
        )


class TestDeleteDataPrincipal:
    async def test_delete_data_principal_success(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.exists_not_deleted.return_value = True
        mock_data_principal_crud.get_consent_status.return_value = "unsent"
        mock_data_principal_crud.soft_delete.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.delete_data_principal(sample_principal_id, sample_user)

        mock_data_principal_crud.exists_not_deleted.assert_called_once_with("dpd", sample_principal_id)
        mock_data_principal_crud.get_consent_status.assert_called_once_with("dpd", sample_principal_id)
        mock_data_principal_crud.soft_delete.assert_called_once_with("dpd", sample_principal_id)
        assert result == {"message": "Data Principal deleted successfully"}
        mock_log_business_event.assert_called_with(
            event_type="DELETE_DP_SUCCESS",
            user_email=sample_user["email"],
            message=f"Data Principal deleted successfully for principal_id={sample_principal_id}",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "action": "delete",
                    "status": "soft_deleted",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_delete_data_principal_failure_unauthorized(
        self,
        data_principal_service,
        sample_principal_id,
        monkeypatch,
    ):
        user_without_df_id = {"email": "test@example.com"}

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.delete_data_principal(sample_principal_id, user_without_df_id)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_log_business_event.assert_called_with(
            event_type="DELETE_DP_FAILED",
            user_email=user_without_df_id["email"],
            message=f"Unauthorized delete attempt for principal_id={sample_principal_id}",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": None,
                    "reason": "Unauthorized user (missing df_id)",
                    "action": "delete",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_delete_data_principal_failure_not_found_or_deleted(
        self, data_principal_service, mock_data_principal_crud, sample_principal_id, sample_user, monkeypatch
    ):
        mock_data_principal_crud.exists_not_deleted.return_value = False

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.delete_data_principal(sample_principal_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Data Principal not found or already deleted"
        mock_log_business_event.assert_called_with(
            event_type="DELETE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Delete failed: Data Principal not found or already deleted (principal_id={sample_principal_id})",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Not found or already deleted",
                    "action": "delete",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_delete_data_principal_failure_active_consent(
        self, data_principal_service, mock_data_principal_crud, sample_principal_id, sample_user, monkeypatch
    ):
        mock_data_principal_crud.exists_not_deleted.return_value = True
        mock_data_principal_crud.get_consent_status.return_value = "given"

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.delete_data_principal(sample_principal_id, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Cannot delete active Data Principal: consent given or in progress"
        mock_log_business_event.assert_called_with(
            event_type="DELETE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Delete failed: Active or in-progress consent for principal_id={sample_principal_id}",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Consent status = given",
                    "action": "delete",
                }
            ),
            business_logs_collection="business_logs",
        )


class TestGetAllDataPrincipals:
    async def test_get_all_data_principals_success_no_filters(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.count.return_value = 1
        mock_data_principal_crud.fetch_all.return_value = [
            {
                "dp_id": str(uuid.uuid4()),
                "dp_system_id": "system1",
                "dp_identifiers": ["email"],
                "dp_email": ["test@example.com"],
                "dp_mobile": ["1234567890"],
                "dp_other_identifier": [],
                "dp_tags": [],
                "dp_preferred_lang": "eng",
                "dp_country": "india",
                "dp_state": "karnataka",
                "dp_active_devices": [],
                "is_active": True,
                "is_legacy": False,
                "added_by": "user_id_123",
                "added_with": "manual",
                "created_at_df": datetime.now(UTC),
                "last_activity": datetime.now(UTC),
                "consent_count": 0,
                "consent_status": "unsent",
                "df_id": "df_id_123",
            }
        ]
        mock_data_principal_crud.fetch_options.return_value = {
            "dp_country": ["india"],
            "dp_preferred_lang": ["eng"],
            "is_legacy": [True, False],
            "consent_status": ["unsent"],
            "added_with": ["manual"],
            "dp_tags": ["tag1"],
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)
        monkeypatch.setattr("app.services.data_principal_service.mask_email", lambda e: f"{e[0]}**@e")

        monkeypatch.setattr("app.services.data_principal_service.mask_mobile", lambda m: f"{str(m)[0]}**")

        result = await data_principal_service.get_all_data_principals(page=1, limit=10, user=sample_user)

        mock_data_principal_crud.count.assert_called_once()
        mock_data_principal_crud.fetch_all.assert_called_once()
        mock_data_principal_crud.fetch_options.assert_called_once()
        assert result["totalPrincipals"] == 1
        assert len(result["dataPrincipals"]) == 1
        assert result["dataPrincipals"][0]["dp_email"][0].startswith("t**@e")  # masked email
        assert result["dataPrincipals"][0]["dp_mobile"][0].startswith("1**")  # masked mobile
        mock_log_business_event.assert_called_with(
            event_type="GET_ALL_DP_SUCCESS",
            user_email=sample_user["email"],
            message="All Data Principals fetched successfully",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "df_id": sample_user["df_id"],
                    "page": 1,
                    "limit": 10,
                    "total_principals": 1,
                    "action": "get_all",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_get_all_data_principals_success_with_filters(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.count.return_value = 1
        mock_data_principal_crud.fetch_all.return_value = [
            {
                "dp_id": str(uuid.uuid4()),
                "dp_system_id": "system1",
                "dp_identifiers": ["email"],
                "dp_email": ["test@example.com"],
                "dp_mobile": ["1234567890"],
                "dp_other_identifier": [],
                "dp_tags": [],
                "dp_preferred_lang": "eng",
                "dp_country": "india",
                "dp_state": "karnataka",
                "dp_active_devices": [],
                "is_active": True,
                "is_legacy": False,
                "added_by": "user_id_123",
                "added_with": "manual",
                "created_at_df": datetime.now(UTC),
                "last_activity": datetime.now(UTC),
                "consent_count": 0,
                "consent_status": "unsent",
                "df_id": "df_id_123",
            }
        ]
        mock_data_principal_crud.fetch_options.return_value = {
            "dp_country": ["india"],
            "dp_preferred_lang": ["eng"],
            "is_legacy": [True, False],
            "consent_status": ["unsent"],
            "added_with": ["manual"],
            "dp_tags": ["tag1"],
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)
        monkeypatch.setattr("app.services.data_principal_service.mask_email", lambda e: f"{e[0]}**@e")

        monkeypatch.setattr("app.services.data_principal_service.mask_mobile", lambda m: f"{str(m)[0]}**")

        result = await data_principal_service.get_all_data_principals(
            page=1,
            limit=10,
            user=sample_user,
            dp_country="india",
            is_legacy=False,
            search="test",
        )

        mock_data_principal_crud.count.assert_called_once()
        mock_data_principal_crud.fetch_all.assert_called_once()
        mock_data_principal_crud.fetch_options.assert_called_once()
        assert result["totalPrincipals"] == 1
        assert len(result["dataPrincipals"]) == 1


class TestUpdateDataPrincipal:
    async def test_update_data_principal_success(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        sample_update_dp_payload,
        monkeypatch,
    ):
        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.return_value = {
            "dp_email": ["old@example.com"],
            "dp_mobile": ["9876543210"],
            "dp_other_identifier": [],
        }
        mock_data_principal_crud.update_principal.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.update_data_principal(sample_principal_id, sample_update_dp_payload, sample_user)

        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.assert_called_once_with("dpd", sample_principal_id)
        mock_data_principal_crud.update_principal.assert_called_once()
        assert result == {"message": "Data Principal updated successfully", "principal_id": sample_principal_id}
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_SUCCESS",
            user_email=sample_user["email"],
            message=f"Data Principal updated successfully for principal_id={sample_principal_id}",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_update_data_principal_failure_unauthorized(
        self,
        data_principal_service,
        sample_principal_id,
        sample_update_dp_payload,
        monkeypatch,
    ):
        user_without_df_id = {"email": "test@example.com"}

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.update_data_principal(sample_principal_id, sample_update_dp_payload, user_without_df_id)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_FAILED",
            user_email=user_without_df_id["email"],
            message=f"Unauthorized update attempt for principal_id={sample_principal_id}",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": None,
                    "reason": "Unauthorized user (missing df_id)",
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_update_data_principal_failure_not_found(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        sample_update_dp_payload,
        monkeypatch,
    ):
        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.update_data_principal(sample_principal_id, sample_update_dp_payload, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Principal ID does not exist"
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Update failed: Data Principal not found (principal_id={sample_principal_id})",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Principal not found",
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_update_data_principal_failure_no_update_found(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.return_value = {
            "dp_email": [],
            "dp_mobile": [],
            "dp_other_identifier": [],
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        empty_update_payload = UpdateDP()

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.update_data_principal(sample_principal_id, empty_update_payload, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "No update found"
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"No valid update fields found for principal_id={sample_principal_id}",
            log_level="WARNING",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "No update content provided",
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )

    @pytest.mark.parametrize(
        "emails, error_detail",
        [
            (["invalid-email"], "Invalid email address format"),
            (["test@example.com", "bad-email"], "Invalid email address format"),
        ],
    )
    async def test_update_data_principal_failure_invalid_email_format(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        emails,
        error_detail,
        monkeypatch,
    ):
        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.return_value = {
            "dp_email": [],
            "dp_mobile": [],
            "dp_other_identifier": [],
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        update_payload = UpdateDP(dp_email=emails)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.update_data_principal(sample_principal_id, update_payload, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_detail
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Invalid email format during update for principal_id={sample_principal_id}",
            log_level="ERROR",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Invalid email format",
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )

    @pytest.mark.parametrize(
        "mobiles, error_detail",
        [
            ([123], "Mobile number must be exactly 10 digits and cannot be 0."),
            ([0], "Mobile number must be exactly 10 digits and cannot be 0."),
            ([1234567890, 123], "Mobile number must be exactly 10 digits and cannot be 0."),
        ],
    )
    async def test_update_data_principal_failure_invalid_mobile_format(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_principal_id,
        sample_user,
        mobiles,
        error_detail,
        monkeypatch,
    ):
        mock_data_principal_crud.get_emails_mobiles_and_other_identifiers.return_value = {
            "dp_email": [],
            "dp_mobile": [],
            "dp_other_identifier": [],
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        update_payload = UpdateDP(dp_mobile=mobiles)

        with pytest.raises(HTTPException) as exc_info:
            await data_principal_service.update_data_principal(sample_principal_id, update_payload, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_detail
        mock_log_business_event.assert_called_with(
            event_type="UPDATE_DP_FAILED",
            user_email=sample_user["email"],
            message=f"Invalid mobile number format for principal_id={sample_principal_id}",
            log_level="ERROR",
            context=AnyDictContaining(
                {
                    "dp_id": sample_principal_id,
                    "df_id": sample_user["df_id"],
                    "reason": "Mobile number not 10 digits or zero",
                    "action": "update",
                }
            ),
            business_logs_collection="business_logs",
        )


class TestGetAllDpTags:
    async def test_get_all_dp_tags_success(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.fetch_all_tags.return_value = ["tag1", "tag2"]

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.get_all_dp_tags(sample_user)

        mock_data_principal_crud.fetch_all_tags.assert_called_once_with("dpd")
        assert result == {"dp_tags": ["tag1", "tag2"]}
        mock_log_business_event.assert_called_with(
            event_type="GET_ALL_DP_TAGS_SUCCESS",
            user_email=sample_user["email"],
            message="All Data Principal tags fetched successfully",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "df_id": sample_user["df_id"],
                    "action": "get_all_dp_tags",
                    "tag_count": 2,
                }
            ),
            business_logs_collection="business_logs",
        )

    async def test_get_all_dp_tags_no_tags(
        self,
        data_principal_service,
        mock_data_principal_crud,
        sample_user,
        monkeypatch,
    ):
        mock_data_principal_crud.fetch_all_tags.return_value = []

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.get_all_dp_tags(sample_user)

        assert result == {"dp_tags": []}
        mock_log_business_event.assert_called_with(
            event_type="GET_ALL_DP_TAGS_SUCCESS",
            user_email=sample_user["email"],
            message="All Data Principal tags fetched successfully",
            log_level="INFO",
            context=AnyDictContaining(
                {
                    "df_id": sample_user["df_id"],
                    "action": "get_all_dp_tags",
                    "tag_count": 0,
                }
            ),
            business_logs_collection="business_logs",
        )


class TestGetDpsByDataElements:
    async def test_get_dps_by_data_elements_no_dp_ids_found(
        self,
        data_principal_service,
        mock_consent_latest_artifacts_collection,
        sample_user,
        monkeypatch,
    ):
        de_titles = ["data_element_1"]
        mock_consent_latest_artifacts_collection.distinct.return_value = []

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr("app.services.data_principal_service.log_business_event", mock_log_business_event)

        result = await data_principal_service.get_dps_by_data_elements(de_titles, sample_user)

        mock_consent_latest_artifacts_collection.distinct.assert_called_once()
        assert result == []
        # No business event logged if no DPs found
        mock_log_business_event.assert_not_called()
