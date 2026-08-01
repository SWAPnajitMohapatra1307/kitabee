"""Tests for the health and cache metrics endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx

from src.main import app


async def _get(path: str) -> httpx.Response:
    """Send a GET request to the test app."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        return await client.get(path)


class TestHealthEndpoint:
    async def test_returns_200(self):
        response = await _get("/health")
        assert response.status_code == 200

    async def test_success_envelope_shape(self):
        response = await _get("/health")
        body = response.json()

        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_data_contains_status_ok(self):
        response = await _get("/health")
        assert response.json()["data"]["status"] == "ok"

    async def test_meta_has_version_v1(self):
        response = await _get("/health")
        assert response.json()["meta"]["version"] == "v1"

    async def test_meta_has_timestamp(self):
        response = await _get("/health")
        meta = response.json()["meta"]

        assert "timestamp" in meta
        assert meta["timestamp"]


class TestCacheMetricsConnected:
    async def test_returns_200(self):
        mock_info = {"connected_clients": 1, "used_memory_human": "1.00M"}

        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=mock_info,
        ):
            response = await _get("/health/cache")

        assert response.status_code == 200

    async def test_connected_true_when_info_returned(self):
        mock_info = {"connected_clients": 1, "used_memory_human": "1.00M"}

        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=mock_info,
        ):
            response = await _get("/health/cache")

        assert response.json()["data"]["connected"] is True

    async def test_info_payload_returned(self):
        mock_info = {"connected_clients": 1, "used_memory_human": "1.00M"}

        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=mock_info,
        ):
            response = await _get("/health/cache")

        assert response.json()["data"]["info"] == mock_info

    async def test_success_envelope_shape(self):
        mock_info = {"connected_clients": 1}

        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=mock_info,
        ):
            response = await _get("/health/cache")

        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body


class TestCacheMetricsDisconnected:
    async def test_returns_200_even_when_redis_down(self):
        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await _get("/health/cache")

        assert response.status_code == 200

    async def test_connected_false_when_none_returned(self):
        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await _get("/health/cache")

        assert response.json()["data"]["connected"] is False

    async def test_info_is_none_when_redis_down(self):
        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await _get("/health/cache")

        assert response.json()["data"]["info"] is None

    async def test_empty_dict_treated_as_connected(self):
        """Empty dict means Redis responded but returned no fields."""
        with patch(
            "src.api.routes.health.redis_client.get_info",
            new_callable=AsyncMock,
            return_value={},
        ):
            response = await _get("/health/cache")

        assert response.json()["data"]["connected"] is True