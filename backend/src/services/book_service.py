"""Book service — business logic layer for book search and retrieval.

Sits between the API route and the external Google Books client.
Responsibilities:
- Delegate to GoogleBooksClient for data fetching (which handles caching + retry).
- Convert raw dicts into Pydantic response models.
- Assemble paginated response envelopes.

Does NOT handle HTTP concerns (that's the route's job) or caching
(that's already inside GoogleBooksClient).
"""

from __future__ import annotations

import logging

from src.external.google_books import GoogleBooksClient
from src.schemas.book import BookSearchResponse, BookSearchResult


logger = logging.getLogger(__name__)


# Public API

class BookService:
    """Business logic for book operations.

    Injected with a GoogleBooksClient. Route handlers instantiate one
    per request via FastAPI's Depends system, or the app can share a
    single client via app.state for connection reuse.
    """

    def __init__(self, google_books: GoogleBooksClient) -> None:
        """Initialize with an external books client.

        Args:
            google_books: An initialized GoogleBooksClient instance.
        """
        self._google_books = google_books

    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> BookSearchResponse:
        """Search books and return a paginated response envelope.

        Note: Google Books API does not natively support offset-based
        pagination — it uses startIndex. Day 5 implementation fetches
        limit results per call. Full pagination via startIndex will
        land when we add multi-page support in a later iteration.

        Args:
            query: The search string (already validated by route).
            limit: Maximum results to return (already bounded by route).
            offset: Number of results to skip (currently unused — see note).

        Returns:
            BookSearchResponse with query context, pagination metadata,
            and mapped BookSearchResult items.
        """
        logger.info(
            "Book search dispatched",
            extra={"query": query, "limit": limit, "offset": offset},
        )

        raw_items = await self._google_books.search(
            query=query,
            max_results=limit,
        )

        results = [BookSearchResult.model_validate(item) for item in raw_items]

        logger.info(
            "Book search completed",
            extra={
                "query": query,
                "returned": len(results),
            },
        )

        return BookSearchResponse(
            query=query,
            total_count=len(results),
            limit=limit,
            offset=offset,
            results=results,
        )