import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime, UTC
from enum import Enum # Added this import

from app.services.purpose_service import PurposeService
from app.crud.purpose_crud import PurposeCRUD
from app.services.data_element_service import DataElementService
from app.schemas.purpose_schema import LanguageCodes, PurposeInDB

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
        "translations": {"eng": "Test Purpose English"}, # Changed to 'eng'
        "reconsent": False,
    }

def dummy_object_id():
    return str(ObjectId())

# -------------------------
# CREATE PURPOSE TESTS
# -------------------------
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

    mock_purpose_crud.is_duplicate_name.assert_called_once_with(purpose_data["purpose_title"], user_data["df_id"])
    mock_purpose_crud.create_purpose.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["purpose_title"] == purpose_data["purpose_title"]

@pytest.mark.asyncio
async def test_create_purpose_duplicate_name(purpose_service, mock_purpose_crud, user_data, purpose_data):
    mock_purpose_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.create_purpose(purpose_data.copy(), user_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Purpose title already exists."
    mock_purpose_crud.create_purpose.assert_not_called()

# -------------------------
# COPY PURPOSE TESTS
# -------------------------
@pytest.mark.asyncio
async def test_copy_purpose_success(purpose_service, mock_purpose_crud, mock_data_element_service, user_data, monkeypatch):
    template_id = dummy_object_id()
    copied_purpose_id = dummy_object_id()
    data_elements_to_copy = ["DE1", "DE2"]

    mock_purpose_crud.get_all_purpose_templates.return_value = {
        "data": [{
            "_id": template_id,
            "translations": {"eng": "Template Purpose Title"}, # Corrected to 'eng'
        }],
        "total": 1
    }
    mock_purpose_crud.is_duplicate_name.return_value = False
    mock_purpose_crud.create_purpose.return_value = {
        "_id": copied_purpose_id,
        "purpose_title": "Template Purpose Title",
        "df_id": user_data["df_id"],
        "created_by": user_data["_id"],
        "data_elements": [],
    }
    mock_purpose_crud.update_purpose.return_value = None # We don't verify the return, just that it's called

    mock_data_element_service.copy_data_element_by_title.side_effect = [
        {"_id": dummy_object_id(), "de_name": "DE1"},
        {"_id": dummy_object_id(), "de_name": "DE2"},
    ]

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.copy_purpose(template_id, user_data, data_elements_to_copy)

    mock_purpose_crud.get_all_purpose_templates.assert_called_once_with(id=template_id)
    mock_purpose_crud.is_duplicate_name.assert_called_once_with("Template Purpose Title", user_data["df_id"])
    mock_purpose_crud.create_purpose.assert_called_once()
    assert mock_data_element_service.copy_data_element_by_title.call_count == len(data_elements_to_copy)
    mock_purpose_crud.update_purpose.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["_id"] == copied_purpose_id
    assert len(result["data_elements"]) == len(data_elements_to_copy)

@pytest.mark.asyncio
async def test_copy_purpose_template_not_found(purpose_service, mock_purpose_crud, user_data):
    mock_purpose_crud.get_all_purpose_templates.return_value = {"data": [], "total": 0}

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.copy_purpose(dummy_object_id(), user_data, [])

    assert exc_info.value.status_code == 404
    assert "Purpose template with ID" in exc_info.value.detail
    mock_purpose_crud.is_duplicate_name.assert_not_called()

@pytest.mark.asyncio
async def test_copy_purpose_duplicate_name(purpose_service, mock_purpose_crud, user_data):
    template_id = dummy_object_id()
    mock_purpose_crud.get_all_purpose_templates.return_value = {
        "data": [{
            "_id": template_id,
            "translations": {"eng": "Duplicate Purpose Title"}, # Changed to 'eng'
        }],
        "total": 1
    }
    mock_purpose_crud.is_duplicate_name.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.copy_purpose(template_id, user_data, [])

    assert exc_info.value.status_code == 400
    assert "Purpose title 'Duplicate Purpose Title' already exists." in exc_info.value.detail
    mock_purpose_crud.create_purpose.assert_not_called()

# -------------------------
# DELETE PURPOSE TESTS
# -------------------------
@pytest.mark.asyncio
async def test_delete_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": "draft", "purpose_title": "Test Delete"}
    mock_purpose_crud.update_purpose.return_value = {"_id": purpose_id, "purpose_status": "archived"}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.delete_purpose(purpose_id, user_data)

    mock_purpose_crud.get_purpose_master.assert_called_once_with(purpose_id, user_data["df_id"])
    mock_purpose_crud.update_purpose.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["purpose_status"] == "archived"

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected_result",
    [
        (None, None), # Not found
        ("archived", None), # Already archived
    ]
)
async def test_delete_purpose_not_found_or_archived(purpose_service, mock_purpose_crud, user_data, status, expected_result):
    mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": status} if status else None

    result = await purpose_service.delete_purpose(dummy_object_id(), user_data)

    assert result == expected_result
    mock_purpose_crud.update_purpose.assert_not_called()

# -------------------------
# GET ALL PURPOSE TEMPLATES TESTS
# -------------------------
@pytest.mark.asyncio
async def test_get_all_purpose_templates_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    mock_purpose_crud.get_all_purpose_templates.return_value = {"data": [1, 2], "total": 2}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_all_purpose_templates(user_data, 1, 10, title="Test")

    mock_purpose_crud.get_all_purpose_templates.assert_called_once_with(offset=0, limit=10, title="Test", id=None, industry=None, sub_category=None)
    mock_log_business_event.assert_called_once()
    assert result["total_items"] == 2
    assert result["total_pages"] == 1
    assert result["data"] == [1, 2]

# -------------------------
# PUBLISH PURPOSE TESTS
# -------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_purpose_state, expected_status_code, expected_detail",
    [
        (None, 404, "Purpose not found or does not belong to the current domain."),
        ({"purpose_status": "published"}, 400, "Purpose is already published."),
        ({"purpose_status": "archived"}, 400, "Cannot publish an archived purpose."),
        ({"purpose_status": "draft", "consent_time_period": None}, 400, "Retention period (consent_time_period) is required before publishing."),
        ({"purpose_status": "draft", "consent_time_period": 30, "translations": {}}, 400, "Translations are required and cannot be empty or contain invalid language codes before publishing."),
        ({"purpose_status": "draft", "consent_time_period": 30, "translations": {"eng": ""}}, 400, "Translations are required and cannot be empty or contain invalid language codes before publishing."), # Changed to 'eng'
        ({"purpose_status": "draft", "consent_time_period": 30, "translations": {"invalid": "text"}}, 400, "Translations are required and cannot be empty or contain invalid language codes before publishing."),
    ],
)
async def test_publish_purpose_failure_cases(
    purpose_service, mock_purpose_crud, user_data, initial_purpose_state, expected_status_code, expected_detail
):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = initial_purpose_state

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.publish_purpose(purpose_id, user_data)

    assert exc_info.value.status_code == expected_status_code
    assert exc_info.value.detail == expected_detail

@pytest.mark.asyncio
async def test_publish_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = {
        "_id": ObjectId(purpose_id),
        "purpose_title": "Publishable Purpose",
        "purpose_status": "draft",
        "consent_time_period": 30,
        "translations": {"eng": "English"}, # Changed to 'eng'
    }
    mock_purpose_crud.update_purpose.return_value = {"_id": purpose_id, "purpose_status": "published"}

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)
    monkeypatch.setattr("app.services.purpose_service.generate_blockchain_hash", MagicMock(return_value="mock_hash"))

    result = await purpose_service.publish_purpose(purpose_id, user_data)

    mock_purpose_crud.get_purpose_master.assert_called_once_with(purpose_id, user_data["df_id"])
    mock_purpose_crud.update_purpose.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["purpose_status"] == "published"

# -------------------------
# GET ALL PURPOSE TESTS
# -------------------------
@pytest.mark.asyncio
async def test_get_all_purpose_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    mock_purpose_crud.get_all_purpose_master.return_value = {"data": [1, 2, 3], "total": 3}
    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_all_purpose(user_data, 1, 3)

    mock_purpose_crud.get_all_purpose_master.assert_called_once_with(df_id=user_data["df_id"], offset=0, limit=3)
    mock_log_business_event.assert_called_once()
    assert result["total_items"] == 3
    assert result["total_pages"] == 1
    assert result["purposes"] == [1, 2, 3]

# -------------------------
# GET PURPOSE TESTS
# -------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "found_purpose, for_system, log_expected",
    [
        ({"_id": "p1"}, False, True),
        ({"_id": "p1"}, True, False),
        (None, False, True),
    ]
)
async def test_get_purpose(purpose_service, mock_purpose_crud, user_data, monkeypatch, found_purpose, for_system, log_expected):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = found_purpose

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)

    result = await purpose_service.get_purpose(purpose_id, user_data, for_system=for_system)

    mock_purpose_crud.get_purpose_master.assert_called_once_with(purpose_id, user_data["df_id"])
    if log_expected:
        mock_log_business_event.assert_called_once()
    else:
        mock_log_business_event.assert_not_called()
    assert result == found_purpose

# -------------------------
# UPDATE PURPOSE DATA TESTS
# -------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_purpose_state, update_data, is_duplicate, expected_status_code, expected_detail",
    [
        (None, {"purpose_title": "New Title"}, False, 404, "Purpose not found."),
        ({"purpose_status": "published"}, {"purpose_title": "New Title"}, False, 400, "Only Purpose in draft status can be updated."),
        ({"purpose_status": "draft"}, {"purpose_title": "Existing Title"}, True, 400, "Purpose title 'Existing Title' already exists."),
        ({"purpose_status": "draft"}, {"translations": {"invalid": "text"}}, False, 400, "Invalid language codes in translations: ['invalid']"),
        ({"purpose_status": "draft"}, {"translations": {"eng": "new", "invalid": "text"}}, False, 400, "Invalid language codes in translations: ['invalid']"), # Changed to 'eng'
    ],
)
async def test_update_purpose_data_failure_cases(
    purpose_service, mock_purpose_crud, user_data, initial_purpose_state, update_data, is_duplicate, expected_status_code, expected_detail
):
    purpose_id = dummy_object_id()
    mock_purpose_crud.get_purpose_master.return_value = initial_purpose_state
    mock_purpose_crud.is_duplicate_name.return_value = is_duplicate

    with pytest.raises(HTTPException) as exc_info:
        await purpose_service.update_purpose_data(purpose_id, update_data, user_data)

    assert exc_info.value.status_code == expected_status_code
    assert exc_info.value.detail == expected_detail

@pytest.mark.asyncio
async def test_update_purpose_data_success(purpose_service, mock_purpose_crud, user_data, monkeypatch):
    purpose_id = dummy_object_id()
    initial_purpose_state = {
        "_id": ObjectId(purpose_id),
        "purpose_title": "Original Title",
        "purpose_status": "draft",
        "df_id": user_data["df_id"],
    }
    update_data = {"purpose_title": "Updated Title", "translations": {"eng": "New Eng"}} # Changed to 'eng'
    updated_purpose_return = {**initial_purpose_state, **update_data}

    mock_purpose_crud.get_purpose_master.return_value = initial_purpose_state
    mock_purpose_crud.is_duplicate_name.return_value = False
    mock_purpose_crud.update_purpose.return_value = updated_purpose_return

    mock_log_business_event = AsyncMock()
    monkeypatch.setattr("app.services.purpose_service.log_business_event", mock_log_business_event)
    monkeypatch.setattr("app.services.purpose_service.datetime", MagicMock(now=MagicMock(return_value=datetime.now(UTC))))

    result = await purpose_service.update_purpose_data(purpose_id, update_data, user_data)

    mock_purpose_crud.get_purpose_master.assert_called_once_with(purpose_id, user_data["df_id"])
    mock_purpose_crud.is_duplicate_name.assert_called_once_with(update_data["purpose_title"], user_data["df_id"])
    mock_purpose_crud.update_purpose.assert_called_once()
    mock_log_business_event.assert_called_once()
    assert result["purpose_title"] == "Updated Title"

# -------------------------
# IS TRANSLATED TESTS
# -------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_lang_codes, purpose_data, expected_result, expected_status_code",
    [
        ({"eng": "English", "fr": "French"}, {"translations": {"eng": "yes", "fr": "oui"}}, True, None), # Changed to 'eng'
        ({"eng": "English", "fr": "French"}, {"translations": {"eng": "yes", "fr": ""}}, False, None), # Changed to 'eng'
        ({"eng": "English"}, {"translations": {"eng": "yes", "fr": "oui"}}, False, None), # Invalid lang code in data, changed to 'eng'
        ({"eng": "English", "fr": "French"}, {"translations": {}}, False, None), # Changed to 'eng'
        ({"eng": "English", "fr": "French"}, None, "exception", 404), # Changed to 'eng'
    ],
)
async def test_is_translated(
    purpose_service, mock_purpose_crud, user_data, monkeypatch,
    mock_lang_codes, purpose_data, expected_result, expected_status_code
):
    purpose_id = dummy_object_id()

    # Mock LanguageCodes directly
    class MockLanguageCodes(Enum):
        # Define some sample members with .value for proper Enum behavior
        eng = "English"
        fr = "French"
        
        # Override __iter__ to return members based on mock_lang_codes
        def __iter__(self):
            # Yield actual Enum members, not just their names
            for k, v in self._member_map_.items():
                if k in mock_lang_codes:
                    yield self[k]

        # Override __len__ to support dynamic length based on mock_lang_codes
        def __len__(self):
            return len(self._member_map_) # Should reflect actual members added

    # Dynamically populate _member_map_ and _member_names_ based on mock_lang_codes
    # This is necessary for MockLanguageCodes to behave like a real Enum with dynamic members.
    MockLanguageCodes._member_map_ = {}
    MockLanguageCodes._member_names_ = []
    for k, v in mock_lang_codes.items():
        # Create actual Enum members
        member = Enum._create_pseudo_member_(MockLanguageCodes, k, v)
        MockLanguageCodes._member_map_[k] = member
        MockLanguageCodes._member_names_.append(k)


    monkeypatch.setattr("app.schemas.purpose_schema.LanguageCodes", MockLanguageCodes)
    monkeypatch.setattr("app.services.purpose_service.LanguageCodes", MockLanguageCodes)

    if expected_result != "exception":
        mock_purpose_crud.get_purpose_master.return_value = purpose_data
    else:
        mock_purpose_crud.get_purpose_master.return_value = None

    if expected_status_code:
        with pytest.raises(HTTPException) as exc_info:
            await purpose_service.is_translated(purpose_id, user_data)
        assert exc_info.value.status_code == expected_status_code
    else:
        result = await purpose_service.is_translated(purpose_id, user_data)
        assert result is expected_result

# -------------------------
# IS PUBLISHED TESTS
# -------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "purpose_status, expected_result",
    [
        ("published", True),
        ("draft", False),
        ("archived", False),
        (None, "exception"),
    ],
)
async def test_is_published(purpose_service, mock_purpose_crud, user_data, purpose_status, expected_result):
    purpose_id = dummy_object_id()
    if expected_result != "exception":
        mock_purpose_crud.get_purpose_master.return_value = {"purpose_status": purpose_status}
    else:
        mock_purpose_crud.get_purpose_master.return_value = None

    if expected_result == "exception":
        with pytest.raises(HTTPException) as exc_info:
            await purpose_service.is_published(purpose_id, user_data)
        assert exc_info.value.status_code == 404
    else:
        result = await purpose_service.is_published(purpose_id, user_data)
        assert result is expected_result
