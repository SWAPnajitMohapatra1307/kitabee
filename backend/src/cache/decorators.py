"""Cache decorators for async functions.

Provides the @cached decorator that wraps async functions with a
cache-aside pattern: check Redis first, call the wrapped function on
miss, then write the result to Redis with a TTL.

Design rules:
- None results are never cached (avoids poisoning on transient errors).
- Exceptions from the wrapped function are never cached.
- Cache errors never affect the wrapped function's behavior.
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
from typing import Any, Awaitable, Callable, TypeVar

from src.cache.redis_client import redis_client


logger = logging.getLogger(__name__)


# Constants

KEY_HASH_LENGTH = 16


# Type aliases

T = TypeVar("T")
AsyncFunc = Callable[..., Awaitable[T]]


# Public API

def cached(
    key_prefix: str,
    ttl_seconds: int,
) -> Callable[[AsyncFunc[T]], AsyncFunc[T]]:
    """Cache the result of an async function in Redis.

    Uses a deterministic key derived from the prefix and a hash of the
    function arguments. Falls back to calling the wrapped function on
    any cache miss or Redis error.

    Args:
        key_prefix: Namespace for the cache key (e.g. "gb:search").
        ttl_seconds: Time-to-live for cached values in seconds.

    Returns:
        A decorator that wraps an async function with caching.

    Raises:
        ValueError: If ttl_seconds is not positive.

    Example:
        @cached(key_prefix="gb:volume", ttl_seconds=86400)
        async def get_volume(volume_id: str) -> dict:
            return await google_books.get_by_id(volume_id)
    """
    if ttl_seconds <= 0:
        raise ValueError(f"ttl_seconds must be positive, got {ttl_seconds}")

    def decorator(func: AsyncFunc[T]) -> AsyncFunc[T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = _build_key(key_prefix, args, kwargs)

            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                logger.debug(
                    "Cache hit",
                    extra={"key": cache_key, "func": func.__name__},
                )
                return cached_value  # type: ignore[return-value]

            logger.debug(
                "Cache miss",
                extra={"key": cache_key, "func": func.__name__},
            )
            result = await func(*args, **kwargs)

            if result is not None:
                await redis_client.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


# Private helpers

def _build_key(prefix: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Build a deterministic cache key from function arguments.

    Serializes args and kwargs to JSON, hashes them with SHA-256, and
    truncates to KEY_HASH_LENGTH characters. This keeps keys short while
    remaining collision-resistant for realistic argument spaces.

    Args:
        prefix: Namespace prefix for the key.
        args: Positional arguments passed to the wrapped function.
        kwargs: Keyword arguments passed to the wrapped function.

    Returns:
        Cache key in the format "{prefix}:{hash}".
    """
    payload = {
        "args": _normalize(args),
        "kwargs": _normalize(kwargs),
    }
    serialized = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:KEY_HASH_LENGTH]}"


def _normalize(value: Any) -> Any:
    """Recursively convert a value into a JSON-serializable form.

    Tuples become lists. Sets become sorted lists. Other types fall
    through to json.dumps's default=str handler.

    Args:
        value: Any Python value.

    Returns:
        A JSON-serializable equivalent.
    """
    if isinstance(value, tuple):
        return [_normalize(v) for v in value]
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        return sorted(_normalize(v) for v in value)
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value