"""Unit tests for the Redis cache layer.

Uses fakeredis to avoid dependency on a running Redis instance.
Every test is isolated: a fresh in-memory Redis is patched into the
module-level redis_client for each test.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import fakeredis.aioredis
import pytest

from src.cache import decorators as decorators_module
from src.cache import redis_client as redis_module
from src.cache.decorators import cached
from src.cache.redis_client import RedisClient


# Fixtures

@pytest.fixture
async def fake_redis() -> AsyncIterator[RedisClient]:
    """Provide a RedisClient backed by fakeredis for one test.

    Patches the module-level singleton in both redis_client and
    decorators modules so decorators use the fake too.
    """
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    client = RedisClient()
    client._client = fake

    original_module_client = redis_module.redis_client
    original_decorator_client = decorators_module.redis_client
    redis_module.redis_client = client
    decorators_module.redis_client = client

    try:
        yield client
    finally:
        await fake.flushall()
        await fake.aclose()
        redis_module.redis_client = original_module_client
        decorators_module.redis_client = original_decorator_client


# RedisClient — basic get/set/delete/exists

class TestRedisClientBasics:
    """Verify core RedisClient operations."""

    async def test_get_returns_none_on_miss(self, fake_redis: RedisClient) -> None:
        result = await fake_redis.get("missing_key")
        assert result is None

    async def test_set_then_get_returns_value(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("key1", {"a": 1, "b": [2, 3]}, ttl_seconds=60)
        result = await fake_redis.get("key1")
        assert result == {"a": 1, "b": [2, 3]}

    async def test_set_stores_strings(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("key2", "hello", ttl_seconds=60)
        assert await fake_redis.get("key2") == "hello"

    async def test_set_stores_lists(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("key3", [1, 2, 3], ttl_seconds=60)
        assert await fake_redis.get("key3") == [1, 2, 3]

    async def test_delete_removes_key(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("key4", "value", ttl_seconds=60)
        assert await fake_redis.get("key4") == "value"
        await fake_redis.delete("key4")
        assert await fake_redis.get("key4") is None

    async def test_delete_nonexistent_key_returns_true(
        self, fake_redis: RedisClient
    ) -> None:
        result = await fake_redis.delete("never_existed")
        assert result is True

    async def test_exists_true_when_key_present(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("key5", "v", ttl_seconds=60)
        assert await fake_redis.exists("key5") is True

    async def test_exists_false_when_key_absent(self, fake_redis: RedisClient) -> None:
        assert await fake_redis.exists("nope") is False


# RedisClient — TTL and validation

class TestRedisClientTTL:
    """Verify TTL enforcement and validation."""

    async def test_set_rejects_zero_ttl(self, fake_redis: RedisClient) -> None:
        with pytest.raises(ValueError, match="ttl_seconds must be positive"):
            await fake_redis.set("k", "v", ttl_seconds=0)

    async def test_set_rejects_negative_ttl(self, fake_redis: RedisClient) -> None:
        with pytest.raises(ValueError, match="ttl_seconds must be positive"):
            await fake_redis.set("k", "v", ttl_seconds=-5)

    async def test_ttl_is_applied(self, fake_redis: RedisClient) -> None:
        await fake_redis.set("k_ttl", "v", ttl_seconds=100)
        ttl = await fake_redis._client.ttl("k_ttl")
        assert 0 < ttl <= 100


# RedisClient — error handling

class TestRedisClientErrorHandling:
    """Verify graceful degradation on errors."""

    async def test_get_returns_none_when_not_connected(self) -> None:
        client = RedisClient()
        assert await client.get("k") is None

    async def test_set_returns_false_when_not_connected(self) -> None:
        client = RedisClient()
        assert await client.set("k", "v", ttl_seconds=60) is False

    async def test_delete_returns_false_when_not_connected(self) -> None:
        client = RedisClient()
        assert await client.delete("k") is False

    async def test_exists_returns_false_when_not_connected(self) -> None:
        client = RedisClient()
        assert await client.exists("k") is False

    async def test_get_info_returns_empty_when_not_connected(self) -> None:
        client = RedisClient()
        assert await client.get_info() == {}

    async def test_get_returns_none_on_invalid_json(
        self, fake_redis: RedisClient
    ) -> None:
        # Insert raw non-JSON bytes directly into fake redis
        await fake_redis._client.set("bad_json", "not{valid}json")
        result = await fake_redis.get("bad_json")
        assert result is None

    async def test_set_returns_false_on_unserializable_value(
        self, fake_redis: RedisClient
    ) -> None:
        # A set is not JSON-serializable
        result = await fake_redis.set("k", {1, 2, 3}, ttl_seconds=60)
        assert result is False


# RedisClient — get_info

class TestRedisClientInfo:
    """Verify info endpoint returns expected keys."""

    async def test_get_info_returns_empty_when_backend_unsupported(
        self, fake_redis: RedisClient
    ) -> None:
        """fakeredis does not implement INFO — verify graceful failure.

        The get_info method catches the RedisError and returns an empty
        dict rather than propagating the exception. A live Redis instance
        is tested separately in the manual smoke tests.
        """
        info = await fake_redis.get_info()
        assert info == {}


# @cached decorator

class TestCachedDecorator:
    """Verify the @cached decorator behavior."""

    async def test_caches_result_across_calls(self, fake_redis: RedisClient) -> None:
        call_count = 0

        @cached(key_prefix="test:add", ttl_seconds=60)
        async def add(a: int, b: int) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        r1 = await add(2, 3)
        r2 = await add(2, 3)

        assert r1 == 5
        assert r2 == 5
        assert call_count == 1

    async def test_different_args_produce_different_keys(
        self, fake_redis: RedisClient
    ) -> None:
        call_count = 0

        @cached(key_prefix="test:mul", ttl_seconds=60)
        async def mul(a: int, b: int) -> int:
            nonlocal call_count
            call_count += 1
            return a * b

        await mul(2, 3)
        await mul(4, 5)
        await mul(2, 3)

        assert call_count == 2

    async def test_kwargs_affect_cache_key(self, fake_redis: RedisClient) -> None:
        call_count = 0

        @cached(key_prefix="test:kw", ttl_seconds=60)
        async def fn(a: int, b: int = 10) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        await fn(1, b=2)
        await fn(1, b=3)
        await fn(1, b=2)

        assert call_count == 2

    async def test_does_not_cache_none_result(self, fake_redis: RedisClient) -> None:
        call_count = 0

        @cached(key_prefix="test:none", ttl_seconds=60)
        async def returns_none() -> None:
            nonlocal call_count
            call_count += 1
            return None

        await returns_none()
        await returns_none()
        await returns_none()

        assert call_count == 3

    async def test_does_not_cache_exceptions(self, fake_redis: RedisClient) -> None:
        call_count = 0

        @cached(key_prefix="test:err", ttl_seconds=60)
        async def raises() -> int:
            nonlocal call_count
            call_count += 1
            raise ValueError("boom")

        with pytest.raises(ValueError):
            await raises()
        with pytest.raises(ValueError):
            await raises()

        assert call_count == 2

    async def test_caches_complex_return_types(self, fake_redis: RedisClient) -> None:
        call_count = 0

        @cached(key_prefix="test:complex", ttl_seconds=60)
        async def fetch() -> dict:
            nonlocal call_count
            call_count += 1
            return {"items": [1, 2, 3], "meta": {"count": 3}}

        r1 = await fetch()
        r2 = await fetch()

        assert r1 == {"items": [1, 2, 3], "meta": {"count": 3}}
        assert r2 == r1
        assert call_count == 1

    async def test_rejects_zero_ttl(self) -> None:
        with pytest.raises(ValueError, match="ttl_seconds must be positive"):

            @cached(key_prefix="test:bad", ttl_seconds=0)
            async def fn() -> int:
                return 1

    async def test_rejects_negative_ttl(self) -> None:
        with pytest.raises(ValueError, match="ttl_seconds must be positive"):

            @cached(key_prefix="test:bad", ttl_seconds=-1)
            async def fn() -> int:
                return 1

    async def test_falls_through_when_cache_unavailable(self) -> None:
        # No fake_redis fixture — module-level client has no _client set
        call_count = 0

        @cached(key_prefix="test:nocache", ttl_seconds=60)
        async def fn() -> int:
            nonlocal call_count
            call_count += 1
            return 42

        r1 = await fn()
        r2 = await fn()

        assert r1 == 42
        assert r2 == 42
        assert call_count == 2

    async def test_preserves_function_metadata(self) -> None:
        @cached(key_prefix="test:meta", ttl_seconds=60)
        async def documented_fn(x: int) -> int:
            """A documented function."""
            return x

        assert documented_fn.__name__ == "documented_fn"
        assert documented_fn.__doc__ == "A documented function."


# Key generation

class TestKeyGeneration:
    """Verify deterministic key building."""

    async def test_same_args_produce_same_key(self, fake_redis: RedisClient) -> None:
        keys_seen = []

        @cached(key_prefix="test:key", ttl_seconds=60)
        async def fn(a: int, b: str) -> str:
            return f"{a}-{b}"

        # Prime cache
        await fn(1, "hello")

        # Track by inspecting fakeredis keyspace
        redis_keys = [k async for k in fake_redis._client.scan_iter(match="test:key:*")]
        keys_seen.append(redis_keys[0])

        # Call again with same args → same key
        await fn(1, "hello")
        redis_keys_after = [
            k async for k in fake_redis._client.scan_iter(match="test:key:*")
        ]

        assert redis_keys == redis_keys_after
        assert len(redis_keys) == 1