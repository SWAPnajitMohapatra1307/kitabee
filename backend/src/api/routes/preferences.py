"""API routes for user preferences.

Endpoints:
    GET  /api/v1/users/me/preferences          — get my preferences
    PUT  /api/v1/users/me/preferences          — upsert my preferences
    POST /api/v1/users/me/preferences/complete — mark onboarding complete
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import success_envelope
from src.auth.dependencies import get_current_user
from src.database.models.user import User
from src.schemas.preferences import PreferencesResponse, PreferencesUpdate
from src.services.preferences_service import PreferencesService

router = APIRouter(tags=["preferences"])


@router.get(
    "/api/v1/users/me/preferences",
    status_code=status.HTTP_200_OK,
)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the current user's preferences or 404 if not yet created."""
    service = PreferencesService(db)
    prefs = await service.get_my_preferences(user_id=current_user.id)
    return success_envelope(
        PreferencesResponse.model_validate(prefs).model_dump(mode="json")
    )


@router.put(
    "/api/v1/users/me/preferences",
    status_code=status.HTTP_200_OK,
)
async def upsert_my_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or fully replace the current user's preferences."""
    service = PreferencesService(db)
    prefs = await service.upsert_my_preferences(
        user_id=current_user.id,
        payload=payload,
    )
    return success_envelope(
        PreferencesResponse.model_validate(prefs).model_dump(mode="json")
    )


@router.post(
    "/api/v1/users/me/preferences/complete",
    status_code=status.HTTP_200_OK,
)
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark the current user's onboarding as completed."""
    service = PreferencesService(db)
    await service.complete_onboarding(user=current_user)
    return success_envelope({"message": "Onboarding marked as complete."})