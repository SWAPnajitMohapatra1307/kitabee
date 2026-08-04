"""Pydantic schemas for the user preferences API.

Defines request and response shapes for:
    GET  /api/v1/users/me/preferences
    PUT  /api/v1/users/me/preferences
    POST /api/v1/users/me/preferences/complete
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationSettings(BaseModel):
    """Notification preference flags."""

    email: bool = False
    push: bool = False


class PrivacySettings(BaseModel):
    """Privacy preference flags."""

    public_library: bool = False
    public_ratings: bool = False


class PreferencesUpdate(BaseModel):
    """Payload for PUT /api/v1/users/me/preferences.

    PUT uses full-replace semantics. Omitted fields fall back to defaults.
    """

    favorite_genres: list[str] = Field(default_factory=list, max_length=50)
    preferred_languages: list[str] = Field(
        default_factory=lambda: ["en"],
        max_length=20,
    )
    excluded_genres: list[str] = Field(default_factory=list, max_length=50)
    content_warnings_hide: list[str] = Field(default_factory=list, max_length=50)
    reading_pace: str | None = Field("medium", pattern="^(slow|medium|fast)$")
    preferred_book_length: str | None = Field(
        "any",
        pattern="^(short|medium|long|any)$",
    )
    theme: str = Field("system", pattern="^(light|dark|system)$")
    notification_settings: NotificationSettings = Field(
        default_factory=NotificationSettings
    )
    privacy_settings: PrivacySettings = Field(default_factory=PrivacySettings)


class PreferencesResponse(BaseModel):
    """User preferences returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    favorite_genres: list[str]
    preferred_languages: list[str]
    excluded_genres: list[str]
    content_warnings_hide: list[str]
    reading_pace: str | None
    preferred_book_length: str | None
    theme: str
    notification_settings: dict[str, Any]
    privacy_settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime