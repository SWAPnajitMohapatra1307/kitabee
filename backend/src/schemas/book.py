"""Pydantic schemas for the book search API.

Defines the request and response shapes for GET /api/v1/books/search.
Fields not yet available at this stage (DB-persisted UUID, kitabee_rating,
metadata) are excluded from the Day 5 response. They will be added in
Day 6 when database persistence lands.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Constants

DEFAULT_LIMIT = 20
MIN_LIMIT = 1
MAX_LIMIT = 40
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 200


# Public API

class BookSearchResult(BaseModel):
    """A single book returned in search results.

    This is the Day 5 shape backed by the Google Books mapper output.
    Day 6 will add id (UUID), external_source, kitabee_rating,
    kitabee_ratings_count, and metadata once DB persistence exists.
    """

    model_config = ConfigDict(from_attributes=True)

    google_books_id: str = Field(
        ...,
        description="Google Books volume ID, used as identifier until DB UUIDs land.",
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
    """Paginated envelope for book search results.

    Wraps a list of BookSearchResult with the query context and
    pagination metadata expected by the frontend.
    """

    query: str
    total_count: int = Field(
        ...,
        ge=0,
        description="Number of results returned in this page.",
    )
    limit: int = Field(..., ge=MIN_LIMIT, le=MAX_LIMIT)
    offset: int = Field(..., ge=0)
    results: list[BookSearchResult]