"""User profile API routes.

Endpoints:
    GET    /api/v1/users/me           — fetch current user profile
    PATCH  /api/v1/users/me           — update profile fields
    DELETE /api/v1/users/me           — soft delete account
    PATCH  /api/v1/users/me/password  — change password
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import error_envelope, success_envelope
from src.auth.dependencies import get_current_user
from src.database.base import User
from src.database.crud.user import soft_delete_user
from src.schemas.user import (
    PasswordChangeRequest,
    UserProfileUpdate,
    UserResponse,
)
from src.services.user_service import UserService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return the authenticated user's profile.

    Args:
        current_user: Injected by get_current_user dependency.

    Returns:
        Standard success envelope containing UserResponse.
    """
    return success_envelope(UserResponse.model_validate(current_user).model_dump())


@router.patch("/me", status_code=status.HTTP_200_OK)
async def update_me(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update the authenticated user's profile fields.

    Only fields included in the request body are updated.
    Omitted fields are left unchanged.

    Args:
        payload: Profile fields to update (all optional).
        current_user: Injected by get_current_user dependency.
        db: Async database session.

    Returns:
        Standard success envelope containing updated UserResponse.
    """
    service = UserService(db)
    updated_user = await service.update_profile(current_user, payload)
    return success_envelope(UserResponse.model_validate(updated_user).model_dump())


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft delete the authenticated user's account.

    Sets is_active=False and deleted_at=now. The user can no longer
    log in or use protected endpoints after this call.

    Args:
        current_user: Injected by get_current_user dependency.
        db: Async database session.

    Returns:
        Standard success envelope with confirmation message.
    """
    await soft_delete_user(db, current_user)

    logger.info(
        "User account soft deleted",
        extra={"user_id": str(current_user.id)},
    )

    return success_envelope({"message": "Account deleted successfully."})


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change the authenticated user's password.

    Verifies the current password before applying the new one.

    Args:
        payload: Current and new password.
        current_user: Injected by get_current_user dependency.
        db: Async database session.

    Returns:
        Standard success envelope with confirmation message.

    Raises:
        HTTPException 400: If current password is wrong.
        HTTPException 400: If new password exceeds bcrypt 72-byte limit.
    """
    service = UserService(db)

    try:
        await service.change_password(
            current_user,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "WRONG_PASSWORD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "WRONG_PASSWORD",
                    "message": "Current password is incorrect.",
                },
            )

        # bcrypt 72-byte limit exceeded
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PASSWORD",
                "message": "Password exceeds maximum allowed length.",
            },
        )

    return success_envelope({"message": "Password changed successfully."})