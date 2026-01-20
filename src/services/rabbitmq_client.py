"""
RabbitMQ client for task queue and agent communication.

Provides async message publishing and consuming for
agent task distribution and inter-agent communication.
"""

from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)

# Type alias for message handlers
MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


class RabbitMQClient:
    """Async RabbitMQ client wrapper."""

    def __init__(self) -> None:
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queues: dict[str, AbstractQueue] = {}

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        settings = get_settings()
        self._connection = await connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        logger.info("rabbitmq_connected", url=settings.rabbitmq_url)

    async def disconnect(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._queues.clear()
            logger.info("rabbitmq_disconnected")

    @property
    def channel(self) -> AbstractChannel:
        """Get the channel instance."""
        if not self._channel:
            raise RuntimeError("RabbitMQ client not connected")
        return self._channel

    async def declare_queue(
        self, queue_name: str, durable: bool = True
    ) -> AbstractQueue:
        """Declare a queue and cache it."""
        if queue_name not in self._queues:
            queue = await self.channel.declare_queue(queue_name, durable=durable)
            self._queues[queue_name] = queue
        return self._queues[queue_name]

    async def publish(
        self,
        queue_name: str,
        message: dict[str, Any],
        priority: int = 0,
    ) -> None:
        """Publish a message to a queue."""
        import json

        await self.declare_queue(queue_name)
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                priority=priority,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )
        logger.debug("message_published", queue=queue_name)

    async def consume(
        self, queue_name: str, handler: MessageHandler, no_ack: bool = False
    ) -> None:
        """Start consuming messages from a queue."""
        import json

        queue = await self.declare_queue(queue_name)

        async def process_message(
            message: aio_pika.abc.AbstractIncomingMessage,
        ) -> None:
            async with message.process(ignore_processed=no_ack):
                try:
                    body = json.loads(message.body.decode())
                    await handler(body)
                except Exception as e:
                    logger.error(
                        "message_processing_failed",
                        queue=queue_name,
                        error=str(e),
                    )
                    if not no_ack:
                        raise

        await queue.consume(process_message, no_ack=no_ack)
        logger.info("consumer_started", queue=queue_name)

    # Predefined queues for the application
    async def publish_agent_task(
        self, agent_type: str, task: dict[str, Any]
    ) -> None:
        """Publish a task to an agent's queue."""
        await self.publish(f"agent.{agent_type}.tasks", task)

    async def publish_hitl_request(self, request: dict[str, Any]) -> None:
        """Publish a HITL approval request."""
        await self.publish("hitl.requests", request, priority=5)

    async def publish_hitl_response(self, response: dict[str, Any]) -> None:
        """Publish a HITL approval response."""
        await self.publish("hitl.responses", response, priority=5)

    async def publish_orchestrator_event(self, event: dict[str, Any]) -> None:
        """Publish an event to the orchestrator."""
        await self.publish("orchestrator.events", event)


# Singleton instance
_rabbitmq_client: RabbitMQClient | None = None


async def get_rabbitmq_client() -> RabbitMQClient:
    """Get or create RabbitMQ client singleton."""
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
        await _rabbitmq_client.connect()
    return _rabbitmq_client


async def close_rabbitmq_client() -> None:
    """Close RabbitMQ client if exists."""
    global _rabbitmq_client
    if _rabbitmq_client:
        await _rabbitmq_client.disconnect()
        _rabbitmq_client = None
