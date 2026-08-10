"""Book endpoints — search, detail, similar.

All endpoints now accept prefixed content_id strings (gb:, cv:, ia:)
instead of internal UUIDs. The ContentRouter dispatches to the correct
external API based on the prefix.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.deps import get_content_router, get_book_service
from src.api.response import success_envelope
from src.schemas.book import (
    DEFAULT_LIMIT,
    DEFAULT_SIMILAR_LIMIT,
    MAX_LIMIT,
    MAX_QUERY_LENGTH,
    MIN_LIMIT,
    MIN_QUERY_LENGTH,
    ContentItemResponse,
    ContentItemListResponse,
)
from src.services.content_router import ContentRouter
from src.services.book_service import BookService
from src.services.content_normalizer import parse_content_id


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/books", tags=["books"])


def _raise_404(content_id: str) -> None:
    """Raise 404 for an unknown content_id.

    Args:
        content_id: The prefixed ID that was not found.

    Raises:
        HTTPException: Always raises 404 NOT_FOUND.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "CONTENT_NOT_FOUND",
            "message": f"No content found with id {content_id}.",
        },
    )


def _raise_400(content_id: str) -> None:
    """Raise 400 for a malformed content_id.

    Args:
        content_id: The malformed ID string.

    Raises:
        HTTPException: Always raises 400 BAD_REQUEST.
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "INVALID_CONTENT_ID",
            "message": (
                f"Invalid content_id format: '{content_id}'. "
                "Expected format: gb:{{id}}, cv:{{id}}, or ia:{{id}}."
            ),
        },
    )


def _raise_503(message: str, exc: Exception) -> None:
    """Raise 503 for upstream API failures.

    Args:
        message: Human-readable error message.
        exc: Original exception chained onto the HTTPException.

    Raises:
        HTTPException: Always raises 503 SERVICE_UNAVAILABLE.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "UPSTREAM_UNAVAILABLE",
            "message": message,
        },
    ) from exc


@router.get("/search")
async def search_books(
    q: str = Query(
        ...,
        min_length=MIN_QUERY_LENGTH,
        max_length=MAX_QUERY_LENGTH,
        description="Search query (title, author, ISBN, character).",
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Maximum results per source (1-40).",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Results to skip (currently unused).",
    ),
    sources: str = Query(
        "google_books,comic_vine,internet_archive",
        description="Comma-separated source list. Options: google_books, comic_vine, internet_archive.",
    ),
    router: ContentRouter = Depends(get_content_router),
) -> JSONResponse:
    """Search content across Google Books, Comic Vine, and Internet Archive.

    Returns a unified list of ContentItemResponse objects regardless of source.
    Empty results return an empty list, not a 404.

    Args:
        q: Search string (2-200 chars).
        limit: Max results per source (1-40, default 20).
        offset: Results to skip (default 0, currently unused).
        sources: Comma-separated source names to search.
        router: Injected ContentRouter dependency.

    Returns:
        JSON envelope wrapping ContentItemListResponse.

    Raises:
        HTTPException 503: When all upstream sources fail.
    """
    source_list = [s.strip() for s in sources.split(",") if s.strip()]

    try:
        items = await router.search(
            query=q,
            limit=limit,
            sources=source_list if source_list else None,
        )
    except Exception as exc:
        logger.error(
            "Search failed across all sources",
            extra={"query": q, "error": str(exc)},
            exc_info=True,
        )
        _raise_503("Search is temporarily unavailable. Please try again.", exc)

    paginated = items[offset: offset + limit] if offset else items

    payload = ContentItemListResponse(
        total_count=len(items),
        limit=limit,
        offset=offset,
        results=[ContentItemResponse(**item) for item in paginated],
    )

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))


@router.get("/{content_id}/similar")
async def get_similar_content(
    content_id: str,
    limit: int = Query(
        DEFAULT_SIMILAR_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Maximum similar items to return (1-40).",
    ),
    router: ContentRouter = Depends(get_content_router),
) -> JSONResponse:
    """Find content similar to a given item by prefixed content_id.

    Similarity strategy depends on source:
        gb: — author + genre search via Google Books
        cv: — series name search via Comic Vine
        ia: — subject search via Internet Archive

    Args:
        content_id: Prefixed ID like "gb:ByLKDQAAQBAJ".
        limit: Maximum results (1-40, default 10).
        router: Injected ContentRouter dependency.

    Returns:
        JSON envelope wrapping ContentItemListResponse.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When source item is not found.
    """
    if parse_content_id(content_id) is None:
        _raise_400(content_id)

    try:
        items = await router.get_similar(content_id=content_id, limit=limit)
    except Exception as exc:
        logger.error(
            "Similar content lookup failed",
            extra={"content_id": content_id, "error": str(exc)},
            exc_info=True,
        )
        _raise_503("Similar content is temporarily unavailable. Please try again.", exc)

    payload = ContentItemListResponse(
        total_count=len(items),
        limit=limit,
        offset=0,
        results=[ContentItemResponse(**item) for item in items],
    )

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))


@router.get("/{content_id}")
async def get_content_detail(
    content_id: str,
    router: ContentRouter = Depends(get_content_router),
) -> JSONResponse:
    """Fetch full content detail by prefixed content_id.

    Accepts any valid prefixed ID:
        gb:{google_books_id}    — fetches from Google Books
        cv:{comic_vine_id}      — fetches from Comic Vine
        ia:{archive_identifier} — fetches from Internet Archive

    DB is checked first. External API called on cache miss.

    Args:
        content_id: Prefixed content identifier.
        router: Injected ContentRouter dependency.

    Returns:
        JSON envelope wrapping ContentItemResponse.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When content is not found in any source.
        HTTPException 503: When upstream API fails.
    """
    if parse_content_id(content_id) is None:
        _raise_400(content_id)

    try:
        item = await router.get_by_content_id(content_id)
    except Exception as exc:
        logger.error(
            "Content detail lookup failed",
            extra={"content_id": content_id, "error": str(exc)},
            exc_info=True,
        )
        _raise_503("Content details are temporarily unavailable. Please try again.", exc)

    if item is None:
        _raise_404(content_id)

    payload = ContentItemResponse(**item)

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))
