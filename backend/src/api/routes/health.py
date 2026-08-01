"""Health and metrics endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.api.response import success_envelope
from src.cache.redis_client import redis_client


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> JSONResponse:
    """Basic health check.

    Returns:
        JSON response confirming the API is reachable.
    """
    return JSONResponse(content=success_envelope({"status": "ok"}))


@router.get("/cache")
async def cache_metrics() -> JSONResponse:
    """Return Redis cache metrics.

    Reports connected clients, memory usage, keyspace hit and miss
    counts, and uptime. Returns connected=False when Redis is unreachable.

    Returns:
        JSON response with cache metrics under data.
    """
    info = await redis_client.get_info()
    return JSONResponse(
        content=success_envelope({"connected": info is not None, "info": info})
    )