import asyncio
import json
import uuid
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import aio_pika
import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.services.webhooks_service import WebhooksService
from app.schemas.webhooks_schema import WebhookCreate, WebhookUpdate

# -------------------------
# Fixtures & helpers
# -------------------------


@pytest.fixture
def mock_webhook_crud():
    return AsyncMock()


@pytest.fixture
def mock_webhook_event_crud():
    return AsyncMock()


@pytest.fixture
def business_logs_collection():
    return "test_business_logs"


@pytest.fixture
def service(mock_webhook_crud, mock_webhook_event_crud, business_logs_collection, monkeypatch):
    # Patch out logger to avoid noisy logs in tests
    monkeypatch.setattr("app.services.webhooks_service.log_business_event", AsyncMock())
    # Create service instance
    return WebhooksService(
        webhook_crud=mock_webhook_crud,
        business_logs_collection=business_logs_collection,
        webhook_event_crud=mock_webhook_event_crud,
    )


@pytest.fixture
def sample_user():
    return {"df_id": "df-123", "_id": "user-1", "email": "owner@example.com"}


# -------------------------
# create_webhook
# -------------------------


@pytest.mark.asyncio
async def test_create_webhook_success(service, mock_webhook_crud, sample_user):
    data = WebhookCreate(url="https://example.com/hook", webhook_for="df", environment="testing", dpr_id=None)
    mock_webhook_crud.get_webhook_by_url_and_df.return_value = None
    mock_webhook_crud.create_webhook.return_value = "new-webhook-id"

    result = await service.create_webhook(data, sample_user)

    assert result["message"] == "Webhook created successfully"
    assert "webhook_id" in result
    assert "secret_token" in result
    mock_webhook_crud.get_webhook_by_url_and_df.assert_awaited_once()
    mock_webhook_crud.create_webhook.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_webhook_duplicate_url(service, mock_webhook_crud, sample_user):
    data = WebhookCreate(url="https://example.com/hook", webhook_for="df", environment="testing", dpr_id=None)
    mock_webhook_crud.get_webhook_by_url_and_df.return_value = {"_id": "existing"}

    with pytest.raises(HTTPException) as exc:
        await service.create_webhook(data, sample_user)

    assert exc.value.status_code == 400
    mock_webhook_crud.get_webhook_by_url_and_df.assert_awaited_once()


# -------------------------
# get / list / list_paginated / delete
# -------------------------


@pytest.mark.asyncio
async def test_list_webhooks_success(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.list_all_webhooks_by_df.return_value = [{"_id": "w1"}, {"_id": "w2"}]
    res = await service.list_webhooks(sample_user)
    assert isinstance(res, list) and len(res) == 2
    mock_webhook_crud.list_all_webhooks_by_df.assert_awaited_once_with(sample_user["df_id"])


@pytest.mark.asyncio
async def test_list_paginated_webhooks_success(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.list_webhooks_by_df.return_value = {"total": 3, "data": [{"_id": "w1"}]}
    res = await service.list_paginated_webhooks(sample_user, current_page=1, data_per_page=2)
    assert res["total_items"] == 3
    assert res["total_pages"] == 2
    mock_webhook_crud.list_webhooks_by_df.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_webhook_success(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = {"_id": "w1", "url": "u"}
    out = await service.get_webhook("w1", sample_user)
    assert out["url"] == "u"
    mock_webhook_crud.get_webhook.assert_awaited_once_with("w1", sample_user["df_id"])


@pytest.mark.asyncio
async def test_get_webhook_not_found(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.get_webhook("w-not", sample_user)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_webhook_success(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = {"_id": "w1"}
    mock_webhook_crud.delete_webhook.return_value = True
    res = await service.delete_webhook("w1", sample_user)
    assert res["message"] == "Webhook deleted successfully"
    mock_webhook_crud.get_webhook.assert_awaited_once_with("w1", sample_user["df_id"])
    mock_webhook_crud.delete_webhook.assert_awaited_once_with("w1")


@pytest.mark.asyncio
async def test_delete_webhook_not_found(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.delete_webhook("w1", sample_user)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_webhook_db_failure(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = {"_id": "w1"}
    mock_webhook_crud.delete_webhook.return_value = False
    with pytest.raises(HTTPException) as exc:
        await service.delete_webhook("w1", sample_user)
    assert exc.value.status_code == 500


# -------------------------
# update_webhook (url conflict + activation path)
# -------------------------


@pytest.mark.asyncio
async def test_update_webhook_url_conflict(service, mock_webhook_crud, sample_user):
    webhook_id = "wh1"
    existing = {"_id": webhook_id, "url": "https://old", "status": "inactive", "environment": "testing"}
    mock_webhook_crud.get_webhook.return_value = existing
    # Simulate another webhook with the new URL
    mock_webhook_crud.get_webhook_by_url_and_df.return_value = {"_id": "other"}
    update = WebhookUpdate(url="https://other", status="inactive")
    with pytest.raises(HTTPException) as exc:
        await service.update_webhook(webhook_id, update, sample_user)
    assert exc.value.status_code == 400
    mock_webhook_crud.get_webhook.assert_awaited_once_with(webhook_id, sample_user["df_id"])


@pytest.mark.asyncio
async def test_update_webhook_activate_runs_test_and_updates(service, mock_webhook_crud, mock_webhook_event_crud, sample_user, monkeypatch):
    webhook_id = "wh1"
    existing = {"_id": webhook_id, "url": "https://old", "status": "inactive", "environment": "testing"}
    mock_webhook_crud.get_webhook.return_value = existing
    # Make test_webhook return success
    monkeypatch.setattr(service, "test_webhook", AsyncMock(return_value={"status": "success"}))
    mock_webhook_crud.update_webhook.return_value = {"_id": webhook_id, "status": "active"}

    update = WebhookUpdate(status="active")
    res = await service.update_webhook(webhook_id, update, sample_user)
    assert res["status"] == "active"
    mock_webhook_crud.update_webhook.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_webhook_not_found(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.update_webhook("w1", WebhookUpdate(status="active"), sample_user)
    assert exc.value.status_code == 404


# -------------------------
# test_webhook
# -------------------------


@pytest.mark.asyncio
async def test_test_webhook_success(service, mock_webhook_crud, sample_user, monkeypatch):
    # setup webhook in testing environment
    webhook_id = "wh-test"
    mock_webhook_crud.get_webhook.return_value = {"_id": webhook_id, "environment": "testing"}

    fake_conn = MagicMock()
    fake_channel = AsyncMock()

    # Fake message that mimics aio_pika.Message enough for our code
    class FakeMessage:
        def __init__(self, body_bytes, correlation_id):
            self.body = body_bytes
            self.correlation_id = correlation_id
            self._acked = False

        async def ack(self):
            self._acked = True

    # FakeQueue returns an object that is an async context manager and async iterator
    class FakeQueue:
        def __init__(self, expected_cid, payload):
            self.name = "reply-q"
            self._expected_cid = expected_cid
            self._payload = payload

        # IMPORTANT: this must be a regular function (not async) returning an async context manager
        def iterator(self, timeout=None):
            expected_cid = self._expected_cid
            payload = self._payload

            class _Iter:
                def __init__(self, expected_cid, payload):
                    self._expected_cid = expected_cid
                    self._payload = payload
                    self._sent = False

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if not self._sent:
                        self._sent = True
                        # create a FakeMessage with body bytes and matching correlation_id
                        body_bytes = json.dumps(self._payload).encode()
                        return FakeMessage(body_bytes, self._expected_cid)
                    raise StopAsyncIteration

            return _Iter(expected_cid, payload)

    # prepare fake reply payload and correlation id to match
    fake_cid = str(uuid.uuid4())
    fake_reply_payload = {"status": "ok", "message": "pong", "correlation_id": fake_cid}
    fake_reply_queue = FakeQueue(fake_cid, fake_reply_payload)

    # monkeypatch publish_message so _publish_webhook_event won't actually publish
    monkeypatch.setattr("app.services.webhooks_service.publish_message", AsyncMock())

    # fake rabbit pool returning (connection, channel)
    fake_rabbit_pool = MagicMock()
    fake_rabbit_pool.get_connection = AsyncMock(return_value=(fake_conn, fake_channel))
    fake_rabbit_pool.release_connection = AsyncMock()

    # channel.declare_queue should return our fake reply queue
    async def fake_declare_queue(*args, **kwargs):
        return fake_reply_queue

    fake_channel.declare_queue = AsyncMock(side_effect=fake_declare_queue)

    # attach fake pool to service
    service.rabbitmq_pool = fake_rabbit_pool

    # Now call test_webhook. It should find the fake reply and return its payload.
    res = await service.test_webhook(webhook_id, sample_user)

    assert isinstance(res, dict)
    assert res.get("status") == "ok"
    assert res.get("message") == "pong"


@pytest.mark.asyncio
async def test_test_webhook_not_found(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.test_webhook("not-exist", sample_user)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_test_webhook_wrong_environment(service, mock_webhook_crud, sample_user):
    mock_webhook_crud.get_webhook.return_value = {"_id": "w1", "environment": "production"}
    with pytest.raises(HTTPException) as exc:
        await service.test_webhook("w1", sample_user)
    assert exc.value.status_code == 403


# -------------------------
# _publish_webhook_event
# -------------------------


@pytest.mark.asyncio
async def test__publish_webhook_event_inserts_and_publishes(service, mock_webhook_event_crud, monkeypatch):
    webhook_id = "wh-pub"
    df_id = "df-x"
    dp_id = "dp-y"
    payload = {"foo": "bar"}

    # make create_event return an inserted id
    mock_webhook_event_crud.create_event.return_value = "inserted-id-123"

    # capture publish_message call
    pub_mock = AsyncMock()
    monkeypatch.setattr("app.services.webhooks_service.publish_message", pub_mock)

    # call method
    event_id = await service._publish_webhook_event(
        webhook_id=webhook_id, df_id=df_id, dp_id=dp_id, payload=payload, channel=None, correlation_id=None, reply_to=None, is_test=False
    )

    # verify DB create called
    mock_webhook_event_crud.create_event.assert_awaited_once()
    # verify publish called with expected exchange/routing (we just check it was awaited)
    pub_mock.assert_awaited_once()
    assert event_id == "inserted-id-123"


@pytest.mark.asyncio
async def test__publish_webhook_event_is_test_does_not_create_db(monkeypatch):
    # When is_test=True it should not call create_event and should use payload event_id if present
    webhook_id = "wh-test2"
    df_id = "df-x"
    dp_id = "dp-y"
    payload = {"event_id": "my-event-1", "x": 1}

    pub_mock = AsyncMock()
    monkeypatch.setattr("app.services.webhooks_service.publish_message", pub_mock)

    # instantiate a fresh service with a webhook_event_crud whose create_event would raise if called
    dummy_crud = AsyncMock()
    svc = WebhooksService(webhook_crud=AsyncMock(), business_logs_collection="b", webhook_event_crud=dummy_crud)
    # call
    event_id = await svc._publish_webhook_event(webhook_id=webhook_id, df_id=df_id, dp_id=dp_id, payload=payload, is_test=True)
    # publish called
    pub_mock.assert_awaited_once()
    # create_event must not have been called
    dummy_crud.create_event.assert_not_awaited()
    assert event_id == "my-event-1"
