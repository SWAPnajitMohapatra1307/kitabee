"""FastAPI dependency providers for authentication."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.auth.jwt_handler import verify_token
from src.database.crud.user import get_by_id
from src.database.base import User


_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and verify Bearer token, return the authenticated user.

    Args:
        credentials: Bearer token from Authorization header.
        db: Async database session.

    Returns:
        Authenticated User ORM instance.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired.
        HTTPException 401: If user not found, inactive, or deleted.
    """
    token = credentials.credentials
    user_id_str = verify_token(token, expected_type="access")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
        )

    user = await get_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": "Account is inactive.",
            },
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify the authenticated user has superuser privileges.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        The authenticated superuser.

    Raises:
        HTTPException 403: If user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Superuser access required.",
            },
        )

    return current_user