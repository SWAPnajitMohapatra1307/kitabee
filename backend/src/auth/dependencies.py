"""FastAPI dependency providers for authentication."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.jwt_handler import verify_token

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Extract and verify Bearer token, return the authenticated user.

    Args:
        credentials: Bearer token from Authorization header.

    Returns:
        Authenticated User ORM instance.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired.
        HTTPException 401: If user not found or inactive.

    Note:
        DB lookup wired in Day 9 when crud/user.py is available.
    """
    token = credentials.credentials
    user_id = verify_token(token, expected_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
        )

    # DB lookup added Day 9
    return user_id


async def get_current_superuser(
    current_user=Depends(get_current_user),
):
    """Verify the authenticated user has superuser privileges.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        The authenticated superuser.

    Raises:
        HTTPException 403: If user is not a superuser.

    Note:
        Superuser check wired in Day 9 when User ORM is available.
    """
    # Full superuser check added Day 9
    return current_user