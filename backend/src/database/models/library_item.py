"""SQLAlchemy ORM model for the ``library`` table.

See ``docs/SCHEMA.md`` §4.4 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
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


class LibraryStatus(str, PyEnum):
    """Reading status of a book in a user's library."""

    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    READ = "read"
    DNF = "dnf"


class Library(Base):
    """A user's personal book collection entry with reading status and progress."""

    __tablename__ = "library"

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
    status: Mapped[LibraryStatus] = mapped_column(
        SAEnum(
            LibraryStatus,
            name="library_status_enum",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        server_default=text("'want_to_read'"),
    )
    current_page: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    total_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_reading_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_reading_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    user: Mapped["User"] = relationship("User", back_populates="library_items")
    book: Mapped["Book"] = relationship("Book", back_populates="library_items")

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="library_user_book_unique"),
        CheckConstraint(
            "current_page >= 0 AND (total_pages IS NULL OR current_page <= total_pages)",
            name="library_page_valid",
        ),
        CheckConstraint(
            "finished_reading_at IS NULL OR started_reading_at IS NULL "
            "OR finished_reading_at >= started_reading_at",
            name="library_dates_valid",
        ),
        Index("idx_library_user_id", "user_id"),
        Index("idx_library_book_id", "book_id"),
        Index("idx_library_user_status", "user_id", "status"),
        Index(
            "idx_library_added_at",
            text("added_at DESC"),
        ),
    )
