"""Pydantic schemas for the library API.

Defines request and response shapes for:
    POST   /api/v1/library
    GET    /api/v1/library
    PATCH  /api/v1/library/{content_id}
    DELETE /api/v1/library/{content_id}
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.database.models.library_item import LibraryStatus


class LibraryItemAdd(BaseModel):
    """Payload for adding a content item to the library.

    content_id uses the prefixed convention: gb:{id}, cv:{id}, ia:{id}.
    The service layer resolves this to an internal book UUID before
    writing to the DB.
    """

    content_id: str = Field(
        ...,
        description="Prefixed content identifier (gb:, cv:, ia:).",
    )
    status: LibraryStatus = Field(LibraryStatus.WANT_TO_READ)
    current_page: Optional[int] = Field(None, ge=0)
    total_pages: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = Field(None, max_length=5000)
    is_favorite: bool = Field(False)


class LibraryItemUpdate(BaseModel):
    """Payload for updating a library entry.

    All fields are optional — only provided fields are applied.
    """

    status: Optional[LibraryStatus] = None
    current_page: Optional[int] = Field(None, ge=0)
    total_pages: Optional[int] = Field(None, ge=1)
    started_reading_at: Optional[datetime] = None
    finished_reading_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=5000)
    is_favorite: Optional[bool] = None


class LibraryItemResponse(BaseModel):
    """A single library entry returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    book_id: UUID
    status: LibraryStatus
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    started_reading_at: Optional[datetime] = None
    finished_reading_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_favorite: bool
    added_at: datetime
    updated_at: datetime


class MyLibraryResponse(BaseModel):
    """Paginated list of the current user's library entries."""

    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)
    results: list[LibraryItemResponse]