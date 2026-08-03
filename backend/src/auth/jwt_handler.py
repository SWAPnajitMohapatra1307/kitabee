"""JWT token creation and verification."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt

from src.config import settings

_ALGORITHM = settings.jwt_algorithm
_SECRET = settings.jwt_secret_key


def create_access_token(user_id: UUID) -> str:
    """Create a signed JWT access token for the given user.

    Args:
        user_id: The UUID of the authenticated user.

    Returns:
        Signed JWT access token string.
    """
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "exp": expires,
        "type": "access",
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a signed JWT refresh token for the given user.

    Args:
        user_id: The UUID of the authenticated user.

    Returns:
        Signed JWT refresh token string.
    """
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "exp": expires,
        "type": "refresh",
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def verify_token(token: str, expected_type: str) -> Optional[str]:
    """Verify a JWT token and return the user_id if valid.

    Args:
        token: The JWT token string to verify.
        expected_type: Either 'access' or 'refresh'.

    Returns:
        user_id string if token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if user_id is None or token_type != expected_type:
            return None

        return user_id
    except JWTError:
        return None