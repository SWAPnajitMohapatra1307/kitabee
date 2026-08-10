"""API routes for the library feature.

Endpoints:
    POST   /api/v1/library                      — add item to library
    GET    /api/v1/library                      — get my library (paginated)
    PATCH  /api/v1/library/{content_id}         — update status / progress
    DELETE /api/v1/library/{content_id}         — remove from library

content_id uses the prefixed convention: gb:{id}, cv:{id}, ia:{id}.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_content_router
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
from src.services.content_router import ContentRouter
from src.services.content_normalizer import parse_content_id
from src.services.library_service import LibraryService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["library"])


async def _resolve_content_id_to_uuid(
    content_id: str,
    service: LibraryService,
    content_router: ContentRouter,
):
    """Resolve a content_id to an internal book UUID for PATCH and DELETE.

    Args:
        content_id: Prefixed content identifier.
        service: LibraryService for DB resolution.
        content_router: For fetching unknown items from external APIs.

    Returns:
        Internal book UUID.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When content is not found.
    """
    if parse_content_id(content_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CONTENT_ID",
                "message": f"Invalid content_id format: '{content_id}'.",
            },
        )

    book_uuid = await service.resolve_content_id(content_id)

    if book_uuid is None:
        item = await content_router.get_by_content_id(content_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CONTENT_NOT_FOUND",
                    "message": f"No content found with id {content_id}.",
                },
            )
        book_uuid = await service.resolve_content_id(content_id)

    if book_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTENT_NOT_FOUND",
                "message": f"Content {content_id} could not be resolved.",
            },
        )

    return book_uuid


@router.post(
    "/api/v1/library",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_library(
    payload: LibraryItemAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    """Add a content item to the current user's library.

    Args:
        payload: Request body with content_id and optional status/progress.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving and fetching unknown content.

    Returns:
        Success envelope wrapping LibraryItemResponse.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When content is not found.
        HTTPException 409: When item is already in library.
    """
    service = LibraryService(db)
    item = await service.add_book(
        user_id=current_user.id,
        payload=payload,
        content_router=content_router,
    )
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
    """Get the current user's library, paginated and optionally filtered.

    Args:
        current_user: Authenticated user.
        db: Database session.
        status_filter: Optional reading status filter.
        limit: Page size (1-100, default 20).
        offset: Results to skip (default 0).

    Returns:
        Success envelope wrapping MyLibraryResponse.
    """
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
    "/api/v1/library/{content_id:path}",
    status_code=status.HTTP_200_OK,
)
async def update_library_entry(
    content_id: str,
    payload: LibraryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    """Update reading status or progress for an item in the library.

    Args:
        content_id: Prefixed content identifier.
        payload: Partial update body.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving content_id to UUID.

    Returns:
        Success envelope wrapping LibraryItemResponse.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When item is not found.
    """
    service = LibraryService(db)
    book_uuid = await _resolve_content_id_to_uuid(content_id, service, content_router)

    item = await service.update_entry(
        user_id=current_user.id,
        book_id=book_uuid,
        payload=payload,
    )
    return success_envelope(
        LibraryItemResponse.model_validate(item).model_dump(mode="json")
    )


@router.delete(
    "/api/v1/library/{content_id:path}",
    status_code=status.HTTP_200_OK,
)
async def remove_from_library(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    """Remove a content item from the current user's library.

    Args:
        content_id: Prefixed content identifier.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving content_id to UUID.

    Returns:
        Success envelope with confirmation message.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When item is not in library.
    """
    service = LibraryService(db)
    book_uuid = await _resolve_content_id_to_uuid(content_id, service, content_router)

    deleted = await service.remove_book(
        user_id=current_user.id,
        book_id=book_uuid,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "LIBRARY_ITEM_NOT_FOUND",
                "message": "This item is not in your library.",
            },
        )
    return success_envelope({"message": "Item removed from library successfully."})