"""SQLAlchemy ORM model for the ``books`` table.

See ``docs/SCHEMA.md`` §4.2 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.library_item import Library
    from src.database.models.rating import Rating


class Book(Base):
    """Cached book metadata sourced from external APIs (Google Books, Open Library, etc.)."""

    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_source: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=text("'google_books'")
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    authors: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genres: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'")
    )
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True, server_default=text("'{}'")
    )
    isbn_10: Mapped[str | None] = mapped_column(String(10), nullable=True)
    isbn_13: Mapped[str | None] = mapped_column(String(13), nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default=text("'en'")
    )
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url_large: Mapped[str | None] = mapped_column(Text, nullable=True)
    average_rating: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), nullable=True, server_default=text("0.00")
    )
    ratings_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    kitabee_rating: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    kitabee_ratings_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        server_default=text("'{}'"),
    )
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
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

    ratings: Mapped[list["Rating"]] = relationship(
        "Rating", back_populates="book", cascade="all, delete-orphan"
    )
    library_items: Mapped[list["Library"]] = relationship(
        "Library", back_populates="book", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "average_rating BETWEEN 0 AND 5",
            name="books_rating_range",
        ),
        CheckConstraint(
            "page_count > 0 OR page_count IS NULL",
            name="books_page_count_positive",
        ),
        CheckConstraint(
            "published_year BETWEEN 1000 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1",
            name="books_year_valid",
        ),
        Index(
            "books_external_unique",
            "external_source",
            "external_id",
            unique=True,
        ),
        Index("idx_books_external", "external_source", "external_id"),
        Index(
            "idx_books_isbn_13",
            "isbn_13",
            postgresql_where=text("isbn_13 IS NOT NULL"),
        ),
        Index(
            "idx_books_title_gin",
            text("to_tsvector('english', title)"),
            postgresql_using="gin",
        ),
        Index(
            "idx_books_authors_gin",
            "authors",
            postgresql_using="gin",
        ),
        Index(
            "idx_books_genres_gin",
            "genres",
            postgresql_using="gin",
        ),
        Index(
            "idx_books_avg_rating",
            text("average_rating DESC"),
        ),
        Index("idx_books_cached_at", "cached_at"),
    )


# Silence unused-import warning; ``ForeignKeyConstraint`` is kept available for
# future FK declarations on this table.
_ = ForeignKeyConstraint
