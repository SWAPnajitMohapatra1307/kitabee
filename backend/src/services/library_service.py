"""Business logic for the library feature."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.book import get_book_by_external_id
from src.database.crud.library import (
    create_library_item,
    delete_library_item,
    get_library_item,
    get_library_items_by_user,
    update_library_item,
)
from src.database.models.library_item import Library, LibraryStatus
from src.schemas.library import LibraryItemAdd, LibraryItemUpdate
from src.services.content_normalizer import parse_content_id, get_source_for_prefix

logger = logging.getLogger(__name__)


class LibraryService:
    """Handles library entry operations for a single request."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialise the service with a database session.

        Args:
            db: Active async database session bound to the current request.
        """
        self.db = db

    async def resolve_content_id(self, content_id: str) -> UUID | None:
        """Resolve a prefixed content_id to an internal book UUID.

        Args:
            content_id: Prefixed ID like "gb:ByLKDQAAQBAJ".

        Returns:
            Internal book UUID, or None when not found in DB.
        """
        parsed = parse_content_id(content_id)
        if parsed is None:
            logger.warning(
                "Invalid content_id in library resolution",
                extra={"content_id": content_id},
            )
            return None

        prefix, raw_id = parsed
        source = get_source_for_prefix(prefix)
        if source is None:
            return None

        book = await get_book_by_external_id(
            self.db,
            external_id=raw_id,
            external_source=source,
        )

        if book is None:
            logger.info(
                "Book not in DB for library — fetch via detail endpoint first",
                extra={"content_id": content_id},
            )
            return None

        return book.id

    async def add_book(
        self,
        *,
        user_id: UUID,
        payload: LibraryItemAdd,
        content_router: object,
    ) -> Library:
        """Add a content item to the user's library.

        Resolves content_id to an internal book UUID. If the book is not
        yet in the DB, fetches it from the external API first.

        Args:
            user_id: UUID of the authenticated user.
            payload: Validated request body with content_id.
            content_router: ContentRouter for fetching unknown items.

        Returns:
            The newly created Library entry.

        Raises:
            HTTPException 400: When content_id format is invalid.
            HTTPException 404: When content cannot be found.
            HTTPException 409: When book is already in library.
        """
        if parse_content_id(payload.content_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CONTENT_ID",
                    "message": f"Invalid content_id format: '{payload.content_id}'.",
                },
            )

        book_uuid = await self.resolve_content_id(payload.content_id)

        if book_uuid is None:
            item = await content_router.get_by_content_id(payload.content_id)
            if item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "CONTENT_NOT_FOUND",
                        "message": f"No content found with id {payload.content_id}.",
                    },
                )
            book_uuid = await self.resolve_content_id(payload.content_id)

        if book_uuid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CONTENT_NOT_FOUND",
                    "message": f"Content {payload.content_id} could not be resolved.",
                },
            )

        existing = await get_library_item(
            self.db, user_id=user_id, book_id=book_uuid
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "ALREADY_IN_LIBRARY",
                    "message": "This item is already in your library.",
                },
            )

        return await create_library_item(
            self.db,
            user_id=user_id,
            book_id=book_uuid,
            status=payload.status,
            current_page=payload.current_page,
            total_pages=payload.total_pages,
            notes=payload.notes,
            is_favorite=payload.is_favorite,
        )

    async def get_my_library(
        self,
        *,
        user_id: UUID,
        status: LibraryStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Library], int]:
        """Return paginated library entries for the user.

        Args:
            user_id: UUID of the authenticated user.
            status: Optional filter by reading status.
            limit: Maximum number of results to return.
            offset: Number of results to skip.

        Returns:
            Tuple of (list of Library entries, total count).
        """
        return await get_library_items_by_user(
            self.db,
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def update_entry(
        self,
        *,
        user_id: UUID,
        book_id: UUID,
        payload: LibraryItemUpdate,
    ) -> Library:
        """Update an existing library entry.

        Args:
            user_id: UUID of the authenticated user.
            book_id: Internal book UUID.
            payload: Validated partial update body.

        Returns:
            The updated Library entry.

        Raises:
            HTTPException 404: When the entry does not exist.
        """
        item = await get_library_item(self.db, user_id=user_id, book_id=book_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "LIBRARY_ITEM_NOT_FOUND",
                    "message": "This item is not in your library.",
                },
            )

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return item

        return await update_library_item(self.db, item, **updates)

    async def remove_book(self, *, user_id: UUID, book_id: UUID) -> bool:
        """Remove a book from the user's library.

        Args:
            user_id: UUID of the authenticated user.
            book_id: Internal book UUID.

        Returns:
            True if deleted, False if entry was not found.
        """
        return await delete_library_item(self.db, user_id=user_id, book_id=book_id)