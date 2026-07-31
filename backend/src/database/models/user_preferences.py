"""SQLAlchemy ORM model for the ``user_preferences`` table.

See ``docs/SCHEMA.md`` §4.6 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.user import User


class UserPreferences(Base):
    """Extended per-user settings (favorite genres, theme, notifications, privacy)."""

    __tablename__ = "user_preferences"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    favorite_genres: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'")
    )
    preferred_languages: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{en}'")
    )
    excluded_genres: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True, server_default=text("'{}'")
    )
    content_warnings_hide: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True, server_default=text("'{}'")
    )
    reading_pace: Mapped[str | None] = mapped_column(
        String(20), nullable=True, server_default=text("'medium'")
    )
    preferred_book_length: Mapped[str | None] = mapped_column(
        String(20), nullable=True, server_default=text("'any'")
    )
    theme: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'system'")
    )
    notification_settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{\"email\": false, \"push\": false}'"),
    )
    privacy_settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{\"public_library\": false, \"public_ratings\": false}'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    user: Mapped["User"] = relationship("User", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint("user_id", name="user_preferences_user_unique"),
        CheckConstraint(
            "theme IN ('light', 'dark', 'system')",
            name="user_preferences_theme_valid",
        ),
        CheckConstraint(
            "reading_pace IN ('slow', 'medium', 'fast')",
            name="user_preferences_pace_valid",
        ),
        Index("idx_user_preferences_user_id", "user_id"),
        Index(
            "idx_user_preferences_genres_gin",
            "favorite_genres",
            postgresql_using="gin",
        ),
    )
