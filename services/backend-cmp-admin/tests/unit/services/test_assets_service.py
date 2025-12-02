import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.assets_service import AssetService
from app.schemas.assets_schema import MetaCookies


@pytest.fixture
def mock_crud():
    return MagicMock()


@pytest.fixture
def service(mock_crud):
    return AssetService(mock_crud, "logs")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_duplicate, expected_exception",
    [
        (False, None),
        (True, HTTPException(status_code=409)),
    ],
)
async def test_create_asset(service, mock_crud, monkeypatch, is_duplicate, expected_exception):
    mock_crud.is_duplicate_name = AsyncMock(return_value=is_duplicate)
    mock_crud.create_asset = AsyncMock(
        return_value={
            "_id": "abc123",
            "asset_name": "Test Asset",
            "df_id": "df123",
            "asset_status": "draft",
        }
    )

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"_id": "u1", "email": "t@e.com", "df_id": "df123"}
    asset_data = {"asset_name": "Test Asset", "category": "Website", "usage_url": "https://example.com"}

    if expected_exception:
        with pytest.raises(HTTPException) as exc:
            await service.create_asset(asset_data, user)
        assert exc.value.status_code == expected_exception.status_code
        mock_crud.create_asset.assert_not_called()
    else:
        result = await service.create_asset(asset_data.copy(), user)
        mock_crud.create_asset.assert_called_once()
        mock_log.assert_called_once()
        assert result["_id"] == "abc123"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_asset_return, is_duplicate, expected_exception",
    [
        (None, False, HTTPException(status_code=404)),
        ({"asset_status": "draft"}, True, HTTPException(status_code=400)),
        ({"asset_status": "published"}, False, HTTPException(status_code=400)),
        ({"asset_status": "draft"}, False, None),
    ],
)
async def test_update_asset(service, mock_crud, monkeypatch, get_asset_return, is_duplicate, expected_exception):
    mock_crud.get_asset = AsyncMock(return_value=get_asset_return)
    mock_crud.is_duplicate_name = AsyncMock(return_value=is_duplicate)
    mock_crud.update_asset_by_id = AsyncMock(return_value={"_id": "a1", "updated": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception:
        with pytest.raises(HTTPException) as exc:
            await service.update_asset("a1", {"asset_name": "New"}, user)
        assert exc.value.status_code == expected_exception.status_code
    else:
        result = await service.update_asset("a1", {"asset_name": "A"}, user)
        mock_crud.update_asset_by_id.assert_called_once()
        mock_log.assert_called_once()
        assert result["_id"] == "a1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_asset_return, expected_result",
    [
        ({"_id": "a1", "category": "website", "meta_cookies": {"cookies_count": 5}}, True),
        ({"category": "mobile"}, False),
        (None, False),
    ],
)
async def test_update_asset_cookie_fields(service, mock_crud, monkeypatch, get_asset_return, expected_result):
    mock_crud.get_asset = AsyncMock(return_value=get_asset_return)
    mock_crud.update_asset_by_id = AsyncMock(return_value={"updated": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}
    meta = MetaCookies(cookies_count=10)

    if get_asset_return is None:
        with pytest.raises(HTTPException) as exc:
            await service.update_asset_cookie_fields("a1", user, meta)
        assert exc.value.status_code == 404
    elif expected_result:
        result = await service.update_asset_cookie_fields("a1", user, meta)
        mock_crud.update_asset_by_id.assert_called_once()
        mock_log.assert_called_once()
        assert result["updated"] is True
    else:
        result = await service.update_asset_cookie_fields("a1", {"df_id": "df1"}, MetaCookies())
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_asset_return, expected_exception",
    [
        (None, HTTPException(status_code=404)),
        ({"asset_status": "published"}, HTTPException(status_code=400)),
        ({"asset_status": "archived"}, HTTPException(status_code=400)),
        ({"asset_status": "draft"}, None),
    ],
)
async def test_publish_asset(service, mock_crud, monkeypatch, get_asset_return, expected_exception):
    mock_crud.get_asset = AsyncMock(return_value=get_asset_return)
    mock_crud.update_asset_by_id = AsyncMock(return_value={"_id": "a1", "published": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1", "email": "t@e.com"}

    if expected_exception:
        with pytest.raises(HTTPException) as exc:
            await service.publish_asset("a1", user)
        assert exc.value.status_code == expected_exception.status_code
    else:
        result = await service.publish_asset("a1", user)
        assert result["published"] is True
        mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_asset_return, expected_result",
    [
        ({"asset_status": "draft"}, True),
        ({"asset_status": "archived"}, False),
        (None, False),
    ],
)
async def test_delete_asset(service, mock_crud, monkeypatch, get_asset_return, expected_result):
    mock_crud.get_asset = AsyncMock(return_value=get_asset_return)
    mock_crud.update_asset_by_id = AsyncMock(return_value={"archived": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"df_id": "df1", "_id": "u1"}

    if get_asset_return is None:
        result = await service.delete_asset("a1", user)
        assert result is None
    elif expected_result:
        result = await service.delete_asset("a1", user)
        assert result["archived"] is True
        mock_log.assert_called_once()
    else:
        result = await service.delete_asset("a1", user)
        assert result is None


@pytest.mark.asyncio
async def test_create_asset_missing_fields(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.is_duplicate_name = AsyncMock(return_value=False)

    monkeypatch.setattr("app.services.assets_service.log_business_event", AsyncMock())

    service = AssetService(mock_crud, "logs")
    user = {"_id": "u1", "email": "t@e.com", "df_id": "df123"}

    asset_data = {"asset_name": "Test"}

    with pytest.raises(Exception):
        await service.create_asset(asset_data, user)


@pytest.mark.asyncio
async def test_create_asset_crud_failure(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.is_duplicate_name = AsyncMock(return_value=False)
    mock_crud.create_asset = AsyncMock(side_effect=Exception("DB error"))

    monkeypatch.setattr("app.services.assets_service.log_business_event", AsyncMock())

    service = AssetService(mock_crud, "logs")
    user = {"_id": "u1", "email": "t@e.com", "df_id": "df123"}

    asset_data = {"asset_name": "Test Asset", "category": "Website", "usage_url": "x"}

    with pytest.raises(Exception):
        await service.create_asset(asset_data, user)


@pytest.mark.asyncio
async def test_update_asset_status_not_draft():
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value={"asset_status": "published"})

    service = AssetService(mock_crud, "logs")

    with pytest.raises(HTTPException) as exc:
        await service.update_asset("a1", {}, {"df_id": "df1", "_id": "u1"})

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_asset_no_name_no_duplicate_check(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value={"asset_status": "draft"})
    mock_crud.update_asset_by_id = AsyncMock(return_value={"_id": "a1"})

    mock_crud.is_duplicate_name = AsyncMock()

    monkeypatch.setattr("app.services.assets_service.log_business_event", AsyncMock())

    service = AssetService(mock_crud, "logs")
    user = {"df_id": "df1", "_id": "u1", "email": "x"}

    await service.update_asset("a1", {"description": "new desc"}, user)

    mock_crud.is_duplicate_name.assert_not_called()


@pytest.mark.asyncio
async def test_update_asset_sets_updated_fields(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value={"asset_status": "draft"})
    mock_crud.is_duplicate_name = AsyncMock(return_value=False)

    updated_response = {"_id": "a1", "updated": True}
    mock_crud.update_asset_by_id = AsyncMock(return_value=updated_response)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    service = AssetService(mock_crud, "logs")
    user = {"df_id": "df1", "_id": "u1", "email": "test"}

    await service.update_asset("a1", {}, user)

    args = mock_crud.update_asset_by_id.call_args[0][2]
    assert "updated_at" in args
    assert args["updated_by"] == "u1"


@pytest.mark.asyncio
async def test_update_asset_cookie_fields_not_found():
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value=None)

    service = AssetService(mock_crud, "logs")

    with pytest.raises(HTTPException) as exc:
        await service.update_asset_cookie_fields("a1", {"df_id": "df1"}, MetaCookies())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_publish_asset_archived():
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value={"asset_status": "archived"})

    service = AssetService(mock_crud, "logs")

    with pytest.raises(HTTPException) as exc:
        await service.publish_asset("a1", {"df_id": "df1"})

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_publish_asset_success(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.get_asset = AsyncMock(return_value={"asset_status": "draft"})
    mock_crud.update_asset_by_id = AsyncMock(return_value={"_id": "a1", "published": True})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    service = AssetService(mock_crud, "logs")

    result = await service.publish_asset("a1", {"df_id": "df1", "_id": "u1", "email": "t@e.com"})

    assert result["published"] is True
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_assets_success(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.get_all_assets = AsyncMock(return_value={"data": [1, 2], "total": 2})

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    service = AssetService(mock_crud, "logs")
    user = {"df_id": "df1", "email": "x"}

    res = await service.get_all_assets(user, current_page=1, data_per_page=1)

    assert res["total_items"] == 2
    assert res["total_pages"] == 2
    assert res["assets"] == [1, 2]


@pytest.mark.asyncio
async def test_get_all_assets_with_category(monkeypatch):
    mock_crud = MagicMock()
    mock_crud.get_all_assets = AsyncMock(return_value={"data": [], "total": 0})

    monkeypatch.setattr("app.services.assets_service.log_business_event", AsyncMock())

    service = AssetService(mock_crud, "logs")
    user = {"df_id": "df1", "email": "x"}

    await service.get_all_assets(user, category="Website")

    mock_crud.get_all_assets.assert_called_with(df_id="df1", offset=0, limit=20, category="Website")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "get_asset_return, for_system, expected_log_called",
    [
        ({"_id": "a1"}, False, True),
        ({"_id": "a1"}, True, False),
        (None, False, True),
    ],
)
async def test_get_asset(service, mock_crud, monkeypatch, get_asset_return, for_system, expected_log_called):
    mock_crud.get_asset = AsyncMock(return_value=get_asset_return)

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.assets_service.log_business_event", mock_log)

    user = {"df_id": "df1", "email": "x"}

    res = await service.get_asset("a1", user, for_system=for_system)

    if get_asset_return:
        assert res["_id"] == "a1"
    else:
        assert res is None

    if expected_log_called:
        mock_log.assert_called_once()
    else:
        mock_log.assert_not_called()
