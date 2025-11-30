from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from app.schemas.assets_schema import (
    BusinessLogsResponse,
    LogFilters,
    LogPaginationMeta,
    LogStatistics,
)
from app.utils.business_logger import opensearch_client

router = APIRouter()


@router.get("/logs/business", response_model=BusinessLogsResponse)
def get_business_logs(
    current_page: int = Query(1, ge=1, description="Current page number"),
    data_per_page: int = Query(20, ge=1, le=100, description="Number of items per page"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    log_level: Optional[str] = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    start_time: Optional[datetime] = Query(None, description="Filter logs from this time"),
    end_time: Optional[datetime] = Query(None, description="Filter logs until this time"),
    search: Optional[str] = Query(None, description="Search in message, event_type, and user_email"),
):

    must_clauses = []

    if user_email is not None:
        must_clauses.append({"term": {"user_email.keyword": user_email}})
    if event_type is not None:
        must_clauses.append({"term": {"event_type.keyword": event_type}})
    if log_level is not None:
        must_clauses.append({"term": {"log_level.keyword": log_level.upper()}})

    if start_time is not None or end_time is not None:
        range_clause = {}
        if start_time is not None:
            range_clause["gte"] = start_time.isoformat() + "Z"
        if end_time is not None:
            range_clause["lte"] = end_time.isoformat() + "Z"
        must_clauses.append({"range": {"@timestamp": range_clause}})

    if search is not None and search.strip():
        must_clauses.append({"multi_match": {"query": search, "fields": ["message", "event_type", "user_email"], "type": "phrase_prefix"}})

    from_offset = (current_page - 1) * data_per_page

    query_body = {
        "query": {"bool": {"must": must_clauses if must_clauses else [{"match_all": {}}]}},
        "sort": [{"@timestamp": {"order": "desc"}}],
        "from": from_offset,
        "size": data_per_page,
        "aggs": {
            "log_levels": {"terms": {"field": "log_level.keyword", "size": 10}},
            "unique_events": {"terms": {"field": "event_type.keyword", "size": 100}},
            "unique_user_emails": {"terms": {"field": "user_email.keyword", "size": 100}},
        },
    }

    resp = opensearch_client.search(index="app-logs-business", body=query_body)

    hits = resp["hits"]["hits"]
    total_items = resp["hits"]["total"]["value"]

    log_level_buckets = resp["aggregations"]["log_levels"]["buckets"]
    log_level_counts = {bucket["key"]: bucket["doc_count"] for bucket in log_level_buckets}

    statistics = LogStatistics(
        total_logs=total_items,
        errors=log_level_counts.get("ERROR", 0),
        warnings=log_level_counts.get("WARNING", 0),
        info=log_level_counts.get("INFO", 0),
    )

    event_buckets = resp["aggregations"]["unique_events"]["buckets"]
    unique_events = [bucket["key"] for bucket in event_buckets]

    user_email_buckets = resp["aggregations"]["unique_user_emails"]["buckets"]
    unique_user_emails = [bucket["key"] for bucket in user_email_buckets]

    available_filters = LogFilters(events=unique_events, user_emails=unique_user_emails)

    total_pages = (total_items + data_per_page - 1) // data_per_page if total_items > 0 else 1
    has_next = current_page < total_pages
    has_previous = current_page > 1

    pagination = LogPaginationMeta(
        current_page=current_page,
        data_per_page=data_per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )

    logs = [hit["_source"] for hit in hits]

    return BusinessLogsResponse(statistics=statistics, available_filters=available_filters, pagination=pagination, logs=logs)
