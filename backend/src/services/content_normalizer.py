"""Unified content normalizer for all three external API sources.

Converts raw client output from Google Books, Comic Vine, and Internet
Archive into a single ContentItem shape used throughout the API layer.

ID convention (constructed here, never stored in DB):
    gb:{google_books_id}   — Google Books volumes
    cv:{comic_vine_id}     — Comic Vine issues and volumes
    ia:{archive_identifier} — Internet Archive items
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

SOURCE_GOOGLE_BOOKS = "google_books"
SOURCE_COMIC_VINE = "comic_vine"
SOURCE_INTERNET_ARCHIVE = "internet_archive"

PREFIX_GB = "gb"
PREFIX_CV = "cv"
PREFIX_IA = "ia"

SOURCE_TO_PREFIX: dict[str, str] = {
    SOURCE_GOOGLE_BOOKS: PREFIX_GB,
    SOURCE_COMIC_VINE: PREFIX_CV,
    SOURCE_INTERNET_ARCHIVE: PREFIX_IA,
}

PREFIX_TO_SOURCE: dict[str, str] = {v: k for k, v in SOURCE_TO_PREFIX.items()}


def _coerce_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v)
    return str(value)


def make_content_id(prefix: str, raw_id: Any) -> Optional[str]:
    if raw_id is None:
        return None
    cleaned = str(raw_id).strip()
    if not cleaned:
        return None
    return f"{prefix}:{cleaned}"


def parse_content_id(content_id: str) -> tuple[str, str] | None:
    if not isinstance(content_id, str):
        return None
    parts = content_id.split(":", 1)
    if len(parts) != 2:
        return None
    prefix, raw_id = parts
    if prefix not in PREFIX_TO_SOURCE:
        return None
    if not raw_id.strip():
        return None
    return prefix, raw_id.strip()


def get_source_for_prefix(prefix: str) -> Optional[str]:
    return PREFIX_TO_SOURCE.get(prefix)


def normalize_google_books(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    raw_id = raw.get("google_books_id")
    content_id = make_content_id(PREFIX_GB, raw_id)
    if content_id is None:
        logger.warning("Google Books item missing google_books_id — skipped")
        return None

    authors = raw.get("authors") or []
    author_str = ", ".join(authors) if authors else None

    return {
        "content_id": content_id,
        "external_id": str(raw_id),
        "external_source": SOURCE_GOOGLE_BOOKS,
        "title": raw.get("title") or "Unknown Title",
        "author": author_str,
        "authors": authors,
        "description": _coerce_str(raw.get("description")),
        "cover_url": raw.get("thumbnail_url"),
        "cover_url_large": raw.get("thumbnail_url"),
        "content_type": "book",
        "is_free": False,
        "free_url": None,
        "genres": raw.get("categories") or [],
        "language": raw.get("language") or "en",
        "publisher": raw.get("publisher"),
        "published_date": raw.get("published_date"),
        "page_count": raw.get("page_count"),
        "isbn_10": raw.get("isbn_10"),
        "isbn_13": raw.get("isbn_13"),
        "average_rating": raw.get("average_rating"),
        "rating_count": raw.get("ratings_count") or 0,
        "series_id": None,
        "series_order": None,
        "source": SOURCE_GOOGLE_BOOKS,
    }


def normalize_comic_vine_issue(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    raw_id_field = raw.get("id")
    if raw_id_field is None:
        logger.warning("Comic Vine issue missing id — skipped")
        return None

    raw_id_str = str(raw_id_field)
    if raw_id_str.startswith("cv_"):
        raw_id_str = raw_id_str[3:]
    elif raw_id_str.startswith("cv:"):
        raw_id_str = raw_id_str[3:]

    content_id = make_content_id(PREFIX_CV, raw_id_str)
    if content_id is None:
        return None

    series = raw.get("series")
    issue_number = raw.get("issue_number")
    title = raw.get("title")

    if not title and series and issue_number:
        title = f"{series} #{issue_number}"
    elif not title and series:
        title = series
    elif not title:
        title = "Unknown Comic"

    return {
        "content_id": content_id,
        "external_id": raw_id_str,
        "external_source": SOURCE_COMIC_VINE,
        "title": title,
        "author": None,
        "authors": [],
        "description": _coerce_str(raw.get("description")),
        "cover_url": raw.get("cover_image"),
        "cover_url_large": raw.get("cover_image"),
        "content_type": "comic",
        "is_free": False,
        "free_url": None,
        "genres": [],
        "language": "en",
        "publisher": None,
        "published_date": raw.get("published_date"),
        "page_count": None,
        "isbn_10": None,
        "isbn_13": None,
        "average_rating": None,
        "rating_count": 0,
        "series_id": None,
        "series_order": raw.get("issue_number"),
        "source": SOURCE_COMIC_VINE,
    }


def normalize_comic_vine_volume(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    raw_id_field = raw.get("id")
    if raw_id_field is None:
        logger.warning("Comic Vine volume missing id — skipped")
        return None

    raw_id_str = str(raw_id_field)
    if raw_id_str.startswith("cv_"):
        raw_id_str = raw_id_str[3:]
    elif raw_id_str.startswith("cv:"):
        raw_id_str = raw_id_str[3:]

    content_id = make_content_id(PREFIX_CV, raw_id_str)
    if content_id is None:
        return None

    return {
        "content_id": content_id,
        "external_id": raw_id_str,
        "external_source": SOURCE_COMIC_VINE,
        "title": raw.get("title") or "Unknown Volume",
        "author": None,
        "authors": [],
        "description": _coerce_str(raw.get("description")),
        "cover_url": raw.get("cover_image"),
        "cover_url_large": raw.get("cover_image"),
        "content_type": "comic",
        "is_free": False,
        "free_url": None,
        "genres": [],
        "language": "en",
        "publisher": raw.get("publisher"),
        "published_date": raw.get("start_year"),
        "page_count": None,
        "isbn_10": None,
        "isbn_13": None,
        "average_rating": None,
        "rating_count": 0,
        "series_id": None,
        "series_order": None,
        "source": SOURCE_COMIC_VINE,
    }


def normalize_internet_archive(raw: dict[str, Any]) -> Optional[dict[str, Any]]:
    raw_id_field = raw.get("id")
    if raw_id_field is None:
        logger.warning("Internet Archive item missing id — skipped")
        return None

    raw_id_str = str(raw_id_field)
    if raw_id_str.startswith("ia_"):
        raw_id_str = raw_id_str[3:]
    elif raw_id_str.startswith("ia:"):
        raw_id_str = raw_id_str[3:]

    content_id = make_content_id(PREFIX_IA, raw_id_str)
    if content_id is None:
        return None

    authors = raw.get("authors") or []
    author_str = ", ".join(authors) if authors else None

    subjects = raw.get("subjects") or []

    return {
        "content_id": content_id,
        "external_id": raw_id_str,
        "external_source": SOURCE_INTERNET_ARCHIVE,
        "title": raw.get("title") or "Unknown Title",
        "author": author_str,
        "authors": authors,
        "description": _coerce_str(raw.get("description")),
        "cover_url": raw.get("thumbnail_url"),
        "cover_url_large": raw.get("thumbnail_url"),
        "content_type": "book",
        "is_free": True,
        "free_url": raw.get("read_url"),
        "genres": subjects,
        "language": raw.get("language") or "en",
        "publisher": None,
        "published_date": raw.get("published_date"),
        "page_count": None,
        "isbn_10": None,
        "isbn_13": None,
        "average_rating": None,
        "rating_count": 0,
        "series_id": None,
        "series_order": None,
        "source": SOURCE_INTERNET_ARCHIVE,
    }


def normalize_any(raw: dict[str, Any], source: str) -> Optional[dict[str, Any]]:
    if source == SOURCE_GOOGLE_BOOKS:
        return normalize_google_books(raw)
    if source == SOURCE_COMIC_VINE:
        return normalize_comic_vine_issue(raw)
    if source == SOURCE_INTERNET_ARCHIVE:
        return normalize_internet_archive(raw)
    logger.warning("Unknown source in normalize_any", extra={"source": source})
    return None