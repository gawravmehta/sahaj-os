import json
import asyncio
import httpx
import hmac
import hashlib
import aio_pika
import motor.motor_asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


from app.core.config import settings
from app.schemas.webhook_events_schema import WebhookEventInDB
from app.crud.webhook_events_crud import WebhookEventCRUD
from app.db.rabbitmq import rabbitmq_pool, declare_queues
from app.crud.webhooks_crud import WebhooksCrud
from app.core.logger import setup_logging, get_logger


MAX_RETRIES = settings.WEBHOOK_MAX_RETRIES


db_client: AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
concur_master_db: AsyncIOMotorDatabase = db_client[settings.DB_NAME_CONCUR_MASTER]

webhook_events_collection: AsyncIOMotorCollection = concur_master_db["webhook_events"]
webhooks_collection: AsyncIOMotorCollection = concur_master_db["webhooks"]

webhook_event_crud = WebhookEventCRUD(collection=webhook_events_collection)
webhooks_crud = WebhooksCrud(webhooks_collection=webhooks_collection)


async def publish_to_queue(queue_name: str, message: str, channel: aio_pika.Channel):
    """Publish a message using the same channel (no new connections)."""

    if queue_name == "webhook_main":
        exchange = await channel.get_exchange("webhook_exchange")
        routing_key = "webhook_main"
    elif queue_name == "webhook_dlq":
        exchange = await channel.get_exchange("dlq_exchange")
        routing_key = "webhook_dlq"
    else:

        exchange = channel.default_exchange
        routing_key = queue_name

    await exchange.publish(aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT), routing_key=routing_key)
    logger.info(f"Published event to {queue_name}")


async def publish_response(
    channel: aio_pika.Channel,
    reply_to: str,
    correlation_id: str,
    status: str,
    message: str = None,
    event_id: str = None,
):
    """Publishes a response back to the reply_to queue."""
    response_payload = {"status": status, "message": message, "event_id": event_id}
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(response_payload).encode(),
            content_type="application/json",
            correlation_id=correlation_id,
        ),
        routing_key=reply_to,
    )
    logger.info(f"Published response to {reply_to} for correlation_id {correlation_id} with status: {status}")


async def process_webhook_event(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    """Process messages from webhook_main queue with safe ack/nack handling."""
    event_id = None
    correlation_id = None
    reply_to = None
    is_test = False

    try:

        event_data = json.loads(message.body.decode())
        event_id = event_data.get("_id")
        correlation_id = message.correlation_id or event_data.get("correlation_id")
        reply_to = message.reply_to or event_data.get("reply_to")
        is_test = event_data.get("is_test", False)

        logger.info(f"Starting to process event {event_id or 'Unknown'}...")
        logger.debug(f"   - Is Test: {is_test}")
        logger.debug(f"   - Correlation ID (from message property): {message.correlation_id}")
        logger.debug(f"   - Correlation ID (from event_data): {event_data.get('correlation_id')}")
        logger.debug(f"   - Final Correlation ID: {correlation_id}")
        logger.debug(f"   - Reply To (from message property): {message.reply_to}")
        logger.debug(f"   - Reply To (from event_data): {event_data.get('reply_to')}")
        logger.debug(f"   - Final Reply To: {reply_to}")

        if not event_id and not is_test:
            raise ValueError("Message body is missing '_id' field for non-test event.")

        webhook_id = event_data["webhook_id"]
        payload = event_data["payload"]

        webhook_config = await webhooks_crud.get_webhook(webhook_id, event_data["df_id"])
        if not webhook_config:
            error_msg = f"Webhook config not found for webhook_id: {webhook_id}."
            logger.error(f"{error_msg} Event {event_id} will be DLQ'd (if not test).")
            if is_test and reply_to and correlation_id:
                await publish_response(channel, reply_to, correlation_id, "error", error_msg, event_id)
            else:
                await publish_to_queue("webhook_dlq", message.body.decode(), channel)
            await message.ack()
            return

        headers = {}
        auth_cfg = webhook_config.get("auth")
        if auth_cfg and auth_cfg.get("type") == "header":
            webhook_secret = auth_cfg.get("secret")
            if not webhook_secret:
                error_msg = f"Webhook auth secret missing for webhook_id: {webhook_id}."
                logger.error(f"{error_msg} Event {event_id} will be DLQ'd (if not test).")
                if is_test and reply_to and correlation_id:
                    await publish_response(channel, reply_to, correlation_id, "error", error_msg, event_id)
                else:
                    await publish_to_queue("webhook_dlq", message.body.decode(), channel)
                await message.ack()
                return
            payload_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            signature = hmac.new(
                webhook_secret.encode(),
                msg=payload_str.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()
            headers = {auth_cfg["key"]: signature}

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_config["url"], json=payload, headers=headers)
            if not 200 <= resp.status_code < 300:
                raise httpx.HTTPStatusError(
                    f"Webhook responded with status {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            resp_json = resp.json()
            if resp_json.get("status") != "ok":
                raise Exception(f"Webhook response status not 'ok': {resp_json}")

        x_death_headers = message.headers.get("x-death", [])
        retries = x_death_headers[0]["count"] if x_death_headers else 0

        if event_id:
            await webhook_event_crud.update_event_status(event_id, "sent", retries)
            logger.info(f"Webhook event {event_id} sent successfully after {retries} attempts. ACKING.")
        else:
            logger.info(
                f"Webhook event {event_id or 'Unknown'} sent successfully after {retries} attempts. ACKING (Skipping MongoDB update due to missing ID)."
            )

        if is_test and reply_to and correlation_id:
            await publish_response(channel, reply_to, correlation_id, "success", "Webhook tested successfully.", event_id)

        await message.ack()

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to send webhook event {event_id}: {error_message}")
        await handle_failure(message, event_id, error_message, channel, correlation_id, reply_to, is_test)
    finally:
        logger.info(f"Finished processing event {event_id or 'Unknown'} (Test: {is_test}).")


async def handle_failure(
    message: aio_pika.IncomingMessage,
    event_id: str,
    error_message: str,
    channel: aio_pika.Channel,
    correlation_id: str = None,
    reply_to: str = None,
    is_test: bool = False,
):
    """
    Handle failed webhook events: send to retry queue or DLQ using the consumer channel.
    If it's a test message, publish an error response.
    """

    x_death_headers = message.headers.get("x-death", [])

    retries = x_death_headers[0]["count"] if x_death_headers else 0
    current_attempt = retries + 1

    logger.warning(f"Handling failure for event {event_id or 'None'} (Attempt {current_attempt}, Test: {is_test})...")

    if is_test and reply_to and correlation_id:
        logger.warning(f"Test webhook event {event_id} failed. Publishing error response.")
        await publish_response(channel, reply_to, correlation_id, "error", error_message, event_id)
        try:
            await message.ack()
            logger.info(f"Test message {event_id} successfully ACKed after sending error response.")
        except Exception as ack_e:
            logger.critical(f"CRITICAL ACK FAILURE for test message {event_id}: Could not acknowledge message. Error: {ack_e}.")
        return

    if event_id:
        await webhook_event_crud.update_event_status(
            event_id, "dlq_pending" if current_attempt >= MAX_RETRIES else "failed", current_attempt, error_message
        )
    else:

        logger.warning(f"Cannot update MongoDB status: Event ID is missing or None for message that failed.")

    if current_attempt >= MAX_RETRIES:
        logger.critical(f"Webhook event {event_id} reached max retries ({MAX_RETRIES}). Sending to DLQ. CRITICAL ACK REQUIRED.")

        await publish_to_queue("webhook_dlq", message.body.decode(), channel)

        try:
            await message.ack()
            logger.info(f"Message {event_id} successfully ACKed from main queue after DLQ copy.")
        except Exception as ack_e:
            logger.critical(
                f"CRITICAL ACK FAILURE for {event_id}: Could not acknowledge message after DLQ copy. Error: {ack_e}. This may cause the consumer to stall."
            )

    else:

        logger.warning(f"Webhook event {event_id} failed. Nacking to trigger retry (attempt {current_attempt}).")

        try:

            await message.nack(requeue=False)
            logger.info(f"Message {event_id} successfully NACKed (requeue=False). Triggering TTL.")
        except Exception as nack_e:
            logger.critical(f"CRITICAL NACK FAILURE for {event_id}: Could not nack message. Error: {nack_e}")


async def main() -> None:

    await rabbitmq_pool.init_pool()
    await declare_queues()

    while True:
        connection, channel = None, None

        try:
            connection, channel = await rabbitmq_pool.get_connection()

            await channel.set_qos(prefetch_count=10)
            queue = await channel.get_queue("webhook_main")
            logger.info("Waiting for messages on 'webhook_main'...")

            await queue.consume(lambda msg: process_webhook_event(msg, channel))

            await asyncio.Future()

        except asyncio.CancelledError:
            logger.info("Consumer task cancelled gracefully.")
            break
        except Exception as main_e:

            logger.critical(f"CRITICAL EXCEPTION IN MAIN CONSUMER LOOP (Restarting): {main_e}")

            await asyncio.sleep(5)
            continue
        finally:

            if connection and channel:
                logger.info("Consumer attempting to release connection/channel...")

                await rabbitmq_pool.release_connection(connection, channel)
                logger.info("Connection/channel released.")
            else:
                logger.info("RabbitMQ connection/channel was not established or already released.")


if __name__ == "__main__":
    setup_logging()
    logger = get_logger("worker.webhook_consumer")
    logger.info("Webhook consumer starting up.")
    asyncio.run(main())
