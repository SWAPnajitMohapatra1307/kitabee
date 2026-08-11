"""Content router — dispatches fetch requests by content_id prefix.

Given a prefixed content_id (e.g. "gb:ByLKDQAAQBAJ"), this module
determines which external API to call, fetches the raw data, normalizes
it into a unified ContentItem dict, and optionally persists it to the DB.

Prefix conventions:
    gb:{id}  — Google Books
    cv:{id}  — Comic Vine issue
    ia:{id}  — Internet Archive
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.external.google_books import GoogleBooksClient
from src.external.comic_vine import ComicVineClient
from src.external.internet_archive import InternetArchiveClient
from src.services.content_normalizer import (
    PREFIX_CV,
    PREFIX_GB,
    PREFIX_IA,
    SOURCE_COMIC_VINE,
    SOURCE_GOOGLE_BOOKS,
    SOURCE_INTERNET_ARCHIVE,
    normalize_comic_vine_issue,
    normalize_google_books,
    normalize_internet_archive,
    parse_content_id,
)
from src.database.crud.book import (
    get_book_by_external_id,
    upsert_book_from_google,
    upsert_book_from_comic_vine,
    upsert_book_from_internet_archive,
)

logger = logging.getLogger(__name__)


class ContentRouter:
    """Fetches and normalizes content from any supported external source.

    Injected with all three API clients and a DB session. Route handlers
    receive one per request via FastAPI Depends.
    """

    def __init__(
        self,
        google_books: GoogleBooksClient,
        comic_vine: ComicVineClient,
        internet_archive: InternetArchiveClient,
        db: AsyncSession,
    ) -> None:
        self._gb = google_books
        self._cv = comic_vine
        self._ia = internet_archive
        self._db = db

    async def get_by_content_id(
        self,
        content_id: str,
    ) -> Optional[dict[str, Any]]:
        """Fetch and normalize a single item by prefixed content_id.

        Read order for all sources:
            1. PostgreSQL — check if already persisted.
            2. External API — fetch, normalize, persist, return.

        Args:
            content_id: Prefixed ID like "gb:ByLKDQAAQBAJ".

        Returns:
            Normalized ContentItem dict, or None when not found.
        """
        parsed = parse_content_id(content_id)
        if parsed is None:
            logger.warning(
                "Invalid content_id format",
                extra={"content_id": content_id},
            )
            return None

        prefix, raw_id = parsed

        if prefix == PREFIX_GB:
            return await self._fetch_google_books(raw_id)
        if prefix == PREFIX_CV:
            return await self._fetch_comic_vine(raw_id)
        if prefix == PREFIX_IA:
            return await self._fetch_internet_archive(raw_id)

        logger.warning("Unhandled prefix", extra={"prefix": prefix})
        return None

    async def get_similar(
        self,
        content_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch similar content based on a source item's metadata.

        Strategy per source:
            gb: — search Google Books by author + genre of source item
            cv: — search Comic Vine by series name of source item
            ia: — search Internet Archive by subject of source item

        Args:
            content_id: Prefixed ID of the source item.
            limit: Maximum number of similar items to return.

        Returns:
            List of normalized ContentItem dicts (may be empty).
        """
        source_item = await self.get_by_content_id(content_id)
        if source_item is None:
            return []

        parsed = parse_content_id(content_id)
        if parsed is None:
            return []

        prefix, raw_id = parsed

        if prefix == PREFIX_GB:
            return await self._similar_google_books(source_item, raw_id, limit)
        if prefix == PREFIX_CV:
            return await self._similar_comic_vine(source_item, raw_id, limit)
        if prefix == PREFIX_IA:
            return await self._similar_internet_archive(source_item, raw_id, limit)

        return []

    async def search(
        self,
        query: str,
        limit: int = 10,
        sources: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search across one or more sources and return normalized results.

        Args:
            query: Free-text search string.
            limit: Maximum results per source.
            sources: List of source strings to search. Defaults to all three.

        Returns:
            Combined list of normalized ContentItem dicts.
        """
        if sources is None:
            sources = [SOURCE_GOOGLE_BOOKS, SOURCE_COMIC_VINE, SOURCE_INTERNET_ARCHIVE]

        results: list[dict[str, Any]] = []

        if SOURCE_GOOGLE_BOOKS in sources:
            try:
                raw_items = await self._gb.search(query=query, max_results=limit)
                for raw in raw_items:
                    normalized = normalize_google_books(raw)
                    if normalized is not None:
                        results.append(normalized)
            except Exception:
                logger.warning(
                    "Google Books search failed in router",
                    extra={"query": query},
                    exc_info=True,
                )

        if SOURCE_COMIC_VINE in sources:
            try:
                raw_items = await self._cv.search_comics(query=query, limit=limit)
                for raw in raw_items:
                    normalized = normalize_comic_vine_issue(raw)
                    if normalized is not None:
                        results.append(normalized)
            except Exception:
                logger.warning(
                    "Comic Vine search failed in router",
                    extra={"query": query},
                    exc_info=True,
                )

        if SOURCE_INTERNET_ARCHIVE in sources:
            try:
                raw_items = await self._ia.search_free_books(query=query, limit=limit)
                for raw in raw_items:
                    normalized = normalize_internet_archive(raw)
                    if normalized is not None:
                        results.append(normalized)
            except Exception:
                logger.warning(
                    "Internet Archive search failed in router",
                    extra={"query": query},
                    exc_info=True,
                )

        return results

    async def _fetch_google_books(self, raw_id: str) -> Optional[dict[str, Any]]:
        """Fetch a Google Books item — DB first, then API."""
        existing = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=SOURCE_GOOGLE_BOOKS,
        )
        if existing is not None:
            return _db_book_to_content_item(existing, PREFIX_GB)

        raw = await self._gb.get_by_id(raw_id)
        if raw is None:
            return None

        normalized = normalize_google_books(raw)
        if normalized is None:
            return None

        try:
            await upsert_book_from_google(self._db, raw)
        except Exception:
            logger.warning(
                "Failed to persist Google Books item",
                extra={"raw_id": raw_id},
                exc_info=True,
            )

        return normalized

    async def _fetch_comic_vine(self, raw_id: str) -> Optional[dict[str, Any]]:
        """Fetch a Comic Vine item — DB first, then API."""
        existing = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=SOURCE_COMIC_VINE,
        )
        if existing is not None:
            return _db_book_to_content_item(existing, PREFIX_CV)

        raw = await self._cv.get_comic(raw_id)
        if raw is None:
            return None

        normalized = normalize_comic_vine_issue(raw)
        if normalized is None:
            return None

        try:
            await upsert_book_from_comic_vine(self._db, raw)
        except Exception:
            logger.warning(
                "Failed to persist Comic Vine item",
                extra={"raw_id": raw_id},
                exc_info=True,
            )

        return normalized

    async def _fetch_internet_archive(self, raw_id: str) -> Optional[dict[str, Any]]:
        """Fetch an Internet Archive item — DB first, then API."""
        existing = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=SOURCE_INTERNET_ARCHIVE,
        )
        if existing is not None:
            return _db_book_to_content_item(existing, PREFIX_IA)

        raw = await self._ia.get_item(raw_id)
        if raw is None:
            return None

        normalized = normalize_internet_archive(raw)
        if normalized is None:
            return None

        try:
            await upsert_book_from_internet_archive(self._db, normalized)
        except Exception:
            logger.warning(
                "Failed to persist Internet Archive item",
                extra={"raw_id": raw_id},
                exc_info=True,
            )

        return normalized

    async def _similar_google_books(
        self,
        source_item: dict[str, Any],
        raw_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Find similar books via Google Books search."""
        parts: list[str] = []
        authors = source_item.get("authors") or []
        genres = source_item.get("genres") or []

        if authors:
            parts.append(authors[0])
        if genres:
            parts.append(genres[0])
        if not parts:
            parts.append(source_item.get("title", ""))

        query = " ".join(parts).strip()
        if not query:
            return []

        try:
            raw_items = await self._gb.search(
                query=query,
                max_results=min(limit + 1, 40),
            )
        except Exception:
            logger.warning("Google Books similar search failed", exc_info=True)
            return []

        results: list[dict[str, Any]] = []
        for raw in raw_items:
            if raw.get("google_books_id") == raw_id:
                continue
            normalized = normalize_google_books(raw)
            if normalized is not None:
                results.append(normalized)
            if len(results) >= limit:
                break

        return results

    async def _similar_comic_vine(
        self,
        source_item: dict[str, Any],
        raw_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Find similar comics via Comic Vine search by series name."""
        title = source_item.get("title", "")
        if not title:
            return []

        try:
            raw_items = await self._cv.search_comics(
                query=title,
                limit=min(limit + 1, 100),
            )
        except Exception:
            logger.warning("Comic Vine similar search failed", exc_info=True)
            return []

        results: list[dict[str, Any]] = []
        for raw in raw_items:
            raw_item_id = str(raw.get("id", "")).replace("cv_", "").replace("cv:", "")
            if raw_item_id == raw_id:
                continue
            normalized = normalize_comic_vine_issue(raw)
            if normalized is not None:
                results.append(normalized)
            if len(results) >= limit:
                break

        return results

    async def _similar_internet_archive(
        self,
        source_item: dict[str, Any],
        raw_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Find similar IA items by subject."""
        genres = source_item.get("genres") or []
        title = source_item.get("title", "")
        query = genres[0] if genres else title
        if not query:
            return []

        try:
            raw_items = await self._ia.search_free_books(
                query=query,
                limit=min(limit + 1, 50),
            )
        except Exception:
            logger.warning("Internet Archive similar search failed", exc_info=True)
            return []

        results: list[dict[str, Any]] = []
        for raw in raw_items:
            raw_item_id = str(raw.get("id", "")).replace("ia_", "").replace("ia:", "")
            if raw_item_id == raw_id:
                continue
            normalized = normalize_internet_archive(raw)
            if normalized is not None:
                results.append(normalized)
            if len(results) >= limit:
                break

        return results

def _extract_free_url(book: Any, prefix: str) -> Optional[str]:
    """Return the free read URL for a persisted book if available."""
    if prefix != PREFIX_IA:
        return None
    meta = getattr(book, "metadata_json", None) or {}
    if isinstance(meta, dict):
        url = meta.get("read_url") or meta.get("free_url")
        if url:
            return url
    return f"https://archive.org/details/{book.external_id}"

def _db_book_to_content_item(book: Any, prefix: str) -> dict[str, Any]:
    """Convert a DB Book ORM object into a normalized ContentItem dict.

    Args:
        book: SQLAlchemy Book ORM instance.
        prefix: Source prefix string ("gb", "cv", "ia").

    Returns:
        Normalized ContentItem dict.
    """
    from src.services.content_normalizer import make_content_id

    content_id = make_content_id(prefix, book.external_id)
    authors = book.authors or []
    author_str = ", ".join(authors) if authors else None
    is_free = book.external_source == SOURCE_INTERNET_ARCHIVE

    return {
        "content_id": content_id,
        "external_id": book.external_id,
        "external_source": book.external_source,
        "title": book.title,
        "author": author_str,
        "authors": authors,
        "description": book.description,
        "cover_url": book.cover_url,
        "cover_url_large": book.cover_url_large,
        "content_type": "comic" if prefix == PREFIX_CV else "book",
        "is_free": is_free,
        "free_url": _extract_free_url(book, prefix),
        "genres": book.genres or [],
        "language": book.language or "en",
        "publisher": book.publisher,
        "published_date": str(book.published_year) if book.published_year else None,
        "page_count": book.page_count,
        "isbn_10": book.isbn_10,
        "isbn_13": book.isbn_13,
        "average_rating": float(book.average_rating) if book.average_rating else None,
        "rating_count": book.ratings_count or 0,
        "series_id": None,
        "series_order": None,
        "source": book.external_source,
    }