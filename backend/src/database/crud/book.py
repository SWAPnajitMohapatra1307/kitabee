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

# Fields updated on every upsert. Excludes identity fields (external_id,
# external_source) and Kitabee-owned fields (kitabee_rating,
# kitabee_ratings_count) which are never overwritten by upstream data.
_MUTABLE_FIELDS = (
    "title",
    "subtitle",
    "authors",
    "description",
    "genres",
    "tags",
    "isbn_10",
    "isbn_13",
    "published_year",
    "publisher",
    "page_count",
    "language",
    "cover_url",
    "cover_url_large",
    "average_rating",
    "ratings_count",
    "metadata_json",
    "cached_at",
    "updated_at",
)


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
    """Apply mutable fields onto an existing Book ORM object.

    Only fields listed in ``_MUTABLE_FIELDS`` are written. Identity
    and Kitabee-owned fields are never touched.
    """
    for field in _MUTABLE_FIELDS:
        setattr(book, field, values[field])


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

COMIC_VINE_SOURCE = "comic_vine"
INTERNET_ARCHIVE_SOURCE = "internet_archive"


def _book_kwargs_from_comic_vine(data: dict[str, Any]) -> dict[str, Any]:
    """Translate Comic Vine normalized data into Book ORM fields."""
    external_id = data.get("external_id")
    if not external_id:
        raise ValueError("external_id is required to persist a Comic Vine item")

    now = datetime.now(timezone.utc)

    return {
        "external_id": str(external_id),
        "external_source": COMIC_VINE_SOURCE,
        "title": data.get("title") or "Unknown Title",
        "subtitle": None,
        "authors": data.get("authors") or [],
        "description": data.get("description"),
        "genres": data.get("genres") or [],
        "tags": [],
        "isbn_10": None,
        "isbn_13": None,
        "published_year": _extract_published_year(data.get("published_date")),
        "publisher": data.get("publisher"),
        "page_count": None,
        "language": data.get("language") or "en",
        "cover_url": data.get("cover_url"),
        "cover_url_large": data.get("cover_url_large"),
        "average_rating": None,
        "ratings_count": 0,
        "kitabee_rating": None,
        "kitabee_ratings_count": 0,
        "metadata_json": {},
        "cached_at": now,
        "updated_at": now,
    }


def _book_kwargs_from_internet_archive(data: dict[str, Any]) -> dict[str, Any]:
    """Translate Internet Archive normalized data into Book ORM fields."""
    external_id = data.get("external_id")
    if not external_id:
        raise ValueError("external_id is required to persist an Internet Archive item")

    now = datetime.now(timezone.utc)

    read_url = data.get("free_url") or data.get("read_url")
    metadata: dict[str, Any] = {}
    if read_url:
        metadata["read_url"] = read_url

    return {
        "external_id": str(external_id),
        "external_source": INTERNET_ARCHIVE_SOURCE,
        "title": data.get("title") or "Unknown Title",
        "subtitle": None,
        "authors": data.get("authors") or [],
        "description": data.get("description"),
        "genres": data.get("genres") or [],
        "tags": [],
        "isbn_10": None,
        "isbn_13": None,
        "published_year": _extract_published_year(data.get("published_date")),
        "publisher": None,
        "page_count": None,
        "language": data.get("language") or "en",
        "cover_url": data.get("cover_url"),
        "cover_url_large": data.get("cover_url_large"),
        "average_rating": None,
        "ratings_count": 0,
        "kitabee_rating": None,
        "kitabee_ratings_count": 0,
        "metadata_json": metadata,
        "cached_at": now,
        "updated_at": now,
    }


async def upsert_book_from_comic_vine(
    db: AsyncSession,
    data: dict[str, Any],
) -> Book:
    """Create or update a book row from Comic Vine normalized data.

    Accepts output from content_normalizer.normalize_comic_vine_issue()
    or normalize_comic_vine_volume(). Uses external_id + external_source
    as the unique key.

    Args:
        db: Active async SQLAlchemy session.
        data: Normalized ContentItem dict from the Comic Vine normalizer.

    Returns:
        Persisted Book ORM instance.
    """
    values = _book_kwargs_from_comic_vine(data)

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


async def upsert_book_from_internet_archive(
    db: AsyncSession,
    data: dict[str, Any],
) -> Book:
    """Create or update a book row from Internet Archive normalized data.

    Accepts output from content_normalizer.normalize_internet_archive().
    Uses external_id + external_source as the unique key.

    Args:
        db: Active async SQLAlchemy session.
        data: Normalized ContentItem dict from the IA normalizer.

    Returns:
        Persisted Book ORM instance.
    """
    values = _book_kwargs_from_internet_archive(data)

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