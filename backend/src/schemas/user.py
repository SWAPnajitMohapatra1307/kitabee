"""Pydantic schemas for user authentication APIs.

Defines request and response shapes for:
    POST /api/v1/auth/register
    POST /api/v1/auth/login
    POST /api/v1/auth/refresh

`admin_key` is intentionally omitted from the public registration schema
so it never appears in OpenAPI/Swagger. The register route can read it
directly from the raw request body and pass it to the service layer.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
MAX_EMAIL_LENGTH = 255
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_PASSWORD_LENGTH = 8


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Public registration payload.

    Note:
        `admin_key` is intentionally not declared here so it remains
        hidden from generated OpenAPI docs.
    """

    email: str = Field(
        ...,
        max_length=MAX_EMAIL_LENGTH,
        pattern=EMAIL_PATTERN,
    )
    name: str = Field(
        ...,
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
    )
    password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
    )


class UserLogin(BaseModel):
    """Login payload using email and password."""

    email: str = Field(
        ...,
        max_length=MAX_EMAIL_LENGTH,
        pattern=EMAIL_PATTERN,
    )
    password: str = Field(
        ...,
        min_length=1,
    )


class RefreshTokenRequest(BaseModel):
    """Request body for refreshing JWT tokens."""

    refresh_token: str = Field(
        ...,
        min_length=1,
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Safe public view of a user account.

    Intentionally excludes:
    - password_hash
    - is_superuser
    - deleted_at
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    avatar_url: str | None = None
    bio: str | None = None
    date_of_birth: date | None = None
    onboarding_completed: bool
    email_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT token pair returned after login or refresh."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"