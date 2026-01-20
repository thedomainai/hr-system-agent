"""Service clients for external dependencies."""

from .rabbitmq_client import (
    RabbitMQClient,
    close_rabbitmq_client,
    get_rabbitmq_client,
)
from .redis_client import RedisClient, close_redis_client, get_redis_client
from .vault_client import VaultClient, close_vault_client, get_vault_client

__all__ = [
    "RedisClient",
    "get_redis_client",
    "close_redis_client",
    "RabbitMQClient",
    "get_rabbitmq_client",
    "close_rabbitmq_client",
    "VaultClient",
    "get_vault_client",
    "close_vault_client",
]
