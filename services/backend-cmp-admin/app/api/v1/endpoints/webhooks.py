from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any, List, Optional


from app.api.v1.deps import get_current_user, get_webhooks_service
from app.services.webhooks_service import WebhooksService

from app.schemas.webhooks_schema import WebhookCreate, WebhookResponse, WebhookUpdate, WebhookPaginatedResponse

router = APIRouter()


@router.post(
    "/create-webhook",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new webhook configuration",
)
async def create_webhook_endpoint(
    webhook_data: WebhookCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
):
    """
    Creates a new webhook configuration (URL, event types, secret) for the user's DF.
    """
    try:
        response = await service.create_webhook(webhook_data, current_user)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-all-webhooks",
    summary="Retrieve all active webhooks for the current DF",
    response_model=WebhookPaginatedResponse,
)
async def get_all_webhooks_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
    current_page: int = Query(1, ge=1, description="Current page number"),
    data_per_page: int = Query(20, ge=1, le=100, description="Number of items per page"),
):
    """
    Retrieves all non-deleted webhook configurations belonging to the current user's DF.
    """
    try:
        webhooks = await service.list_paginated_webhooks(current_user, current_page, data_per_page)
        return webhooks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/get-one-webhook/{webhook_id}",
    response_model=WebhookResponse,
    summary="Retrieve a specific webhook by ID",
)
async def get_webhook_by_id_endpoint(
    webhook_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
):
    """
    Retrieves a single webhook configuration by its ID, enforcing DF ownership.
    """
    try:
        webhook = await service.get_webhook(webhook_id, current_user)
        return webhook
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/update-webhook/{webhook_id}",
    response_model=WebhookResponse,
    summary="Update an existing webhook configuration",
)
async def update_webhook_endpoint(
    webhook_id: str,
    update_data: WebhookUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
):
    """
    Updates the fields of an existing webhook configuration by ID.
    """
    try:

        response = await service.update_webhook(webhook_id, update_data, current_user)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/delete-webhook/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete (soft-delete) a webhook configuration",
)
async def delete_webhook_endpoint(
    webhook_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
):
    """
    Soft-deletes a webhook configuration by ID, preventing further notifications.
    """
    try:
        await service.delete_webhook(webhook_id, current_user)
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/test/{webhook_id}",
    summary="Send a test payload to a configured webhook URL",
)
async def test_webhook_endpoint(
    webhook_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: WebhooksService = Depends(get_webhooks_service),
):
    """
    Triggers an immediate test fire of the specified webhook to check connectivity and configuration.
    """

    response = await service.test_webhook(webhook_id, current_user)
    return response
