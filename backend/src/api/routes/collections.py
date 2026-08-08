"""API routes for Netflix-style collection rows.

Endpoints:
    GET /api/v1/collections  — home screen themed rows
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import success_envelope
from src.auth.jwt_handler import verify_token
from src.database.crud.preferences import get_preferences
from src.database.crud.rating import get_ratings_by_user
from src.database.crud.user import get_by_id
from src.database.models.user import User
from src.services.collection_service import CollectionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["collections"])

_bearer = HTTPBearer(auto_error=False)

_CATALOG_SEED: list[dict[str, Any]] = [
    {
        "id": "seed-1",
        "title": "Dune",
        "description": "A science fiction epic set on a desert planet.",
        "genres": ["sci-fi", "adventure"],
        "mood": "epic",
        "source": "gb",
        "published_date": "1965",
    },
    {
        "id": "seed-2",
        "title": "Neuromancer",
        "description": "Cyberpunk noir set in a dark dystopian future.",
        "genres": ["sci-fi", "cyberpunk"],
        "mood": "dark",
        "source": "gb",
        "published_date": "1984",
    },
    {
        "id": "seed-3",
        "title": "Foundation",
        "description": "The fall of a galactic empire and a plan to preserve knowledge.",
        "genres": ["sci-fi", "political"],
        "mood": "epic",
        "source": "gb",
        "published_date": "1951",
    },
    {
        "id": "seed-4",
        "title": "The Left Hand of Darkness",
        "description": "An envoy visits a planet with no fixed gender.",
        "genres": ["sci-fi", "literary"],
        "mood": "thoughtful",
        "source": "gb",
        "published_date": "1969",
    },
    {
        "id": "seed-5",
        "title": "Hyperion",
        "description": "Seven pilgrims travel to meet a creature called the Shrike.",
        "genres": ["sci-fi", "horror"],
        "mood": "dark",
        "source": "gb",
        "published_date": "1989",
    },
    {
        "id": "seed-6",
        "title": "Pride and Prejudice",
        "description": "Romance and manners in Regency England.",
        "genres": ["romance", "literary"],
        "mood": "warm",
        "source": "internet_archive",
        "published_date": "1813",
        "is_public_domain": True,
    },
    {
        "id": "seed-7",
        "title": "Frankenstein",
        "description": "A scientist creates life and faces monstrous consequences.",
        "genres": ["horror", "gothic"],
        "mood": "dark",
        "source": "internet_archive",
        "published_date": "1818",
        "is_public_domain": True,
    },
    {
        "id": "seed-8",
        "title": "Saga Vol. 1",
        "description": "An epic space opera graphic novel.",
        "genres": ["sci-fi", "comics"],
        "mood": "adventurous",
        "source": "cv_saga_1",
        "published_date": "2012",
    },
    {
        "id": "seed-9",
        "title": "The Name of the Wind",
        "description": "A legendary wizard recounts his life story.",
        "genres": ["fantasy", "adventure"],
        "mood": "epic",
        "source": "gb",
        "published_date": "2007",
    },
    {
        "id": "seed-10",
        "title": "Kafka on the Shore",
        "description": "A surreal journey of two intertwined stories.",
        "genres": ["literary", "magical realism"],
        "mood": "thoughtful",
        "source": "gb",
        "published_date": "2002",
    },
    {
        "id": "seed-11",
        "title": "The Road",
        "description": "A father and son traverse a post-apocalyptic landscape.",
        "genres": ["literary", "post-apocalyptic"],
        "mood": "dark",
        "source": "gb",
        "published_date": "2006",
    },
    {
        "id": "seed-12",
        "title": "Maus",
        "description": "A Holocaust survivor's story told through mice and cats.",
        "genres": ["biography", "history", "comics"],
        "mood": "dark",
        "source": "cv_maus_1",
        "published_date": "1991",
    },
    {
        "id": "seed-13",
        "title": "Moby Dick",
        "description": "Captain Ahab's obsessive quest for the white whale.",
        "genres": ["literary", "adventure"],
        "mood": "epic",
        "source": "internet_archive",
        "published_date": "1851",
        "is_public_domain": True,
    },
    {
        "id": "seed-14",
        "title": "The Hitchhiker's Guide to the Galaxy",
        "description": "Comedy and absurdist sci-fi across the universe.",
        "genres": ["sci-fi", "comedy"],
        "mood": "funny",
        "source": "gb",
        "published_date": "1979",
    },
    {
        "id": "seed-15",
        "title": "Beloved",
        "description": "A haunting story about slavery and its aftermath.",
        "genres": ["literary", "historical fiction"],
        "mood": "dark",
        "source": "gb",
        "published_date": "2024",
    },
]


async def _get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Return authenticated user or None for anonymous requests."""
    if credentials is None:
        return None

    user_id_str = verify_token(credentials.credentials, expected_type="access")
    if user_id_str is None:
        return None

    try:
        from uuid import UUID
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    return await get_by_id(db, user_id)


@router.get(
    "/api/v1/collections",
    status_code=status.HTTP_200_OK,
)
async def get_collections(
    n_collections: int = Query(default=6, ge=1, le=20),
    row_limit: int = Query(default=20, ge=1, le=50),
    current_user: User | None = Depends(_get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Return themed collection rows for the home screen.

    Anonymous users receive genre/mood rows and special rows.
    Authenticated users also receive personalized and 'Because you loved X' rows.
    """
    user_id: str | None = None
    user_ratings: list[dict[str, Any]] = []
    content_preference = "both"

    if current_user is not None:
        user_id = str(current_user.id)

        ratings_result, _ = await get_ratings_by_user(
            db,
            user_id=current_user.id,
            limit=100,
            offset=0,
        )
        user_ratings = [
            {
                "user_id": str(current_user.id),
                "content_id": str(r.book_id),
                "rating": float(r.rating),
            }
            for r in ratings_result
        ]

        prefs = await get_preferences(db, user_id=current_user.id)
        if prefs is not None and hasattr(prefs, "content_type_preference"):
            content_preference = getattr(prefs, "content_type_preference", "both")

    service = CollectionService()
    rows = service.build_home_screen(
        catalog=_CATALOG_SEED,
        user_id=user_id,
        user_ratings=user_ratings,
        content_preference=content_preference,
        n_collections=n_collections,
        row_limit=row_limit,
    )

    return success_envelope(
        {
            "collections": rows,
            "total": len(rows),
            "personalized": user_id is not None and len(user_ratings) > 0,
        }
    )