"""
Redis client for session management and agent state.

Provides async Redis operations for caching, session storage,
and agent state management.
"""

import json
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self) -> None:
        self._client: Redis | None = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        settings = get_settings()
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._client.ping()
        logger.info("redis_connected", url=settings.redis_url)

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("redis_disconnected")

    @property
    def client(self) -> Redis:
        """Get the Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return self._client

    async def get(self, key: str) -> str | None:
        """Get a value by key."""
        return await self.client.get(key)

    async def set(
        self, key: str, value: str, expire_seconds: int | None = None
    ) -> None:
        """Set a value with optional expiration."""
        if expire_seconds:
            await self.client.setex(key, expire_seconds, value)
        else:
            await self.client.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete a key."""
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return bool(await self.client.exists(key))

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Get and parse JSON value."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self, key: str, value: dict[str, Any], expire_seconds: int | None = None
    ) -> None:
        """Serialize and set JSON value."""
        await self.set(key, json.dumps(value), expire_seconds)

    # Agent state management
    async def get_agent_state(self, agent_id: str) -> dict[str, Any] | None:
        """Get agent state."""
        return await self.get_json(f"agent:state:{agent_id}")

    async def set_agent_state(
        self, agent_id: str, state: dict[str, Any], ttl: int = 3600
    ) -> None:
        """Set agent state with TTL."""
        await self.set_json(f"agent:state:{agent_id}", state, ttl)

    async def update_agent_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat timestamp."""
        settings = get_settings()
        await self.set(
            f"agent:heartbeat:{agent_id}",
            "1",
            settings.agent_heartbeat_interval_seconds * 3,
        )

    async def is_agent_alive(self, agent_id: str) -> bool:
        """Check if agent is alive based on heartbeat."""
        return await self.exists(f"agent:heartbeat:{agent_id}")

    # Session management
    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session data."""
        return await self.get_json(f"session:{session_id}")

    async def set_session(
        self, session_id: str, data: dict[str, Any], ttl: int = 86400
    ) -> None:
        """Set session data with TTL (default 24 hours)."""
        await self.set_json(f"session:{session_id}", data, ttl)

    async def delete_session(self, session_id: str) -> None:
        """Delete session."""
        await self.delete(f"session:{session_id}")


# Singleton instance
_redis_client: RedisClient | None = None


async def get_redis_client() -> RedisClient:
    """Get or create Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client if exists."""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
