"""Pydantic schemas for the library API.

Defines request and response shapes for:
    POST   /api/v1/library
    GET    /api/v1/library
    PATCH  /api/v1/library/{content_id}
    DELETE /api/v1/library/{content_id}
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.database.models.library_item import LibraryStatus
from src.services.content_normalizer import SOURCE_TO_PREFIX


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
    content_id: str
    status: LibraryStatus
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    started_reading_at: Optional[datetime] = None
    finished_reading_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_favorite: bool
    title: Optional[str] = None
    cover_url: Optional[str] = None
    authors: Optional[list[str]] = None
    added_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def inject_content_id(cls, data: Any) -> Any:
        """Compute content_id from the joined book's external_source and external_id.

        When data is an ORM Library instance, reads data.book.external_source
        and data.book.external_id to construct the prefixed content_id.

        Args:
            data: Raw input — either an ORM instance or a dict.

        Returns:
            The input unchanged if content_id is already present,
            otherwise with content_id injected.
        """
        if isinstance(data, dict):
            if "content_id" not in data:
                source = data.get("external_source") or ""
                prefix = SOURCE_TO_PREFIX.get(source, "")
                raw_id = data.get("external_id") or ""
                data["content_id"] = f"{prefix}:{raw_id}" if prefix and raw_id else ""
            return data

        # ORM instance path
        book = getattr(data, "book", None)
        if book is not None:
            source = getattr(book, "external_source", "") or ""
            prefix = SOURCE_TO_PREFIX.get(source, "")
            raw_id = getattr(book, "external_id", "") or ""
            content_id = f"{prefix}:{raw_id}" if prefix and raw_id else ""
            book_title = getattr(book, "title", None)
            book_cover = getattr(book, "cover_url", None)
            book_authors = getattr(book, "authors", None)
        else:
            content_id = ""
            book_title = None
            book_cover = None
            book_authors = None

        # Pydantic model_validator mode="before" on ORM objects:
        # must return a dict that Pydantic can use to build the model.
        return {
            "id": data.id,
            "user_id": data.user_id,
            "book_id": data.book_id,
            "content_id": content_id,
            "status": data.status,
            "current_page": data.current_page,
            "total_pages": data.total_pages,
            "started_reading_at": data.started_reading_at,
            "finished_reading_at": data.finished_reading_at,
            "notes": data.notes,
            "is_favorite": data.is_favorite,
            "added_at": data.added_at,
            "updated_at": data.updated_at,
            "cover_url": book_cover,
            "authors": book_authors,
            "title": book_title,
        }


class MyLibraryResponse(BaseModel):
    """Paginated list of the current user's library entries."""

    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    offset: int = Field(..., ge=0)
    results: list[LibraryItemResponse]