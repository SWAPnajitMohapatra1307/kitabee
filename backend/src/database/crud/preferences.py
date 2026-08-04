"""CRUD operations for the user_preferences table."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user_preferences import UserPreferences


async def get_preferences(db: AsyncSession, *, user_id: UUID) -> UserPreferences | None:
    """Return the preferences row for a user, or None if not yet created."""
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_preferences(
    db: AsyncSession,
    *,
    user_id: UUID,
    favorite_genres: list[str],
    preferred_languages: list[str],
    excluded_genres: list[str],
    content_warnings_hide: list[str],
    reading_pace: str | None,
    preferred_book_length: str | None,
    theme: str,
    notification_settings: dict,
    privacy_settings: dict,
) -> UserPreferences:
    """Insert a new preferences row and return it."""
    prefs = UserPreferences(
        user_id=user_id,
        favorite_genres=favorite_genres,
        preferred_languages=preferred_languages,
        excluded_genres=excluded_genres,
        content_warnings_hide=content_warnings_hide,
        reading_pace=reading_pace,
        preferred_book_length=preferred_book_length,
        theme=theme,
        notification_settings=notification_settings,
        privacy_settings=privacy_settings,
    )
    db.add(prefs)
    await db.commit()
    await db.refresh(prefs)
    return prefs


async def update_preferences(
    db: AsyncSession,
    prefs: UserPreferences,
    **fields,
) -> UserPreferences:
    """Apply field updates to an existing preferences row and return it."""
    for key, value in fields.items():
        setattr(prefs, key, value)
    await db.commit()
    await db.refresh(prefs)
    return prefs