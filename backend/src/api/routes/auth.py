"""Authentication endpoints — register, login, refresh."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import success_envelope
from src.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from src.services.user_service import UserService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _raise_409_email_taken() -> None:
    """Raise a 409 conflict when email is already registered."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "EMAIL_TAKEN",
            "message": "An account with this email already exists.",
        },
    )


def _raise_400_password_too_long() -> None:
    """Raise a 400 when password exceeds bcrypt's 72-byte limit."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "INVALID_PASSWORD",
            "message": "Password must not exceed 72 bytes.",
        },
    )


def _raise_401_invalid_credentials() -> None:
    """Raise a generic 401 for failed login attempts."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password.",
        },
    )


def _raise_401_invalid_refresh_token() -> None:
    """Raise a generic 401 for invalid or expired refresh tokens."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "INVALID_TOKEN",
            "message": "Invalid or expired refresh token.",
        },
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Register a new user account.

    Public schema intentionally excludes `admin_key` so it never appears
    in OpenAPI/Swagger. If present in the raw JSON body, it is read here
    silently and passed to the service layer.
    """
    body = await request.json()
    admin_key = body.get("admin_key")

    service = UserService(db)

    try:
        user = await service.create_user(payload, admin_key=admin_key)
    except ValueError as exc:
        if str(exc) == "EMAIL_TAKEN":
            _raise_409_email_taken()
        _raise_400_password_too_long()

    response_payload = UserResponse.model_validate(user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_envelope(response_payload.model_dump(mode="json")),
    )


@router.post("/login")
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Authenticate a user and return a JWT token pair."""
    service = UserService(db)
    user = await service.authenticate_user(
        email=payload.email,
        password=payload.password,
    )

    if user is None:
        _raise_401_invalid_credentials()

    response_payload = TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
    return JSONResponse(
        content=success_envelope(response_payload.model_dump(mode="json")),
    )


@router.post("/refresh")
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Verify a refresh token and issue a fresh token pair."""
    user_id = verify_token(payload.refresh_token, expected_type="refresh")

    if user_id is None:
        _raise_401_invalid_refresh_token()

    try:
        parsed_user_id = UUID(user_id)
    except ValueError:
        _raise_401_invalid_refresh_token()

    service = UserService(db)
    user = await service.get_by_id(parsed_user_id)

    if user is None or not user.is_active:
        _raise_401_invalid_refresh_token()

    response_payload = TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
    return JSONResponse(
        content=success_envelope(response_payload.model_dump(mode="json")),
    )