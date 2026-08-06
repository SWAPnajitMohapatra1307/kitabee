"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.response import error_envelope
from src.api.routes import auth, books, health, library, preferences, ratings, users
from src.api.routes.series import router as series_router
from src.cache.redis_client import redis_client
from src.external.google_books import GoogleBooksClient


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    Startup:
    - Connect to Redis. Cache failures at startup are non-fatal — the
      app still serves requests, cache operations degrade to misses.
    - Instantiate a single GoogleBooksClient stored on app.state so all
      requests share one httpx connection pool.

    Shutdown:
    - Close the Google Books client.
    - Close the Redis connection pool.
    """
    try:
        await redis_client.connect()
    except Exception as exc:
        logger.warning(
            "Redis unavailable at startup; cache disabled",
            extra={"error": str(exc)},
        )

    app.state.google_books_client = GoogleBooksClient()
    logger.info("Google Books client initialized")

    yield

    await app.state.google_books_client.close()
    logger.info("Google Books client closed")

    await redis_client.close()


app = FastAPI(
    title="Kitabee API",
    version="0.1.0",
    lifespan=lifespan,
)


# Exception handlers — normalize all errors to the standard envelope

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert Pydantic validation errors into the standard error envelope."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_envelope(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=exc.errors(),
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Convert HTTPException into the standard error envelope.

    Accepts two detail shapes:
    - A dict with keys 'code' and 'message' (our preferred style).
    - A plain string (FastAPI default) — mapped to a generic code.
    """
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        code = exc.detail["code"]
        message = exc.detail["message"]
        details = exc.detail.get("details")
    else:
        code = _default_code_for_status(exc.status_code)
        message = str(exc.detail) if exc.detail is not None else "An error occurred."
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(code=code, message=message, details=details),
    )


def _default_code_for_status(status_code: int) -> str:
    """Map an HTTP status code to a default machine-readable error code."""
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    return mapping.get(status_code, "ERROR")


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(ratings.router)
app.include_router(library.router)
app.include_router(preferences.router)
app.include_router(series_router)