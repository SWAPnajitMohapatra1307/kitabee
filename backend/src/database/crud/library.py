"""CRUD operations for the library table."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.library_item import Library, LibraryStatus


async def get_library_item(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
) -> Library | None:
    """Fetch a single library entry by user and book, with book relationship loaded.

    Args:
        db: Active async database session.
        user_id: UUID of the owning user.
        book_id: UUID of the book.

    Returns:
        The Library row with book eagerly loaded, or None if not found.
    """
    result = await db.execute(
        select(Library)
        .options(selectinload(Library.book))
        .where(
            Library.user_id == user_id,
            Library.book_id == book_id,
        )
    )
    return result.scalar_one_or_none()


async def get_library_items_by_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    status: LibraryStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Library], int]:
    """Fetch paginated library entries for a user, with optional status filter.

    Eagerly loads the book relationship so callers can access
    book.external_id and book.external_source without additional queries.

    Args:
        db: Active async database session.
        user_id: UUID of the owning user.
        status: Optional status filter.
        limit: Maximum number of rows to return.
        offset: Number of rows to skip.

    Returns:
        Tuple of (list of Library rows, total count).
    """
    base_query = (
        select(Library)
        .options(selectinload(Library.book))
        .where(Library.user_id == user_id)
    )
    count_query = select(func.count()).where(Library.user_id == user_id)

    if status is not None:
        base_query = base_query.where(Library.status == status)
        count_query = count_query.where(Library.status == status)

    count_result = await db.execute(count_query.select_from(Library))
    total = count_result.scalar_one()

    items_result = await db.execute(
        base_query.order_by(Library.added_at.desc()).limit(limit).offset(offset)
    )
    items = list(items_result.scalars().all())

    return items, total


async def create_library_item(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
    status: LibraryStatus = LibraryStatus.WANT_TO_READ,
    current_page: int | None = None,
    total_pages: int | None = None,
    notes: str | None = None,
    is_favorite: bool = False,
) -> Library:
    """Insert a new library entry.

    Args:
        db: Active async database session.
        user_id: UUID of the owning user.
        book_id: UUID of the book to add.
        status: Initial reading status.
        current_page: Current page number.
        total_pages: Total pages in the book.
        notes: Optional personal notes.
        is_favorite: Whether the book is marked as favourite.

    Returns:
        The newly created Library row with book eagerly loaded.
    """
    item = Library(
        user_id=user_id,
        book_id=book_id,
        status=status,
        current_page=current_page,
        total_pages=total_pages,
        notes=notes,
        is_favorite=is_favorite,
    )
    db.add(item)
    await db.flush()

    result = await db.execute(
        select(Library)
        .options(selectinload(Library.book))
        .where(Library.id == item.id)
    )
    return result.scalar_one()


async def update_library_item(
    db: AsyncSession,
    item: Library,
    **fields: object,
) -> Library:
    """Apply partial updates to an existing library entry.

    Only the keyword arguments provided are written to the row.

    Args:
        db: Active async database session.
        item: The Library ORM instance to update.
        **fields: Column-value pairs to update.

    Returns:
        The updated Library row with book eagerly loaded.
    """
    from datetime import datetime, timezone

    for key, value in fields.items():
        setattr(item, key, value)

    item.updated_at = datetime.now(timezone.utc)
    await db.flush()

    result = await db.execute(
        select(Library)
        .options(selectinload(Library.book))
        .where(Library.id == item.id)
    )
    return result.scalar_one()


async def delete_library_item(
    db: AsyncSession,
    *,
    user_id: UUID,
    book_id: UUID,
) -> bool:
    """Delete a library entry by user and book.

    Args:
        db: Active async database session.
        user_id: UUID of the owning user.
        book_id: UUID of the book.

    Returns:
        True if a row was deleted, False if not found.
    """
    item = await get_library_item(db, user_id=user_id, book_id=book_id)
    if item is None:
        return False

    await db.delete(item)
    await db.flush()
    return True