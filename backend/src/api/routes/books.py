"""Book endpoints — search, details, similar."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.deps import get_book_service
from src.api.response import success_envelope
from src.external.google_books import TransientAPIError
from src.schemas.book import (
    DEFAULT_LIMIT,
    DEFAULT_SIMILAR_LIMIT,
    MAX_LIMIT,
    MAX_QUERY_LENGTH,
    MIN_LIMIT,
    MIN_QUERY_LENGTH,
    BookDetailResponse,
    BookSearchResponse,
)
from src.services.book_service import BookService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.get("/search")
async def search_books(
    q: str = Query(
        ...,
        min_length=MIN_QUERY_LENGTH,
        max_length=MAX_QUERY_LENGTH,
        description="Search query (title, author, ISBN).",
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Maximum results to return (1-40).",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of results to skip (currently unused).",
    ),
    service: BookService = Depends(get_book_service),
) -> JSONResponse:
    """Search books via the Google Books API.

    Returns a paginated envelope of book results. Empty results return
    an empty list, not a 404. Upstream failures return 503.

    Args:
        q: Search string (2-200 chars).
        limit: Page size (1-40, default 20).
        offset: Results to skip (default 0).
        service: Injected BookService dependency.

    Returns:
        JSON response with the standard envelope wrapping BookSearchResponse.

    Raises:
        HTTPException 503: When the upstream Google Books API fails.
    """
    try:
        payload: BookSearchResponse = await service.search(
            query=q,
            limit=limit,
            offset=offset,
        )
    except TransientAPIError as exc:
        logger.error(
            "Book search upstream failure",
            extra={"query": q, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "UPSTREAM_UNAVAILABLE",
                "message": "Book search is temporarily unavailable. Please try again.",
            },
        ) from exc

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))


@router.get("/{book_id}/similar")
async def get_similar_books(
    book_id: UUID,
    limit: int = Query(
        DEFAULT_SIMILAR_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description="Maximum similar books to return (1-40).",
    ),
    service: BookService = Depends(get_book_service),
) -> JSONResponse:
    """Find books similar to a given Kitabee book UUID.

    Similarity is based on the source book's author and genre.
    The source book is excluded from results. Unknown UUIDs return 404.

    Args:
        book_id: Kitabee internal UUID of the source book.
        limit: Maximum results (1-40, default 10).
        service: Injected BookService dependency.

    Returns:
        JSON response with the standard envelope wrapping BookSearchResponse.

    Raises:
        HTTPException 404: When book_id is not found in the database.
        HTTPException 503: When the upstream Google Books API fails.
    """
    try:
        payload: BookSearchResponse | None = await service.get_similar(
            book_id=book_id,
            limit=limit,
        )
    except TransientAPIError as exc:
        logger.error(
            "Similar books upstream failure",
            extra={"book_id": str(book_id), "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "UPSTREAM_UNAVAILABLE",
                "message": "Similar books are temporarily unavailable. Please try again.",
            },
        ) from exc

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "BOOK_NOT_FOUND",
                "message": f"No book found with id {book_id}.",
            },
        )

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))


@router.get("/{book_id}")
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
) -> JSONResponse:
    """Fetch full book details by Kitabee UUID.

    The UUID is assigned when a book is first seen in search results
    and persisted to the database. Unknown UUIDs return 404.

    Args:
        book_id: Kitabee internal UUID from URL path.
        service: Injected BookService dependency.

    Returns:
        JSON response with the standard envelope wrapping BookDetailResponse.

    Raises:
        HTTPException 404: When the UUID is not found in the database.
        HTTPException 503: When an upstream failure occurs.
    """
    try:
        payload: BookDetailResponse | None = await service.get_by_id(book_id)
    except TransientAPIError as exc:
        logger.error(
            "Book detail upstream failure",
            extra={"book_id": str(book_id), "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "UPSTREAM_UNAVAILABLE",
                "message": "Book details are temporarily unavailable. Please try again.",
            },
        ) from exc

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "BOOK_NOT_FOUND",
                "message": f"No book found with id {book_id}.",
            },
        )

    return JSONResponse(content=success_envelope(payload.model_dump(mode="json")))