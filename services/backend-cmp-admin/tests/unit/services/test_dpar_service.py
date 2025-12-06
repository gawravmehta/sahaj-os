
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from app.services.dpar_service import DPARequestService, EXPORT_FIELDS
from app.schemas.dpar_schema import DPARCreateRequest, DPARReportCreate, ReportTypeEnum, SendToEnum
from datetime import datetime, timezone, timedelta, UTC
import uuid
import json
import io
from pydantic import ValidationError
from bson import ObjectId

# Helper class for partial dictionary matching
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


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_dpar_crud():
    return AsyncMock()


@pytest.fixture
def mock_user_collection():
    return AsyncMock()


@pytest.fixture
def mock_s3_client():
    return MagicMock()


@pytest.fixture
def mock_consent_artifact_crud():
    return AsyncMock()


@pytest.fixture
def business_logs_collection():
    return "business_logs"


@pytest.fixture
def dpa_request_service(
    mock_dpar_crud,
    mock_user_collection,
    mock_s3_client,
    mock_consent_artifact_crud,
    business_logs_collection,
):
    return DPARequestService(
        dpa_crud=mock_dpar_crud,
        user_collection=mock_user_collection,
        s3_client=mock_s3_client,
        bucket_name="test-bucket",
        consent_artifact_crud=mock_consent_artifact_crud,
        business_logs_collection=business_logs_collection,
    )


@pytest.fixture
def sample_user():
    return {"email": "test@example.com", "df_id": "df_id_123", "_id": str(ObjectId()), "first_name": "Test", "last_name": "User", "image_url": "http://example.com/image.png"}


@pytest.fixture
def sample_dpar_create_request_payload():
    return DPARCreateRequest(
        first_name="John",
        last_name="Doe",
        core_identifier="john.doe@example.com",
        request_type="data_retention_period",
        subject="Data Retention Request",
        message="Please update my data retention period.",
    )


@pytest.fixture
def sample_dpar_report_create_payload():
    return DPARReportCreate(
        report_type=ReportTypeEnum.message,
        template_id="template123",
        send_to=SendToEnum.core,
        subject="DPAR Report Subject",
        message="This is a DPAR report message.",
    )


@pytest.fixture
def sample_request_id():
    return str(ObjectId())


@pytest.fixture
def sample_note_id():
    return str(ObjectId())


@pytest.fixture
def mock_request_details():
    request = AsyncMock(spec=Request)
    request.headers = {"user-agent": "test-browser", "accept": "*/*"}
    return request


class TestGetAllRequests:
    async def test_get_all_requests_success_no_filters(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.count_requests.return_value = 1
        mock_dpar_crud.get_requests.return_value = [
            {
                "_id": ObjectId(),
                "dpar_request_id": "dpar1",
                "request_origin": "portal",
                "created_timestamp": datetime.now(UTC) - timedelta(days=5),
                "first_name": "John",
                "last_name": "Doe",
                "core_identifier": "john.doe@example.com",
                "secondary_identifier": None,
                "status": "new",
                "last_updated": datetime.now(UTC) - timedelta(days=1),
                "urgency_level": "medium",
                "deadline": datetime.now(UTC) + timedelta(days=25),
                "dp_type": "individual",
            }
        ]

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.get_all_requests(
            request=mock_request_details, current_user=sample_user, page=1, page_size=10, status=None, dp_type=None, created_from=None, created_to=None
        )

        mock_dpar_crud.count_requests.assert_called_once_with({"is_deleted": False})
        mock_dpar_crud.get_requests.assert_called_once()
        assert result["pagination"]["total_records"] == 1
        assert len(result["data"]) == 1
        mock_log_business_event.assert_called_once_with(
            event_type="LIST_DPAR_REQUESTS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"]}),
            message="User listed DPAR requests. Page: 1, Size: 10.",
            business_logs_collection="business_logs",
        )

    @pytest.mark.parametrize(
        "status, dp_type, created_from, created_to, expected_filter_keys",
        [
            ("new", None, None, None, ["is_deleted", "status"]),
            (None, "individual", None, None, ["is_deleted", "dp_type"]),
            (None, None, "2023-01-01", None, ["is_deleted", "created_timestamp"]),
            (None, None, None, "2023-01-31", ["is_deleted", "created_timestamp"]),
            ("completed", "corporate", "2023-01-01", "2023-01-31", ["is_deleted", "status", "dp_type", "created_timestamp"]),
        ],
    )
    async def test_get_all_requests_with_filters(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        mock_request_details,
        monkeypatch,
        status, dp_type, created_from, created_to, expected_filter_keys
    ):
        mock_dpar_crud.count_requests.return_value = 1
        mock_dpar_crud.get_requests.return_value = []

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        await dpa_request_service.get_all_requests(
            request=mock_request_details, current_user=sample_user, page=1, page_size=10, status=status, dp_type=dp_type, created_from=created_from, created_to=created_to
        )

        args, kwargs = mock_dpar_crud.count_requests.call_args
        assert all(key in args[0] for key in expected_filter_keys)


class TestCreateRequest:
    async def test_create_request_success_new(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_dpar_create_request_payload,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.get_last_request.return_value = None
        inserted_id = str(ObjectId())
        mock_dpar_crud.insert_request.return_value = inserted_id

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.create_request(
            request=sample_dpar_create_request_payload, request_details=mock_request_details, current_user=sample_user
        )

        mock_dpar_crud.get_last_request.assert_called_once_with(sample_user["_id"])
        mock_dpar_crud.insert_request.assert_called_once()
        assert "dpar_request_id" in result
        assert result["status"] == "created"
        mock_log_business_event.assert_called_once_with(
            event_type="CREATE_DPAR_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"]}),
            message=f"DPAR request '{inserted_id}' created successfully by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_create_request_success_with_related_request(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_dpar_create_request_payload,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.get_last_request.return_value = {"_id": ObjectId()}
        inserted_id = str(ObjectId())
        mock_dpar_crud.insert_request.return_value = inserted_id

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.create_request(
            request=sample_dpar_create_request_payload, request_details=mock_request_details, current_user=sample_user
        )

        mock_dpar_crud.get_last_request.assert_called_once_with(sample_user["_id"])
        mock_dpar_crud.insert_request.assert_called_once()
        assert "dpar_request_id" in result
        assert result["status"] == "created"
        mock_log_business_event.assert_called_once_with(
            event_type="CREATE_DPAR_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"]}),
            message=f"DPAR request '{inserted_id}' created successfully by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_create_request_failure_db_insert(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_dpar_create_request_payload,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.get_last_request.return_value = None
        mock_dpar_crud.insert_request.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.create_request(
                request=sample_dpar_create_request_payload, request_details=mock_request_details, current_user=sample_user
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to create request"
        mock_log_business_event.assert_called_once_with(
            event_type="CREATE_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "error": "Failed to insert into DB"}),
            message=f"Failed to create DPAR request for user {sample_user['email']}.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    def test_create_request_validation_error_identifiers(self):
        with pytest.raises(ValidationError) as exc_info:
            DPARCreateRequest(
                first_name="John",
                last_name="Doe",
                request_type="data_retention_period",
                subject="Data Retention Request",
                message="Please update my data retention period.",
            )
        assert "Either core_identifier or secondary_identifier must be provided" in str(exc_info.value)


class TestGetOneRequest:
    async def test_get_one_request_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {
            "_id": ObjectId(sample_request_id),
            "dpar_request_id": "dpar1",
            "df_id": sample_user["df_id"],
            "created_timestamp": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
        }

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )
        
        mock_convert_objectid_to_str = MagicMock(side_effect=lambda x: x)
        monkeypatch.setattr("app.utils.common.convert_objectid_to_str", mock_convert_objectid_to_str)

        result = await dpa_request_service.get_one_request(sample_request_id, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(
            sample_request_id, {"df_id": sample_user["df_id"]}
        )
        assert result["_id"] == sample_request_id
        assert isinstance(result["created_timestamp"], str)
        mock_log_business_event.assert_called_once_with(
            event_type="GET_DPAR_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id}),
            message=f"User fetched DPAR request '{sample_request_id}'.",
            business_logs_collection="business_logs",
        )
        mock_convert_objectid_to_str.assert_called_once()

    async def test_get_one_request_failure_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.get_one_request(sample_request_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="GET_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "DPA request not found"}),
            message=f"Failed to fetch DPAR request '{sample_request_id}': Not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )


class TestSetStatus:
    async def test_set_status_success_rejected(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "requested_by": sample_user["_id"], "data_element_id": "test_de_id"}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": ObjectId(), "artifact": {"consent_scope": {"data_elements": [{"de_id": "test_de_id", "data_retention_period": "1 year"}]}, "cp_name": "test_cp"}}]
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        status = "rejected"
        status_details = "Not approved"
        result = await dpa_request_service.set_status(sample_request_id, status, status_details, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once()
        assert result["message"] == f"DPA request '{sample_request_id}' was rejected"
        mock_log_business_event.assert_called_once_with(
            event_type="SET_DPAR_STATUS_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "new_status": status}),
            message=f"DPAR request '{sample_request_id}' status updated to '{status}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_set_status_success_approved_update_data(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "request_type": "update_data", "data_element_id": "test_de_id", "requested_by": sample_user["_id"]}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": ObjectId(), "artifact": {"consent_scope": {"data_elements": [{"de_id": "test_de_id", "data_retention_period": "1 year", "title": "test_de_title"}]}, "cp_name": "test_cp", "data_principal": {"dp_id": sample_user["_id"]}}}]
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )
        mock_publish_message = AsyncMock()
        monkeypatch.setattr("app.services.dpar_service.publish_message", mock_publish_message)

        status = "approved"
        status_details = "Approved"
        result = await dpa_request_service.set_status(sample_request_id, status, status_details, sample_user)

        mock_publish_message.assert_called_once()
        assert result["message"] == f"DPA request '{sample_request_id}' was marked completed"
        mock_log_business_event.assert_any_call(
            event_type="DPAR_DATA_UPDATE_MESSAGE_PUBLISHED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "event_type": "data_update_requested"}),
            message=f"DPAR data update message for request '{sample_request_id}' published to queue.",
            business_logs_collection="business_logs",
        )
        mock_log_business_event.assert_any_call(
            event_type="SET_DPAR_STATUS_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "new_status": status}),
            message=f"DPAR request '{sample_request_id}' status updated to '{status}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_set_status_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.set_status(sample_request_id, "approved", "Approved", sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="SET_DPAR_STATUS_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "status": "approved", "error": "DPAR request not found"}),
            message=f"Failed to set status for DPAR request '{sample_request_id}': Not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_set_status_failure_consent_artifact_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "requested_by": sample_user["_id"], "data_element_id": "test_de_id", "request_type": "update_data"}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [] # No artifact found
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.set_status(sample_request_id, "approved", "Approved", sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Consent artifact not found"
        mock_log_business_event.assert_called_once_with(
            event_type="SET_DPAR_STATUS_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "status": "approved", "error": "Consent artifact not found"}),
            message=f"Failed to set status for DPAR request '{sample_request_id}': Consent artifact not found.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )
    
    async def test_set_status_failure_data_element_not_found_for_update_data(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "request_type": "update_data", "data_element_id": "non_existent_de_id", "requested_by": sample_user["_id"]}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": ObjectId(), "artifact": {"consent_scope": {"data_elements": [{"de_id": "test_de_id", "data_retention_period": "1 year", "title": "test_de_title"}]}, "cp_name": "test_cp", "data_principal": {"dp_id": sample_user["_id"]}}}]
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.set_status(sample_request_id, "approved", "Approved", sample_user)
        assert exc_info.value.status_code == 404
        assert "Data element non_existent_de_id not found" in exc_info.value.detail

    async def test_set_status_failure_invalid_status(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "requested_by": sample_user["_id"], "data_element_id": "test_de_id"}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": ObjectId(), "artifact": {"consent_scope": {"data_elements": [{"de_id": "test_de_id", "data_retention_period": "1 year"}]}, "cp_name": "test_cp"}}]
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.set_status(sample_request_id, "invalid_status", "Details", sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid status"
        mock_log_business_event.assert_called_once_with(
            event_type="SET_DPAR_STATUS_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "status": "invalid_status", "error": "Invalid status provided"}),
            message=f"Failed to set status for DPAR request '{sample_request_id}': Invalid status 'invalid_status'.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_set_status_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_consent_artifact_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        created_ts = datetime.now(UTC) - timedelta(days=1)
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "created_timestamp": created_ts, "requested_by": sample_user["_id"], "data_element_id": "test_de_id"}
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": ObjectId(), "artifact": {"consent_scope": {"data_elements": [{"de_id": "test_de_id", "data_retention_period": "1 year"}]}, "cp_name": "test_cp"}}]
        mock_consent_artifact_crud.get_filtered_consent_artifacts.return_value = mock_cursor

        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate DB update failure
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.set_status(sample_request_id, "rejected", "Not approved", sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="SET_DPAR_STATUS_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "status": "rejected", "error": "Failed to update DPAR request in DB"}),
            message=f"Failed to set status for DPAR request '{sample_request_id}': DB update failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestRequestKyc:
    async def test_request_kyc_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.request_kyc(sample_request_id, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once()
        assert result == {"message": "Resend KYC requested successfully"}
        mock_log_business_event.assert_called_once_with(
            event_type="REQUEST_KYC_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "new_status": "kyc_requested"}),
            message=f"KYC requested for DPAR request '{sample_request_id}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_request_kyc_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.request_kyc(sample_request_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_not_called() # No business log on initial not found check

    async def test_request_kyc_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate DB update failure
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.request_kyc(sample_request_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="REQUEST_KYC_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Failed to update DPAR request status in DB"}),
            message=f"Failed to request KYC for DPAR request '{sample_request_id}': DB update failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestClarificationRequest:
    async def test_clarification_request_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "clarification_action": []}
        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        clarification_details = MagicMock()
        clarification_details.model_dump.return_value = {"message": "Please clarify"}

        result = await dpa_request_service.clarification_request(sample_request_id, clarification_details, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once()
        assert result == {"message": "Clarification requested successfully", "request_id": sample_request_id}
        mock_log_business_event.assert_called_once_with(
            event_type="CLARIFICATION_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "status": "clarification_requested"}),
            message=f"Clarification requested for DPAR request '{sample_request_id}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_clarification_request_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        clarification_details = MagicMock()
        clarification_details.model_dump.return_value = {"message": "Please clarify"}

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.clarification_request(sample_request_id, clarification_details, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="CLARIFICATION_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "DPAR request not found"}),
            message=f"Failed to send clarification request for DPAR request '{sample_request_id}': Not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_clarification_request_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "clarification_action": []}
        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate DB update failure
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        clarification_details = MagicMock()
        clarification_details.model_dump.return_value = {"message": "Please clarify"}

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.clarification_request(sample_request_id, clarification_details, sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to update clarification request"
        mock_log_business_event.assert_called_once_with(
            event_type="CLARIFICATION_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Failed to update DPAR request in DB"}),
            message=f"Failed to send clarification request for DPAR request '{sample_request_id}': DB update failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestAddNotes:
    async def test_add_notes_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        note_title = "Test Note"
        note_str = "This is a test note."
        result = await dpa_request_service.add_notes(sample_request_id, note_title, note_str, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once()
        assert result == {"message": "Note added successfully", "request_id": sample_request_id}
        mock_log_business_event.assert_called_once_with(
            event_type="ADD_NOTE_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "note_title": note_title}),
            message=f"Note '{note_title}' added successfully to DPAR request '{sample_request_id}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_add_notes_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.add_notes(sample_request_id, "Title", "Note", sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="ADD_NOTE_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "DPAR request not found"}),
            message=f"Failed to add note to DPAR request '{sample_request_id}': Not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_add_notes_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate DB update failure
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        note_title = "Test Note"
        note_str = "This is a test note."
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.add_notes(sample_request_id, note_title, note_str, sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to add note"
        mock_log_business_event.assert_called_once_with(
            event_type="ADD_NOTE_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "note_title": note_title, "error": "Failed to update DPAR request in DB"}),
            message=f"Failed to add note '{note_title}' to DPAR request '{sample_request_id}': DB update failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestDeleteNotes:
    async def test_delete_notes_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_note_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "admin_notes": [{"_id": sample_note_id}]}
        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.delete_notes(sample_request_id, sample_note_id, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once_with(
            sample_request_id,
            {
                "$pull": {
                    "admin_notes": {"_id": sample_note_id},
                },
                "$set": {
                    "last_updated": datetime.now(UTC),
                },
            },
        )
        assert result == {"message": "Note deleted successfully", "request_id": sample_request_id}
        mock_log_business_event.assert_called_once_with(
            event_type="DELETE_NOTE_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "note_id": sample_note_id}),
            message=f"Note '{sample_note_id}' deleted successfully from DPAR request '{sample_request_id}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_delete_notes_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_note_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.delete_notes(sample_request_id, sample_note_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="DELETE_NOTE_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "note_id": sample_note_id, "error": "DPAR request not found"}),
            message=f"Failed to delete note '{sample_note_id}' from DPAR request '{sample_request_id}': Request not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_delete_notes_failure_note_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_note_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "admin_notes": []}
        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate note not found/updated
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.delete_notes(sample_request_id, sample_note_id, sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to delete note"
        mock_log_business_event.assert_called_once_with(
            event_type="DELETE_NOTE_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "note_id": sample_note_id, "error": "Failed to update DPAR request in DB"}),
            message=f"Failed to delete note '{sample_note_id}' from DPAR request '{sample_request_id}': DB update failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestUpdateRequest:
    async def test_update_request_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        initial_request = {
            "_id": ObjectId(sample_request_id),
            "df_id": sample_user["df_id"],
            "first_name": "Old",
            "last_name": "Name",
            "created_timestamp": datetime.now(UTC) - timedelta(days=10),
        }
        updated_request_data = {
            "_id": ObjectId(sample_request_id),
            "df_id": sample_user["df_id"],
            "first_name": "New",
            "last_name": "Name",
            "created_timestamp": (datetime.now(UTC) - timedelta(days=10)).isoformat(),
            "last_updated": datetime.now(UTC).isoformat(),
        }
        mock_dpar_crud.get_by_id.side_effect = [initial_request, updated_request_data]
        
        modified_result = MagicMock()
        modified_result.modified_count = 1
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        update_payload = DPARCreateRequest(first_name="New", core_identifier="test@example.com")
        result = await dpa_request_service.update_request(sample_request_id, update_payload, sample_user)

        assert mock_dpar_crud.get_by_id.call_count == 2
        mock_dpar_crud.update_request.assert_called_once()
        assert result["first_name"] == "New"
        mock_log_business_event.assert_called_once_with(
            event_type="UPDATE_DPAR_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "updated_fields": ["first_name", "last_updated"]}),
            message=f"DPAR request '{sample_request_id}' updated successfully. Fields: first_name, last_updated.",
            business_logs_collection="business_logs",
        )

    async def test_update_request_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        update_payload = DPARCreateRequest(first_name="New", core_identifier="test@example.com")
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.update_request(sample_request_id, update_payload, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Request not found or not owned by the user"
        mock_log_business_event.assert_called_once_with(
            event_type="UPDATE_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Request not found or not owned by the user"}),
            message=f"Failed to update DPAR request '{sample_request_id}': Not found or unauthorized access.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_update_request_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {
            "_id": ObjectId(sample_request_id),
            "df_id": sample_user["df_id"],
            "first_name": "Old",
            "last_name": "Name",
        }
        modified_result = MagicMock()
        modified_result.modified_count = 0  # Simulate DB update failure
        mock_dpar_crud.update_request.return_value = modified_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        update_payload = DPARCreateRequest(first_name="New", core_identifier="test@example.com")
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.update_request(sample_request_id, update_payload, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Failed to update the request"
        mock_log_business_event.assert_called_once_with(
            event_type="UPDATE_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Failed to update the request in DB"}),
            message=f"Failed to update DPAR request '{sample_request_id}': DB update failed or no changes.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestAllocateRequest:
    async def test_allocate_request_success(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_user_collection,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        assignee_id = str(ObjectId())
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        mock_user_collection.find_one.return_value = {"_id": ObjectId(assignee_id)}
        mock_dpar_crud.update_request.return_value = None # Return value not used for this particular call

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.allocate_request(sample_request_id, assignee_id, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_user_collection.find_one.assert_called_once_with({"_id": ObjectId(assignee_id), "df_id": sample_user["df_id"]})
        mock_dpar_crud.update_request.assert_called_once()
        assert result == {"message": "Request allocated successfully"}
        mock_log_business_event.assert_called_once_with(
            event_type="ALLOCATE_DPAR_REQUEST_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "assignee_id": assignee_id}),
            message=f"DPAR request '{sample_request_id}' allocated to '{assignee_id}' by user {sample_user['email']}.",
            business_logs_collection="business_logs",
        )

    async def test_allocate_request_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_user_collection,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        assignee_id = str(ObjectId())
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.allocate_request(sample_request_id, assignee_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPA request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="ALLOCATE_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "assignee_id": assignee_id, "error": "DPAR request not found"}),
            message=f"Failed to allocate DPAR request '{sample_request_id}': Request not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_allocate_request_failure_assignee_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        mock_user_collection,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        assignee_id = str(ObjectId())
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"]}
        mock_user_collection.find_one.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.allocate_request(sample_request_id, assignee_id, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Assignee not found"
        mock_log_business_event.assert_called_once_with(
            event_type="ALLOCATE_DPAR_REQUEST_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "assignee_id": assignee_id, "error": "Assignee not found"}),
            message=f"Failed to allocate DPAR request '{sample_request_id}': Assignee '{assignee_id}' not found.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestUploadKycDocuments:
    async def test_upload_kyc_documents_success_all_files(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "requested_by": sample_user["_id"]}
        mock_dpar_crud.update_request.return_value = MagicMock(modified_count=1)

        mock_upload_file_to_s3 = AsyncMock(side_effect=lambda file, field_name: f"http://s3.com/{field_name}_{file.filename}")
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        kyc_front_file = UploadFile(filename="front.jpg", file=io.BytesIO(b"front_content"), content_type="image/jpeg")
        kyc_back_file = UploadFile(filename="back.png", file=io.BytesIO(b"back_content"), content_type="image/png")
        attachment_file1 = UploadFile(filename="doc1.pdf", file=io.BytesIO(b"doc1_content"), content_type="application/pdf")
        attachment_file2 = UploadFile(filename="doc2.txt", file=io.BytesIO(b"doc2_content"), content_type="text/plain")

        result = await dpa_request_service.upload_kyc_documents(
            request_id=sample_request_id,
            current_user=sample_user,
            kyc_front=kyc_front_file,
            kyc_back=kyc_back_file,
            upload_attachments=[attachment_file1, attachment_file2],
        )

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"requested_by": sample_user["_id"]})
        assert mock_upload_file_to_s3.call_count == 4
        mock_dpar_crud.update_request.assert_called_once()
        assert "kyc_front_url" in result
        assert "kyc_back_url" in result
        assert len(result["request_attachments"]) == 2
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "kyc_front_uploaded": True, "kyc_back_uploaded": True, "num_attachments_uploaded": 2}),
            message=f"KYC documents and attachments uploaded successfully for DPAR request '{sample_request_id}'.",
            business_logs_collection="business_logs",
        )

    async def test_upload_kyc_documents_failure_unauthorized(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        monkeypatch,
    ):
        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        kyc_front_file = UploadFile(filename="front.jpg", file=io.BytesIO(b"front_content"), content_type="image/jpeg")
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.upload_kyc_documents(
                request_id=sample_request_id,
                current_user=None,
                kyc_front=kyc_front_file,
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_FAILED",
            user_email="anonymous",
            context=AnyDictContaining({"error": "Unauthorized user"}),
            message="Unauthorized attempt to upload KYC documents.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_upload_kyc_documents_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        kyc_front_file = UploadFile(filename="front.jpg", file=io.BytesIO(b"front_content"), content_type="image/jpeg")
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.upload_kyc_documents(
                request_id=sample_request_id,
                current_user=sample_user,
                kyc_front=kyc_front_file,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Request not found or unauthorized access"
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Request not found or unauthorized access"}),
            message=f"Failed to upload KYC for DPAR request '{sample_request_id}': Request not found or unauthorized access.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_upload_kyc_documents_failure_no_files_provided(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "requested_by": sample_user["_id"]}

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.upload_kyc_documents(
                request_id=sample_request_id,
                current_user=sample_user,
                kyc_front="",  # Empty string treated as None
                kyc_back="",  # Empty string treated as None
                upload_attachments=[],
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "No KYC files or attachments provided for upload"
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "No files provided"}),
            message=f"No KYC files or attachments provided for DPAR request '{sample_request_id}'.",
            log_level="INFO",
            business_logs_collection="business_logs",
        )

    async def test_upload_kyc_documents_failure_s3_upload_kyc_front(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "requested_by": sample_user["_id"]}

        mock_upload_file_to_s3 = AsyncMock(side_effect=HTTPException(status_code=500, detail="S3 error"))
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        kyc_front_file = UploadFile(filename="front.jpg", file=io.BytesIO(b"front_content"), content_type="image/jpeg")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.upload_kyc_documents(
                request_id=sample_request_id,
                current_user=sample_user,
                kyc_front=kyc_front_file,
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "S3 error"
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "file_type": "kyc_front", "error": "S3 error"}),
            message=f"Failed to upload front KYC for request '{sample_request_id}': S3 error.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_upload_kyc_documents_failure_db_update_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "requested_by": sample_user["_id"]}
        mock_dpar_crud.update_request.return_value = MagicMock(modified_count=0) # Simulate DB update failure

        mock_upload_file_to_s3 = AsyncMock(return_value="http://s3.com/kyc_front.jpg")
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        kyc_front_file = UploadFile(filename="front.jpg", file=io.BytesIO(b"front_content"), content_type="image/jpeg")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.upload_kyc_documents(
                request_id=sample_request_id,
                current_user=sample_user,
                kyc_front=kyc_front_file,
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to update KYC information in database"
        mock_log_business_event.assert_called_once_with(
            event_type="UPLOAD_KYC_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "DB update failed"}),
            message=f"Failed to update DPAR request '{sample_request_id}' with KYC/attachment URLs in DB.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestGetPresignedUrl:
    @pytest.fixture
    def mock_minio_client(self):
        with patch("app.services.dpar_service.Minio") as mock_minio:
            mock_minio_instance = mock_minio.return_value
            yield mock_minio_instance

    async def test_get_presigned_url_success(self,
        dpa_request_service,
        mock_s3_client,
        sample_user,
        monkeypatch,
    ):
        file_url = "http://164.52.205.97:9000/test-bucket/kyc_front_123.jpg"
        mock_s3_client.presigned_get_object.return_value = "http://presigned.url/kyc_front_123.jpg"
        mock_s3_client.stat_object.return_value = None # Simulate object exists

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        result = await dpa_request_service.get_presigned_url(file_url, sample_user)

        mock_s3_client.presigned_get_object.assert_called_once()
        assert result == {"url": "http://presigned.url/kyc_front_123.jpg"}
        mock_log_business_event.assert_any_call(
            event_type="GET_PRESIGNED_URL_START",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "file_url": file_url}),
            message=f"Attempting to generate presigned URL for '{file_url}'.",
            business_logs_collection="business_logs",
        )
        mock_log_business_event.assert_any_call(
            event_type="GET_PRESIGNED_URL_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "object_key": "kyc_front_123.jpg"}),
            message=f"Successfully generated presigned URL for object 'kyc_front_123.jpg'.",
            business_logs_collection="business_logs",
        )

    async def test_get_presigned_url_failure_invalid_object_url_format(self,
        dpa_request_service,
        mock_s3_client,
        sample_user,
        monkeypatch,
    ):
        file_url = "http://invalid-url.com/missing-bucket-name.jpg"

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.get_presigned_url(file_url, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid object URL"
        mock_log_business_event.assert_called_once_with(
            event_type="GET_PRESIGNED_URL_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "file_url": file_url, "error": "Invalid object URL format"}),
            message=f"Failed to get presigned URL for '{file_url}': Invalid object URL format.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_get_presigned_url_failure_object_not_found(self,
        dpa_request_service,
        mock_s3_client,
        sample_user,
        monkeypatch,
    ):
        file_url = "http://164.52.205.97:9000/test-bucket/non_existent.jpg"
        mock_s3_client.stat_object.side_effect = Exception("Object not found") # Simulate object not found

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.get_presigned_url(file_url, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Object not found or not accessible"
        mock_log_business_event.assert_called_once_with(
            event_type="GET_PRESIGNED_URL_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "object_key": "non_existent.jpg", "error": "Object not found or not accessible"}),
            message=f"Failed to get presigned URL for 'non_existent.jpg': Object not found or not accessible.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_get_presigned_url_failure_generic_exception(self,
        dpa_request_service,
        mock_s3_client,
        sample_user,
        monkeypatch,
    ):
        file_url = "http://164.52.205.97:9000/test-bucket/error.jpg"
        mock_s3_client.stat_object.side_effect = Exception("Generic S3 error")

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.get_presigned_url(file_url, sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Generic S3 error"
        mock_log_business_event.assert_called_once_with(
            event_type="GET_PRESIGNED_URL_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "file_url": file_url, "error": "Generic S3 error"}),
            message=f"Failed to get presigned URL for '{file_url}': Generic S3 error.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestSendDparReport:
    async def test_send_dpar_report_success_core_identifier(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "core_identifier": "core@example.com", "request_conversation": []}
        
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        mock_dpar_crud.insert_report.return_value = mock_insert_result
        mock_dpar_crud.add_conversation.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        sample_dpar_report_create_payload.send_to = SendToEnum.core
        result = await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.insert_report.assert_called_once()
        mock_dpar_crud.add_conversation.assert_called_once()
        assert "report_id" in result
        assert result["recipient"] == "core@example.com"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "recipient": "core@example.com"}),
            message=f"DPAR report '{str(mock_insert_result.inserted_id)}' sent successfully for request '{sample_request_id}' to 'core@example.com'.",
            business_logs_collection="business_logs",
        )

    async def test_send_dpar_report_success_secondary_identifier(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "secondary_identifier": "secondary@example.com", "request_conversation": []}
        
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        mock_dpar_crud.insert_report.return_value = mock_insert_result
        mock_dpar_crud.add_conversation.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        sample_dpar_report_create_payload.send_to = SendToEnum.secondary
        result = await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, sample_user)

        mock_dpar_crud.get_by_id.assert_called_once_with(sample_request_id, {"df_id": sample_user["df_id"]})
        mock_dpar_crud.insert_report.assert_called_once()
        mock_dpar_crud.add_conversation.assert_called_once()
        assert "report_id" in result
        assert result["recipient"] == "secondary@example.com"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "recipient": "secondary@example.com"}),
            message=f"DPAR report '{str(mock_insert_result.inserted_id)}' sent successfully for request '{sample_request_id}' to 'secondary@example.com'.",
            business_logs_collection="business_logs",
        )

    async def test_send_dpar_report_failure_unauthorized(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        monkeypatch,
    ):
        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_FAILED",
            user_email="anonymous",
            context=AnyDictContaining({"error": "Unauthorized user"}),
            message="Unauthorized attempt to send DPAR report.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_send_dpar_report_failure_request_not_found(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = None

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, sample_user)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "DPAR request not found"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "DPAR request not found"}),
            message=f"Failed to send DPAR report for request '{sample_request_id}': Request not found.",
            log_level="WARNING",
            business_logs_collection="business_logs",
        )

    async def test_send_dpar_report_failure_recipient_not_available(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "core_identifier": None, "secondary_identifier": None}
        
        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        sample_dpar_report_create_payload.send_to = SendToEnum.core # Neither core nor secondary available
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, sample_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "core identifier not available for this request"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "send_to": "core", "error": "Recipient identifier not available"}),
            message=f"Failed to send DPAR report for request '{sample_request_id}': core identifier not available.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_send_dpar_report_failure_db_insert_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_request_id,
        sample_dpar_report_create_payload,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_by_id.return_value = {"_id": ObjectId(sample_request_id), "df_id": sample_user["df_id"], "core_identifier": "core@example.com", "request_conversation": []}
        
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = None # Simulate DB insert failure
        mock_dpar_crud.insert_report.return_value = mock_insert_result

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        sample_dpar_report_create_payload.send_to = SendToEnum.core
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.send_dpar_report(sample_request_id, sample_dpar_report_create_payload, sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Failed to send report"
        mock_log_business_event.assert_called_once_with(
            event_type="SEND_DPAR_REPORT_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "request_id": sample_request_id, "error": "Failed to insert report into DB"}),
            message=f"Failed to send DPAR report for request '{sample_request_id}': DB insert failed.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestBulkUpload:
    async def test_bulk_upload_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.insert_upload.return_value = MagicMock(acknowledged=True)
        mock_publish_message = AsyncMock()
        monkeypatch.setattr("app.services.dpar_service.publish_message", mock_publish_message)

        mock_upload_file_to_s3 = AsyncMock(return_value=("bulk_upload.csv", "http://s3.com/bulk_upload.csv"))
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        file_content = b"header1,header2\nvalue1,value2"
        upload_file = UploadFile(filename="bulk_upload.csv", file=io.BytesIO(file_content), content_type="text/csv")

        result = await dpa_request_service.bulk_upload(
            request=mock_request_details,
            file=upload_file,
            current_user=sample_user,
        )

        mock_upload_file_to_s3.assert_called_once()
        mock_dpar_crud.insert_upload.assert_called_once()
        mock_publish_message.assert_called_once()
        assert result["message"] == "DPA bulk upload initiated successfully"
        mock_log_business_event.assert_any_call(
            event_type="BULK_UPLOAD_DPAR_INITIATED_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "filename": "bulk_upload.csv"}),
            message=f"DPAR bulk upload initiated successfully for file 'bulk_upload.csv'.",
            business_logs_collection="business_logs",
        )

    async def test_bulk_upload_failure_unauthorized(self,
        dpa_request_service,
        mock_request_details,
        monkeypatch,
    ):
        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        file_content = b"header1,header2\nvalue1,value2"
        upload_file = UploadFile(filename="bulk_upload.csv", file=io.BytesIO(file_content), content_type="text/csv")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.bulk_upload(request=mock_request_details, file=upload_file, current_user={})
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_log_business_event.assert_called_once_with(
            event_type="BULK_UPLOAD_DPAR_FAILED",
            user_email="anonymous",
            context=AnyDictContaining({"error": "Unauthorized user or missing DF/Genie ID"}),
            message="Unauthorized attempt for DPAR bulk upload.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_bulk_upload_failure_unsupported_file_type(self,
        dpa_request_service,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        file_content = b"header1,header2\nvalue1,value2"
        upload_file = UploadFile(filename="bulk_upload.txt", file=io.BytesIO(file_content), content_type="text/plain")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.bulk_upload(request=mock_request_details, file=upload_file, current_user=sample_user)
        assert exc_info.value.status_code == 415
        assert exc_info.value.detail == "Unsupported file type"
        mock_log_business_event.assert_called_once_with(
            event_type="BULK_UPLOAD_DPAR_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "file_type": "txt", "error": "Unsupported file type"}),
            message=f"DPAR bulk upload failed for user {sample_user['email']}: Unsupported file type 'txt'.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_bulk_upload_failure_db_insert_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.insert_upload.side_effect = Exception("DB insert error")
        mock_publish_message = AsyncMock()
        monkeypatch.setattr("app.services.dpar_service.publish_message", mock_publish_message)

        mock_upload_file_to_s3 = AsyncMock(return_value=("bulk_upload.csv", "http://s3.com/bulk_upload.csv"))
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        file_content = b"header1,header2\nvalue1,value2"
        upload_file = UploadFile(filename="bulk_upload.csv", file=io.BytesIO(file_content), content_type="text/csv")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.bulk_upload(request=mock_request_details, file=upload_file, current_user=sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error saving upload record: DB insert error"
        mock_log_business_event.assert_any_call(
            event_type="BULK_UPLOAD_DPAR_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "filename": "bulk_upload.csv", "error": "DB insert error"}),
            message=f"DPAR bulk upload failed for file 'bulk_upload.csv': Error saving upload record: DB insert error.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )

    async def test_bulk_upload_failure_publish_message_fails(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        mock_request_details,
        monkeypatch,
    ):
        mock_dpar_crud.insert_upload.return_value = MagicMock(acknowledged=True)
        mock_publish_message = AsyncMock(side_effect=Exception("RabbitMQ error"))
        monkeypatch.setattr("app.services.dpar_service.publish_message", mock_publish_message)

        mock_upload_file_to_s3 = AsyncMock(return_value=("bulk_upload.csv", "http://s3.com/bulk_upload.csv"))
        monkeypatch.setattr(dpa_request_service, "upload_file_to_s3", mock_upload_file_to_s3)

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        file_content = b"header1,header2\nvalue1,value2"
        upload_file = UploadFile(filename="bulk_upload.csv", file=io.BytesIO(file_content), content_type="text/csv")

        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.bulk_upload(request=mock_request_details, file=upload_file, current_user=sample_user)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error processing file: RabbitMQ error"
        mock_log_business_event.assert_any_call(
            event_type="BULK_UPLOAD_DPAR_FAILED",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "filename": "bulk_upload.csv", "error": "RabbitMQ error"}),
            message=f"DPAR bulk upload failed for file 'bulk_upload.csv': Error publishing message: RabbitMQ error.",
            log_level="ERROR",
            business_logs_collection="business_logs",
        )


class TestExportRequests:
    async def test_export_requests_success(self,
        dpa_request_service,
        mock_dpar_crud,
        sample_user,
        monkeypatch,
    ):
        mock_dpar_crud.get_requests_for_export.return_value = [
            {"first_name": "John", "last_name": "Doe", "core_identifier": "john.doe@example.com", "secondary_identifier": "", "dp_type": "individual", "country": "USA", "request_type": "access", "request_message": "test"},
            {"first_name": "Jane", "last_name": "Smith", "core_identifier": "jane.smith@example.com", "secondary_identifier": "", "dp_type": "corporate", "country": "Canada", "request_type": "delete", "request_message": "test"},
        ]

        mock_log_business_event = AsyncMock()
        monkeypatch.setattr(
            "app.services.dpar_service.log_business_event", mock_log_business_event
        )

        response = await dpa_request_service.export_requests(sample_user)

        mock_dpar_crud.get_requests_for_export.assert_called_once_with(sample_user["df_id"], EXPORT_FIELDS)
        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/csv"
        assert "attachment; filename=dpar_export_" in response.headers["Content-Disposition"]

        async for chunk in response.body_iterator:
            content = chunk.decode()
            break

        expected_header = ",".join(EXPORT_FIELDS)
        expected_row1 = "John,Doe,john.doe@example.com,,individual,USA,access,test"
        expected_row2 = "Jane,Smith,jane.smith@example.com,,corporate,Canada,delete,test"

        assert expected_header in content
        assert expected_row1 in content
        assert expected_row2 in content

        mock_log_business_event.assert_called_once_with(
            event_type="EXPORT_DPAR_REQUESTS_SUCCESS",
            user_email=sample_user["email"],
            context=AnyDictContaining({"df_id": sample_user["df_id"], "num_requests_exported": 2}),
            message=AnyDictContaining("DPAR requests exported successfully"),
            business_logs_collection="business_logs",
        )

    async def test_export_requests_failure_unauthorized(self,
        dpa_request_service,
        mock_dpar_crud,
        monkeypatch,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await dpa_request_service.export_requests(None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_dpar_crud.get_requests_for_export.assert_not_called()
