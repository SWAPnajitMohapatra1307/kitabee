"""SQLAlchemy ORM model for the ``ratings`` table.

See ``docs/SCHEMA.md`` §4.3 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.book import Book
    from src.database.models.user import User


class Rating(Base):
    """A user's star rating (and optional review) of a book."""

    __tablename__ = "ratings"

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
    book_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_spoiler: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    helpful_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
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

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    book: Mapped["Book"] = relationship("Book", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="ratings_user_book_unique"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ratings_value_range"),
        CheckConstraint(
            "LENGTH(review_text) <= 5000",
            name="ratings_review_length",
        ),
        Index("idx_ratings_user_id", "user_id"),
        Index("idx_ratings_book_id", "book_id"),
        Index("idx_ratings_user_book", "user_id", "book_id"),
        Index("idx_ratings_rating", "rating"),
        Index(
            "idx_ratings_created_at",
            text("created_at DESC"),
        ),
    )
