"""Health and metrics endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.cache.redis_client import redis_client


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> JSONResponse:
    """Basic health check.

    Returns:
        JSON response confirming the API is reachable.
    """
    return JSONResponse(content=_wrap({"status": "ok"}))


@router.get("/cache")
async def cache_metrics() -> JSONResponse:
    """Return Redis cache metrics.

    Reports connected clients, memory usage, keyspace hit and miss
    counts, and uptime. Returns an empty info dict with connected=False
    when Redis is unreachable.

    Returns:
        JSON response with cache metrics under data.
    """
    info = await redis_client.get_info()
    payload = {
        "connected": bool(info),
        "info": info,
    }
    return JSONResponse(content=_wrap(payload))


def _wrap(data: dict[str, Any]) -> dict[str, Any]:
    """Wrap a data payload in the standard response envelope.

    Args:
        data: Response payload.

    Returns:
        Envelope with success flag, data, and meta block.
    """
    return {
        "success": True,
        "data": data,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v1",
        },
    }