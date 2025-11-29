import aio_pika
import asyncio
import httpx
import time
from typing import Tuple, Optional
from app.core.config import settings
from app.core.logger import app_logger

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_MANAGEMENT_PORT = settings.RABBITMQ_MANAGEMENT_PORT
RABBITMQ_USER = settings.RABBITMQ_USER
RABBITMQ_PASSWORD = settings.RABBITMQ_PASSWORD
RABBITMQ_VHOST = settings.RABBITMQ_VHOST_NAME
RABBIT_API_URL = f"http://{RABBITMQ_HOST}:{RABBITMQ_MANAGEMENT_PORT}/api"
POOL_SIZE = settings.RABBITMQ_POOL_SIZE
RABBIT_MQ_RETRY_DELAY = 60
RABBIT_MQ_RETRY_LIMIT = 10

QUEUES = [
    "data_element_translation",
    "purpose_translation",
    "dp_processing",
    "send_email",
    "notice_notification_queue",
    "dp_external",
    "failed_queue",
    "consent_bulk_verification",
    "consent_bulk_external_verification",
    "cookie_scan_queue",
    "webhook_main",
    "webhook_retry",
    "webhook_dlq",
    "consent_events_q",
    "consent_retry_q",
    "consent_dlq",
    "consent_processing_q",
    "consent_processing_retry_q",
    "consent_processing_dlq",
    "consent_expiry_delay_queue",
    "consent_expiry_queue",
    "data_expiry_delay_queue",
    "data_expiry_queue",
]

EXCHANGES = {
    "webhook_exchange": "direct",
    "retry_exchange": "direct",
    "dlq_exchange": "direct",
    "consent_events_exchange": "direct",
    "consent_retry_exchange": "direct",
    "consent_dlq_exchange": "direct",
    "consent_expiry_exchange": "direct",
    "consent_processing_retry_exchange": "direct",
    "consent_processing_dlq_exchange": "direct",
    "data_expiry_exchange": "direct",
}


class AsyncRabbitMQConnectionPool:
    """Async RabbitMQ Connection Pool using aio-pika with robust reconnection."""

    def __init__(self, pool_size: int = POOL_SIZE):
        self.pool_size = pool_size
        self._pool: asyncio.Queue = asyncio.Queue()
        self._initialized = False

    async def _create_connection(self) -> Tuple[aio_pika.RobustConnection, aio_pika.Channel]:
        """Creates a new aio-pika connection and channel."""
        retry_times = 0
        while retry_times <= RABBIT_MQ_RETRY_LIMIT:
            try:
                connection = await aio_pika.connect_robust(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    login=RABBITMQ_USER,
                    password=RABBITMQ_PASSWORD,
                    virtualhost=RABBITMQ_VHOST,
                )
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=20)
                return connection, channel
            except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
                retry_times += 1
                app_logger.error(f"Failed to connect to RabbitMQ: {e} - Retry {retry_times}/{RABBIT_MQ_RETRY_LIMIT}")
                time.sleep(RABBIT_MQ_RETRY_DELAY)
                
    async def init_pool(self):
        """Initializes the connection pool by populating it with connections."""
        if self._initialized:
            app_logger.warning("RabbitMQ pool already initialized.")
            return

        app_logger.info(f"Initializing RabbitMQ pool with {self.pool_size} connections...")
        for _ in range(self.pool_size):
            conn, channel = await self._create_connection()
            await self._pool.put((conn, channel))
        self._initialized = True
        app_logger.info("RabbitMQ pool initialized successfully!")

    async def get_connection(self) -> Tuple[aio_pika.RobustConnection, aio_pika.Channel]:
        """Retrieves a connection and channel from the pool."""
        return await self._pool.get()

    async def release_connection(self, connection: aio_pika.RobustConnection, channel: aio_pika.Channel):
        """Releases a connection back to the pool."""
        if not connection.is_closed:
            await self._pool.put((connection, channel))
        else:

            app_logger.warning("Connection was closed, creating a new one to replace it.")
            try:
                conn, new_channel = await self._create_connection()
                await self._pool.put((conn, new_channel))
            except aio_pika.exceptions.ConnectionError:
                app_logger.error("Failed to create a new connection to replace the closed one.")

    async def close_pool(self):
        """Closes all connections in the pool."""
        app_logger.info("Closing all connections in the pool...")
        while not self._pool.empty():
            connection, _ = await self._pool.get()
            if not connection.is_closed:
                await connection.close()
        app_logger.info("RabbitMQ connections closed!")


rabbitmq_pool = AsyncRabbitMQConnectionPool(pool_size=POOL_SIZE)


async def create_vhost():
    """Creates a RabbitMQ vhost if it does not exist."""
    url = f"{RABBIT_API_URL}/vhosts/{RABBITMQ_VHOST}"
    async with httpx.AsyncClient(auth=(RABBITMQ_USER, RABBITMQ_PASSWORD)) as client:
        try:
            response = await client.put(url)
            response.raise_for_status()
            app_logger.info(f"VHost '{RABBITMQ_VHOST}' created successfully.")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                app_logger.warning(f"VHost '{RABBITMQ_VHOST}' already exists.")
            else:
                app_logger.error(f"Failed to create VHost: {e.response.status_code} {e.response.text}")


async def set_user_permissions():
    """Sets user permissions for the vhost."""
    url = f"{RABBIT_API_URL}/permissions/{RABBITMQ_VHOST}/{RABBITMQ_USER}"
    data = {"configure": ".*", "write": ".*", "read": ".*"}
    async with httpx.AsyncClient(auth=(RABBITMQ_USER, RABBITMQ_PASSWORD)) as client:
        try:
            response = await client.put(url, json=data)
            response.raise_for_status()
            app_logger.info(f"Permissions set for user '{RABBITMQ_USER}' on vhost '{RABBITMQ_VHOST}'.")
        except httpx.HTTPStatusError as e:
            app_logger.error(f"Failed to set permissions: {e.response.status_code} {e.response.text}")


async def declare_queues():
    """Declares all queues and exchanges."""
    conn, channel = await rabbitmq_pool.get_connection()
    try:
        app_logger.info("Declaring exchanges...")
        for exchange_name, exchange_type in EXCHANGES.items():
            await channel.declare_exchange(exchange_name, exchange_type, durable=True)
        app_logger.info(f"All {len(EXCHANGES)} exchanges declared.")

        app_logger.info("Declaring specific queues and bindings...")

        await channel.declare_queue(
            "webhook_main", durable=True, arguments={"x-dead-letter-exchange": "retry_exchange", "x-dead-letter-routing-key": "webhook_retry"}
        )
        await channel.declare_queue(
            "webhook_retry",
            durable=True,
            arguments={"x-message-ttl": 10000, "x-dead-letter-exchange": "webhook_exchange", "x-dead-letter-routing-key": "webhook_main"},
        )
        await channel.declare_queue("webhook_dlq", durable=True)
        webhook_exchange = await channel.get_exchange("webhook_exchange")
        await (await channel.get_queue("webhook_main")).bind(webhook_exchange, routing_key="webhook_main")
        retry_exchange = await channel.get_exchange("retry_exchange")
        await (await channel.get_queue("webhook_retry")).bind(retry_exchange, routing_key="webhook_retry")
        dlq_exchange = await channel.get_exchange("dlq_exchange")
        await (await channel.get_queue("webhook_dlq")).bind(dlq_exchange, routing_key="webhook_dlq")
        app_logger.info("Webhook queues and bindings declared.")

        await channel.declare_queue(
            "consent_events_q",
            durable=True,
            arguments={"x-dead-letter-exchange": "consent_retry_exchange", "x-dead-letter-routing-key": "consent_retry_q"},
        )
        await channel.declare_queue(
            "consent_retry_q",
            durable=True,
            arguments={"x-message-ttl": 10000, "x-dead-letter-exchange": "consent_events_exchange", "x-dead-letter-routing-key": "consent_events_q"},
        )
        await channel.declare_queue("consent_dlq", durable=True)
        consent_events_exchange = await channel.get_exchange("consent_events_exchange")
        await (await channel.get_queue("consent_events_q")).bind(consent_events_exchange, routing_key="consent_events_q")
        consent_retry_exchange = await channel.get_exchange("consent_retry_exchange")
        await (await channel.get_queue("consent_retry_q")).bind(consent_retry_exchange, routing_key="consent_retry_q")
        consent_dlq_exchange = await channel.get_exchange("consent_dlq_exchange")
        await (await channel.get_queue("consent_dlq")).bind(consent_dlq_exchange, routing_key="consent_dlq")
        app_logger.info("Consent event queues and bindings declared.")

        await channel.declare_exchange("consent_expiry_exchange", aio_pika.ExchangeType.DIRECT, durable=True)
        await channel.declare_queue(
            "consent_expiry_delay_queue",
            durable=True,
            arguments={"x-dead-letter-exchange": "consent_expiry_exchange", "x-dead-letter-routing-key": "consent_expiry"},
        )
        await channel.declare_queue("consent_expiry_queue", durable=True)
        consent_expiry_exchange = await channel.get_exchange("consent_expiry_exchange")
        await (await channel.get_queue("consent_expiry_queue")).bind(consent_expiry_exchange, routing_key="consent_expiry")
        app_logger.info("Consent expiry queues and bindings declared.")

        await channel.declare_exchange("data_expiry_exchange", aio_pika.ExchangeType.DIRECT, durable=True)
        await channel.declare_queue(
            "data_expiry_delay_queue",
            durable=True,
            arguments={"x-dead-letter-exchange": "data_expiry_exchange", "x-dead-letter-routing-key": "data_expiry"},
        )
        await channel.declare_queue("data_expiry_queue", durable=True)
        data_expiry_exchange = await channel.get_exchange("data_expiry_exchange")
        await (await channel.get_queue("data_expiry_queue")).bind(data_expiry_exchange, routing_key="data_expiry")
        app_logger.info("Data expiry queues and bindings declared.")

        await channel.declare_queue(
            "consent_processing_q",
            durable=True,
            arguments={"x-dead-letter-exchange": "consent_processing_retry_exchange", "x-dead-letter-routing-key": "consent_processing_retry_q"},
        )
        await channel.declare_queue(
            "consent_processing_retry_q",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": "consent_processing_q",
                "x-message-ttl": settings.CONSENT_RETRY_DELAY_MS if hasattr(settings, "CONSENT_RETRY_DELAY_MS") else 5000,
            },
        )
        await channel.declare_queue("consent_processing_dlq", durable=True)
        consent_processing_retry_exchange = await channel.get_exchange("consent_processing_retry_exchange")
        await (await channel.get_queue("consent_processing_retry_q")).bind(
            consent_processing_retry_exchange, routing_key="consent_processing_retry_q"
        )
        consent_processing_dlq_exchange = await channel.get_exchange("consent_processing_dlq_exchange")
        await (await channel.get_queue("consent_processing_dlq")).bind(consent_processing_dlq_exchange, routing_key="consent_processing_dlq")
        app_logger.info("Consent processing queues and bindings declared.")

        generic_queues = [
            q
            for q in QUEUES
            if q
            not in [
                "webhook_main",
                "webhook_retry",
                "webhook_dlq",
                "consent_events_q",
                "consent_retry_q",
                "consent_dlq",
                "consent_expiry_delay_queue",
                "consent_expiry_queue",
                "data_expiry_delay_queue",
                "data_expiry_queue",
                "consent_processing_q",
                "consent_processing_retry_q",
                "consent_processing_dlq",
            ]
        ]
        for queue_name in generic_queues:
            await channel.declare_queue(queue_name, durable=True)
        app_logger.info(f"Declared {len(generic_queues)} generic queues.")

    finally:
        await rabbitmq_pool.release_connection(conn, channel)


async def publish_message(
    queue_name: str,
    message: str,
    channel: Optional[aio_pika.Channel] = None,
    correlation_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    expiration: Optional[int] = None,
):
    """
    Publishes a message to the specified RabbitMQ queue or exchange.
    If a channel is provided, it uses that channel. Otherwise, it acquires a connection
    and channel from the pool, publishes, and releases them.
    Includes optional correlation_id, reply_to, and expiration for RPC patterns and TTL messages.
    """
    app_logger.info(f"Publishing message to queue/exchange '{queue_name}'")
    app_logger.debug(f"Message payload: {message}")

    if queue_name not in QUEUES and queue_name not in EXCHANGES:
        app_logger.error(f"Invalid queue or exchange name for publishing: {queue_name}")
        raise ValueError(f"Invalid queue or exchange name: {queue_name}")

    _connection = None
    _channel = None

    if channel:

        _channel = channel
        app_logger.debug(f"Using provided channel for publishing to '{queue_name}'.")
    else:

        _connection, _channel = await rabbitmq_pool.get_connection()
        app_logger.debug(f"Acquired new connection/channel from pool for publishing to '{queue_name}'.")

    try:
        exchange_obj = None
        routing_key_obj = queue_name

        if queue_name == "webhook_main":
            exchange_obj = await _channel.get_exchange("webhook_exchange")
            routing_key_obj = "webhook_main"
        elif queue_name == "webhook_dlq":
            exchange_obj = await _channel.get_exchange("dlq_exchange")
            routing_key_obj = "webhook_dlq"
        elif queue_name == "consent_expiry_delay_queue":
            exchange_obj = _channel.default_exchange
            routing_key_obj = "consent_expiry_delay_queue"
        elif queue_name == "data_expiry_delay_queue":
            exchange_obj = _channel.default_exchange
            routing_key_obj = "data_expiry_delay_queue"
        elif queue_name == "consent_processing_q":

            exchange_obj = _channel.default_exchange
            routing_key_obj = "consent_processing_q"
        elif queue_name == "consent_processing_retry_q":
            exchange_obj = await _channel.get_exchange("consent_processing_retry_exchange")
            routing_key_obj = "consent_processing_retry_q"
        elif queue_name == "consent_processing_dlq":
            exchange_obj = await _channel.get_exchange("consent_processing_dlq_exchange")
            routing_key_obj = "consent_processing_dlq"
        elif queue_name in EXCHANGES:
            exchange_obj = await _channel.get_exchange(queue_name)
            routing_key_obj = ""
        else:
            exchange_obj = _channel.default_exchange

        message_properties = {
            "body": message.encode(),
            "delivery_mode": aio_pika.DeliveryMode.PERSISTENT,
        }
        if correlation_id:
            message_properties["correlation_id"] = correlation_id
        if reply_to:
            message_properties["reply_to"] = reply_to
        if expiration is not None:
            message_properties["expiration"] = expiration

        await exchange_obj.publish(
            aio_pika.Message(**message_properties),
            routing_key=routing_key_obj,
        )
        app_logger.info(f"Message published to queue/exchange '{queue_name}'.")
    except Exception as e:
        app_logger.error(f"Failed to publish message to queue/exchange '{queue_name}': {e}")
        raise
    finally:

        if _connection and _channel:
            await rabbitmq_pool.release_connection(_connection, _channel)
            app_logger.debug(f"Released connection/channel back to pool after publishing to '{queue_name}'.")
