"""Business logic for the library feature."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.library import (
    create_library_item,
    delete_library_item,
    get_library_item,
    get_library_items_by_user,
    update_library_item,
)
from src.database.models.library_item import Library, LibraryStatus
from src.schemas.library import LibraryItemAdd, LibraryItemUpdate


class LibraryService:
    """Handles library entry operations for a single request."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialise the service with a database session.

        Args:
            db: Active async database session bound to the current request.
        """
        self.db = db

    async def add_book(self, *, user_id: UUID, payload: LibraryItemAdd) -> Library:
        """Add a book to the user's library.

        Raises 409 CONFLICT if the book is already in the library.

        Args:
            user_id: UUID of the authenticated user.
            payload: Validated request body.

        Returns:
            The newly created Library entry.

        Raises:
            HTTPException: 409 if the book already exists in the library.
        """
        existing = await get_library_item(
            self.db, user_id=user_id, book_id=payload.book_id
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "ALREADY_IN_LIBRARY",
                    "message": "This book is already in your library.",
                },
            )

        return await create_library_item(
            self.db,
            user_id=user_id,
            book_id=payload.book_id,
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

        Only fields present in the payload are applied.

        Args:
            user_id: UUID of the authenticated user.
            book_id: UUID of the book to update.
            payload: Validated partial update body.

        Returns:
            The updated Library entry.

        Raises:
            HTTPException: 404 if the entry does not exist.
        """
        item = await get_library_item(self.db, user_id=user_id, book_id=book_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "LIBRARY_ITEM_NOT_FOUND",
                    "message": "This book is not in your library.",
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
            book_id: UUID of the book to remove.

        Returns:
            True if deleted, False if the entry was not found.
        """
        return await delete_library_item(self.db, user_id=user_id, book_id=book_id)