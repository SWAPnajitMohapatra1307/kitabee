"""Pydantic schemas for user authentication and profile APIs.

Defines request and response shapes for:
    POST /api/v1/auth/register
    POST /api/v1/auth/login
    POST /api/v1/auth/refresh
    GET  /api/v1/users/me
    PATCH /api/v1/users/me
    PATCH /api/v1/users/me/password
    DELETE /api/v1/users/me

`admin_key` is intentionally omitted from the public registration schema
so it never appears in OpenAPI/Swagger. The register route reads it
directly from the raw request body and passes it to the service layer.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Constants

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
MAX_EMAIL_LENGTH = 255
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_PASSWORD_LENGTH = 8
MAX_BIO_LENGTH = 500
MAX_AVATAR_URL_LENGTH = 2048


# Request schemas

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


class UserProfileUpdate(BaseModel):
    """Payload for PATCH /api/v1/users/me.

    All fields are optional. Only provided fields are updated.
    Omitted fields are left unchanged.
    """

    name: Optional[str] = Field(
        None,
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
    )
    bio: Optional[str] = Field(
        None,
        max_length=MAX_BIO_LENGTH,
    )
    avatar_url: Optional[str] = Field(
        None,
        max_length=MAX_AVATAR_URL_LENGTH,
    )
    date_of_birth: Optional[date] = None


class PasswordChangeRequest(BaseModel):
    """Payload for PATCH /api/v1/users/me/password."""

    current_password: str = Field(
        ...,
        min_length=1,
    )
    new_password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
    )


# Response schemas

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
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    onboarding_completed: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT token pair returned after login or refresh."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"