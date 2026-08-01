"""Book service — business logic layer for book search and retrieval.

Sits between the API route and the external clients (Google Books, DB, cache).
Responsibilities:
- Delegate to GoogleBooksClient for external data fetching.
- Persist books to PostgreSQL on first fetch (cache-through pattern).
- Convert raw dicts into Pydantic response models.
- Assemble paginated response envelopes.

Cache-through read order for get_by_id:
    1. PostgreSQL (via book CRUD)
    2. Not found → 404 (UUID only exists after search persistence)

Cache-through read order for get_similar:
    1. Google Books API (search by author + genre)
    2. Persist results to DB as side-effect
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.book import (
    get_book_by_external_id,
    get_book_by_id,
    upsert_book_from_google,
)
from src.external.google_books import GoogleBooksClient
from src.schemas.book import (
    BookDetailResponse,
    BookSearchResponse,
    BookSearchResult,
)


logger = logging.getLogger(__name__)

_DEFAULT_SIMILAR_LIMIT = 10


class BookService:
    """Business logic for book operations.

    Injected with a GoogleBooksClient and an AsyncSession. Route handlers
    receive one per request via FastAPI's Depends system.
    """

    def __init__(
        self,
        google_books: GoogleBooksClient,
        db: AsyncSession,
    ) -> None:
        """Initialize with external client and database session.

        Args:
            google_books: Initialized GoogleBooksClient instance.
            db: Active async SQLAlchemy session for the current request.
        """
        self._google_books = google_books
        self._db = db

    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> BookSearchResponse:
        """Search books and return a paginated response envelope.

        Persists each result to the database as a side-effect so that
        subsequent detail lookups can be served from PostgreSQL.

        Note: Google Books API does not natively support offset-based
        pagination — it uses startIndex. Full pagination via startIndex
        will land in a later iteration.

        Args:
            query: The search string (already validated by route).
            limit: Maximum results to return (already bounded by route).
            offset: Number of results to skip (currently unused).

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

        # Persist each result to DB in the background of the request.
        # Failures are logged but never bubble up — search results are
        # still returned from Google Books data even if DB write fails.
        for raw in raw_items:
            try:
                await upsert_book_from_google(self._db, raw)
            except Exception:
                logger.warning(
                    "Failed to persist book from search result",
                    extra={"google_books_id": raw.get("google_books_id")},
                    exc_info=True,
                )

        results = [BookSearchResult.model_validate(item) for item in raw_items]

        logger.info(
            "Book search completed",
            extra={"query": query, "returned": len(results)},
        )

        return BookSearchResponse(
            query=query,
            total_count=len(results),
            limit=limit,
            offset=offset,
            results=results,
        )

    async def get_by_id(self, book_id: UUID) -> BookDetailResponse | None:
        """Fetch a single book by its Kitabee UUID.

        The UUID only exists after a book has been seen in search results
        and persisted. Unknown UUIDs return None → 404 at route layer.

        Args:
            book_id: Internal Kitabee UUID from URL path.

        Returns:
            BookDetailResponse when found, None when UUID is unknown.
        """
        logger.info(
            "Book detail lookup",
            extra={"book_id": str(book_id)},
        )

        book = await get_book_by_id(self._db, book_id)

        if book is None:
            logger.info(
                "Book not found in DB",
                extra={"book_id": str(book_id)},
            )
            return None

        return BookDetailResponse.model_validate(book)

    async def get_by_google_id(self, google_books_id: str) -> BookDetailResponse | None:
        """Fetch a single book by its Google Books volume ID.

        Cache-through read order:
            1. PostgreSQL — check if already persisted.
            2. Google Books API — fetch and persist if not in DB.

        Args:
            google_books_id: Google Books volume ID string.

        Returns:
            BookDetailResponse when found, None when volume does not exist.
        """
        logger.info(
            "Book detail lookup by Google ID",
            extra={"google_books_id": google_books_id},
        )

        book = await get_book_by_external_id(
            self._db,
            external_id=google_books_id,
        )

        if book is not None:
            logger.info(
                "Book detail DB hit",
                extra={"google_books_id": google_books_id},
            )
            return BookDetailResponse.model_validate(book)

        raw = await self._google_books.get_by_id(google_books_id)

        if raw is None:
            return None

        book = await upsert_book_from_google(self._db, raw)
        return BookDetailResponse.model_validate(book)

    async def get_similar(
        self,
        book_id: UUID,
        limit: int = _DEFAULT_SIMILAR_LIMIT,
    ) -> BookSearchResponse | None:
        """Find books similar to a given Kitabee book UUID.

        Similarity strategy (Day 6 — no ML yet):
            1. Fetch source book from DB by UUID.
            2. If not found, return None → 404 at route layer.
            3. Build a query from the book's first author + first genre.
               Falls back to title-only when both are absent.
            4. Search Google Books with that query.
            5. Exclude the source book itself from results.
            6. Persist results to DB as side-effect.
            7. Return BookSearchResponse with the similarity query as context.

        Args:
            book_id: Kitabee internal UUID of the source book.
            limit: Maximum similar books to return (1-40).

        Returns:
            BookSearchResponse when source book is found,
            None when UUID is unknown.
        """
        logger.info(
            "Similar books lookup",
            extra={"book_id": str(book_id), "limit": limit},
        )

        source = await get_book_by_id(self._db, book_id)

        if source is None:
            logger.info(
                "Source book not found for similar lookup",
                extra={"book_id": str(book_id)},
            )
            return None

        # Build similarity query from available metadata.
        parts: list[str] = []
        if source.authors:
            parts.append(source.authors[0])
        if source.genres:
            parts.append(source.genres[0])
        if not parts:
            parts.append(source.title)

        similarity_query = " ".join(parts)

        logger.info(
            "Similar books query built",
            extra={
                "book_id": str(book_id),
                "similarity_query": similarity_query,
            },
        )

        # Fetch one extra to cover the case where source book appears
        # in results and gets filtered out.
        raw_items = await self._google_books.search(
            query=similarity_query,
            max_results=min(limit + 1, 40),
        )

        # Filter out the source book by external_id.
        filtered = [
            item for item in raw_items
            if item.get("google_books_id") != source.external_id
        ][:limit]

        # Persist as side-effect.
        for raw in filtered:
            try:
                await upsert_book_from_google(self._db, raw)
            except Exception:
                logger.warning(
                    "Failed to persist similar book",
                    extra={"google_books_id": raw.get("google_books_id")},
                    exc_info=True,
                )

        results = [BookSearchResult.model_validate(item) for item in filtered]

        logger.info(
            "Similar books lookup completed",
            extra={
                "book_id": str(book_id),
                "returned": len(results),
            },
        )

        return BookSearchResponse(
            query=similarity_query,
            total_count=len(results),
            limit=limit,
            offset=0,
            results=results,
        )