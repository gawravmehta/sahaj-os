import pytest
from unittest.mock import MagicMock, AsyncMock
import json
import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from bson import ObjectId

from app.services.consent_audit_service import ConsentAuditService
from app.crud.consent_audit_crud import ConsentAuditCRUD


@pytest.fixture
def private_key():
    return ec.generate_private_key(ec.SECP256R1(), default_backend())


@pytest.fixture
def public_key_pem(private_key):
    return (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )


@pytest.fixture
def mock_consent_audit_crud():
    return MagicMock(spec=ConsentAuditCRUD)


@pytest.fixture
def consent_audit_service(mock_consent_audit_crud, public_key_pem):
    return ConsentAuditService(crud=mock_consent_audit_crud, public_key_pem=public_key_pem)


@pytest.fixture
def current_user_data():
    return {"df_id": "df123", "email": "test@example.com"}


def sign_record(private_key, record_hash: str) -> str:
    signature = private_key.sign(record_hash.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode()


@pytest.fixture
def generate_valid_log_entry(private_key):
    def _generator(dp_id, df_id, timestamp_str, data_content, prev_record_hash=None):
        clean_record = {
            "dp_id": dp_id,
            "df_id": df_id,
            "timestamp": timestamp_str,
            "data": data_content,
        }
        canonical = json.dumps(clean_record, sort_keys=True, separators=(",", ":"))
        data_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        record_hash_input = (prev_record_hash or "") + data_hash + timestamp_str
        record_hash = hashlib.sha256(record_hash_input.encode("utf-8")).hexdigest()

        signature = sign_record(private_key, record_hash)

        return {
            "_id": str(ObjectId()),
            "dp_id": dp_id,
            "df_id": df_id,
            "timestamp": timestamp_str,
            "data": data_content,
            "data_hash": data_hash,
            "prev_record_hash": prev_record_hash,
            "record_hash": record_hash,
            "signature": signature,
            "signed_with_key_id": "test_key_id",
        }

    return _generator


@pytest.fixture
def generate_tampered_log_entry(private_key, generate_valid_log_entry):
    def _generator(dp_id, df_id, timestamp_str, data_content, prev_record_hash=None, tamper_type="data"):
        valid_log = generate_valid_log_entry(dp_id, df_id, timestamp_str, data_content, prev_record_hash)

        if tamper_type == "data":
            valid_log["data"]["tampered_field"] = "malicious_data"
            canonical = json.dumps(valid_log, sort_keys=True, separators=(",", ":"))
            valid_log["data_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        elif tamper_type == "chain":
            valid_log["prev_record_hash"] = "tampered_prev_hash"
        elif tamper_type == "signature":
            valid_log["signature"] = sign_record(private_key, "fake_hash")

        if tamper_type == "data":

            pass
        elif tamper_type == "signature":

            valid_log["signature"] = sign_record(private_key, "some_other_hash")

        return valid_log

    return _generator


@pytest.mark.asyncio
async def test_get_dp_audit_history_success_single_log(
    consent_audit_service, mock_consent_audit_crud, current_user_data, generate_valid_log_entry, monkeypatch
):
    dp_id = "dp1"
    timestamp = datetime.now().isoformat()
    log_entry = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp, {"action": "consent_given"})

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [log_entry]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    monkeypatch.setattr(consent_audit_service, "_verify_signature", MagicMock(return_value=True))

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    mock_consent_audit_crud.get_logs.assert_called_once_with(dp_id, current_user_data["df_id"])
    assert len(result) == 1
    assert result[0]["dp_id"] == dp_id
    assert result[0]["tampered"] is False
    assert result[0]["integrity"]["data_hash_ok"] is True
    assert result[0]["integrity"]["chain_ok"] is True
    assert result[0]["integrity"]["signature_ok"] is True


@pytest.mark.asyncio
async def test_get_dp_audit_history_success_chained_logs(
    consent_audit_service, mock_consent_audit_crud, current_user_data, generate_valid_log_entry, monkeypatch
):
    dp_id = "dp1"
    timestamp1 = datetime.now().isoformat()
    log1 = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp1, {"action": "consent_given"})

    timestamp2 = datetime.now().isoformat()
    log2 = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp2, {"action": "data_processed"}, prev_record_hash=log1["record_hash"])

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [log1, log2]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    monkeypatch.setattr(consent_audit_service, "_verify_signature", MagicMock(return_value=True))

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    assert len(result) == 2
    assert result[0]["tampered"] is False
    assert result[1]["tampered"] is False
    assert result[1]["integrity"]["chain_ok"] is True


@pytest.mark.asyncio
async def test_get_dp_audit_history_tampered_data(
    consent_audit_service, mock_consent_audit_crud, current_user_data, generate_valid_log_entry, monkeypatch
):
    dp_id = "dp1"
    timestamp = datetime.now().isoformat()
    log_entry = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp, {"action": "consent_given"})

    tampered_log = log_entry.copy()
    tampered_log["data_hash"] = "a_fake_data_hash"

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [tampered_log]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    monkeypatch.setattr(consent_audit_service, "_verify_signature", MagicMock(return_value=True))

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    assert len(result) == 1
    assert result[0]["tampered"] is True
    assert result[0]["integrity"]["data_hash_ok"] is False
    assert result[0]["integrity"]["chain_ok"] is False
    assert result[0]["integrity"]["signature_ok"] is True


@pytest.mark.asyncio
async def test_get_dp_audit_history_tampered_chain(
    consent_audit_service, mock_consent_audit_crud, current_user_data, generate_valid_log_entry, monkeypatch
):
    dp_id = "dp1"
    timestamp = datetime.now().isoformat()
    log1 = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp, {"action": "consent_given"})

    timestamp2 = datetime.now().isoformat()
    log2 = generate_valid_log_entry(
        dp_id, current_user_data["df_id"], timestamp2, {"action": "data_processed"}, prev_record_hash="tampered_prev_hash"
    )

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [log1, log2]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    monkeypatch.setattr(consent_audit_service, "_verify_signature", MagicMock(return_value=True))

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    assert len(result) == 2
    assert result[0]["tampered"] is False
    assert result[1]["tampered"] is True
    assert result[1]["integrity"]["chain_ok"] is False


@pytest.mark.asyncio
async def test_get_dp_audit_history_tampered_signature(
    consent_audit_service, mock_consent_audit_crud, current_user_data, generate_valid_log_entry, monkeypatch
):
    dp_id = "dp1"
    timestamp = datetime.now().isoformat()
    log_entry = generate_valid_log_entry(dp_id, current_user_data["df_id"], timestamp, {"action": "consent_given"})

    tampered_log = log_entry.copy()
    tampered_log["signature"] = base64.b64encode(b"invalid_signature_bytes").decode()

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [tampered_log]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    assert len(result) == 1
    assert result[0]["tampered"] is True
    assert result[0]["integrity"]["signature_ok"] is False


@pytest.mark.asyncio
async def test_get_dp_audit_history_empty_logs(consent_audit_service, mock_consent_audit_crud, current_user_data):
    dp_id = "dp1"

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = []
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    result = await consent_audit_service.get_dp_audit_history(dp_id, current_user_data)

    mock_consent_audit_crud.get_logs.assert_called_once_with(dp_id, current_user_data["df_id"])
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_dp_audit_history_internal_success(consent_audit_service, mock_consent_audit_crud, generate_valid_log_entry, monkeypatch):
    dp_id = "dp1"
    df_id = "df123"
    timestamp = datetime.now().isoformat()
    log_entry = generate_valid_log_entry(dp_id, df_id, timestamp, {"action": "consent_given"})

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [log_entry]
    mock_consent_audit_crud.get_logs.return_value = mock_cursor

    monkeypatch.setattr(consent_audit_service, "_verify_signature", MagicMock(return_value=True))

    result = await consent_audit_service.get_dp_audit_history_internal(dp_id, df_id)

    mock_consent_audit_crud.get_logs.assert_called_once_with(dp_id, df_id)
    assert len(result) == 1
    assert result[0]["dp_id"] == dp_id
    assert result[0]["tampered"] is False
    assert result[0]["integrity"]["data_hash_ok"] is True
    assert result[0]["integrity"]["chain_ok"] is True
    assert result[0]["integrity"]["signature_ok"] is True


@pytest.mark.asyncio
async def test_sha256_method(consent_audit_service):
    test_string = "hello_world"
    expected_hash = hashlib.sha256(test_string.encode("utf-8")).hexdigest()
    assert consent_audit_service._sha256(test_string) == expected_hash


@pytest.mark.asyncio
async def test_verify_signature_method_valid(consent_audit_service, private_key):
    record_hash = "some_hash"
    signature = sign_record(private_key, record_hash)
    assert consent_audit_service._verify_signature(record_hash, signature) is True


@pytest.mark.asyncio
async def test_verify_signature_method_invalid(consent_audit_service, private_key):
    record_hash = "some_hash"
    invalid_signature = sign_record(private_key, "different_hash")
    assert consent_audit_service._verify_signature(record_hash, invalid_signature) is False


@pytest.mark.asyncio
async def test_verify_signature_method_bad_format(consent_audit_service):
    record_hash = "some_hash"
    bad_format_signature = "not-base64-encoded"
    assert consent_audit_service._verify_signature(record_hash, bad_format_signature) is False
