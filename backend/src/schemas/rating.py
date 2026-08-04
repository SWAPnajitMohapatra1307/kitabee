"""Pydantic schemas for the ratings API.

Defines request and response shapes for:
    POST   /api/v1/books/{book_id}/ratings
    GET    /api/v1/books/{book_id}/ratings/me
    DELETE /api/v1/books/{book_id}/ratings/me
    GET    /api/v1/users/me/ratings
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    """Payload for creating or updating a rating."""

    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5.")
    review_title: Optional[str] = Field(None, max_length=200)
    review_text: Optional[str] = Field(None, max_length=5000)
    is_spoiler: bool = Field(False)


class RatingResponse(BaseModel):
    """A single rating returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    book_id: UUID
    rating: int
    review_title: Optional[str] = None
    review_text: Optional[str] = None
    is_spoiler: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime


class MyRatingsResponse(BaseModel):
    """Paginated list of the current user's ratings."""

    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)
    results: list[RatingResponse]