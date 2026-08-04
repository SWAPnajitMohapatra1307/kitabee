"""API routes for the library feature.

Endpoints:
    POST   /api/v1/library              — add a book to the library
    GET    /api/v1/library              — get my library (paginated, filterable)
    PATCH  /api/v1/library/{book_id}    — update status / progress
    DELETE /api/v1/library/{book_id}    — remove a book from the library
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import success_envelope
from src.auth.dependencies import get_current_user
from src.database.models.library_item import LibraryStatus
from src.database.models.user import User
from src.schemas.library import (
    LibraryItemAdd,
    LibraryItemResponse,
    LibraryItemUpdate,
    MyLibraryResponse,
)
from src.services.library_service import LibraryService

router = APIRouter(tags=["library"])


@router.post(
    "/api/v1/library",
    status_code=status.HTTP_201_CREATED,
)
async def add_book_to_library(
    payload: LibraryItemAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a book to the current user's library."""
    service = LibraryService(db)
    item = await service.add_book(user_id=current_user.id, payload=payload)
    return success_envelope(
        LibraryItemResponse.model_validate(item).model_dump(mode="json")
    )


@router.get(
    "/api/v1/library",
    status_code=status.HTTP_200_OK,
)
async def get_my_library(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: LibraryStatus | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get the current user's library, paginated and optionally filtered by status."""
    service = LibraryService(db)
    items, total = await service.get_my_library(
        user_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    response = MyLibraryResponse(
        total=total,
        limit=limit,
        offset=offset,
        results=[LibraryItemResponse.model_validate(i) for i in items],
    )
    return success_envelope(response.model_dump(mode="json"))


@router.patch(
    "/api/v1/library/{book_id}",
    status_code=status.HTTP_200_OK,
)
async def update_library_entry(
    book_id: UUID,
    payload: LibraryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update reading status or progress for a book in the library."""
    service = LibraryService(db)
    item = await service.update_entry(
        user_id=current_user.id,
        book_id=book_id,
        payload=payload,
    )
    return success_envelope(
        LibraryItemResponse.model_validate(item).model_dump(mode="json")
    )


@router.delete(
    "/api/v1/library/{book_id}",
    status_code=status.HTTP_200_OK,
)
async def remove_book_from_library(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a book from the current user's library."""
    service = LibraryService(db)
    deleted = await service.remove_book(
        user_id=current_user.id,
        book_id=book_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "LIBRARY_ITEM_NOT_FOUND",
                "message": "This book is not in your library.",
            },
        )
    return success_envelope({"message": "Book removed from library successfully."})