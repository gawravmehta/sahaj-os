import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, ANY
from fastapi import status

from app.schemas.assets_schema import BusinessLogsResponse

from app.main import app


client = TestClient(app, raise_server_exceptions=False)
# FIX: Changed BASE_URL to a simpler prefix, assuming the router is mounted 
# at /api/v1 and the endpoint path includes /logs/business.
BASE_URL = "/api/v1/business-logs"


@pytest.fixture
def mock_opensearch_client_patch(monkeypatch):
    mock_client = MagicMock()

    mock_client.search.return_value = {}

    # The patch path is correct assuming opensearch_client is imported from app.utils.business_logger
    with patch("app.utils.business_logger.opensearch_client", new=mock_client) as mock:
        yield mock


@pytest.fixture
def mock_opensearch_response():
    """Defines a standardized response structure from OpenSearch."""
    return {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "message": "Log 1",
                        "user_email": "user1@a.com",
                        "event_type": "CREATE",
                        "log_level": "INFO",
                        "@timestamp": "2023-10-20T10:00:00Z",
                    }
                },
                {
                    "_source": {
                        "message": "Log 2",
                        "user_email": "user2@b.com",
                        "event_type": "DELETE",
                        "log_level": "ERROR",
                        "@timestamp": "2023-10-20T10:05:00Z",
                    }
                },
            ],
            "total": {"value": 150},
        },
        "aggregations": {
            "log_levels": {
                "buckets": [
                    {"key": "INFO", "doc_count": 100},
                    {"key": "ERROR", "doc_count": 30},
                    {"key": "WARNING", "doc_count": 20},
                ]
            },
            "unique_events": {
                "buckets": [{"key": "CREATE"}, {"key": "DELETE"}],
            },
            "unique_user_emails": {
                "buckets": [{"key": "user1@a.com"}, {"key": "user2@b.com"}],
            },
        },
    }


def test_get_business_logs_default_success(mock_opensearch_client_patch, mock_opensearch_response):
    """Tests the endpoint with default parameters (page 1, size 20, no filters)."""
    mock_opensearch_client_patch.search.return_value = mock_opensearch_response

    # Test call path is now /api/v1/logs/business
    res = client.get(f"{BASE_URL}/logs/business")

    assert res.status_code == status.HTTP_200_OK

    # Assert that opensearch_client.search was called
    mock_opensearch_client_patch.search.assert_called_once() 
    
    _, kwargs = mock_opensearch_client_patch.search.call_args
    query_body = kwargs["body"]

    assert kwargs["index"] == "app-logs-business"
    assert query_body["from"] == 0
    assert query_body["size"] == 20
    assert query_body["query"]["bool"]["must"] == [{"match_all": {}}]
    assert query_body["sort"] == [{"@timestamp": {"order": "desc"}}]

    response_data = BusinessLogsResponse.model_validate(res.json())

    assert response_data.statistics.total_logs == 150
    assert response_data.statistics.errors == 30
    assert response_data.statistics.info == 100

    assert response_data.pagination.current_page == 1
    assert response_data.pagination.total_items == 150
    assert response_data.pagination.total_pages == 8
    assert response_data.pagination.has_next is True
    assert response_data.pagination.has_previous is False

    assert len(response_data.logs) == 2
    assert response_data.logs[0]["message"] == "Log 1"


@pytest.mark.parametrize(
    "query_params, expected_must_clauses, expected_from_offset",
    [
        ({"current_page": 2, "data_per_page": 50}, [{"match_all": {}}], 50),
        ({"user_email": "test@user.com"}, [{"term": {"user_email.keyword": "test@user.com"}}], 0),
        ({"log_level": "error"}, [{"term": {"log_level.keyword": "ERROR"}}], 0),
        (
            {"search": "asset creation"},
            [{"multi_match": {"query": "asset creation", "fields": ["message", "event_type", "user_email"], "type": "phrase_prefix"}}],
            0,
        ),
        # Note: Datetime query params need to match the format expected by FastAPI/httpx
        ({"start_time": "2023-01-01T12:00:00Z"}, [{"range": {"@timestamp": {"gte": "2023-01-01T12:00:00Z"}}}], 0),
        ({"end_time": "2023-01-31T12:00:00Z"}, [{"range": {"@timestamp": {"lte": "2023-01-31T12:00:00Z"}}}], 0),
        (
            {"user_email": "filter@test.com", "event_type": "UPDATE", "log_level": "warning", "search": "important"},
            [
                {"term": {"user_email.keyword": "filter@test.com"}},
                {"term": {"event_type.keyword": "UPDATE"}},
                {"term": {"log_level.keyword": "WARNING"}},
                {"multi_match": {"query": "important", "fields": ["message", "event_type", "user_email"], "type": "phrase_prefix"}},
            ],
            0,
        ),
    ],
)
def test_get_business_logs_query_construction(
    mock_opensearch_client_patch, mock_opensearch_response, query_params, expected_must_clauses, expected_from_offset
):
    """Tests if the OpenSearch query body is constructed correctly based on query parameters."""
    mock_opensearch_client_patch.search.return_value = mock_opensearch_response

    res = client.get(f"{BASE_URL}/logs/business", params=query_params)

    assert res.status_code == status.HTTP_200_OK
    
    # Assert that opensearch_client.search was called
    mock_opensearch_client_patch.search.assert_called_once()

    _, kwargs = mock_opensearch_client_patch.search.call_args
    query_body = kwargs["body"]

    if expected_must_clauses == [{"match_all": {}}] and not any(k not in ["current_page", "data_per_page"] for k in query_params.keys()):
        assert query_body["query"]["bool"]["must"] == [{"match_all": {}}]
    elif expected_must_clauses == [{"match_all": {}}] and ("current_page" in query_params or "data_per_page" in query_params):
        assert query_body["query"]["bool"]["must"] == [{"match_all": {}}]
    else:
        assert query_body["query"]["bool"]["must"] == expected_must_clauses

    assert query_body["from"] == expected_from_offset
    
    # Reset mock after each test run in the loop
    mock_opensearch_client_patch.search.reset_mock()


@pytest.mark.parametrize(
    "query_params",
    [
        {"current_page": 0},
        {"data_per_page": 0},
        {"data_per_page": 101},
        {"start_time": "not-a-datetime"},
    ],
)
def test_get_business_logs_validation_failures(mock_opensearch_client_patch, query_params):
    """Tests FastAPI's Pydantic validation for query parameters."""

    mock_opensearch_client_patch.search.return_value = mock_opensearch_response

    res = client.get(f"{BASE_URL}/logs/business", params=query_params)

    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in res.json()