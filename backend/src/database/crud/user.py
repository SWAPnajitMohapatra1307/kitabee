"""CRUD helpers for the ``users`` table.

This module is the database repository layer for users.
It handles:
- lookup by internal UUID
- lookup by email
- create
- update
- soft delete
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import User


_MUTABLE_FIELDS = (
    "email",
    "password_hash",
    "name",
    "avatar_url",
    "bio",
    "date_of_birth",
    "onboarding_completed",
    "is_active",
    "is_superuser",
    "email_verified",
    "last_login_at",
    "deleted_at",
)


def _apply_updates(user: User, values: dict[str, Any]) -> None:
    """Apply allowed mutable fields onto an existing User ORM object."""
    for field in _MUTABLE_FIELDS:
        if field in values:
            setattr(user, field, values[field])


async def get_by_id(
    db: AsyncSession,
    user_id: UUID,
    include_deleted: bool = False,
) -> Optional[User]:
    """Fetch a user by internal UUID."""
    stmt = select(User).where(User.id == user_id)

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_email(
    db: AsyncSession,
    email: str,
    include_deleted: bool = False,
) -> Optional[User]:
    """Fetch a user by email address."""
    stmt = select(User).where(User.email == email)

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    password_hash: str,
    name: str,
    is_superuser: bool = False,
) -> User:
    """Create and persist a new user row."""
    user = User(
        email=email,
        password_hash=password_hash,
        name=name,
        is_superuser=is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user: User,
    **fields: Any,
) -> User:
    """Update mutable user fields and persist changes."""
    _apply_updates(user, fields)
    user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)
    return user


async def soft_delete_user(
    db: AsyncSession,
    user: User,
) -> User:
    """Soft-delete a user by setting deleted_at and disabling the account."""
    now = datetime.now(timezone.utc)
    return await update_user(
        db,
        user,
        is_active=False,
        deleted_at=now,
    )