import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException, status
from io import BytesIO
from minio import Minio

from app.services.collection_point_service import CollectionPointService
from app.crud.collection_point_crud import CollectionPointCrud
from app.services.data_element_service import DataElementService
from app.services.purpose_service import PurposeService
from app.services.notice_service import NoticeService
from app.services.data_fiduciary_service import DataFiduciaryService


@pytest.fixture
def mock_collection_point_crud():
    return MagicMock(spec=CollectionPointCrud)


@pytest.fixture
def mock_data_element_service():
    return MagicMock(spec=DataElementService)


@pytest.fixture
def mock_purpose_service():
    return MagicMock(spec=PurposeService)


@pytest.fixture
def mock_notice_service():
    return MagicMock(spec=NoticeService)


@pytest.fixture
def mock_data_fiduciary_service():
    return MagicMock(spec=DataFiduciaryService)


@pytest.fixture
def mock_minio_client():
    return MagicMock(spec=Minio)


@pytest.fixture
def collection_point_service(
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
):
    return CollectionPointService(
        crud=mock_collection_point_crud,
        data_element_service=mock_data_element_service,
        purpose_service=mock_purpose_service,
        notice_service=mock_notice_service,
        data_fiduciary_service=mock_data_fiduciary_service,
        business_logs_collection="test_logs",
    )


@pytest.fixture
def user_data():
    return {"_id": "user1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def cp_data_draft():
    return {
        "cp_name": "Test CP Draft",
        "asset_id": "asset123",
        "cp_type": "new",
        "cp_status": "draft",
        "notice_type": "single",
        "redirection_url": "https://example.com/redirect",
        "data_elements": [
            {
                "de_id": "de1",
                "purposes": [{"purpose_id": "p1"}],
            }
        ],
    }


@pytest.fixture
def cp_data_published():
    return {
        "cp_name": "Test CP Published",
        "asset_id": "asset123",
        "cp_type": "new",
        "cp_status": "published",
        "notice_type": "single",
        "redirection_url": "https://example.com/redirect",
        "data_elements": [
            {
                "de_id": "de1",
                "purposes": [{"purpose_id": "p1"}],
            }
        ],
    }


@pytest.fixture
def enriched_de_purpose_data():
    return [
        {
            "de_obj": {"_id": "de1", "de_name": "DE1", "de_status": "published", "translations": {"en": "DE1"}},
            "purposes": [{"_id": "p1", "purpose_title": "P1", "purpose_status": "published", "translations": {"en": "P1"}}],
        }
    ]


@pytest.mark.asyncio
async def test_create_collection_point_draft_success(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
    user_data,
    cp_data_draft,
    enriched_de_purpose_data,
    monkeypatch,
):
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_data_element_service.get_data_element.return_value = enriched_de_purpose_data[0]["de_obj"]
    mock_purpose_service.get_purpose.return_value = enriched_de_purpose_data[0]["purposes"][0]
    mock_data_fiduciary_service.get_df_name.return_value = "Test DF"
    mock_notice_service.build_notice_data.return_value = {"html": "mock_html"}
    mock_notice_service.render_html.return_value = "<html>Mock Notice</html>"
    mock_collection_point_crud.create_cp.return_value = {"_id": "new_cp_id", **cp_data_draft}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.create_collection_point(cp_data_draft.copy(), user_data)

    mock_collection_point_crud.is_duplicate_name.assert_called_once_with(cp_name="Test CP Draft", asset_id="asset123", df_id="df123")
    mock_data_element_service.get_data_element.assert_called_once_with("de1", user_data, for_system=True)
    mock_purpose_service.get_purpose.assert_called_once_with("p1", user_data, for_system=True)
    mock_notice_service.build_notice_data.assert_called_once()
    mock_notice_service.render_html.assert_called_once()
    mock_collection_point_crud.create_cp.assert_called_once()
    mock_log.assert_called_once()
    assert result["_id"] == "new_cp_id"
    assert result["cp_name"] == "Test CP Draft"


@pytest.mark.asyncio
async def test_create_collection_point_published_success(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
    user_data,
    cp_data_published,
    enriched_de_purpose_data,
    monkeypatch,
):
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_data_element_service.get_data_element.return_value = enriched_de_purpose_data[0]["de_obj"]
    mock_purpose_service.get_purpose.return_value = enriched_de_purpose_data[0]["purposes"][0]
    mock_data_fiduciary_service.get_df_name.return_value = "Test DF"
    mock_notice_service.build_notice_data.return_value = {"html": "mock_html"}
    mock_notice_service.render_html.return_value = "<html>Mock Notice</html>"
    mock_collection_point_crud.create_cp.return_value = {"_id": "new_cp_id", **cp_data_published}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.create_collection_point(cp_data_published.copy(), user_data)

    mock_collection_point_crud.is_duplicate_name.assert_called_once_with(cp_name="Test CP Published", asset_id="asset123", df_id="df123")
    mock_data_element_service.get_data_element.assert_called_once_with("de1", user_data, for_system=True)
    mock_purpose_service.get_purpose.assert_called_once_with("p1", user_data, for_system=True)
    mock_notice_service.build_notice_data.assert_called_once()
    mock_notice_service.render_html.assert_called_once()
    mock_collection_point_crud.create_cp.assert_called_once()
    mock_log.assert_called_once()
    assert result["_id"] == "new_cp_id"
    assert result["cp_name"] == "Test CP Published"


@pytest.mark.asyncio
async def test_create_collection_point_duplicate_name(collection_point_service, mock_collection_point_crud, user_data, cp_data_draft):
    mock_collection_point_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.create_collection_point(cp_data_draft, user_data)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "A Collection Point with the same name already exists."
    mock_collection_point_crud.create_cp.assert_not_called()


@pytest.mark.asyncio
async def test_create_collection_point_published_validation_failure(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    user_data,
    cp_data_published,
    monkeypatch,
):
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_data_element_service.get_data_element.return_value = {
        "_id": "de1",
        "de_name": "DE1",
        "de_status": "draft",
        "translations": {"en": "DE1"},
    }
    mock_purpose_service.get_purpose.return_value = {
        "_id": "p1",
        "purpose_title": "P1",
        "purpose_status": "published",
        "translations": {"en": "P1"},
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.create_collection_point(cp_data_published.copy(), user_data)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "not_published" in exc.value.detail
    assert exc.value.detail["not_published"]["data_elements"][0]["de_id"] == "de1"
    mock_collection_point_crud.create_cp.assert_not_called()


@pytest.mark.asyncio
async def test_publish_collection_point_success(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
    mock_minio_client,
    user_data,
    enriched_de_purpose_data,
    monkeypatch,
):
    cp_id = "existing_cp_id"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Existing CP",
        "asset_id": "asset123",
        "cp_status": "draft",
        "notice_type": "single",
        "data_elements": [{"de_id": "de1", "purposes": [{"purpose_id": "p1"}]}],
        "translated_audio": [],
    }

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_data_element_service.get_data_element.return_value = enriched_de_purpose_data[0]["de_obj"]
    mock_purpose_service.get_purpose.return_value = enriched_de_purpose_data[0]["purposes"][0]
    mock_data_fiduciary_service.get_df_name.return_value = "Test DF"
    mock_notice_service.build_notice_data.return_value = {"html": "mock_html"}
    mock_notice_service.render_html.return_value = "<html>Mock Notice HTML</html>"
    mock_minio_client.put_object = MagicMock()
    mock_minio_client.presigned_get_object.return_value = "http://minio/notice.html"
    mock_collection_point_crud.update_cp_by_id.return_value = {
        **existing_cp,
        "cp_status": "published",
        "notice_url": "http://minio/notice.html",
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")

    result = await collection_point_service.publish_collection_point(cp_id, user_data, mock_minio_client)

    mock_collection_point_crud.get_cp_master.assert_called_once_with(cp_id, "df123")
    mock_notice_service.build_notice_data.assert_called_once()
    mock_notice_service.render_html.assert_called_once()
    mock_minio_client.put_object.assert_called_once()
    mock_minio_client.presigned_get_object.assert_called_once()
    mock_collection_point_crud.update_cp_by_id.assert_called_once()
    mock_log.assert_called_once()
    assert result["cp_status"] == "published"
    assert result["notice_url"] == "http://minio/notice.html"


@pytest.mark.asyncio
async def test_publish_collection_point_not_found(collection_point_service, mock_collection_point_crud, user_data, mock_minio_client):
    mock_collection_point_crud.get_cp_master.return_value = None

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.publish_collection_point("non_existent_id", user_data, mock_minio_client)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.detail


@pytest.mark.asyncio
async def test_publish_collection_point_already_published(collection_point_service, mock_collection_point_crud, user_data, mock_minio_client):
    existing_cp = {"_id": "cp1", "cp_status": "published"}
    mock_collection_point_crud.get_cp_master.return_value = existing_cp

    result = await collection_point_service.publish_collection_point("cp1", user_data, mock_minio_client)

    assert result == existing_cp
    mock_collection_point_crud.update_cp_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_publish_collection_point_validation_failure(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    user_data,
    mock_minio_client,
    monkeypatch,
):
    cp_id = "existing_cp_id"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Existing CP",
        "asset_id": "asset123",
        "cp_status": "draft",
        "notice_type": "single",
        "data_elements": [{"de_id": "de1", "purposes": [{"purpose_id": "p1"}]}],
        "translated_audio": [],
    }

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_data_element_service.get_data_element.return_value = {
        "_id": "de1",
        "de_name": "DE1",
        "de_status": "draft",
        "translations": {"en": "DE1"},
    }
    mock_purpose_service.get_purpose.return_value = {
        "_id": "p1",
        "purpose_title": "P1",
        "purpose_status": "published",
        "translations": {"en": "P1"},
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.publish_collection_point(cp_id, user_data, mock_minio_client)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "not_published" in exc.value.detail
    mock_collection_point_crud.update_cp_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_update_collection_point_success_name_only(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    cp_id = "cp1"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Original Name",
        "asset_id": "asset123",
        "df_id": user_data["df_id"],
        "cp_status": "draft",
        "data_elements": [],
    }
    update_data = {"cp_name": "New Name"}

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_collection_point_crud.update_cp_by_id.side_effect = lambda cp_id, df_id, data: {**existing_cp, **data}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.update_collection_point(cp_id, update_data, user_data)

    mock_collection_point_crud.get_cp_master.assert_called_once_with(cp_id, user_data["df_id"])
    mock_collection_point_crud.is_duplicate_name.assert_called_once_with(cp_name="New Name", asset_id="asset123", df_id="df123")
    mock_collection_point_crud.update_cp_by_id.assert_called_once()
    mock_log.assert_called_once()
    assert result["cp_name"] == "New Name"


@pytest.mark.asyncio
async def test_update_collection_point_not_found(collection_point_service, mock_collection_point_crud, user_data):
    mock_collection_point_crud.get_cp_master.return_value = None

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.update_collection_point("non_existent_id", {"cp_name": "New"}, user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_collection_point_duplicate_name(collection_point_service, mock_collection_point_crud, user_data):
    cp_id = "cp1"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Original Name",
        "asset_id": "asset123",
        "df_id": user_data["df_id"],
        "cp_status": "draft",
    }
    update_data = {"cp_name": "Existing Name"}

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_collection_point_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.update_collection_point(cp_id, update_data, user_data)

    assert exc.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_update_collection_point_data_elements_and_publish_success(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
    user_data,
    enriched_de_purpose_data,
    monkeypatch,
):
    cp_id = "cp1"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Original Name",
        "asset_id": "asset123",
        "df_id": user_data["df_id"],
        "cp_status": "draft",
        "data_elements": [],
        "translated_audio": [],
    }
    update_data = {
        "cp_status": "published",
        "data_elements": [{"de_id": "de1", "purposes": [{"purpose_id": "p1"}]}],
    }

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_data_element_service.get_data_element.return_value = enriched_de_purpose_data[0]["de_obj"]
    mock_purpose_service.get_purpose.return_value = enriched_de_purpose_data[0]["purposes"][0]
    mock_data_fiduciary_service.get_df_name.return_value = "Test DF"
    mock_notice_service.build_notice_data.return_value = {"html": "mock_html"}
    mock_notice_service.render_html.return_value = "<html>Updated Notice HTML</html>"
    mock_collection_point_crud.update_cp_by_id.side_effect = lambda cp_id, df_id, data: {**existing_cp, **data}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.update_collection_point(cp_id, update_data.copy(), user_data)

    mock_data_element_service.get_data_element.assert_called_once()
    mock_purpose_service.get_purpose.assert_called_once()
    mock_notice_service.build_notice_data.assert_called_once()
    mock_notice_service.render_html.assert_called_once()
    mock_collection_point_crud.update_cp_by_id.assert_called_once()
    mock_log.assert_called_once()
    assert result["cp_status"] == "published"
    assert "notice_html" in result


@pytest.mark.asyncio
async def test_update_collection_point_notice_type_only(
    collection_point_service,
    mock_collection_point_crud,
    mock_data_element_service,
    mock_purpose_service,
    mock_notice_service,
    mock_data_fiduciary_service,
    user_data,
    monkeypatch,
):
    cp_id = "cp1"
    existing_cp = {
        "_id": cp_id,
        "cp_name": "Original Name",
        "asset_id": "asset123",
        "df_id": user_data["df_id"],
        "cp_status": "draft",
        "data_elements": [{"de_id": "de1", "purposes": [{"purpose_id": "p1"}]}],
        "translated_audio": [],
        "notice_type": "single",
    }
    update_data = {"notice_type": "layered"}

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_collection_point_crud.is_duplicate_name.return_value = False
    mock_data_element_service.get_data_element.return_value = {
        "_id": "de1",
        "de_name": "DE1",
        "de_status": "published",
        "translations": {"en": "DE1"},
    }
    mock_purpose_service.get_purpose.return_value = {
        "_id": "p1",
        "purpose_title": "P1",
        "purpose_status": "published",
        "translations": {"en": "P1"},
    }
    mock_data_fiduciary_service.get_df_name.return_value = "Test DF"
    mock_notice_service.build_notice_data.return_value = {"html": "mock_html"}
    mock_notice_service.render_html.return_value = "<html>New Notice Type HTML</html>"
    mock_collection_point_crud.update_cp_by_id.side_effect = lambda cp_id, df_id, data: {**existing_cp, **data}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.update_collection_point(cp_id, update_data.copy(), user_data)

    mock_notice_service.render_html.assert_called_once_with({"html": "mock_html"}, df_name="Test DF", notice_type="layered")
    assert result["notice_type"] == "layered"
    assert "notice_html" in result


@pytest.mark.asyncio
async def test_get_all_collection_points_success(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    mock_collection_point_crud.get_all_cps.return_value = {"data": [{"_id": "cp1"}, {"_id": "cp2"}], "total": 2}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.get_all_collection_points(user_data, current_page=1, data_per_page=2)

    mock_collection_point_crud.get_all_cps.assert_called_once_with(df_id="df123", offset=0, limit=2, additional_filters={})
    mock_log.assert_called_once()
    assert result["total_items"] == 2
    assert result["collection_points"][0]["_id"] == "cp1"


@pytest.mark.asyncio
async def test_get_all_collection_points_with_filters(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    mock_collection_point_crud.get_all_cps.return_value = {"data": [{"_id": "cp1"}], "total": 1}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.get_all_collection_points(user_data, current_page=1, data_per_page=10, is_legacy=True, is_published=True)

    mock_collection_point_crud.get_all_cps.assert_called_once_with(
        df_id="df123", offset=0, limit=10, additional_filters={"cp_type": "legacy", "cp_status": "published"}
    )
    assert result["total_items"] == 1


@pytest.mark.asyncio
async def test_get_collection_point_success(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    cp_id = "cp1"
    existing_cp = {"_id": cp_id, "cp_name": "Test CP"}
    mock_collection_point_crud.get_cp_master.return_value = existing_cp

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.get_collection_point(cp_id, user_data)

    mock_collection_point_crud.get_cp_master.assert_called_once_with(cp_id, user_data["df_id"])
    mock_log.assert_called_once()
    assert result == existing_cp


@pytest.mark.asyncio
async def test_get_collection_point_not_found(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    mock_collection_point_crud.get_cp_master.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.get_collection_point("non_existent", user_data)

    assert result is None
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_delete_collection_point_success(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    cp_id = "cp1"
    existing_cp = {"_id": cp_id, "cp_name": "Test CP", "cp_status": "draft"}
    updated_cp = {**existing_cp, "cp_status": "archived"}

    mock_collection_point_crud.get_cp_master.return_value = existing_cp
    mock_collection_point_crud.update_cp_by_id.return_value = updated_cp

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result = await collection_point_service.delete_collection_point(cp_id, user_data)

    mock_collection_point_crud.get_cp_master.assert_called_once_with(cp_id, user_data["df_id"])
    mock_collection_point_crud.update_cp_by_id.assert_called_once()
    mock_log.assert_called_once()
    assert result["cp_status"] == "archived"


@pytest.mark.asyncio
async def test_delete_collection_point_not_found_or_archived(collection_point_service, mock_collection_point_crud, user_data, monkeypatch):
    mock_collection_point_crud.get_cp_master.side_effect = [
        None,
        {"_id": "cp2", "cp_status": "archived"},
    ]

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.collection_point_service.log_business_event", mock_log)

    result1 = await collection_point_service.delete_collection_point("non_existent", user_data)
    assert result1 is None
    mock_collection_point_crud.update_cp_by_id.assert_not_called()
    mock_log.assert_not_called()

    mock_log.reset_mock()

    result2 = await collection_point_service.delete_collection_point("cp2", user_data)
    assert result2 is None
    mock_collection_point_crud.update_cp_by_id.assert_not_called()
    mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_upload_audio_to_minio_success(collection_point_service, mock_minio_client, monkeypatch):
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")
    monkeypatch.setattr("app.services.collection_point_service.settings.CMP_ADMIN_BACKEND_URL", "http://backend")
    monkeypatch.setattr("uuid.uuid4", lambda: "test-uuid")

    file_content = b"audio_data"
    content_type = "audio/mp3"
    file_extension = "mp3"

    mock_minio_client.put_object = MagicMock()

    result_url = await collection_point_service.upload_audio_to_minio(mock_minio_client, file_content, content_type, file_extension)

    expected_object_name = "audio/test-uuid.mp3"
    mock_minio_client.put_object.assert_called_once()
    assert expected_object_name in mock_minio_client.put_object.call_args.kwargs["object_name"]
    assert result_url == "http://backend/api/v1/cp/get-audio/test-uuid.mp3"


@pytest.mark.asyncio
async def test_get_audio_file_success(collection_point_service, mock_minio_client, monkeypatch):
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")
    filename = "test-uuid.mp3"
    mock_response = MagicMock()
    mock_minio_client.get_object.return_value = mock_response

    result = await collection_point_service.get_audio_file(mock_minio_client, filename)

    mock_minio_client.get_object.assert_called_once_with("test-bucket", f"audio/{filename}")
    assert result == mock_response


@pytest.mark.asyncio
async def test_get_audio_file_not_found(collection_point_service, mock_minio_client, monkeypatch):
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")
    filename = "non_existent.mp3"
    mock_minio_client.get_object.side_effect = Exception("File not found")

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.get_audio_file(mock_minio_client, filename)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Audio file not found" in exc.value.detail


@pytest.mark.asyncio
async def test_delete_audio_from_minio_success(collection_point_service, mock_minio_client, user_data, monkeypatch):
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")
    audio_url = "http://backend/api/v1/cp/get-audio/test-uuid.mp3"

    mock_minio_client.remove_object = MagicMock()

    result = await collection_point_service.delete_audio_from_minio(audio_url, user_data, mock_minio_client)

    mock_minio_client.remove_object.assert_called_once_with("test-bucket", "audio/test-uuid.mp3")
    assert result is True


@pytest.mark.asyncio
async def test_delete_audio_from_minio_not_found(collection_point_service, mock_minio_client, user_data, monkeypatch):
    monkeypatch.setattr("app.services.collection_point_service.settings.NOTICE_WORKER_BUCKET", "test-bucket")
    audio_url = "http://backend/api/v1/cp/get-audio/non_existent.mp3"
    mock_minio_client.remove_object.side_effect = Exception("File not found")

    with pytest.raises(HTTPException) as exc:
        await collection_point_service.delete_audio_from_minio(audio_url, user_data, mock_minio_client)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Audio file not found" in exc.value.detail
