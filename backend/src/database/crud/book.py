"""CRUD helpers for the ``books`` table."""

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
COMIC_VINE_SOURCE = "comic_vine"
INTERNET_ARCHIVE_SOURCE = "internet_archive"

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
    if not isinstance(published_date, str):
        return None
    year_part = published_date[:4]
    if len(year_part) != 4 or not year_part.isdigit():
        return None
    return int(year_part)


def _build_google_metadata(data: dict[str, Any]) -> dict[str, Any]:
    google_books_meta: dict[str, Any] = {}

    preview_link = data.get("preview_link")
    if preview_link is not None:
        google_books_meta["preview_link"] = preview_link

    info_link = data.get("info_link")
    if info_link is not None:
        google_books_meta["info_link"] = info_link

    series_info = data.get("series_info")
    if isinstance(series_info, dict):
        google_books_meta["seriesInfo"] = series_info

    if not google_books_meta:
        return {}

    return {"google_books": google_books_meta}


def _build_comic_vine_metadata(data: dict[str, Any]) -> dict[str, Any]:
    comic_vine_meta: dict[str, Any] = {}

    volume = data.get("volume")
    if isinstance(volume, dict) and volume.get("id") and volume.get("name"):
        comic_vine_meta["volume"] = {
            "id": volume["id"],
            "name": volume["name"],
        }

    issue_number = data.get("issue_number")
    if issue_number is not None:
        comic_vine_meta["issue_number"] = issue_number

    if not comic_vine_meta:
        return {}

    return {"comic_vine": comic_vine_meta}


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


def _book_kwargs_from_google(data: dict[str, Any]) -> dict[str, Any]:
    external_id = data.get("google_books_id") or data.get("external_id")
    if not external_id:
        raise ValueError("external_id or google_books_id is required to persist a book")

    now = datetime.now(timezone.utc)

    small_thumbnail_url = data.get("small_thumbnail_url")
    thumbnail_url = data.get("thumbnail_url") or data.get("cover_url")

    return {
        "external_id": str(external_id),
        "external_source": GOOGLE_BOOKS_SOURCE,
        "title": data.get("title") or "Unknown Title",
        "subtitle": data.get("subtitle"),
        "authors": data.get("authors") or [],
        "description": data.get("description"),
        "genres": data.get("categories") or data.get("genres") or [],
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
        "metadata_json": _build_google_metadata(data),
        "cached_at": now,
        "updated_at": now,
    }


def _apply_book_updates(book: Book, values: dict[str, Any]) -> None:
    for field in _MUTABLE_FIELDS:
        setattr(book, field, values[field])


async def get_book_by_id(
    db: AsyncSession,
    book_id: UUID,
) -> Optional[Book]:
    return await db.get(Book, book_id)


async def get_book_by_external_id(
    db: AsyncSession,
    external_id: str,
    external_source: str = GOOGLE_BOOKS_SOURCE,
) -> Optional[Book]:
    stmt = select(Book).where(
        Book.external_source == external_source,
        Book.external_id == external_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_book(
    db: AsyncSession,
    *,
    external_id: str,
    external_source: str = GOOGLE_BOOKS_SOURCE,
    title: str = "Unknown Title",
    authors: Optional[list[str]] = None,
    cover_url: Optional[str] = None,
    description: Optional[str] = None,
    genres: Optional[list[str]] = None,
    content_type: str = "book",
    is_free: bool = False,
    free_url: Optional[str] = None,
) -> Book:
    """Create or return existing book by external_id and external_source."""
    existing = await get_book_by_external_id(
        db, external_id=external_id, external_source=external_source
    )
    if existing is not None:
        return existing

    now = datetime.now(timezone.utc)
    metadata: dict[str, Any] = {}
    if free_url:
        metadata["read_url"] = free_url

    book = Book(
        external_id=external_id,
        external_source=external_source,
        title=title,
        subtitle=None,
        authors=authors or [],
        description=description,
        genres=genres or [],
        tags=[],
        isbn_10=None,
        isbn_13=None,
        published_year=None,
        publisher=None,
        page_count=None,
        language="en",
        cover_url=cover_url,
        cover_url_large=cover_url,
        average_rating=None,
        ratings_count=0,
        kitabee_rating=None,
        kitabee_ratings_count=0,
        metadata_json=metadata,
        cached_at=now,
        updated_at=now,
    )
    db.add(book)

    try:
        await db.commit()
        await db.refresh(book)
        return book
    except IntegrityError:
        await db.rollback()
        existing = await get_book_by_external_id(
            db, external_id=external_id, external_source=external_source
        )
        if existing is None:
            raise
        return existing


async def upsert_book_from_google(
    db: AsyncSession,
    data: dict[str, Any],
) -> Book:
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


def _book_kwargs_from_comic_vine(data: dict[str, Any]) -> dict[str, Any]:
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
        "metadata_json": _build_comic_vine_metadata(data),
        "cached_at": now,
        "updated_at": now,
    }


def _book_kwargs_from_internet_archive(data: dict[str, Any]) -> dict[str, Any]:
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