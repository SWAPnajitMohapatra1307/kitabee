"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.api.routes import health
from src.cache.redis_client import redis_client


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    Connects to Redis at startup and closes the connection at shutdown.
    A Redis connection failure at startup is logged but does not prevent
    the app from serving requests — cache operations degrade gracefully.
    """
    try:
        await redis_client.connect()
    except Exception as exc:
        logger.warning(
            "Redis unavailable at startup; cache disabled",
            extra={"error": str(exc)},
        )

    yield

    await redis_client.close()


app = FastAPI(
    title="Kitabee API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
