"""CRUD operations for the ratings table."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.book import Book
from src.database.models.rating import Rating


async def get_rating(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
) -> Rating | None:
    """Return the rating a user gave a book, or None if not rated."""
    result = await db.execute(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.book_id == book_id,
        )
    )
    return result.scalar_one_or_none()


async def get_ratings_by_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Rating], int]:
    """Return paginated ratings for a user plus total count."""
    count_result = await db.execute(
        select(func.count()).where(Rating.user_id == user_id)
    )
    total = count_result.scalar_one()

    rows_result = await db.execute(
        select(Rating)
        .where(Rating.user_id == user_id)
        .order_by(Rating.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    ratings = list(rows_result.scalars().all())
    return ratings, total


async def upsert_rating(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
    rating: int,
    review_title: str | None = None,
    review_text: str | None = None,
    is_spoiler: bool = False,
) -> Rating:
    """Create a new rating or update an existing one.

    Uses SELECT then INSERT/UPDATE rather than a raw ON CONFLICT clause
    so the ORM session stays consistent.
    """
    existing = await get_rating(db, user_id=user_id, book_id=book_id)

    if existing is not None:
        existing.rating = rating
        existing.review_title = review_title
        existing.review_text = review_text
        existing.is_spoiler = is_spoiler
        await db.flush()
        await db.refresh(existing)
        return existing

    new_rating = Rating(
        user_id=user_id,
        book_id=book_id,
        rating=rating,
        review_title=review_title,
        review_text=review_text,
        is_spoiler=is_spoiler,
    )
    db.add(new_rating)
    await db.flush()
    await db.refresh(new_rating)
    return new_rating


async def delete_rating(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
) -> bool:
    """Delete a rating. Returns True if a row was deleted, False if not found."""
    result = await db.execute(
        delete(Rating).where(
            Rating.user_id == user_id,
            Rating.book_id == book_id,
        )
    )
    return result.rowcount > 0


async def recalculate_book_stats(
    db: AsyncSession,
    *,
    book_id: UUID,
) -> None:
    """Recompute kitabee_rating and kitabee_ratings_count for a book.

    Runs a single aggregate query then updates the books row.
    Called after every create, update, or delete.
    """
    agg_result = await db.execute(
        select(
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.id).label("total"),
        ).where(Rating.book_id == book_id)
    )
    row = agg_result.one()
    avg = round(float(row.avg_rating), 2) if row.avg_rating is not None else None
    count = row.total

    await db.execute(
        update(Book)
        .where(Book.id == book_id)
        .values(kitabee_rating=avg, kitabee_ratings_count=count)
    )