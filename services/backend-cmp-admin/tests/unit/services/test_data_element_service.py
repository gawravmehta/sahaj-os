import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.data_element_service import DataElementService
from app.schemas.data_element_schema import DataElementDB, LanguageCodes


@pytest.fixture
def mock_crud():
    return MagicMock()


@pytest.fixture
def service(mock_crud):
    return DataElementService(mock_crud, "logs")


@pytest.mark.asyncio
async def test_create_data_element_success(service, mock_crud, monkeypatch):
    mock_crud.is_duplicate_name = AsyncMock(return_value=False)
    mock_crud.create_de = AsyncMock(
        return_value={
            "_id": "abc123",
            "de_name": "Test Data Element",
            "df_id": "df123",
            "de_status": "draft",
        }
    )

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"_id": "u1", "email": "t@e.com", "df_id": "df123"}

    de_data = {
        "de_name": "Test Data Element",
        "de_description": "Test Description",
        "de_original_name": "Test Data Element",
        "de_data_type": "string",
        "de_sensitivity": "low",
        "is_core_identifier": False,
        "de_retention_period": 30,
        "translations": {"en": "Test"},
    }

    result = await service.create_data_element(de_data.copy(), user)

    mock_crud.create_de.assert_called_once()
    mock_log.assert_called_once()
    assert result["_id"] == "abc123"


@pytest.mark.asyncio
async def test_create_data_element_duplicate_name(service, mock_crud):
    mock_crud.is_duplicate_name = AsyncMock(return_value=True)

    user = {"_id": "u1", "email": "t@e.com", "df_id": "df123"}
    de_data = {"de_name": "Test Data Element"}

    with pytest.raises(HTTPException) as exc:
        await service.create_data_element(de_data, user)

    assert exc.value.status_code == 409
    mock_crud.create_de.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, is_duplicate, update_data, expected_exception_status",
    [
        (None, False, {"de_name": "New"}, 404),  # Not found
        ({"de_status": "draft"}, True, {"de_name": "New"}, 400),  # Duplicate name
        ({"de_status": "published"}, False, {"de_name": "New"}, 400),  # Not in draft status
        ({"de_status": "draft"}, False, {"de_name": "New"}, None),  # Success
        ({"de_status": "draft"}, False, {"translations": {"invalid_lang": "text"}}, 400),  # Invalid lang code
        ({"de_status": "draft"}, False, {}, None),  # No name change, no duplicate check
    ],
)
async def test_update_data_element(
    service, mock_crud, monkeypatch, get_de_master_return, is_duplicate, update_data, expected_exception_status
):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)
    mock_crud.is_duplicate_name = AsyncMock(return_value=is_duplicate)
    mock_crud.update_data_element_by_id = AsyncMock(return_value={"_id": "a1", "updated": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception_status:
        with pytest.raises(HTTPException) as exc:
            await service.update_data_element("a1", update_data, user)
        assert exc.value.status_code == expected_exception_status
    else:
        result = await service.update_data_element("a1", update_data, user)
        mock_crud.update_data_element_by_id.assert_called_once()
        mock_log.assert_called_once()
        assert result["_id"] == "a1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, expected_exception_status",
    [
        (None, 404),  # Not found
        ({"de_status": "published"}, 400),  # Already published
        ({"de_status": "archived"}, 400),  # Archived
        ({"de_status": "draft"}, 400),  # Missing retention period
        ({"de_status": "draft", "de_retention_period": 30, "translations": {}}, 400),  # Empty translations
        ({"de_status": "draft", "de_retention_period": 30, "translations": {"en": ""}}, 400),  # Empty translation values
        ({"de_status": "draft", "de_retention_period": 30, "translations": {"en": "Test"}}, None),  # Success
    ],
)
async def test_publish_data_element(service, mock_crud, monkeypatch, get_de_master_return, expected_exception_status):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)
    mock_crud.update_data_element_by_id = AsyncMock(return_value={"_id": "a1", "published": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception_status:
        with pytest.raises(HTTPException) as exc:
            await service.publish_data_element("a1", user)
        assert exc.value.status_code == expected_exception_status
    else:
        result = await service.publish_data_element("a1", user)
        assert result["published"] is True
        mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, expected_result",
    [
        ({"de_status": "draft"}, True),
        ({"de_status": "archived"}, False),
        (None, False),
    ],
)
async def test_delete_data_element(service, mock_crud, monkeypatch, get_de_master_return, expected_result):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)
    mock_crud.update_data_element_by_id = AsyncMock(return_value={"archived": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1"}

    if get_de_master_return is None:
        result = await service.delete_data_element("a1", user)
        assert result is None
    elif expected_result:
        result = await service.delete_data_element("a1", user)
        assert result["archived"] is True
        mock_log.assert_called_once()
    else:
        result = await service.delete_data_element("a1", user)
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, for_system, expected_log_called",
    [
        ({"_id": "a1"}, False, True),
        ({"_id": "a1"}, True, False),
        (None, False, True),
    ],
)
async def test_get_data_element(service, mock_crud, monkeypatch, get_de_master_return, for_system, expected_log_called):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "email": "x"}

    res = await service.get_data_element("a1", user, for_system=for_system)

    if get_de_master_return:
        assert res["_id"] == "a1"
    else:
        assert res is None

    if expected_log_called:
        mock_log.assert_called_once()
    else:
        mock_log.assert_not_called()


@pytest.mark.asyncio
async def test_get_all_data_element_templates(service, mock_crud, monkeypatch):
    mock_crud.get_all_de_templates = AsyncMock(return_value={"data": [1, 2], "total": 2})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "email": "x"}

    res = await service.get_all_data_element_templates(user, current_page=1, data_per_page=1)

    assert res["total_items"] == 2
    assert res["total_pages"] == 2
    assert res["data"] == [1, 2]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_all_de_templates_return, is_duplicate, expected_exception",
    [
        ({"data": [{"title": "Test", "description": "Test"}]}, False, None),
        ({"data": []}, False, HTTPException(status_code=404)),
        ({"data": [{"title": "Test", "description": "Test"}]}, True, HTTPException(status_code=409)),
    ],
)
async def test_copy_data_element(service, mock_crud, monkeypatch, get_all_de_templates_return, is_duplicate, expected_exception):
    mock_crud.get_all_de_templates = AsyncMock(return_value=get_all_de_templates_return)
    mock_crud.is_duplicate_name = AsyncMock(return_value=is_duplicate)
    mock_crud.create_de = AsyncMock(return_value={"_id": "abc123"})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception:
        with pytest.raises(HTTPException) as exc:
            await service.copy_data_element("test_id", user)
        assert exc.value.status_code == expected_exception.status_code
    else:
        result = await service.copy_data_element("test_id", user)
        assert result["_id"] == "abc123"
        mock_crud.create_de.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_all_de_templates_return, get_de_master_by_name_return, expected_exception",
    [
        ({"data": [{"title": "Test", "description": "Test"}]}, None, None),
        ({"data": []}, None, HTTPException(status_code=404)),
        ({"data": [{"title": "Test", "description": "Test"}]}, {"_id": "abc123"}, None),
    ],
)
async def test_copy_data_element_by_title(
    service, mock_crud, monkeypatch, get_all_de_templates_return, get_de_master_by_name_return, expected_exception
):
    mock_crud.get_all_de_templates = AsyncMock(return_value=get_all_de_templates_return)
    mock_crud.get_de_master_by_name = AsyncMock(return_value=get_de_master_by_name_return)
    mock_crud.create_de = AsyncMock(return_value={"_id": "abc123"})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception:
        with pytest.raises(HTTPException) as exc:
            await service.copy_data_element_by_title("Test", user)
        assert exc.value.status_code == expected_exception.status_code
    elif get_de_master_by_name_return:
        result = await service.copy_data_element_by_title("Test", user)
        assert result["_id"] == "abc123"
        mock_crud.create_de.assert_not_called()
    else:
        result = await service.copy_data_element_by_title("Test", user)
        assert result["_id"] == "abc123"
        mock_crud.create_de.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_data_element(service, mock_crud, monkeypatch):
    mock_crud.get_all_de_master = AsyncMock(return_value={"data": [1, 2], "total": 2})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.data_element_service.log_business_event", mock_log)

    user = {"df_id": "df1", "email": "x"}

    res = await service.get_all_data_element(user, current_page=1, data_per_page=1, is_core_identifier=True)

    assert res["total_items"] == 2
    assert res["total_pages"] == 2
    assert res["data_elements"] == [1, 2]
    mock_crud.get_all_de_master.assert_called_once_with(
        df_id="df1", offset=0, limit=1, is_core_identifier=True
    )
    mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, expected_result",
    [
        (
            {"translations": {code.name: "test" for code in LanguageCodes}},
            True,
        ),
        ({"translations": {"en": "Test"}}, False),
        ({"translations": {}}, False),
        (None, "exception"),
    ],
)
async def test_is_translated(service, mock_crud, get_de_master_return, expected_result):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)
    user = {"df_id": "df1"}

    if expected_result == "exception":
        with pytest.raises(HTTPException) as exc:
            await service.is_translated("a1", user)
        assert exc.value.status_code == 404
    else:
        result = await service.is_translated("a1", user)
        assert result is expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_de_master_return, expected_result",
    [
        ({"de_status": "published"}, True),
        ({"de_status": "draft"}, False),
        (None, "exception"),
    ],
)
async def test_is_published(service, mock_crud, get_de_master_return, expected_result):
    mock_crud.get_de_master = AsyncMock(return_value=get_de_master_return)
    user = {"df_id": "df1"}

    if expected_result == "exception":
        with pytest.raises(HTTPException) as exc:
            await service.is_published("a1", user)
        assert exc.value.status_code == 404
    else:
        result = await service.is_published("a1", user)
        assert result is expected_result
