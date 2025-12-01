import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC
from bson import ObjectId
import re

from app.services.cookie_service import CookieManagementService
from app.crud.cookie_crud import CookieCrud
from app.services.assets_service import AssetService
from app.services.cookie_scan_service import CookieScanService, CookieScanError
from app.schemas.cookie_schema import CookieCreate, CookieInDB, CookieCategory, LanguageCodes
from app.schemas.assets_schema import MetaCookies
from app.core.logger import app_logger


@pytest.fixture
def mock_cookie_crud():
    return MagicMock(spec=CookieCrud)


@pytest.fixture
def mock_asset_service():
    return MagicMock(spec=AssetService)


@pytest.fixture
def mock_cookie_scan_service():
    return MagicMock(spec=CookieScanService)


@pytest.fixture
def cookie_management_service(mock_cookie_crud, mock_asset_service, mock_cookie_scan_service):
    return CookieManagementService(
        crud=mock_cookie_crud,
        asset_service=mock_asset_service,
        cookie_scan_service=mock_cookie_scan_service,
        business_logs_collection="test_logs",
    )


@pytest.fixture
def user_data():
    return {"_id": "user1", "email": "test@example.com", "df_id": "df123"}


@pytest.fixture
def sample_website_id():
    return str(ObjectId())


@pytest.fixture
def sample_cookie_data_create():
    return {
        "cookie_name": "session_id",
        "description": "Session tracking cookie.",
        "hostname": "example.com",
        "category": CookieCategory.ESSENTIAL,
        "lifespan": "session",
        "path": "/",
        "http_only": True,
        "secure": True,
        "same_site": "Lax",
        "is_third_party": False,
        "cookie_status": "draft",
        "translations": {"eng": "Session tracking cookie."},
    }


@pytest.fixture
def sample_cookie_in_db(sample_website_id, user_data):
    doc = CookieInDB(
        cookie_name="session_id",
        description="Session tracking cookie.",
        hostname="example.com",
        category=CookieCategory.ESSENTIAL,
        lifespan="session",
        path="/",
        http_only=True,
        secure=True,
        same_site="Lax",
        is_third_party=False,
        cookie_status="draft",
        translations={"eng": "Session tracking cookie."},
        source="manual",
        expiry=None,
        website_id=sample_website_id,
        df_id=user_data["df_id"],
        created_by=user_data["_id"],
        created_at=datetime.now(UTC),
        updated_by=None,
        updated_at=None,
    )

    data = doc.model_dump()
    data["_id"] = str(ObjectId())
    return data


def test_calculate_expiry_session(cookie_management_service):
    assert cookie_management_service._calculate_expiry("session") is None
    assert cookie_management_service._calculate_expiry("Session") is None


@pytest.mark.parametrize(
    "lifespan_str, expected_timedelta_args",
    [
        ("1 hour", {"hours": 1}),
        ("2 days", {"days": 2}),
        ("3 weeks", {"weeks": 3}),
        ("1 month", {"days": 30}),
        ("1 year", {"days": 365}),
        ("1 hours", {"hours": 1}),
    ],
)
def test_calculate_expiry_valid_lifespan(cookie_management_service, lifespan_str, expected_timedelta_args):
    now = datetime.now(UTC)
    expiry = cookie_management_service._calculate_expiry(lifespan_str)
    assert expiry is not None

    expected_expiry = now + timedelta(**expected_timedelta_args)
    assert abs((expiry - expected_expiry).total_seconds()) < 2


def test_calculate_expiry_invalid_lifespan(cookie_management_service):
    assert cookie_management_service._calculate_expiry("invalid") is None
    assert cookie_management_service._calculate_expiry("5 years and 2 months") is not None


@pytest.mark.parametrize(
    "epoch_value, expected_datetime",
    [
        (1672531200.0, datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)),
        (None, None),
    ],
)
def test_convert_epoch_to_datetime(cookie_management_service, epoch_value, expected_datetime):
    result = cookie_management_service._convert_epoch_to_datetime(epoch_value)
    assert result == expected_datetime


@pytest.mark.parametrize(
    "max_age, expires, expected_lifespan",
    [
        (3600, None, "1 hour"),
        (86400, None, "1 day"),
        (90000, None, "1 day 1 hour"),
        (None, None, "session"),
        (None, (datetime.now(UTC) + timedelta(days=2)).timestamp(), "2 days"),
        (None, (datetime.now(UTC) + timedelta(minutes=5)).timestamp(), "5 mins"),
    ],
)
def test_calculate_lifespan(cookie_management_service, max_age, expires, expected_lifespan):
    lifespan = cookie_management_service._calculate_lifespan(max_age, expires)

    if expires is not None:
        try:

            expiry_datetime = datetime.fromtimestamp(float(expires), tz=UTC)
            now_for_calc = datetime.now(UTC)
            diff = (expiry_datetime - now_for_calc).total_seconds()
            if diff > 0:

                assert cookie_management_service._format_duration(diff) == lifespan
            else:
                assert lifespan == "session"
        except Exception:
            assert lifespan == "session"
    elif max_age is not None:

        assert cookie_management_service._format_duration(max_age) == lifespan
    else:

        assert lifespan == expected_lifespan


@pytest.mark.parametrize(
    "seconds, expected_format",
    [
        (0, "less than a minute"),
        (30, "less than a minute"),
        (60, "1 min"),
        (120, "2 mins"),
        (3600, "1 hour"),
        (7200, "2 hours"),
        (86400, "1 day"),
        (172800, "2 days"),
        (3600 + 86400, "1 day 1 hour"),
        (60 + 3600 + 86400, "1 day 1 hour"),
    ],
)
def test_format_duration(cookie_management_service, seconds, expected_format):
    assert cookie_management_service._format_duration(seconds) == expected_format


@pytest.mark.asyncio
async def test_create_cookie_success(
    cookie_management_service, mock_cookie_crud, user_data, sample_website_id, sample_cookie_data_create, monkeypatch
):
    mock_cookie_crud.is_duplicate.return_value = False
    mock_cookie_crud.create_cookie.return_value = {
        **sample_cookie_data_create,
        "_id": str(ObjectId()),
        "website_id": sample_website_id,
        "df_id": user_data["df_id"],
        "created_at": datetime.now(UTC),
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.create_cookie(sample_website_id, user_data, sample_cookie_data_create)

    mock_cookie_crud.is_duplicate.assert_called_once()
    mock_cookie_crud.create_cookie.assert_called_once()
    mock_log.assert_called_once()
    assert result["cookie_name"] == sample_cookie_data_create["cookie_name"]
    assert result["website_id"] == sample_website_id
    assert result["df_id"] == user_data["df_id"]
    assert "created_at" in result


@pytest.mark.asyncio
async def test_create_cookie_duplicate(cookie_management_service, mock_cookie_crud, user_data, sample_website_id, sample_cookie_data_create):
    mock_cookie_crud.is_duplicate.return_value = True

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.create_cookie(sample_website_id, user_data, sample_cookie_data_create)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc.value.detail
    mock_cookie_crud.create_cookie.assert_not_called()


@pytest.mark.asyncio
async def test_create_cookie_failure(cookie_management_service, mock_cookie_crud, user_data, sample_website_id, sample_cookie_data_create):
    mock_cookie_crud.is_duplicate.return_value = False
    mock_cookie_crud.create_cookie.return_value = None

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.create_cookie(sample_website_id, user_data, sample_cookie_data_create)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to create cookie" in exc.value.detail
    mock_cookie_crud.create_cookie.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_cookies_for_website_success(
    cookie_management_service, mock_cookie_crud, user_data, sample_website_id, sample_cookie_in_db, monkeypatch
):
    mock_cookie_crud.get_cookies_for_website.return_value = {"data": [sample_cookie_in_db], "total": 1}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.get_all_cookies_for_website(sample_website_id, user_data, 1, 10)

    mock_cookie_crud.get_cookies_for_website.assert_called_once_with(sample_website_id, user_data["df_id"], offset=0, limit=10)

    mock_log.assert_called_once()
    assert result["total_items"] == 1
    assert len(result["cookies"]) == 1
    assert result["cookies"][0]["cookie_name"] == sample_cookie_in_db["cookie_name"]


@pytest.mark.asyncio
async def test_get_cookie_success(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db, monkeypatch):
    mock_cookie_crud.get_cookie_master.return_value = sample_cookie_in_db

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.get_cookie(sample_cookie_in_db["_id"], user_data)

    mock_cookie_crud.get_cookie_master.assert_called_once_with(
        sample_cookie_in_db["_id"],
        user_data["df_id"],
    )

    mock_log.assert_called_once()
    assert result["cookie_name"] == sample_cookie_in_db["cookie_name"]


@pytest.mark.asyncio
async def test_get_cookie_not_found(cookie_management_service, mock_cookie_crud, user_data, monkeypatch):
    mock_cookie_crud.get_cookie_master.return_value = None

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.get_cookie(str(ObjectId()), user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Cookie not found" in exc.value.detail
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_cookie_success(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db, monkeypatch):
    update_data = {"description": "Updated description."}
    updated_cookie_doc = {**sample_cookie_in_db, **update_data}

    mock_cookie_crud.get_cookie_master.return_value = sample_cookie_in_db
    mock_cookie_crud.is_duplicate.return_value = False
    mock_cookie_crud.update_cookie_master.return_value = {
        **updated_cookie_doc,
        "updated_by": user_data["_id"],
        "updated_at": datetime.now(UTC),
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.update_cookie(sample_cookie_in_db["_id"], user_data, update_data)

    mock_cookie_crud.get_cookie_master.assert_called_once()
    mock_cookie_crud.update_cookie_master.assert_called_once()
    mock_log.assert_called_once()
    assert result["description"] == "Updated description."
    assert "updated_at" in result
    assert result["updated_by"] == user_data["_id"]


@pytest.mark.asyncio
async def test_update_cookie_not_found(cookie_management_service, mock_cookie_crud, user_data):
    mock_cookie_crud.get_cookie_master.return_value = None

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.update_cookie(str(ObjectId()), user_data, {"description": "New"})

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Asset not found" in exc.value.detail


@pytest.mark.asyncio
async def test_update_cookie_not_draft(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    published_cookie = {**sample_cookie_in_db, "cookie_status": "published"}
    mock_cookie_crud.get_cookie_master.return_value = published_cookie

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.update_cookie(str(ObjectId()), user_data, {"description": "New"})

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only Cookies in draft status can be updated" in exc.value.detail


@pytest.mark.asyncio
async def test_update_cookie_duplicate_on_name_change(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    mock_cookie_crud.get_cookie_master.return_value = sample_cookie_in_db
    mock_cookie_crud.is_duplicate.return_value = True

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.update_cookie(str(ObjectId()), user_data, {"cookie_name": "existing_name"})

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc.value.detail


@pytest.mark.asyncio
async def test_delete_cookie_success(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db, monkeypatch):
    mock_cookie_crud.get_cookie_master.return_value = sample_cookie_in_db
    mock_cookie_crud.update_cookie_master.return_value = {**sample_cookie_in_db, "cookie_status": "archived"}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.delete_cookie(sample_cookie_in_db["_id"], user_data)

    mock_cookie_crud.get_cookie_master.assert_called_once()
    mock_cookie_crud.update_cookie_master.assert_called_once()
    mock_log.assert_called_once()
    assert result["cookie_status"] == "archived"


@pytest.mark.asyncio
async def test_delete_cookie_not_found(cookie_management_service, mock_cookie_crud, user_data):
    mock_cookie_crud.get_cookie_master.return_value = None

    result = await cookie_management_service.delete_cookie(str(ObjectId()), user_data)

    assert result is None
    mock_cookie_crud.update_cookie_master.assert_not_called()


@pytest.mark.asyncio
async def test_delete_cookie_already_archived(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    archived_cookie = {**sample_cookie_in_db, "cookie_status": "archived"}
    mock_cookie_crud.get_cookie_master.return_value = archived_cookie

    result = await cookie_management_service.delete_cookie(str(ObjectId()), user_data)

    assert result is None
    mock_cookie_crud.update_cookie_master.assert_not_called()


@pytest.mark.asyncio
async def test_publish_cookie_success(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db, monkeypatch):
    draft_cookie = {**sample_cookie_in_db, "cookie_status": "draft", "translations": {"eng": "Test Translation"}}
    published_cookie = {**draft_cookie, "cookie_status": "published"}

    mock_cookie_crud.get_cookie_master.return_value = draft_cookie
    mock_cookie_crud.update_cookie_master.return_value = published_cookie

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.publish_cookie(sample_cookie_in_db["_id"], user_data)

    mock_cookie_crud.get_cookie_master.assert_called_once()
    mock_cookie_crud.update_cookie_master.assert_called_once()
    mock_log.assert_called_once()
    assert result["cookie_status"] == "published"


@pytest.mark.asyncio
async def test_publish_cookie_not_found(cookie_management_service, mock_cookie_crud, user_data):
    mock_cookie_crud.get_cookie_master.return_value = None

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.publish_cookie(str(ObjectId()), user_data)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Cookie not found" in exc.value.detail


@pytest.mark.asyncio
async def test_publish_cookie_already_published(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    published_cookie = {**sample_cookie_in_db, "cookie_status": "published"}
    mock_cookie_crud.get_cookie_master.return_value = published_cookie

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.publish_cookie(str(ObjectId()), user_data)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "already published" in exc.value.detail


@pytest.mark.asyncio
async def test_publish_cookie_archived(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    archived_cookie = {**sample_cookie_in_db, "cookie_status": "archived"}
    mock_cookie_crud.get_cookie_master.return_value = archived_cookie

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.publish_cookie(str(ObjectId()), user_data)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot publish an archived Cookie" in exc.value.detail


@pytest.mark.asyncio
async def test_publish_cookie_missing_translations(cookie_management_service, mock_cookie_crud, user_data, sample_cookie_in_db):
    no_translation_cookie = {**sample_cookie_in_db, "cookie_status": "draft", "translations": {}}
    mock_cookie_crud.get_cookie_master.return_value = no_translation_cookie

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.publish_cookie(str(ObjectId()), user_data)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Translations are required" in exc.value.detail


@pytest.mark.asyncio
async def test_scan_website_cookies_success(
    cookie_management_service,
    mock_cookie_crud,
    mock_asset_service,
    mock_cookie_scan_service,
    user_data,
    sample_website_id,
    monkeypatch,
):
    mock_asset_service.get_asset.return_value = {"_id": sample_website_id, "usage_url": "http://test.com"}
    mock_asset_service.update_asset_cookie_fields.return_value = None
    mock_cookie_crud.is_duplicate.return_value = False
    mock_cookie_crud.create_cookie.return_value = {"_id": str(ObjectId()), "cookie_name": "scanned_cookie"}

    mock_scan_results = {
        "cookies": [
            {
                "name": "scanned_cookie_1",
                "domain": "test.com",
                "path": "/",
                "maxAge": 3600,
                "httpOnly": True,
                "secure": False,
                "sameSite": "Lax",
                "isThirdParty": False,
                "category": "essential",
                "purpose": "tracking",
            },
            {
                "name": "scanned_cookie_2",
                "domain": "test.com",
                "path": "/",
                "expires": (datetime.now(UTC) + timedelta(days=2)).timestamp(),
                "httpOnly": False,
                "secure": True,
                "sameSite": "Strict",
                "isThirdParty": False,
                "category": "analytics",
            },
        ]
    }
    mock_cookie_scan_service.scan.return_value = mock_scan_results

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.scan_website_cookies(user_data, sample_website_id, classify=True)

    mock_asset_service.get_asset.assert_called_once_with(asset_id=sample_website_id, user=user_data, for_system=True)
    mock_asset_service.update_asset_cookie_fields.assert_called()
    mock_cookie_scan_service.scan.assert_called_once_with(df_id=user_data["df_id"], url="http://test.com", classify=True)
    assert mock_cookie_crud.create_cookie.call_count == 2
    mock_log.assert_called_once()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_scan_website_cookies_no_asset(cookie_management_service, mock_asset_service, user_data, sample_website_id):
    mock_asset_service.get_asset.return_value = None

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.scan_website_cookies(user_data, sample_website_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Asset not found" in exc.value.detail


@pytest.mark.asyncio
async def test_scan_website_cookies_no_usage_url(cookie_management_service, mock_asset_service, user_data, sample_website_id):
    mock_asset_service.get_asset.return_value = {"_id": sample_website_id, "usage_url": None}

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.scan_website_cookies(user_data, sample_website_id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Asset does not have a usage_url" in exc.value.detail


@pytest.mark.asyncio
async def test_scan_website_cookies_scan_error(
    cookie_management_service, mock_asset_service, mock_cookie_scan_service, user_data, sample_website_id, monkeypatch
):
    mock_asset_service.get_asset.return_value = {"_id": sample_website_id, "usage_url": "http://test.com"}
    mock_asset_service.update_asset_cookie_fields.return_value = None
    mock_cookie_scan_service.scan.side_effect = CookieScanError("Scan failed")

    mock_log_event = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log_event)

    with pytest.raises(HTTPException) as exc:
        await cookie_management_service.scan_website_cookies(user_data, sample_website_id)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Cookie scanning failed" in exc.value.detail
    mock_log_event.assert_not_called()


@pytest.mark.asyncio
async def test_scan_website_cookies_duplicate_skipped(
    cookie_management_service, mock_cookie_crud, mock_asset_service, mock_cookie_scan_service, user_data, sample_website_id, monkeypatch
):
    mock_asset_service.get_asset.return_value = {"_id": sample_website_id, "usage_url": "http://test.com"}
    mock_asset_service.update_asset_cookie_fields.return_value = None
    mock_cookie_scan_service.scan.return_value = {"cookies": [{"name": "duplicate_cookie", "domain": "test.com", "path": "/", "maxAge": 3600}]}

    mock_cookie_crud.is_duplicate.return_value = True
    mock_cookie_crud.create_cookie.return_value = {"_id": str(ObjectId())}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.scan_website_cookies(user_data, sample_website_id)

    mock_cookie_crud.is_duplicate.assert_called_once()
    mock_cookie_crud.create_cookie.assert_not_called()
    mock_log.assert_called_once()
    assert len(result) == 0
    assert "cookies_skipped_count" in mock_log.call_args[1]["context"]
    assert mock_log.call_args[1]["context"]["cookies_skipped_count"] == 1


@pytest.mark.asyncio
async def test_get_all_websites_with_cookies_success(cookie_management_service, mock_asset_service, user_data, monkeypatch):
    mock_asset_service.get_all_assets.return_value = {
        "total_items": 1,
        "total_pages": 1,
        "assets": [{"_id": str(ObjectId()), "name": "Test Website"}],
    }

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.get_all_websites_with_cookies(user_data, 1, 10)

    mock_asset_service.get_all_assets.assert_called_once_with(user=user_data, current_page=1, data_per_page=10, category="Website")
    mock_log.assert_called_once()
    assert result["total_items"] == 1
    assert len(result["assets"]) == 1


@pytest.mark.asyncio
async def test_get_all_websites_with_cookies_empty(cookie_management_service, mock_asset_service, user_data, monkeypatch):
    mock_asset_service.get_all_assets.return_value = {"total_items": 0, "total_pages": 0, "assets": []}

    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.cookie_service.log_business_event", mock_log)

    result = await cookie_management_service.get_all_websites_with_cookies(user_data, 1, 10)

    assert result["total_items"] == 0
    assert len(result["assets"]) == 0
    mock_log.assert_called_once()
