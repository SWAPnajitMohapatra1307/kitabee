"""SQLAlchemy ORM model for the ``recommendations`` table.

See ``docs/SCHEMA.md`` §4.5 for the canonical column definitions.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.book import Book
    from src.database.models.user import User


class RecommendationModelType(str, PyEnum):
    """The ML model that produced a given recommendation."""

    CONTENT_BASED = "content_based"
    COLLABORATIVE_KNN = "collaborative_knn"
    NEURAL_CF = "neural_cf"
    HYBRID = "hybrid"
    TRENDING = "trending"
    POPULAR = "popular"


class Recommendation(Base):
    """A cached ML-generated book recommendation for a user."""

    __tablename__ = "recommendations"

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
    score: Mapped[Decimal] = mapped_column(Numeric(6, 5), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    model_type: Mapped[RecommendationModelType] = mapped_column(
        SAEnum(
            RecommendationModelType,
            name="recommendation_model_enum",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        server_default=text("'{}'"),
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("(CURRENT_TIMESTAMP + INTERVAL '1 hour')"),
    )

    user: Mapped["User"] = relationship("User")
    book: Mapped["Book"] = relationship("Book")

    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 1", name="recommendations_score_range"),
        CheckConstraint("rank > 0", name="recommendations_rank_positive"),
        Index("idx_recommendations_user_rank", "user_id", "rank"),
        Index(
            "idx_recommendations_user_score",
            "user_id",
            text("score DESC"),
        ),
        Index("idx_recommendations_expires", "expires_at"),
        Index("idx_recommendations_model", "model_type"),
    )
