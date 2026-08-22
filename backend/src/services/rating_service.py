"""Business logic for the ratings feature."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.book import get_book_by_external_id, _extract_published_year
from src.database.crud.rating import (
    delete_rating,
    get_rating,
    get_ratings_by_user,
    recalculate_book_stats,
    upsert_rating,
)
from src.database.models.book import Book
from src.database.models.rating import Rating
from src.schemas.rating import RatingCreate
from src.services.content_normalizer import get_source_for_prefix, parse_content_id

logger = logging.getLogger(__name__)


class RatingService:
    """Handles rating create, update, delete, and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def resolve_content_id(self, content_id: str) -> UUID | None:
        """Resolve a prefixed content_id to an internal book UUID.

        Looks up the book in the DB by external_id + external_source.
        Returns None when the book has not been persisted yet.
        """
        parsed = parse_content_id(content_id)
        if parsed is None:
            raw_id = content_id
            source = "google_books"
        else:
            prefix, raw_id = parsed
            source = get_source_for_prefix(prefix) or "google_books"

        book = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=source,
        )

        if book is None:
            logger.info(
                "Book not in DB for rating — not yet persisted",
                extra={"content_id": content_id},
            )
            return None

        return book.id

    async def ensure_book_in_db(self, item: dict[str, Any]) -> UUID:
        """Ensure a book item exists in the DB, creating it if missing."""
        content_id = str(item.get("content_id") or item.get("id") or "")
        parsed = parse_content_id(content_id)

        if parsed is None:
            raw_id = str(item.get("external_id") or content_id)
            source = str(item.get("external_source") or item.get("source") or "google_books")
        else:
            prefix, raw_id = parsed
            source = get_source_for_prefix(prefix) or "google_books"

        # Check again in case it was created concurrently
        existing = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=source,
        )
        if existing is not None:
            return existing.id

        # Determine authors list
        authors_list: list[str] = []
        raw_authors = item.get("authors")
        if isinstance(raw_authors, list):
            authors_list = [str(a) for a in raw_authors if a]
        elif isinstance(raw_authors, str) and raw_authors:
            authors_list = [raw_authors]

        if not authors_list:
            single_author = item.get("author")
            if single_author:
                authors_list = [str(single_author)]

        now = datetime.now(timezone.utc)

        new_book = Book(
            id=uuid4(),
            external_id=raw_id,
            external_source=source,
            title=item.get("title") or "Untitled",
            authors=authors_list,
            description=item.get("description"),
            cover_url=item.get("cover_url"),
            cover_url_large=item.get("cover_url_large") or item.get("cover_url"),
            genres=item.get("genres") or [],
            published_year=_extract_published_year(item.get("published_date")),
            cached_at=now,
            updated_at=now,
        )

        self._db.add(new_book)
        await self._db.commit()
        await self._db.refresh(new_book)
        logger.info(
            "Created new book record in DB for seed/external content",
            extra={"content_id": content_id, "book_id": str(new_book.id)},
        )
        return new_book.id

    async def rate_book(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
        payload: RatingCreate,
    ) -> Rating:
        """Create or update a rating, then refresh book stats."""
        rating = await upsert_rating(
            self._db,
            user_id=user_id,
            book_id=book_id,
            rating=payload.rating,
            review_title=payload.review_title,
            review_text=payload.review_text,
            is_spoiler=payload.is_spoiler,
        )
        await recalculate_book_stats(self._db, book_id=book_id)
        await self._db.commit()
        await self._db.refresh(rating)
        return rating

    async def get_my_rating(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
    ) -> Rating | None:
        """Return the current user's rating for a book, or None."""
        return await get_rating(self._db, user_id=user_id, book_id=book_id)

    async def delete_my_rating(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
    ) -> bool:
        """Delete the current user's rating for a book."""
        deleted = await delete_rating(self._db, user_id=user_id, book_id=book_id)
        if deleted:
            await recalculate_book_stats(self._db, book_id=book_id)
            await self._db.commit()
        return deleted

    async def get_my_ratings(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Rating], int]:
        """Return paginated list of all ratings by the current user."""
        return await get_ratings_by_user(
            self._db,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )