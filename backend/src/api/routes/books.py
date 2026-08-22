"""API routes for books and comics content."""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.deps import get_content_router
from src.api.response import success_envelope
from src.api.routes.collections import optimize_cover_url
from src.services.content_router import ContentRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/books", tags=["books"])


def _clean_title(title: str | None) -> str:
    """Normalize title by removing punctuation, subtitles, edition info, and brackets."""
    if not title:
        return ""
    # Remove contents inside brackets e.g. "Frankenstein (1818 Edition)" -> "Frankenstein"
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", "", title)
    # Remove subtitles after colon or dash e.g. "Frankenstein: Or, The Modern Prometheus"
    t = re.split(r"[:\-\u2013\u2014]", t)[0]
    # Keep only alphanumeric characters and spaces
    t = re.sub(r"[^a-zA-Z0-9\s]", "", t)
    return t.strip().lower()


def _is_same_book(target_title: str, candidate_title: str) -> bool:
    """Return True if candidate title is an edition, duplicate, or variant of target title."""
    c_target = _clean_title(target_title)
    c_cand = _clean_title(candidate_title)

    if not c_target or not c_cand:
        return False

    # Exact match after cleaning
    if c_target == c_cand:
        return True

    # Substring containment (e.g. "frankenstein" in "frankenstein or the modern prometheus")
    if len(c_target) >= 4 and (c_target in c_cand or c_cand in c_target):
        return True

    return False


@router.get("/search", status_code=status.HTTP_200_OK)
async def search_books(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=10, ge=1, le=40),
    content_router: ContentRouter = Depends(get_content_router),
) -> dict[str, Any]:
    """Search for books/comics across Google Books, Comic Vine, and Internet Archive."""
    items: list[dict[str, Any]] = []
    try:
        items = await content_router.search(query=q, limit=limit)
        for item in items:
            if item.get("cover_url"):
                item["cover_url"] = optimize_cover_url(item["cover_url"], width=260)
    except Exception as exc:
        logger.warning("Search failed", extra={"query": q, "error": str(exc)})
        items = []

    return success_envelope({"items": items, "total": len(items)})


@router.get("/{content_id:path}/similar", status_code=status.HTTP_200_OK)
async def get_similar_books(
    content_id: str,
    limit: int = Query(default=10, ge=1, le=20),
    content_router: ContentRouter = Depends(get_content_router),
) -> dict[str, Any]:
    """Get similar books based on shared genres, mood, or author (excluding duplicate editions)."""
    from src.api.routes.collections import _CATALOG_BY_ID, _CATALOG_SEED

    items: list[dict[str, Any]] = []
    seen_cids: set[str] = set()
    seen_titles: set[str] = set()

    # 1. Resolve target item metadata
    target: dict[str, Any] | None = _CATALOG_BY_ID.get(content_id)
    if not target and ":" in content_id:
        raw_id = content_id.split(":", 1)[1]
        target = _CATALOG_BY_ID.get(raw_id)

    if not target:
        try:
            target = await content_router.get_by_content_id(content_id)
        except Exception as exc:
            logger.warning(
                "Failed to resolve target for similar books",
                extra={"content_id": content_id, "error": str(exc)},
            )
            target = None

    target_title = str(target.get("title") or "") if target else ""

    # Safe extraction of author and genres to satisfy Pylance type checker
    target_author = ""
    if target:
        author_val = target.get("author")
        authors_val = target.get("authors")
        if author_val:
            target_author = str(author_val)
        elif isinstance(authors_val, list) and len(authors_val) > 0:
            target_author = str(authors_val[0])

    target_genres: list[str] = []
    if target:
        genres_val = target.get("genres")
        if isinstance(genres_val, list):
            target_genres = [str(g).strip() for g in genres_val if isinstance(g, str)]

    target_cid = str(target.get("content_id") or target.get("id") or content_id) if target else content_id
    seen_cids.add(target_cid)
    seen_cids.add(content_id)

    if target_title:
        seen_titles.add(_clean_title(target_title))

    # Helper to format and optimize response item
    def _format_item(seed: dict[str, Any]) -> dict[str, Any]:
        cid = str(seed.get("content_id") or seed.get("id") or "")
        author = seed.get("author")
        authors = seed.get("authors", [])
        if not author and authors:
            author = authors[0] if isinstance(authors, list) else str(authors)

        raw_cover = seed.get("cover_url", "")
        optimized_cover = optimize_cover_url(raw_cover, width=260) if raw_cover else ""

        return {
            "content_id": cid,
            "title": seed.get("title", "Unknown"),
            "author": author or "Unknown",
            "authors": authors if authors else ([author] if author else []),
            "cover_url": optimized_cover,
            "description": seed.get("description", ""),
            "genres": seed.get("genres", []),
            "is_free": bool(seed.get("is_free", False)),
            "free_url": seed.get("free_url"),
            "source": seed.get("source") or seed.get("external_source") or "google_books",
            "published_date": str(seed.get("published_date") or ""),
        }

    def _should_add(candidate_title: str, candidate_cid: str) -> bool:
        """Check if candidate should be added (not duplicate ID or same book title)."""
        if candidate_cid in seen_cids:
            return False
        if _is_same_book(target_title, candidate_title):
            return False
        clean_cand = _clean_title(candidate_title)
        if clean_cand in seen_titles:
            return False
        return True

    # 2. Match similar books in local seed catalog by genre/author overlap
    target_genres_lower = {g.lower() for g in target_genres}
    if target_genres_lower or target_author:
        for seed in _CATALOG_SEED:
            s_cid = str(seed.get("content_id") or seed.get("id") or "")
            s_title = str(seed.get("title") or "")

            if not _should_add(s_title, s_cid):
                continue

            s_genres = {g.lower().strip() for g in seed.get("genres", []) if isinstance(g, str)}
            s_author = str(seed.get("author") or "")

            # Match if genre overlap OR same author
            if (target_genres_lower and target_genres_lower.intersection(s_genres)) or (target_author and target_author.lower() in s_author.lower()):
                seen_cids.add(s_cid)
                seen_titles.add(_clean_title(s_title))
                items.append(_format_item(seed))
                if len(items) >= limit:
                    break

    # 3. Fallback: Search external router by Genre or Author (NOT exact book title)
    if len(items) < limit:
        # Build search query using genre or author to get TRULY similar books instead of same book editions
        ext_query = ""
        if target_genres:
            ext_query = f"{target_genres[0]} books"
        elif target_author:
            ext_query = f"books by {target_author}"

        if ext_query:
            try:
                ext_items = await content_router.search(query=ext_query, limit=limit * 2)
                for ext in ext_items:
                    cid = str(ext.get("content_id") or ext.get("id") or "")
                    ext_title = str(ext.get("title") or "")

                    if _should_add(ext_title, cid):
                        seen_cids.add(cid)
                        seen_titles.add(_clean_title(ext_title))
                        items.append(_format_item(ext))
                        if len(items) >= limit:
                            break
            except Exception as exc:
                logger.warning("Similar external search failed", extra={"error": str(exc)})

    # 4. Final safety fallback: Fill remaining slots with general catalog seeds
    if len(items) < limit:
        for seed in _CATALOG_SEED:
            s_cid = str(seed.get("content_id") or seed.get("id") or "")
            s_title = str(seed.get("title") or "")

            if _should_add(s_title, s_cid):
                seen_cids.add(s_cid)
                seen_titles.add(_clean_title(s_title))
                items.append(_format_item(seed))
                if len(items) >= limit:
                    break

    final_items = items[:limit]
    return success_envelope({"items": final_items, "total": len(final_items)})


@router.get("/{content_id:path}", status_code=status.HTTP_200_OK)
async def get_book_by_content_id(
    content_id: str,
    content_router: ContentRouter = Depends(get_content_router),
) -> dict[str, Any]:
    """Get book details by content ID (e.g. gb:zbBDDwAAQBAJ or gb:seed-1)."""
    item: dict[str, Any] | None = None
    try:
        item = await content_router.get_by_content_id(content_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(
            "Failed to fetch book by content_id",
            extra={"content_id": content_id, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching content: {content_id}",
        )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book not found: {content_id}",
        )

    # Wrap detail cover in same CDN proxy for instant cache hit
    if item.get("cover_url"):
        item["cover_url"] = optimize_cover_url(item["cover_url"], width=260)

    return success_envelope(item)