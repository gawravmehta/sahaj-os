import asyncio
import json
import aio_pika
import uuid
from fastapi import HTTPException
from datetime import UTC, datetime, timezone
from typing import Dict, Any, List, Optional
import hmac
import hashlib
import secrets
from bson import ObjectId

import httpx

from app.schemas.webhooks_schema import AuthConfig, RetryPolicy, WebhookMetrics, WebhookCreate, WebhookUpdate, WebhookInDB
from app.utils.business_logger import log_business_event
from app.crud.webhooks_crud import WebhooksCrud
from app.schemas.webhook_events_schema import WebhookEventInDB
from app.crud.webhook_events_crud import WebhookEventCRUD
from typing import Optional
from app.db.rabbitmq import publish_message, rabbitmq_pool


class WebhooksService:
    def __init__(self, webhook_crud: WebhooksCrud, business_logs_collection: str, webhook_event_crud: WebhookEventCRUD):
        self.webhook_crud = webhook_crud
        self.business_logs_collection = business_logs_collection
        self.webhook_event_crud = webhook_event_crud
        self.rabbitmq_pool = rabbitmq_pool

    async def create_webhook(self, webhook_data: WebhookCreate, current_user: Dict[str, Any]):
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")
        webhook_url = str(webhook_data.url)

        existing = await self.webhook_crud.get_webhook_by_url_and_df(webhook_url, df_id)
        if existing:
            await log_business_event(
                event_type="WEBHOOK_CREATION_FAILED",
                user_email=user_email,
                message="Webhook creation failed: URL already registered",
                log_level="WARNING",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_url": webhook_url, "reason": "Webhook URL already registered for this DF"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=400, detail="Webhook URL already registered for this DF")

        secret_token = secrets.token_hex(32)
        auth = AuthConfig(type="header", key="X-Consent-Signature", secret=secret_token)
        retry_policy = RetryPolicy()
        metrics = WebhookMetrics()

        hmac_token = hmac.new(key=auth.secret.encode(), msg=webhook_url.encode(), digestmod=hashlib.sha256).hexdigest()

        webhook_db_obj = WebhookInDB(
            url=webhook_url,
            webhook_for=webhook_data.webhook_for,
            dpr_id=webhook_data.dpr_id,
            environment=webhook_data.environment,
            created_by=user_id,
            df_id=df_id,
            auth=auth,
            retry_policy=retry_policy,
            metrics=metrics,
        )

        webhook_dict = webhook_db_obj.model_dump()
        webhook_dict["hmac_token"] = hmac_token
        webhook_id = await self.webhook_crud.create_webhook(webhook_dict)

        await log_business_event(
            event_type="WEBHOOK_CREATED",
            user_email=user_email,
            message="Webhook created successfully",
            log_level="INFO",
            context={"user_id": str(user_id), "webhook_id": str(webhook_id), "df_id": df_id, "webhook_url": webhook_url},
            business_logs_collection=self.business_logs_collection,
        )

        return {"message": "Webhook created successfully", "webhook_id": str(webhook_id), "secret_token": secret_token}

    async def update_webhook(self, webhook_id: str, update_data: WebhookUpdate, current_user: Dict[str, Any]):
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")

        existing = await self.webhook_crud.get_webhook(webhook_id, df_id)
        if not existing:
            await log_business_event(
                event_type="WEBHOOK_UPDATE_FAILED",
                user_email=user_email,
                message="Webhook update failed: Webhook not found",
                log_level="WARNING",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": "Webhook not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Webhook not found")

        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

        if "url" in update_dict:
            update_dict["url"] = str(update_dict["url"])
            new_url = update_dict["url"]
            if new_url != existing["url"]:

                url_conflict = await self.webhook_crud.get_webhook_by_url_and_df(new_url, df_id)
                if url_conflict:
                    await log_business_event(
                        event_type="WEBHOOK_UPDATE_FAILED",
                        user_email=user_email,
                        message="Webhook update failed: URL conflict",
                        log_level="WARNING",
                        context={
                            "user_id": str(user_id),
                            "df_id": df_id,
                            "webhook_id": webhook_id,
                            "new_url": new_url,
                            "reason": "Another webhook with this URL already exists for this DF",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(status_code=400, detail="Another webhook with this URL already exists for this DF")

        update_dict["updated_at"] = datetime.now(UTC)
        update_dict["updated_by"] = current_user["_id"]

        if update_data.status == "active" and existing["status"] != "active":
            try:
                original_environment = existing.get("environment")
                if original_environment != "testing":
                    pass

                test_result = await self.test_webhook(webhook_id, current_user)
                if test_result.get("status") != "success":
                    await log_business_event(
                        event_type="WEBHOOK_ACTIVATION_FAILED",
                        user_email=user_email,
                        message="Webhook activation failed: Test event failed",
                        log_level="ERROR",
                        context={
                            "user_id": str(user_id),
                            "df_id": df_id,
                            "webhook_id": webhook_id,
                            "test_result": test_result,
                            "reason": "Webhook test failed during activation attempt",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(status_code=400, detail="Webhook test failed. Cannot set status to active.")
            except HTTPException as e:
                await log_business_event(
                    event_type="WEBHOOK_ACTIVATION_FAILED",
                    user_email=user_email,
                    message=f"Webhook activation failed: {e.detail}",
                    log_level="ERROR",
                    context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": e.detail},
                    business_logs_collection=self.business_logs_collection,
                )
                raise e
            except Exception as e:
                await log_business_event(
                    event_type="WEBHOOK_ACTIVATION_FAILED",
                    user_email=user_email,
                    message=f"Webhook activation failed due to internal error: {str(e)}",
                    log_level="ERROR",
                    context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": str(e)},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail=f"Error during webhook test before activation: {str(e)}")

        try:
            updated_webhook = await self.webhook_crud.update_webhook(webhook_id, update_dict)
            if not updated_webhook:
                await log_business_event(
                    event_type="WEBHOOK_UPDATE_FAILED",
                    user_email=user_email,
                    message="Webhook update failed: Database operation failed",
                    log_level="ERROR",
                    context={
                        "user_id": str(user_id),
                        "df_id": df_id,
                        "webhook_id": webhook_id,
                        "update_data": update_dict,
                        "reason": "Database update returned no webhook",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail="Failed to update webhook")

            await log_business_event(
                event_type="WEBHOOK_UPDATED",
                user_email=user_email,
                message="Webhook updated successfully",
                log_level="INFO",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "updated_fields": update_dict},
                business_logs_collection=self.business_logs_collection,
            )
            return updated_webhook
        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="WEBHOOK_UPDATE_FAILED",
                user_email=user_email,
                message=f"Unhandled exception during webhook update: {str(e)}",
                log_level="ERROR",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": str(e)},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Error updating webhook: {str(e)}")

    async def delete_webhook(self, webhook_id: str, current_user: Dict[str, Any]):
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")

        existing = await self.webhook_crud.get_webhook(webhook_id, df_id)
        if not existing:
            await log_business_event(
                event_type="WEBHOOK_DELETION_FAILED",
                user_email=user_email,
                message="Webhook deletion failed: Webhook not found",
                log_level="WARNING",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": "Webhook not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Webhook not found")

        try:
            success = await self.webhook_crud.delete_webhook(webhook_id)
            if not success:
                await log_business_event(
                    event_type="WEBHOOK_DELETION_FAILED",
                    user_email=user_email,
                    message="Webhook deletion failed: Database operation failed",
                    log_level="ERROR",
                    context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": "Database deletion failed"},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=500, detail="Failed to delete webhook")

            await log_business_event(
                event_type="WEBHOOK_DELETED",
                user_email=user_email,
                message="Webhook deleted successfully",
                log_level="INFO",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id},
                business_logs_collection=self.business_logs_collection,
            )
            return {"message": "Webhook deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="WEBHOOK_DELETION_FAILED",
                user_email=user_email,
                message=f"Unhandled exception during webhook deletion: {str(e)}",
                log_level="ERROR",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": str(e)},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Error deleting webhook: {str(e)}")

    async def list_webhooks(self, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        df_id = current_user["df_id"]
        try:
            webhooks = await self.webhook_crud.list_all_webhooks_by_df(df_id)
            return webhooks
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")

    async def list_paginated_webhooks(self, current_user: Dict[str, Any], current_page: int = 1, data_per_page: int = 20) -> Dict[str, Any]:
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")

        try:
            offset = (current_page - 1) * data_per_page
            response = await self.webhook_crud.list_webhooks_by_df(df_id, offset=offset, limit=data_per_page)

            total_items = response.get("total", 0)
            total_pages = (total_items + data_per_page - 1) // data_per_page

            await log_business_event(
                event_type="LIST_PAGINATED_WEBHOOKS_SUCCESS",
                user_email=user_email,
                message="Successfully listed paginated webhooks",
                log_level="INFO",
                context={
                    "user_id": str(user_id),
                    "df_id": df_id,
                    "current_page": current_page,
                    "data_per_page": data_per_page,
                    "total_items": total_items,
                },
                business_logs_collection=self.business_logs_collection,
            )

            return {
                "current_page": current_page,
                "data_per_page": data_per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "webhooks": response.get("data", []),
            }
        except Exception as e:
            await log_business_event(
                event_type="LIST_PAGINATED_WEBHOOKS_FAILED",
                user_email=user_email,
                message=f"Failed to list paginated webhooks: {str(e)}",
                log_level="ERROR",
                context={
                    "user_id": str(user_id),
                    "df_id": df_id,
                    "current_page": current_page,
                    "data_per_page": data_per_page,
                    "reason": str(e),
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Failed to list paginated webhooks: {str(e)}")

    async def get_webhook(self, webhook_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")

        try:
            webhook = await self.webhook_crud.get_webhook(webhook_id, df_id)
            if not webhook:
                await log_business_event(
                    event_type="GET_WEBHOOK_FAILED",
                    user_email=user_email,
                    message="Webhook not found",
                    log_level="WARNING",
                    context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": "Webhook does not exist"},
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=404, detail="Webhook not found")

            await log_business_event(
                event_type="GET_WEBHOOK_SUCCESS",
                user_email=user_email,
                message="Webhook fetched successfully",
                log_level="INFO",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "webhook_url": webhook.get("url")},
                business_logs_collection=self.business_logs_collection,
            )
            return webhook
        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="GET_WEBHOOK_FAILED",
                user_email=user_email,
                message=f"Unhandled exception during webhook retrieval: {str(e)}",
                log_level="ERROR",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": str(e)},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Error retrieving webhook: {str(e)}")

    async def test_webhook(self, webhook_id: str, current_user: dict):
        df_id = current_user["df_id"]
        user_id = current_user["_id"]
        user_email = current_user.get("email")

        webhook = await self.webhook_crud.get_webhook(webhook_id, df_id)
        if not webhook:
            await log_business_event(
                event_type="WEBHOOK_TEST_FAILED",
                user_email=user_email,
                message="Webhook test failed: Webhook not found",
                log_level="WARNING",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "reason": "Webhook not found"},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=404, detail="Webhook not found")

        if webhook.get("environment") != "testing":
            await log_business_event(
                event_type="WEBHOOK_TEST_FAILED",
                user_email=user_email,
                message="Webhook test failed: Test events can only be sent to testing environment webhooks",
                log_level="WARNING",
                context={
                    "user_id": str(user_id),
                    "df_id": df_id,
                    "webhook_id": webhook_id,
                    "environment": webhook.get("environment"),
                    "reason": "Test events not allowed for this environment",
                },
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=403, detail="Test events can only be sent to webhooks in testing environment")

        correlation_id = str(uuid.uuid4())
        connection = None
        channel = None
        try:
            connection, channel = await self.rabbitmq_pool.get_connection()

            reply_queue = await channel.declare_queue(exclusive=True, auto_delete=True, arguments={"x-expires": 30000})

            test_payload = {
                "webhook_id": webhook_id,
                "event_id": str(ObjectId()),
                "dp_id": "1231231",
                "df_id": df_id,
                "dpr_id": "",
                "event": "WEBHOOK_TEST",
                "environment": "testing",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "This is a test event to verify webhook integration.",
            }

            await self._publish_webhook_event(
                webhook_id=webhook_id,
                df_id=df_id,
                dp_id=test_payload["dp_id"],
                payload=test_payload,
                channel=channel,
                correlation_id=correlation_id,
                reply_to=reply_queue.name,
                is_test=True,
            )

            await log_business_event(
                event_type="WEBHOOK_TEST_INITIATED",
                user_email=user_email,
                message="Test webhook event published to RabbitMQ",
                log_level="INFO",
                context={
                    "user_id": str(user_id),
                    "df_id": df_id,
                    "webhook_id": webhook_id,
                    "correlation_id": correlation_id,
                    "reply_to_queue": reply_queue.name,
                },
                business_logs_collection=self.business_logs_collection,
            )

            response_message = None
            try:

                async with reply_queue.iterator(timeout=30) as queue_iter:
                    async for message in queue_iter:

                        if message.correlation_id == correlation_id:
                            response_message = message
                            break
                        await message.ack()

                if response_message:
                    await response_message.ack()
                    response_data = json.loads(response_message.body.decode())

                    await log_business_event(
                        event_type="WEBHOOK_TEST_SUCCESS",
                        user_email=user_email,
                        message="Webhook test completed successfully with response",
                        log_level="INFO",
                        context={
                            "user_id": str(user_id),
                            "df_id": df_id,
                            "webhook_id": webhook_id,
                            "correlation_id": correlation_id,
                            "response_status": response_data.get("status"),
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    return response_data
                else:

                    await log_business_event(
                        event_type="WEBHOOK_TEST_FAILED",
                        user_email=user_email,
                        message="Webhook test failed: No response received from consumer within timeout.",
                        log_level="ERROR",
                        context={
                            "user_id": str(user_id),
                            "df_id": df_id,
                            "webhook_id": webhook_id,
                            "correlation_id": correlation_id,
                            "reason": "No response from consumer",
                        },
                        business_logs_collection=self.business_logs_collection,
                    )
                    raise HTTPException(status_code=504, detail="No response received from consumer within timeout.")

            except asyncio.TimeoutError:
                await log_business_event(
                    event_type="WEBHOOK_TEST_FAILED",
                    user_email=user_email,
                    message="Webhook test failed: Consumer response timed out.",
                    log_level="ERROR",
                    context={
                        "user_id": str(user_id),
                        "df_id": df_id,
                        "webhook_id": webhook_id,
                        "correlation_id": correlation_id,
                        "reason": "Consumer response timed out",
                    },
                    business_logs_collection=self.business_logs_collection,
                )
                raise HTTPException(status_code=504, detail="Consumer response timed out.")

        except HTTPException:
            raise
        except Exception as e:
            await log_business_event(
                event_type="WEBHOOK_TEST_FAILED",
                user_email=user_email,
                message=f"Unhandled exception during webhook test: {str(e)}",
                log_level="ERROR",
                context={"user_id": str(user_id), "df_id": df_id, "webhook_id": webhook_id, "correlation_id": correlation_id, "reason": str(e)},
                business_logs_collection=self.business_logs_collection,
            )
            raise HTTPException(status_code=500, detail=f"Service error during webhook test: {str(e)}")
        finally:
            if connection and channel:
                await self.rabbitmq_pool.release_connection(connection, channel)

    async def _publish_webhook_event(
        self,
        webhook_id: str,
        df_id: str,
        dp_id: str,
        payload: Dict[str, Any],
        channel: Optional[aio_pika.Channel] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        is_test: bool = False,
    ):
        """
        Stores the webhook event in MongoDB and publishes it to RabbitMQ.
        If a channel is provided, it uses that channel for publishing.
        """
        event_doc = WebhookEventInDB(
            webhook_id=webhook_id,
            df_id=df_id,
            dp_id=dp_id,
            payload=payload,
            status="pending",
            attempts=0,
            last_error=None,
        )

        if not is_test:
            inserted_id = await self.webhook_event_crud.create_event(event_doc)

            event_doc.id = str(inserted_id)
        else:

            event_doc.id = payload.get("event_id", str(ObjectId()))

        message_body_json_str = event_doc.model_dump_json(by_alias=True)
        message_body = json.loads(message_body_json_str)

        message_body["correlation_id"] = correlation_id
        message_body["reply_to"] = reply_to
        message_body["is_test"] = is_test

        await publish_message(
            "webhook_main",
            json.dumps(message_body),
            channel=channel,
            correlation_id=correlation_id,
            reply_to=reply_to,
        )

        return event_doc.id
