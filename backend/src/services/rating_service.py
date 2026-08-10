"""Business logic for the ratings feature."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.book import get_book_by_external_id
from src.database.crud.rating import (
    delete_rating,
    get_rating,
    get_ratings_by_user,
    recalculate_book_stats,
    upsert_rating,
)
from src.database.models.rating import Rating
from src.schemas.rating import RatingCreate
from src.services.content_normalizer import parse_content_id, get_source_for_prefix

logger = logging.getLogger(__name__)


class RatingService:
    """Handles rating create, update, delete, and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def resolve_content_id(self, content_id: str) -> UUID | None:
        """Resolve a prefixed content_id to an internal book UUID.

        Looks up the book in the DB by external_id + external_source.
        Returns None when the book has not been persisted yet.

        Args:
            content_id: Prefixed ID like "gb:ByLKDQAAQBAJ".

        Returns:
            Internal book UUID, or None when not found in DB.
        """
        parsed = parse_content_id(content_id)
        if parsed is None:
            logger.warning(
                "Invalid content_id in rating resolution",
                extra={"content_id": content_id},
            )
            return None

        prefix, raw_id = parsed
        source = get_source_for_prefix(prefix)
        if source is None:
            return None

        book = await get_book_by_external_id(
            self._db,
            external_id=raw_id,
            external_source=source,
        )

        if book is None:
            logger.info(
                "Book not in DB for rating — not yet fetched via detail endpoint",
                extra={"content_id": content_id},
            )
            return None

        return book.id

    async def rate_book(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
        payload: RatingCreate,
    ) -> Rating:
        """Create or update a rating, then refresh book stats.

        Args:
            user_id: Internal user UUID.
            book_id: Internal book UUID (resolved from content_id at route layer).
            payload: Rating data from request body.

        Returns:
            Persisted Rating ORM instance.
        """
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
        """Return the current user's rating for a book, or None.

        Args:
            user_id: Internal user UUID.
            book_id: Internal book UUID.

        Returns:
            Rating ORM instance, or None when not found.
        """
        return await get_rating(self._db, user_id=user_id, book_id=book_id)

    async def delete_my_rating(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
    ) -> bool:
        """Delete the current user's rating for a book.

        Args:
            user_id: Internal user UUID.
            book_id: Internal book UUID.

        Returns:
            True when deleted, False when no rating existed.
        """
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
        """Return paginated list of all ratings by the current user.

        Args:
            user_id: Internal user UUID.
            limit: Page size.
            offset: Results to skip.

        Returns:
            Tuple of (ratings list, total count).
        """
        return await get_ratings_by_user(
            self._db,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )