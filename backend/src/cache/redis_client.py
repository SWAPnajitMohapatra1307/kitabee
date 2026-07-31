"""Async Redis client wrapper for Kitabee.

Provides a single shared connection to Redis with safe get/set/delete
helpers. Cache failures are logged but never propagate to callers —
the caller always falls back to the real data source on a miss.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError, TimeoutError as RedisTimeoutError

from src.config import settings


logger = logging.getLogger(__name__)


# Constants

CACHE_ENCODING = "utf-8"


# Public API

class RedisClient:
    """Async Redis client with JSON serialization and safe error handling.

    A single instance is created at module level and reused across the
    application. Connection pooling is handled internally by redis-py.

    Cache operations never raise on connection or serialization errors —
    they log a warning and return a miss-equivalent value so the caller
    can fall back to the source of truth.
    """

    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize the Redis connection pool.

        Called once at application startup. Verifies connectivity by
        issuing a PING before returning.

        Raises:
            RedisConnectionError: If Redis is unreachable at startup.
        """
        self._client = redis.from_url(
            settings.redis_url,
            encoding=CACHE_ENCODING,
            decode_responses=True,
        )
        await self._client.ping()
        logger.info("Redis connection established", extra={"url": settings.redis_url})

    async def close(self) -> None:
        """Close the Redis connection pool.

        Called once at application shutdown. Safe to call if never connected.
        """
        if self._client is None:
            return
        await self._client.aclose()
        self._client = None
        logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a JSON-decoded value by key.

        Args:
            key: Redis key string.

        Returns:
            Deserialized Python object on hit, or None on miss or error.
        """
        if self._client is None:
            return None

        try:
            raw = await self._client.get(key)
        except (RedisConnectionError, RedisTimeoutError, RedisError) as exc:
            logger.warning(
                "Redis GET failed",
                extra={"key": key, "error": str(exc)},
            )
            return None

        if raw is None:
            return None

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Redis GET returned invalid JSON",
                extra={"key": key, "error": str(exc)},
            )
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Serialize a value to JSON and store it with a TTL.

        Args:
            key: Redis key string.
            value: Any JSON-serializable Python object.
            ttl_seconds: Expiry in seconds. Must be positive.

        Returns:
            True if stored successfully, False on serialization or Redis error.

        Raises:
            ValueError: If ttl_seconds is not positive.
        """
        if ttl_seconds <= 0:
            raise ValueError(f"ttl_seconds must be positive, got {ttl_seconds}")

        if self._client is None:
            return False

        try:
            serialized = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            logger.warning(
                "Redis SET serialization failed",
                extra={"key": key, "error": str(exc)},
            )
            return False

        try:
            await self._client.set(key, serialized, ex=ttl_seconds)
            return True
        except (RedisConnectionError, RedisTimeoutError, RedisError) as exc:
            logger.warning(
                "Redis SET failed",
                extra={"key": key, "error": str(exc)},
            )
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis.

        Args:
            key: Redis key string.

        Returns:
            True if the command succeeded, False on error.
            Note: Returns True even if the key did not exist.
        """
        if self._client is None:
            return False

        try:
            await self._client.delete(key)
            return True
        except (RedisConnectionError, RedisTimeoutError, RedisError) as exc:
            logger.warning(
                "Redis DELETE failed",
                extra={"key": key, "error": str(exc)},
            )
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis.

        Args:
            key: Redis key string.

        Returns:
            True if the key exists, False on miss or error.
        """
        if self._client is None:
            return False

        try:
            result = await self._client.exists(key)
            return bool(result)
        except (RedisConnectionError, RedisTimeoutError, RedisError) as exc:
            logger.warning(
                "Redis EXISTS failed",
                extra={"key": key, "error": str(exc)},
            )
            return False

    async def get_info(self) -> dict[str, Any]:
        """Retrieve Redis server info for the metrics endpoint.

        Returns:
            Dictionary with connected_clients, used_memory_human,
            keyspace_hits, keyspace_misses, and uptime_in_seconds.
            Returns an empty dict on error.
        """
        if self._client is None:
            return {}

        try:
            info = await self._client.info()
        except (RedisConnectionError, RedisTimeoutError, RedisError) as exc:
            logger.warning("Redis INFO failed", extra={"error": str(exc)})
            return {}

        return {
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
        }


# Module-level singleton

redis_client = RedisClient()