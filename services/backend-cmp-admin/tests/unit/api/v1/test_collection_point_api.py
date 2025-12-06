import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.main import app
from app.api.v1.deps import get_current_user, get_cp_service, get_s3_client
from minio import Minio

client = TestClient(app)
BASE_URL = "/api/v1/cp"


# ---------------- FIXTURES ---------------- #


@pytest.fixture
def mock_user():
    return {"_id": "u1", "email": "test@example.com", "df_id": "df123"}


def collection_point_response():
    """Return a complete schema-valid CpResponse dict."""
    return {
        "_id": "cp1",
        "cp_name": "Test CP",
        "cp_description": "Description",
        "cp_type": "new",
        "notice_type": "single",
        "cp_status": "draft",
        "redirection_url": "https://example.com/redirect",
        "fallback_url": None,
        "default_language": "English",
        "asset_id": "a1",
        "is_verification_required": False,
        "verification_done_by": None,
        "prefered_verification_medium": None,
        "notice_popup_window_timeout": None,
        "data_elements": [],
        "notice_url": "",
        "is_translation_done": False,
        "notice_html": "<html></html>",
        "df_id": "df123",
        "created_at": "2025-01-01T00:00:00Z",
        "created_at_by": "u1",
        "updated_at": None,
        "updated_by": None,
        "translated_audio": [],
    }


@pytest.fixture
def mock_service():
    service = MagicMock()
    service.create_collection_point = AsyncMock()
    service.update_collection_point = AsyncMock()
    service.publish_collection_point = AsyncMock()
    service.get_all_collection_points = AsyncMock()
    service.get_collection_point = AsyncMock()
    service.delete_collection_point = AsyncMock()
    service.upload_audio_to_minio = AsyncMock()
    service.delete_audio_from_minio = AsyncMock()
    service.get_audio_file = AsyncMock()
    return service


@pytest.fixture
def mock_s3_client():
    client = MagicMock(spec=Minio)
    return client


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_service, mock_s3_client):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_cp_service] = lambda: mock_service
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client
    yield
    app.dependency_overrides = {}


# ---------------- TEST CREATE COLLECTION POINT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, collection_point_response(), 200),
        (HTTPException(status_code=409, detail="duplicate"), None, 409),
        (Exception("boom"), None, 500),
    ],
)
def test_create_collection_point(mock_service, side_effect, return_value, expected_status):
    mock_service.create_collection_point.side_effect = side_effect
    mock_service.create_collection_point.return_value = return_value

    body = {
        "cp_name": "Test CP",
        "redirection_url": "https://example.com/redirect",
        "asset_id": "a1",
    }
    res = client.post(f"{BASE_URL}/create-collection-point", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["cp_id"] == "cp1"
        mock_service.create_collection_point.assert_called_once()
    else:
        assert "detail" in res.json()


def test_create_collection_point_validation_error():
    res = client.post(f"{BASE_URL}/create-collection-point", json={"wrong_field": "value"})
    assert res.status_code == 422


# ---------------- TEST UPDATE COLLECTION POINT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status, body",
    [
        (None, collection_point_response(), 200, {"cp_name": "Updated CP"}),
        (None, None, 404, {"cp_name": "NewName"}),
        (HTTPException(status_code=400, detail="bad"), None, 400, {"cp_name": "NewName"}),
        (Exception("boom"), None, 500, {"cp_name": "NewName"}),
        (None, None, 404, {"redirection_url": "http://new.url"}), # Adding a specific 404 case for valid body
    ],
)
def test_update_collection_point(mock_service, side_effect, return_value, expected_status, body):
    if return_value:
        temp_return_value = collection_point_response()
        temp_return_value.update(return_value)
        temp_return_value["cp_name"] = body.get("cp_name", temp_return_value["cp_name"])
        mock_service.update_collection_point.return_value = temp_return_value
    else:
        mock_service.update_collection_point.return_value = None

    mock_service.update_collection_point.side_effect = side_effect

    res = client.put(f"{BASE_URL}/update-cp/cp1", json=body)

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["cp_id"] == "cp1"
        mock_service.update_collection_point.assert_called_once()
    else:
        assert "detail" in res.json()


def test_update_collection_point_invalid_body():
    res = client.put(f"{BASE_URL}/update-cp/cp1", json={"redirection_url": 12345})
    assert res.status_code == 422


# ---------------- TEST PUBLISH COLLECTION POINT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**collection_point_response(), "cp_status": "published"}, 200),
        (HTTPException(status_code=404, detail="not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_publish_collection_point(mock_service, side_effect, return_value, expected_status):
    mock_service.publish_collection_point.side_effect = side_effect
    mock_service.publish_collection_point.return_value = return_value

    res = client.patch(f"{BASE_URL}/publish-cp/cp1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["cp_status"] == "published"
    else:
        assert "detail" in res.json()


# ---------------- TEST GET ALL COLLECTION POINTS ---------------- #


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
                "collection_points": [collection_point_response()],
            },
            200,
        ),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_all_collection_points(mock_service, side_effect, return_value, expected_status):
    mock_service.get_all_collection_points.side_effect = side_effect
    mock_service.get_all_collection_points.return_value = return_value

    res = client.get(f"{BASE_URL}/get-all-cps")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["collection_points"][0]["cp_id"] == "cp1"
    else:
        assert "detail" in res.json()


def test_get_all_collection_points_invalid_query():
    res = client.get(f"{BASE_URL}/get-all-cps?current_page=0")
    assert res.status_code == 422


# ---------------- TEST GET COLLECTION POINT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, collection_point_response(), 200),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_get_collection_point(mock_service, side_effect, return_value, expected_status):
    mock_service.get_collection_point.side_effect = side_effect
    mock_service.get_collection_point.return_value = return_value

    res = client.get(f"{BASE_URL}/get-cp/cp1")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["cp_id"] == "cp1"
    else:
        assert "detail" in res.json()


# ---------------- TEST DELETE COLLECTION POINT ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, {**collection_point_response(), "cp_status": "archived"}, 204),
        (None, None, 404),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_collection_point(mock_service, side_effect, return_value, expected_status):
    mock_service.delete_collection_point.side_effect = side_effect
    mock_service.delete_collection_point.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-cp/cp1")

    assert res.status_code == expected_status
    if expected_status == 204:
        mock_service.delete_collection_point.assert_called_once()
    else:
        assert "detail" in res.json()


# ---------------- TEST UPLOAD AUDIO ---------------- #
from unittest.mock import patch, mock_open

@pytest.mark.parametrize(
    "side_effect, service_return_value, expected_status, content_type",
    [
        (None, "http://test.com/audio.mp3", 200, "audio/mpeg"),
        (HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed."), None, 400, "image/jpeg"),
        (Exception("boom"), None, 500, "audio/mpeg"),
    ],
)
def test_upload_audio(mock_service, side_effect, service_return_value, expected_status, content_type):
    mock_service.upload_audio_to_minio.side_effect = side_effect
    mock_service.upload_audio_to_minio.return_value = service_return_value

    # Create a dummy audio file for testing
    file_content = b"dummy audio data"

    res = client.post(
        f"{BASE_URL}/upload-audio",
        files={"file": ("audio.mp3", file_content, content_type)},
    )

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json() == {"audio_url": "http://test.com/audio.mp3"}
        mock_service.upload_audio_to_minio.assert_called_once()
    else:
        assert "detail" in res.json()


# ---------------- TEST DELETE AUDIO ---------------- #


@pytest.mark.parametrize(
    "side_effect, return_value, expected_status",
    [
        (None, True, 204),
        (None, False, 404),
        (HTTPException(status_code=400, detail="bad"), None, 400),
        (Exception("boom"), None, 500),
    ],
)
def test_delete_audio(mock_service, side_effect, return_value, expected_status):
    mock_service.delete_audio_from_minio.side_effect = side_effect
    mock_service.delete_audio_from_minio.return_value = return_value

    res = client.delete(f"{BASE_URL}/delete-audio/audio.mp3")

    assert res.status_code == expected_status
    if expected_status == 204:
        mock_service.delete_audio_from_minio.assert_called_once()
    else:
        assert "detail" in res.json()


# ---------------- TEST GET AUDIO ---------------- #

from minio.datatypes import Object

@pytest.fixture
def mock_minio_get_object_response():
    # Minio's get_object returns a GetObjectResponse which is file-like
    mock_response = MagicMock()
    mock_response.stream.return_value = [b"chunk1", b"chunk2"]
    mock_response.close.return_value = None
    mock_response.release_conn.return_value = None
    return mock_response


@pytest.mark.parametrize(
    "side_effect, service_return_value, expected_status",
    [
        (None, "mock_minio_get_object_response", 200),
        (HTTPException(status_code=404, detail="Audio file not found"), None, 404),
        (Exception("boom"), None, 500),
    ],
)
def test_get_audio(mock_service, mock_minio_get_object_response, side_effect, service_return_value, expected_status):
    if service_return_value == "mock_minio_get_object_response":
        mock_service.get_audio_file.return_value = mock_minio_get_object_response
    else:
        mock_service.get_audio_file.return_value = service_return_value
    mock_service.get_audio_file.side_effect = side_effect

    res = client.get(f"{BASE_URL}/get-audio/audio.mp3")

    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.content == b"chunk1chunk2"
        mock_service.get_audio_file.assert_called_once()
    else:
        assert "detail" in res.json()
