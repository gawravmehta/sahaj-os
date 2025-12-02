import logging
import os
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from fastapi import Request
from opensearchpy import OpenSearch
from app.core.logger import app_logger
from app.core.request_context import get_request
from app.core.config import settings


async def extract_request_info(request: Optional[Request]) -> Optional[Dict[str, Any]]:
    if not request:
        return None
    try:
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8") if body_bytes else None
    except Exception:
        body = None

    headers = dict(request.headers)
    if "authorization" in headers:
        headers["authorization"] = "***masked***"

    return {
        "method": request.method,
        "url": str(request.url),
        "headers": headers,
        "query_params": dict(request.query_params),
        "path_params": getattr(request, "path_params", {}),
        "client": request.client.host if request.client else None,
        "body": body,
    }


opensearch_client = OpenSearch(
    hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
    http_auth=(settings.OPENSEARCH_USERNAME, settings.TEMPORARY_PASSWORD),
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


async def log_business_event(
    *,
    event_type: str,
    user_email: str,
    context: Dict[str, Any],
    message: str,
    business_logs_collection: str,
    log_level: str = "INFO",
    error_details: Optional[str] = None,
) -> None:
    """
    Logs a business-level event to OpenSearch and application logger.
    Production-ready version with env, service, event_type, and more.
    """

    try:
        request = get_request()
        request_info = await extract_request_info(request) if request else None

        request_id = getattr(request.state, "request_id", None) if request else None
        client_ip = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None

        opensearch_doc = {
            "@timestamp": datetime.now(UTC).isoformat(),
            "environment": settings.ENVIRONMENT,
            "service": settings.SERVICE_NAME,
            "log_level": log_level,
            "event_type": event_type,
            "message": message,
            "context": context,
            "user_email": user_email,
            "request_id": request_id,
            "request": request_info,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "error_details": error_details,
        }

        app_logger.info(f"Business Log: {message}", extra={"user_email": user_email, "event": event_type})

        try:
            opensearch_client.index(
                index=business_logs_collection,
                body=opensearch_doc,
                refresh=False,
            )
        except Exception as os_e:
            app_logger.error(f"Failed to log business event to OpenSearch: {os_e}", exc_info=True)

    except Exception as e:
        app_logger.error(f"Failed to log business event: {e}", exc_info=True)
