import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime, UTC

from app.services.purpose_service import PurposeService
from app.crud.purpose_crud import PurposeCRUD
from app.services.data_element_service import DataElementService


def dummy_object_id():
    return str(ObjectId())


@pytest.fixture
def mock_purpose_crud():
    return MagicMock(spec=PurposeCRUD)


@pytest.fixture
def mock_data_element_service():
    return MagicMock(spec=DataElementService)


@pytest.fixture
def mock_business_logs_collection():
    return AsyncMock()


@pytest.fixture
def purpose_service(mock_purpose_crud, mock_data_element_service, mock_business_logs_collection):
    return PurposeService(mock_purpose_crud, mock_data_element_service, mock_business_logs_collection)


@pytest.fixture
def user_data():
    return {"_id": "user1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def purpose_data():
    return {
        "purpose_title": "Test Purpose",
        "purpose_description": "A description",
        "purpose_priority": "low",
        "review_frequency": "quarterly",
        "consent_time_period": 30,
        "translations": {"eng": "Test Purpose English"},
        "reconsent": False,
    }


@pytest.mark.asyncio
async def test_create_purpose_success(purpose_service, mock_purpose_crud, user_data, purpose_data, monkeypatch):
    mock_purpose_crud.is_duplicate_name.return_value = False
    mock_purpose_crud.create_purpose.return_value = {
        "_id": dummy_object_id(),
        **purpose_data,
        "df_id": user_data["df_id"],
        "created_by": user_data["_id"],
    }

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.create_purpose(purpose_data.copy(), user_data)

    assert result["purpose_title"] == purpose_data["purpose_title"]
    mock_log_business_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_purpose_duplicate_name(purpose_service, mock_purpose_crud, user_data, purpose_data):
    mock_purpose_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.create_purpose(purpose_data.copy(), user_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Purpose title already exists."


@pytest.mark.asyncio
async def test_copy_purpose_success(purpose_service, mock_purpose_crud, mock_data_element_service, user_data, monkeypatch):
    template_id = dummy_object_id()
    new_purpose_id = dummy_object_id()
    data_elements_to_copy = ["DE1", "DE2"]

    mock_purpose_crud.get_all_purpose_templates.return_value = {
        "data": [
            {
                "_id": template_id,
                "translations": {"eng": "Template Purpose Title", "en": "Template Purpose Title"},
            }
        ],
        "total": 1,
    }

    mock_purpose_crud.is_duplicate_name.return_value = False

    mock_purpose_crud.create_purpose.return_value = {
        "_id": new_purpose_id,
        "purpose_title": "Template Purpose Title",
        "df_id": user_data["df_id"],
        "created_by": user_data["_id"],
        "data_elements": [],
    }

    mock_data_element_service.copy_data_element_by_title.side_effect = [
        {"_id": dummy_object_id(), "de_name": "DE1"},
        {"_id": dummy_object_id(), "de_name": "DE2"},
    ]

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.copy_purpose(template_id, user_data, data_elements_to_copy)

    assert result["_id"] == new_purpose_id
    assert len(result["data_elements"]) == 2


@pytest.mark.asyncio
async def test_copy_purpose_template_not_found(purpose_service, mock_purpose_crud, user_data):
    mock_purpose_crud.get_all_purpose_templates.return_value = {"data": [], "total": 0}

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.copy_purpose(dummy_object_id(), user_data, [])

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_copy_purpose_duplicate_name(purpose_service, mock_purpose_crud, user_data):
    mock_purpose_crud.get_all_purpose_templates.return_value = {
        "data": [
            {
                "translations": {"eng": "Duplicate Purpose Title", "en": "Duplicate Purpose Title"},
            }
        ],
        "total": 1,
    }

    mock_purpose_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.copy_purpose(dummy_object_id(), user_data, [])

    assert exc_info.value.status_code == 400
    assert "Duplicate Purpose Title" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()

    mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": "draft", "purpose_title": "Test Delete"}

    mock_purpose_crud.update_purpose.return_value = {"_id": purpose_id, "purpose_status": "archived"}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.delete_purpose(purpose_id, user_data)

    assert result["purpose_status"] == "archived"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected",
    [
        (None, None),
        ("archived", None),
    ],
)
async def test_delete_purpose_not_found_or_archived(purpose_service, mock_purpose_crud, user_data, status, expected):
    mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": status} if status else None
    result = await purpose_service.delete_purpose(dummy_object_id(), user_data)
    assert result == expected


@pytest.mark.asyncio
async def test_get_all_purpose_templates_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    mock_purpose_crud.get_all_purpose_templates.return_value = {"data": [1, 2], "total": 2}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_all_purpose_templates(user_data, 1, 10, title="Test")

    assert result["total_items"] == 2
    assert result["data"] == [1, 2]


@pytest.mark.asyncio
async def test_publish_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()

    mock_purpose_crud.get_purpose_master.return_value = {
        "_id": ObjectId(purpose_id),
        "purpose_title": "Publishable Purpose",
        "purpose_status": "draft",
        "consent_time_period": 30,
        "translations": {"eng": "English"},
    }

    mock_purpose_crud.update_purpose.return_value = {"_id": purpose_id, "purpose_status": "published"}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)
    monkeypatch.setattr("app.services.purpose_service.generate_blockchain_hash", MagicMock(return_value="mock_hash"))

    result = await purpose_service.publish_purpose(purpose_id, user_data)

    assert result["purpose_status"] == "published"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_state, expected_code, expected_detail",
    [
        (None, 404, "Purpose not found"),
        ({"purpose_status": "published"}, 400, "Purpose is already published."),
        ({"purpose_status": "archived"}, 400, "Cannot publish an archived purpose."),
        ({"purpose_status": "draft", "consent_time_period": None}, 400, "Retention period"),
        ({"purpose_status": "draft", "consent_time_period": 30, "translations": {}}, 400, "Translations"),
    ],
)
async def test_publish_purpose_failures(purpose_service, mock_purpose_crud, user_data, initial_state, expected_code, expected_detail):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = initial_state

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.publish_purpose(purpose_id, user_data)

    assert exc_info.value.status_code == expected_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "found_purpose, log_expected",
    [
        ({"_id": "p1"}, True),
        (None, True),
    ],
)
async def test_get_purpose(purpose_service, mock_purpose_crud, user_data, monkeypatch, found_purpose, log_expected):
    purpose_id = dummy_object_id()

    mock_purpose_crud.get_purpose_master.return_value = found_purpose

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_purpose(purpose_id, user_data)

    if found_purpose:
        assert result == found_purpose


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_state, update_data, is_dup, expected_code",
    [
        (None, {"purpose_title": "New Title"}, False, 404),
        ({"purpose_status": "published"}, {"purpose_title": "New Title"}, False, 400),
        ({"purpose_status": "draft"}, {"purpose_title": "Existing"}, True, 400),
        ({"purpose_status": "draft"}, {"translations": {"invalid": "text"}}, False, 400),
        ({"purpose_status": "draft"}, {"translations": {"eng": "ok", "invalid": "bad"}}, False, 400),
    ],
)
async def test_update_purpose_failures(purpose_service, mock_purpose_crud, user_data, initial_state, update_data, is_dup, expected_code):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = initial_state
    mock_purpose_crud.is_duplicate_name.return_value = is_dup

    with pytest.raises(HTTPException) as exc:
        await purpose_service.update_purpose_data(purpose_id, update_data, user_data)

    assert exc.value.status_code == expected_code


@pytest.mark.asyncio
async def test_update_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()

    initial_state = {
        "_id": ObjectId(purpose_id),
        "purpose_title": "Original Title",
        "purpose_status": "draft",
        "df_id": user_data["df_id"],
    }

    update_data = {"purpose_title": "Updated Title", "translations": {"eng": "Updated"}}

    mock_purpose_crud.get_purpose_master.return_value = initial_state
    mock_purpose_crud.is_duplicate_name.return_value = False
    mock_purpose_crud.update_purpose.return_value = {**initial_state, **update_data}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.update_purpose_data(purpose_id, update_data, user_data)

    assert result["purpose_title"] == "Updated Title"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "purpose_data, expected",
    [
        ({"translations": {"eng": "yes", "hin": "haan"}}, False),
        ({"translations": {"eng": "yes", "hin": ""}}, False),
        ({"translations": {"eng": "yes"}}, False),
        ({"translations": {}}, False),
    ],
)
async def test_is_translated(purpose_service, mock_purpose_crud, user_data, purpose_data, expected):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = purpose_data

    result = await purpose_service.is_translated(purpose_id, user_data)

    assert result is expected


@pytest.mark.asyncio
async def test_is_translated_not_found(purpose_service, mock_purpose_crud, user_data):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = None

    with pytest.raises(HTTPException):
        await purpose_service.is_translated(purpose_id, user_data)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected",
    [
        ("published", True),
        ("draft", False),
        ("archived", False),
    ],
)
async def test_is_published(purpose_service, mock_purpose_crud, user_data, status, expected):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": status}

    result = await purpose_service.is_published(purpose_id, user_data)

    assert result == expected


@pytest.mark.asyncio
async def test_is_published_not_found(purpose_service, mock_purpose_crud, user_data):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = None

    with pytest.raises(HTTPException):
        await purpose_service.is_published(purpose_id, user_data)


@pytest.mark.asyncio
async def test_get_all_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):

    mock_purpose_crud.get_all_purpose_master.return_value = {"data": [{"_id": "p1"}, {"_id": "p2"}, {"_id": "p3"}], "total": 3}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_all_purpose(user_data, current_page=1, data_per_page=3)

    mock_purpose_crud.get_all_purpose_master.assert_called_once_with(df_id=user_data["df_id"], offset=0, limit=3)

    mock_log_business_event.assert_called_once()

    assert result["current_page"] == 1
    assert result["data_per_page"] == 3
    assert result["total_items"] == 3
    assert result["total_pages"] == 1
    assert result["purposes"] == [{"_id": "p1"}, {"_id": "p2"}, {"_id": "p3"}]


@pytest.mark.asyncio
async def test_get_all_purpose_empty(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    mock_purpose_crud.get_all_purpose_master.return_value = {"data": [], "total": 0}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_all_purpose(user_data, current_page=2, data_per_page=10)

    mock_purpose_crud.get_all_purpose_master.assert_called_once_with(df_id=user_data["df_id"], offset=10, limit=10)

    assert result["current_page"] == 2
    assert result["data_per_page"] == 10
    assert result["total_items"] == 0
    assert result["total_pages"] == 0
    assert result["purposes"] == []
