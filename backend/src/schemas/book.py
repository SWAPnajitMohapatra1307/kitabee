"""Pydantic schemas for the book search and detail APIs.

Defines the request and response shapes for:
    GET /api/v1/books/search
    GET /api/v1/books/{book_id}

Day 5: BookSearchResult backed by Google Books mapper output.
Day 6: BookDetailResponse adds DB-persisted fields (UUID, kitabee_rating,
        external_source, metadata_json).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_LIMIT = 20
MIN_LIMIT = 1
MAX_LIMIT = 40
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 200
DEFAULT_SIMILAR_LIMIT = 10


# ---------------------------------------------------------------------------
# Search schemas
# ---------------------------------------------------------------------------

class BookSearchResult(BaseModel):
    """A single book returned in search results.

    Backed by the Google Books mapper output. Does not include DB fields
    (UUID, kitabee_rating) because books may not be persisted yet at the
    time the search response is assembled.
    """

    model_config = ConfigDict(from_attributes=True)

    google_books_id: str = Field(
        ...,
        description="Google Books volume ID.",
    )
    title: str = Field(..., max_length=500)
    subtitle: Optional[str] = Field(None, max_length=500)
    authors: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = Field(
        None,
        description="Normalized YYYY-MM-DD from Google Books publishedDate.",
    )
    page_count: Optional[int] = Field(None, gt=0)
    categories: list[str] = Field(default_factory=list)
    language: Optional[str] = None
    isbn_10: Optional[str] = Field(None, max_length=10)
    isbn_13: Optional[str] = Field(None, max_length=13)
    thumbnail_url: Optional[str] = None
    small_thumbnail_url: Optional[str] = None
    average_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    ratings_count: Optional[int] = Field(None, ge=0)
    preview_link: Optional[str] = None
    info_link: Optional[str] = None


class BookSearchResponse(BaseModel):
    """Paginated envelope for book search results."""

    query: str
    total_count: int = Field(..., ge=0)
    limit: int = Field(..., ge=MIN_LIMIT, le=MAX_LIMIT)
    offset: int = Field(..., ge=0)
    results: list[BookSearchResult]


# ---------------------------------------------------------------------------
# Detail schema
# ---------------------------------------------------------------------------

class BookDetailResponse(BaseModel):
    """Full book detail returned from GET /api/v1/books/{book_id}.

    Backed by the Book ORM model. Includes DB-persisted fields that are
    not available in search results (UUID, kitabee_rating, metadata).
    """

    model_config = ConfigDict(from_attributes=True)

    # DB identity
    id: UUID = Field(..., description="Kitabee internal UUID.")
    external_id: str = Field(..., description="Google Books volume ID.")
    external_source: str = Field(..., description="Source API identifier.")

    # Core metadata
    title: str
    subtitle: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    page_count: Optional[int] = None
    genres: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    language: str = "en"

    # Identifiers
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None

    # Images
    cover_url: Optional[str] = None
    cover_url_large: Optional[str] = None

    # Ratings — external source
    average_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    ratings_count: Optional[int] = Field(None, ge=0)

    # Ratings — Kitabee users
    kitabee_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    kitabee_ratings_count: int = Field(0, ge=0)

    # Flexible metadata from source API
    metadata_json: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra fields from the source API (preview links, etc.).",
    )


class ContentItemResponse(BaseModel):
    """Unified response shape for any content item regardless of source.

    Used by:
        GET /api/v1/books/{content_id}
        GET /api/v1/books/{content_id}/similar
        GET /api/v1/collections (items inside rows)

    The content_id field uses the prefixed convention:
        gb:{id}  — Google Books
        cv:{id}  — Comic Vine
        ia:{id}  — Internet Archive
    """

    model_config = ConfigDict(from_attributes=True)

    content_id: str = Field(
        ...,
        description="Prefixed canonical identifier (gb:, cv:, ia:).",
    )
    external_id: str = Field(
        ...,
        description="Raw ID from the external source.",
    )
    external_source: str = Field(
        ...,
        description="Source API: google_books, comic_vine, internet_archive.",
    )
    title: str
    author: Optional[str] = Field(
        None,
        description="Primary author display string (joined from authors list).",
    )
    authors: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    cover_url_large: Optional[str] = None
    content_type: str = Field(
        "book",
        description="'book' or 'comic'.",
    )
    is_free: bool = Field(
        False,
        description="True for Internet Archive public domain content.",
    )
    free_url: Optional[str] = Field(
        None,
        description="Direct read URL when is_free is True.",
    )
    genres: list[str] = Field(default_factory=list)
    language: str = "en"
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = Field(None, gt=0)
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    average_rating: Optional[float] = Field(None, ge=0, le=5)
    rating_count: int = Field(0, ge=0)
    series_id: Optional[str] = None
    series_order: Optional[str] = None
    source: str = Field(
        ...,
        description="Source string matching external_source.",
    )
    
class ContentItemListResponse(BaseModel):
    """Paginated list of ContentItemResponse objects."""

    total_count: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    results: list[ContentItemResponse]