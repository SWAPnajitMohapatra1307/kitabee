"""Business logic for the ratings feature."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.rating import (
    delete_rating,
    get_rating,
    get_ratings_by_user,
    recalculate_book_stats,
    upsert_rating,
)
from src.database.models.rating import Rating
from src.schemas.rating import RatingCreate


class RatingService:
    """Handles rating create, update, delete, and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def rate_book(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
        payload: RatingCreate,
    ) -> Rating:
        """Create or update a rating, then refresh book stats.

        Upsert pattern: one call handles both first-time and repeat ratings.
        Book stats (avg, count) are recalculated after every change.
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
        """Return the current user's rating for a book, or None."""
        return await get_rating(self._db, user_id=user_id, book_id=book_id)

    async def delete_my_rating(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
    ) -> bool:
        """Delete the current user's rating for a book.

        Returns True if deleted, False if no rating existed.
        Book stats are recalculated after deletion.
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
        """Return paginated list of all ratings by the current user."""
        return await get_ratings_by_user(
            self._db,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )