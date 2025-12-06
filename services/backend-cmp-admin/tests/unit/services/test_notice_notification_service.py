import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import UTC, datetime
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse

from app.services.notice_notification_service import NoticeNotificationService
from app.crud.notice_notification_crud import NoticeNotificationCRUD

# pytest config
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_crud():
    return AsyncMock(spec=NoticeNotificationCRUD)


@pytest.fixture
def business_logs_collection():
    return "business_logs"


@pytest.fixture
def service(mock_crud, business_logs_collection):
    return NoticeNotificationService(crud=mock_crud, business_logs_collection=business_logs_collection)


@pytest.fixture
def sample_user():
    return {"_id": "user123", "email": "user@example.com", "df_id": "df123"}


@pytest.fixture(autouse=True)
def patch_logger_and_publish(monkeypatch):
    # Patch business logger to avoid noisy logs and to assert calls if needed
    mock_log = AsyncMock()
    monkeypatch.setattr("app.services.notice_notification_service.log_business_event", mock_log)

    # Patch publish_message that is imported in module
    mock_publish = AsyncMock()
    monkeypatch.setattr("app.services.notice_notification_service.publish_message", mock_publish)

    return {"log": mock_log, "publish": mock_publish}


async def test_send_notice_success(service, mock_crud, sample_user, patch_logger_and_publish):
    # Prepare a Pydantic-like object for notice_notification with model_dump()
    class FakeNotice:
        def model_dump(self):
            return {"title": "Test Notice", "dp_tags": ["t1", "t2"]}

    fake_result = MagicMock()
    fake_result.inserted_id = "ins123"
    mock_crud.insert_notice_notification.return_value = fake_result

    res = await service.send_notice(FakeNotice(), sample_user)

    # CRUD insert called
    mock_crud.insert_notice_notification.assert_awaited_once()
    # Rabbit publish called with expected queue and payload (json string)
    patch_logger_and_publish["publish"].assert_awaited_once()
    # response content
    assert res["message"] == "Notice Sent Successfully"
    assert res["notice_notification_id"] == "ins123"

    # verify business logger was called at least once
    patch_logger_and_publish["log"].assert_awaited()


async def test_send_notice_failed_raises_http_exception(service, mock_crud, sample_user, patch_logger_and_publish):
    class FakeNotice:
        def model_dump(self):
            return {"title": "Bad Notice"}

    mock_crud.insert_notice_notification.side_effect = Exception("db error")

    with pytest.raises(HTTPException) as excinfo:
        await service.send_notice(FakeNotice(), sample_user)

    assert excinfo.value.status_code == 500
    # logger should have been called with failure
    patch_logger_and_publish["log"].assert_awaited()


async def test_get_notifications_overview_success(service, mock_crud, sample_user, patch_logger_and_publish):
    # happy path: page and limit valid, df_id present
    mock_crud.get_total_notice_notifications_count.return_value = 5
    # return two sample notification dicts
    mock_crud.get_notice_notifications.return_value = [
        {"notification_id": "n1", "is_notification_read": False},
        {"notification_id": "n2", "is_notification_clicked": True},
    ]

    res = await service.get_notifications_overview(page=1, limit=2, current_user=sample_user)

    mock_crud.get_total_notice_notifications_count.assert_awaited_once_with("df123")
    mock_crud.get_notice_notifications.assert_awaited_once()
    assert "notifications" in res
    assert "pagination" in res
    # ensure booleans are normalized
    assert isinstance(res["notifications"][0]["is_notification_read"], bool)
    # logger called
    patch_logger_and_publish["log"].assert_awaited()


@pytest.mark.parametrize(
    "page,limit,expected_status",
    [
        (0, 10, 400),
        (1, 0, 400),
    ],
)
async def test_get_notifications_overview_invalid_pagination_raises(service, page, limit, sample_user, expected_status):
    with pytest.raises(HTTPException) as excinfo:
        await service.get_notifications_overview(page=page, limit=limit, current_user=sample_user)
    assert excinfo.value.status_code == expected_status


async def test_get_notifications_overview_missing_df(service, sample_user, mock_crud):
    # user missing df_id
    user_no_df = {"_id": "u1", "email": "a@b.com"}
    with pytest.raises(HTTPException) as excinfo:
        await service.get_notifications_overview(page=1, limit=10, current_user=user_no_df)
    assert excinfo.value.status_code == 400


async def test_track_pixel_success(service, mock_crud, patch_logger_and_publish):
    # mark_notification_as_read should be awaited
    mock_crud.mark_notification_as_read.return_value = "OK"
    # call and assert StreamingResponse returned and DB update called
    res = await service.track_pixel(event_id="evt1")
    mock_crud.mark_notification_as_read.assert_awaited_once_with("evt1")
    # should return a StreamingResponse containing a 1x1 png
    assert isinstance(res, StreamingResponse)
    patch_logger_and_publish["log"].assert_awaited()


async def test_track_pixel_failure_logs_and_raises(service, mock_crud, patch_logger_and_publish):
    mock_crud.mark_notification_as_read.side_effect = Exception("db fail")
    with pytest.raises(HTTPException) as excinfo:
        await service.track_pixel(event_id="evt-x")
    assert excinfo.value.status_code == 500
    patch_logger_and_publish["log"].assert_awaited()


async def test_track_click_ln_and_mln_success(service, mock_crud, monkeypatch, patch_logger_and_publish):
    # patch settings used to build redirect URL
    monkeypatch.setattr(
        "app.services.notice_notification_service.settings",
        MagicMock(CMP_NOTICE_WORKER_URL="http://worker", SMS_SENDER_ID="SENDER"),
    )
    mock_crud.mark_notification_as_clicked.return_value = "OK"

    # ln type
    resp_ln = await service.track_click(event_id="e1", token="tok123", url_type="ln")
    mock_crud.mark_notification_as_clicked.assert_awaited_with("e1")
    assert isinstance(resp_ln, RedirectResponse)
    assert resp_ln.status_code in (307, 302, 301)
    # RedirectResponse stores location header in headers
    assert resp_ln.headers["location"].startswith("http://worker/api/v1/ln/")

    # mln type
    resp_mln = await service.track_click(event_id="e2", token="tok-mln", url_type="mln")
    assert isinstance(resp_mln, RedirectResponse)
    assert resp_mln.headers["location"].endswith("/mln/tok-mln")
    patch_logger_and_publish["log"].assert_awaited()


async def test_track_click_unknown_type_raises(service, mock_crud, patch_logger_and_publish):
    mock_crud.mark_notification_as_clicked.return_value = "OK"
    with pytest.raises(HTTPException) as excinfo:
        await service.track_click(event_id="e1", token="t", url_type="unknown")
    assert excinfo.value.status_code == 400
    patch_logger_and_publish["log"].assert_awaited()
