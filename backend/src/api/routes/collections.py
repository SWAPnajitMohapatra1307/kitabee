"""API routes for Netflix-style collection rows.

Endpoints:
    GET /api/v1/collections  - home screen themed rows

Collections are now enriched with real data from Google Books,
Comic Vine, and Internet Archive based on the seed catalog source field.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_content_router
from src.api.response import success_envelope
from src.auth.jwt_handler import verify_token
from src.database.crud.preferences import get_preferences
from src.database.crud.rating import get_ratings_by_user
from src.database.crud.user import get_by_id
from src.database.models.user import User
from src.services.collection_service import CollectionService
from src.services.content_router import ContentRouter
from src.services.content_normalizer import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_COMIC_VINE,
    SOURCE_INTERNET_ARCHIVE,
)

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
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Dune Frank Herbert",
        "published_date": "1965",
    },
    {
        "id": "seed-2",
        "title": "Neuromancer",
        "description": "Cyberpunk noir set in a dark dystopian future.",
        "genres": ["sci-fi", "cyberpunk"],
        "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Neuromancer William Gibson",
        "published_date": "1984",
    },
    {
        "id": "seed-3",
        "title": "Foundation",
        "description": "The fall of a galactic empire.",
        "genres": ["sci-fi", "political"],
        "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Foundation Isaac Asimov",
        "published_date": "1951",
    },
    {
        "id": "seed-4",
        "title": "The Left Hand of Darkness",
        "description": "An envoy visits a planet with no fixed gender.",
        "genres": ["sci-fi", "literary"],
        "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Left Hand of Darkness Ursula Le Guin",
        "published_date": "1969",
    },
    {
        "id": "seed-5",
        "title": "Hyperion",
        "description": "Seven pilgrims travel to meet the Shrike.",
        "genres": ["sci-fi", "horror"],
        "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Hyperion Dan Simmons",
        "published_date": "1989",
    },
    {
        "id": "seed-6",
        "title": "Pride and Prejudice",
        "description": "Romance and manners in Regency England.",
        "genres": ["romance", "literary"],
        "mood": "warm",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Pride and Prejudice Jane Austen",
        "published_date": "1813",
        "is_public_domain": True,
    },
    {
        "id": "seed-7",
        "title": "Frankenstein",
        "description": "A scientist creates life and faces consequences.",
        "genres": ["horror", "gothic"],
        "mood": "dark",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Frankenstein Mary Shelley",
        "published_date": "1818",
        "is_public_domain": True,
    },
    {
        "id": "seed-8",
        "title": "Saga",
        "description": "An epic space opera graphic novel.",
        "genres": ["sci-fi", "comics"],
        "mood": "adventurous",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Saga Brian K Vaughan",
        "published_date": "2012",
    },
    {
        "id": "seed-9",
        "title": "The Name of the Wind",
        "description": "A legendary wizard recounts his life story.",
        "genres": ["fantasy", "adventure"],
        "mood": "epic",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Name of the Wind Patrick Rothfuss",
        "published_date": "2007",
    },
    {
        "id": "seed-10",
        "title": "Kafka on the Shore",
        "description": "A surreal journey of two intertwined stories.",
        "genres": ["literary", "magical realism"],
        "mood": "thoughtful",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Kafka on the Shore Haruki Murakami",
        "published_date": "2002",
    },
    {
        "id": "seed-11",
        "title": "The Road",
        "description": "A father and son traverse a post-apocalyptic landscape.",
        "genres": ["literary", "post-apocalyptic"],
        "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "The Road Cormac McCarthy",
        "published_date": "2006",
    },
    {
        "id": "seed-12",
        "title": "Maus",
        "description": "A Holocaust story told through mice and cats.",
        "genres": ["biography", "history", "comics"],
        "mood": "dark",
        "source": SOURCE_COMIC_VINE,
        "search_query": "Maus Art Spiegelman",
        "published_date": "1991",
    },
    {
        "id": "seed-13",
        "title": "Moby Dick",
        "description": "Captain Ahab's obsessive quest for the white whale.",
        "genres": ["literary", "adventure"],
        "mood": "epic",
        "source": SOURCE_INTERNET_ARCHIVE,
        "search_query": "Moby Dick Herman Melville",
        "published_date": "1851",
        "is_public_domain": True,
    },
    {
        "id": "seed-14",
        "title": "The Hitchhiker's Guide to the Galaxy",
        "description": "Comedy and absurdist sci-fi.",
        "genres": ["sci-fi", "comedy"],
        "mood": "funny",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Hitchhiker's Guide to the Galaxy Douglas Adams",
        "published_date": "1979",
    },
    {
        "id": "seed-15",
        "title": "Beloved",
        "description": "A haunting story about slavery and its aftermath.",
        "genres": ["literary", "historical fiction"],
        "mood": "dark",
        "source": SOURCE_GOOGLE_BOOKS,
        "search_query": "Beloved Toni Morrison",
        "published_date": "1987",
    },
]

_CATALOG_BY_ID: dict[str, dict[str, Any]] = {
    item["id"]: item for item in _CATALOG_SEED
}


def _source_prefix(external_source: str) -> str:
    if external_source == SOURCE_COMIC_VINE:
        return "cv"
    if external_source == SOURCE_INTERNET_ARCHIVE:
        return "ia"
    return "gb"


async def _enrich_item_real(
    seed: dict[str, Any],
    content_router: ContentRouter,
) -> dict[str, Any] | None:
    """Fetch real metadata for a seed item from the appropriate external API."""
    source = seed.get("source", SOURCE_GOOGLE_BOOKS)
    query = seed.get("search_query") or seed.get("title", "")

    try:
        if source == SOURCE_GOOGLE_BOOKS:
            results = await content_router.search(
                query=query,
                limit=1,
                sources=[SOURCE_GOOGLE_BOOKS],
            )
        elif source == SOURCE_COMIC_VINE:
            results = await content_router.search(
                query=query,
                limit=1,
                sources=[SOURCE_COMIC_VINE],
            )
        elif source == SOURCE_INTERNET_ARCHIVE:
            results = await content_router.search(
                query=query,
                limit=1,
                sources=[SOURCE_INTERNET_ARCHIVE],
            )
        else:
            results = []

        if results:
            item = results[0]
            return {
                "content_id": item["content_id"],
                "title": item["title"],
                "author": item.get("author") or "Unknown",
                "cover_url": item.get("cover_url"),
                "content_type": item.get("content_type", "book"),
                "is_free": item.get("is_free", False),
                "free_url": item.get("free_url"),
                "source": item.get("source", source),
                "description": item.get("description"),
                "genres": item.get("genres") or seed.get("genres", []),
            }

    except Exception:
        logger.warning(
            "Failed to enrich seed item from API",
            extra={"seed_id": seed.get("id"), "source": source, "query": query},
            exc_info=True,
        )

    return None


async def _enrich_row_real(
    row: dict[str, Any],
    content_router: ContentRouter,
) -> dict[str, Any]:
    """Enrich all items in a collection row with real API data."""
    raw_items = row.get("items", [])
    seeds: list[dict[str, Any]] = []

    for entry in raw_items:
        if isinstance(entry, str):
            seed = _CATALOG_BY_ID.get(entry)
            if seed is not None:
                seeds.append(seed)
        elif isinstance(entry, dict):
            seeds.append(entry)

    tasks = [_enrich_item_real(seed, content_router) for seed in seeds]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched: list[dict[str, Any]] = []
    for result in results:
        if isinstance(result, dict):
            enriched.append(result)
        elif isinstance(result, Exception):
            logger.warning(
                "Item enrichment raised exception",
                extra={"error": str(result)},
            )

    return {
        "id": row.get("id", ""),
        "title": row.get("title", ""),
        "mood": row.get("mood", ""),
        "items": enriched,
        "item_count": len(enriched),
    }


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
    request: Request,
    n_collections: int = Query(default=6, ge=1, le=20),
    row_limit: int = Query(default=20, ge=1, le=50),
    current_user: User | None = Depends(_get_optional_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
) -> dict[str, Any]:
    """Return themed collection rows for the home screen."""
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

        for r in ratings_result:
            if r.book is None:
                continue
            prefix = _source_prefix(r.book.external_source)
            content_id = f"{prefix}:{r.book.external_id}"
            user_ratings.append({
                "user_id": str(current_user.id),
                "content_id": content_id,
                "rating": float(r.rating),
                "title": r.book.title,
            })

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

    enrich_tasks = [_enrich_row_real(row, content_router) for row in rows]
    enriched_rows = await asyncio.gather(*enrich_tasks, return_exceptions=True)

    final_rows: list[dict[str, Any]] = []
    for result in enriched_rows:
        if isinstance(result, dict) and result.get("items"):
            final_rows.append(result)
        elif isinstance(result, Exception):
            logger.warning(
                "Row enrichment raised exception",
                extra={"error": str(result)},
            )

    return success_envelope(
        {
            "rows": final_rows,
            "total": len(final_rows),
            "personalized": user_id is not None and len(user_ratings) > 0,
        }
    )