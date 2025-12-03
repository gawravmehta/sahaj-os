import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.event_classification_service import EventClassificationService


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_webhooks_service():
    service = AsyncMock()
    service.list_webhooks = AsyncMock()
    service._publish_webhook_event = AsyncMock()
    return service


@pytest.fixture
def classification_service(mock_webhooks_service):
    return EventClassificationService(webhooks_service=mock_webhooks_service)


def sample_event():
    return {
        "event_type": "consent_given",
        "df_id": "df123",
        "dp_id": "dp789",
        "purposes": [
            {
                "purpose_id": "p1",
                "data_processors": [{"data_processor_id": "dpr1"}]
            }
        ],
        "data_elements": [
            {
                "title": "de1",
                "consents": [
                    {
                        "consent_id": "c1",
                        "data_processors": [{"data_processor_id": "dpr1"}],
                        "purpose_hash_id": "remove",
                        "consent_mode": "remove",
                    }
                ],
                "de_hash_id": "remove",
                "de_status": "remove"
            }
        ],
    }

async def test_filter_payload_removes_hash_fields(classification_service):
    event = sample_event()

    filtered = classification_service._filter_payload(event)

    assert "purpose_hash_id" not in filtered["data_elements"][0]["consents"][0]
    assert "consent_mode" not in filtered["data_elements"][0]["consents"][0]
    assert "de_hash_id" not in filtered["data_elements"][0]
    assert "de_status" not in filtered["data_elements"][0]

async def test_classify_and_publish_event_missing_df_id(classification_service):
    event = sample_event()
    event["df_id"] = None

    result = await classification_service.classify_and_publish_event(event)

    assert result == {"status": "failed", "reason": "df_id missing"}

async def test_classify_no_webhooks_found(classification_service, mock_webhooks_service):
    event = sample_event()
    mock_webhooks_service.list_webhooks.return_value = []

    result = await classification_service.classify_and_publish_event(event)

    assert result["status"] == "classified"
    assert result["reason"] == "no webhooks found"
    mock_webhooks_service._publish_webhook_event.assert_not_called()

async def test_classify_publish_to_df_webhook(classification_service, mock_webhooks_service):
    event = sample_event()

    mock_webhooks_service.list_webhooks.return_value = [
        {
            "_id": "w1",
            "webhook_for": "df",
            "subscribed_events": ["CONSENT_GIVEN"]
        }
    ]

    mock_webhooks_service._publish_webhook_event.return_value = "evt123"

    result = await classification_service.classify_and_publish_event(event)

    mock_webhooks_service._publish_webhook_event.assert_called_once()

    assert result["status"] == "classified and published"
    assert result["event_ids"] == ["evt123"]

async def test_classify_df_webhook_not_subscribed(classification_service, mock_webhooks_service):
    event = sample_event()

    mock_webhooks_service.list_webhooks.return_value = [
        {
            "_id": "w1",
            "webhook_for": "df",
            "subscribed_events": ["CONSENT_WITHDRAWN"]  # does NOT match
        }
    ]

    result = await classification_service.classify_and_publish_event(event)

    mock_webhooks_service._publish_webhook_event.assert_not_called()
    assert result["event_ids"] == []

async def test_classify_publish_to_dpr_webhook(classification_service, mock_webhooks_service):
    event = sample_event()

    mock_webhooks_service.list_webhooks.return_value = [
        {
            "_id": "w2",
            "webhook_for": "dpr",
            "dpr_id": "dpr1",
            "subscribed_events": ["CONSENT_GIVEN"],
        }
    ]

    mock_webhooks_service._publish_webhook_event.return_value = "evt456"

    result = await classification_service.classify_and_publish_event(event)

    # Must publish because DPR ID is found inside event payload
    mock_webhooks_service._publish_webhook_event.assert_called_once()

    assert result["event_ids"] == ["evt456"]

async def test_classify_dpr_webhook_not_matching_dpr(classification_service, mock_webhooks_service):
    event = sample_event()

    mock_webhooks_service.list_webhooks.return_value = [
        {
            "_id": "w2",
            "webhook_for": "dpr",
            "dpr_id": "unknown_dpr",
            "subscribed_events": ["CONSENT_GIVEN"],
        }
    ]

    result = await classification_service.classify_and_publish_event(event)

    mock_webhooks_service._publish_webhook_event.assert_not_called()
    assert result["event_ids"] == []

async def test_event_classification_logic(classification_service):
    event = sample_event()

    result = await classification_service.classify_and_publish_event(event)

    # inside the payload sent out, classification should exist
    args, kwargs = classification_service.webhooks_service._publish_webhook_event.call_args
    payload_sent = kwargs["payload"]

    assert payload_sent["classification"] == "approved"
    assert "classification_timestamp" in payload_sent

