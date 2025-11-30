import pytest
from unittest.mock import MagicMock

from fastapi import Request
from app.utils.business_logger import log_business_event, extract_request_info


class FakeClient:
    host = "127.0.0.1"


class FakeRequest(Request):
    def __init__(self, method="GET", url="http://test.com", body=b"{}", headers=None):
        scope = {
            "type": "http",
            "method": method,
            "path": "/",
        }
        super().__init__(scope)

        self._method = method
        self._url = url
        self._body = body
        self._headers = headers or {
            "authorization": "Bearer token",
            "user-agent": "pytest-agent",
        }

    # --------- READ-ONLY PROPERTIES (override) ----------
    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def client(self):
        return FakeClient()

    @property
    def headers(self):
        return self._headers

    @property
    def query_params(self):
        return {"q": "1"}

    @property
    def path_params(self):
        return {"id": "123"}

    # --------- BODY HANDLER ----------
    async def body(self):
        return self._body


# -------------------------------------------------------------------
# extract_request_info TESTS
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_request_info_success():
    req = FakeRequest()
    data = await extract_request_info(req)

    assert data["method"] == "GET"
    assert data["url"] == "http://test.com"
    assert data["client"] == "127.0.0.1"
    assert data["headers"]["authorization"] == "***masked***"
    assert data["body"] == "{}"


@pytest.mark.asyncio
async def test_extract_request_info_no_request():
    assert await extract_request_info(None) is None


@pytest.mark.asyncio
async def test_extract_request_info_body_error(monkeypatch):
    req = FakeRequest()

    async def bad_body():
        raise Exception("fail")

    monkeypatch.setattr(req, "body", bad_body)

    data = await extract_request_info(req)
    assert data["body"] is None


# -------------------------------------------------------------------
# log_business_event TESTS
# -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_business_event_success(monkeypatch):
    fake_os = MagicMock()
    fake_logger = MagicMock()
    fake_logger.info = MagicMock()
    fake_logger.error = MagicMock()

    monkeypatch.setattr("app.utils.business_logger.opensearch_client", fake_os)
    monkeypatch.setattr("app.utils.business_logger.app_logger", fake_logger)
    monkeypatch.setattr("app.utils.business_logger.get_request", lambda: FakeRequest())

    await log_business_event(
        event_type="TEST",
        user_email="test@x.com",
        context={"a": 1},
        message="OK",
        business_logs_collection="logs",
    )

    fake_os.index.assert_called_once()
    fake_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_log_business_event_opensearch_failure(monkeypatch):
    fake_logger = MagicMock()
    fake_logger.info = MagicMock()
    fake_logger.error = MagicMock()

    fake_os = MagicMock()
    fake_os.index.side_effect = Exception("OS down")

    monkeypatch.setattr("app.utils.business_logger.opensearch_client", fake_os)
    monkeypatch.setattr("app.utils.business_logger.app_logger", fake_logger)
    monkeypatch.setattr("app.utils.business_logger.get_request", lambda: FakeRequest())

    await log_business_event(
        event_type="ERR",
        user_email="a@a.com",
        context={},
        message="Oops",
        business_logs_collection="logs",
    )

    fake_logger.info.assert_called_once()  # original log
    fake_logger.error.assert_called_once()  # OS error logged


@pytest.mark.asyncio
async def test_log_business_event_extract_request_fails(monkeypatch):
    fake_os = MagicMock()
    fake_logger = MagicMock()
    fake_logger.info = MagicMock()
    fake_logger.error = MagicMock()

    monkeypatch.setattr("app.utils.business_logger.opensearch_client", fake_os)
    monkeypatch.setattr("app.utils.business_logger.app_logger", fake_logger)

    # invalid request object (string)
    monkeypatch.setattr("app.utils.business_logger.get_request", lambda: "INVALID")

    await log_business_event(
        event_type="ERR2",
        user_email="x@x.com",
        context={},
        message="bad",
        business_logs_collection="logs",
    )

    fake_logger.error.assert_called_once()
    fake_logger.info.assert_not_called()
