"""SQLAlchemy ORM model for the ``search_history`` table.

See ``docs/SCHEMA.md`` §4.7 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.book import Book
    from src.database.models.user import User


class SearchHistory(Base):
    """A logged user search query for analytics and personalization."""

    __tablename__ = "search_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_query: Mapped[str] = mapped_column(String(500), nullable=False)
    results_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    clicked_book_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    user: Mapped["User | None"] = relationship("User", back_populates="search_history")
    clicked_book: Mapped["Book | None"] = relationship("Book")

    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(query)) > 0",
            name="search_history_query_not_empty",
        ),
        Index("idx_search_history_user_id", "user_id"),
        Index(
            "idx_search_history_searched_at",
            text("searched_at DESC"),
        ),
        Index("idx_search_history_normalized", "normalized_query"),
    )
