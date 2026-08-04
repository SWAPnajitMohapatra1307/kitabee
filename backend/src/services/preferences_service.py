"""Business logic for user preferences."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import preferences as preferences_crud
from src.database.crud.user import update_user
from src.database.models.user import User
from src.database.models.user_preferences import UserPreferences
from src.schemas.preferences import PreferencesUpdate


class PreferencesService:
    """Service layer for reading and updating user preferences."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_my_preferences(self, *, user_id: UUID) -> UserPreferences:
        """Return the current user's preferences or raise 404 if missing."""
        prefs = await preferences_crud.get_preferences(self.db, user_id=user_id)
        if prefs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PREFERENCES_NOT_FOUND",
                    "message": "Preferences not found for this user.",
                },
            )
        return prefs

    async def upsert_my_preferences(
        self,
        *,
        user_id: UUID,
        payload: PreferencesUpdate,
    ) -> UserPreferences:
        """Create or replace the current user's preferences."""
        prefs = await preferences_crud.get_preferences(self.db, user_id=user_id)
        fields = payload.model_dump()

        if prefs is None:
            return await preferences_crud.create_preferences(
                self.db,
                user_id=user_id,
                **fields,
            )

        return await preferences_crud.update_preferences(
            self.db,
            prefs,
            **fields,
        )

    async def complete_onboarding(self, *, user: User) -> User:
        """Mark onboarding as completed for the current user."""
        if user.onboarding_completed:
            return user

        return await update_user(
            self.db,
            user,
            onboarding_completed=True,
        )