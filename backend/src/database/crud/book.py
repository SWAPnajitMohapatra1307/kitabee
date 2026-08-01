"""CRUD helpers for the ``books`` table.

This module is the database repository layer for books.
It handles:
- lookup by internal UUID
- lookup by external source + external ID
- create/update from Google Books mapped payloads
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import Book


GOOGLE_BOOKS_SOURCE = "google_books"


def _extract_published_year(published_date: Any) -> Optional[int]:
    """Extract a year from a normalized YYYY-MM-DD date string."""
    if not isinstance(published_date, str):
        return None

    year_part = published_date[:4]
    if len(year_part) != 4 or not year_part.isdigit():
        return None

    return int(year_part)


def _build_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Build the JSONB metadata payload for the books table."""
    google_books_meta: dict[str, Any] = {}

    preview_link = data.get("preview_link")
    if preview_link is not None:
        google_books_meta["preview_link"] = preview_link

    info_link = data.get("info_link")
    if info_link is not None:
        google_books_meta["info_link"] = info_link

    if not google_books_meta:
        return {}

    return {"google_books": google_books_meta}


def _to_decimal(value: Any) -> Optional[Decimal]:
    """Convert numeric input to Decimal, preserving None."""
    if value is None:
        return None
    return Decimal(str(value))


def _book_kwargs_from_google(data: dict[str, Any]) -> dict[str, Any]:
    """Translate Google Books mapped data into Book ORM fields."""
    external_id = data.get("google_books_id")
    if not external_id:
        raise ValueError("google_books_id is required to persist a book")

    now = datetime.now(timezone.utc)

    small_thumbnail_url = data.get("small_thumbnail_url")
    thumbnail_url = data.get("thumbnail_url")

    return {
        "external_id": external_id,
        "external_source": GOOGLE_BOOKS_SOURCE,
        "title": data.get("title") or "Unknown Title",
        "subtitle": data.get("subtitle"),
        "authors": data.get("authors") or [],
        "description": data.get("description"),
        "genres": data.get("categories") or [],
        "tags": [],
        "isbn_10": data.get("isbn_10"),
        "isbn_13": data.get("isbn_13"),
        "published_year": _extract_published_year(data.get("published_date")),
        "publisher": data.get("publisher"),
        "page_count": data.get("page_count"),
        "language": data.get("language") or "en",
        "cover_url": small_thumbnail_url or thumbnail_url,
        "cover_url_large": thumbnail_url or small_thumbnail_url,
        "average_rating": _to_decimal(data.get("average_rating")),
        "ratings_count": data.get("ratings_count") or 0,
        "kitabee_rating": None,
        "kitabee_ratings_count": 0,
        "metadata_json": _build_metadata(data),
        "cached_at": now,
        "updated_at": now,
    }


def _apply_book_updates(book: Book, values: dict[str, Any]) -> None:
    """Apply mutable fields onto an existing Book ORM object."""
    book.title = values["title"]
    book.subtitle = values["subtitle"]
    book.authors = values["authors"]
    book.description = values["description"]
    book.genres = values["genres"]
    book.tags = values["tags"]
    book.isbn_10 = values["isbn_10"]
    book.isbn_13 = values["isbn_13"]
    book.published_year = values["published_year"]
    book.publisher = values["publisher"]
    book.page_count = values["page_count"]
    book.language = values["language"]
    book.cover_url = values["cover_url"]
    book.cover_url_large = values["cover_url_large"]
    book.average_rating = values["average_rating"]
    book.ratings_count = values["ratings_count"]
    book.metadata_json = values["metadata_json"]
    book.cached_at = values["cached_at"]
    book.updated_at = values["updated_at"]


async def get_book_by_id(
    db: AsyncSession,
    book_id: UUID,
) -> Optional[Book]:
    """Fetch a book by internal UUID."""
    return await db.get(Book, book_id)


async def get_book_by_external_id(
    db: AsyncSession,
    external_id: str,
    external_source: str = GOOGLE_BOOKS_SOURCE,
) -> Optional[Book]:
    """Fetch a book by external source and external ID."""
    stmt = select(Book).where(
        Book.external_source == external_source,
        Book.external_id == external_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_book_from_google(
    db: AsyncSession,
    data: dict[str, Any],
) -> Book:
    """Create or update a book row from Google Books mapped data.

    First tries lookup by (external_source, external_id).
    If found, updates mutable metadata.
    If not found, creates a new row.

    Handles unique-race collisions by rolling back and re-fetching.
    """
    values = _book_kwargs_from_google(data)

    existing = await get_book_by_external_id(
        db=db,
        external_id=values["external_id"],
        external_source=values["external_source"],
    )

    if existing is not None:
        _apply_book_updates(existing, values)
        await db.commit()
        await db.refresh(existing)
        return existing

    book = Book(**values)
    db.add(book)

    try:
        await db.commit()
        await db.refresh(book)
        return book
    except IntegrityError:
        await db.rollback()

        existing = await get_book_by_external_id(
            db=db,
            external_id=values["external_id"],
            external_source=values["external_source"],
        )
        if existing is None:
            raise

        _apply_book_updates(existing, values)
        await db.commit()
        await db.refresh(existing)
        return existing