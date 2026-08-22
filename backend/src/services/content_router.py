"""ContentRouter service for resolving external content items and seed fallbacks."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, cast
from urllib.parse import quote, unquote

from fastapi import HTTPException, status

from src.external.google_books import GoogleBooksClient
from src.external.comic_vine import ComicVineClient
from src.external.internet_archive import InternetArchiveClient
from src.services.content_normalizer import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_COMIC_VINE,
    SOURCE_INTERNET_ARCHIVE,
)

logger = logging.getLogger(__name__)

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]


def optimize_cover_url(url: str | None, width: int = 260) -> str | None:
    """Normalize and optimize cover URLs across Google, Comic Vine, IA, and Open Library."""
    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    if not url:
        return None

    # Force HTTPS
    if url.startswith("http://"):
        url = "https://" + url[7:]

    # 1. GOOGLE BOOKS: Bypass wsrv.nl proxy (Google blocks proxy scrapers with 403)
    if "books.google.com" in url or "googleusercontent.com" in url:
        if "edge=curl" in url:
            url = url.replace("edge=curl", "")
        return url

    # Strip pre-existing wsrv.nl proxy wrappers to avoid duplicate proxying
    if "wsrv.nl/?url=" in url:
        parts = url.split("wsrv.nl/?url=")
        url = unquote(parts[-1].split("&")[0])

    # 2. COMIC VINE, INTERNET ARCHIVE, OPEN LIBRARY, & OTHERS:
    # Route through Cloudflare Edge CDN (wsrv.nl) -> converts heavy PNG/JPG into ~15KB WebP
    encoded_target = quote(url, safe="")
    return f"https://wsrv.nl/?url={encoded_target}&w={width}&output=webp"


class ContentRouter:
    """Routes content requests to Google Books, Comic Vine, Internet Archive, or seed fallback."""

    def __init__(
        self,
        gb_client: GoogleBooksClient | None = None,
        cv_client: ComicVineClient | None = None,
        ia_client: InternetArchiveClient | None = None,
        google_books: GoogleBooksClient | None = None,
        comic_vine: ComicVineClient | None = None,
        internet_archive: InternetArchiveClient | None = None,
        google_books_client: GoogleBooksClient | None = None,
        comic_vine_client: ComicVineClient | None = None,
        internet_archive_client: InternetArchiveClient | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ContentRouter accepting all parameter alias variations."""
        self._gb_client = (
            gb_client or google_books or google_books_client or GoogleBooksClient()
        )
        self._cv_client = (
            cv_client or comic_vine or comic_vine_client or ComicVineClient()
        )
        self._ia_client = (
            ia_client or internet_archive or internet_archive_client or InternetArchiveClient()
        )

    def parse_content_id(self, content_id: str) -> tuple[str, str]:
        """Parse 'prefix:id' string into (source_name, raw_id)."""
        if ":" not in content_id:
            return SOURCE_GOOGLE_BOOKS, content_id
        prefix, raw_id = content_id.split(":", 1)
        prefix_map = {
            "gb": SOURCE_GOOGLE_BOOKS,
            "cv": SOURCE_COMIC_VINE,
            "ia": SOURCE_INTERNET_ARCHIVE,
        }
        source = prefix_map.get(prefix.lower(), SOURCE_GOOGLE_BOOKS)
        return source, raw_id

    async def get_by_content_id(self, content_id: str) -> dict[str, Any]:
        """Fetch book details instantly from catalog or fallback to live search."""
        from src.api.routes.collections import _CATALOG_BY_ID

        source, raw_id = self.parse_content_id(content_id)

        # 1. Instant Catalog Lookup
        catalog_item = (
            _CATALOG_BY_ID.get(content_id)
            or _CATALOG_BY_ID.get(raw_id)
            or _CATALOG_BY_ID.get(f"seed-{raw_id}")
        )
        if catalog_item:
            author = catalog_item.get("author")
            authors = catalog_item.get("authors", [])
            if not author and authors:
                author = authors[0] if isinstance(authors, list) else str(authors)

            raw_cover = catalog_item.get("cover_url", "")
            optimized_cover = optimize_cover_url(raw_cover) or ""

            return {
                "content_id": catalog_item.get("content_id", content_id),
                "external_id": raw_id,
                "external_source": catalog_item.get("source", source),
                "title": catalog_item.get("title", "Unknown Title"),
                "author": author or "Unknown Author",
                "authors": authors if isinstance(authors, list) else ([author] if author else []),
                "description": catalog_item.get("description", ""),
                "cover_url": optimized_cover,
                "genres": catalog_item.get("genres", []),
                "source": catalog_item.get("source", source),
                "published_date": catalog_item.get("published_date", ""),
                "content_type": catalog_item.get("content_type", "book"),
                "is_free": catalog_item.get("is_free", False),
                "free_url": catalog_item.get("free_url"),
            }

        # 2. Live External API Fallback
        item: dict[str, Any] | None = None
        try:
            if source == SOURCE_GOOGLE_BOOKS:
                raw_gb = await self._gb_client.get_by_id(raw_id)
                if raw_gb:
                    item = self._normalize_gb_item(raw_gb)
            elif source == SOURCE_COMIC_VINE:
                raw_cv = await self._fetch_cv_by_id(raw_id)
                if raw_cv:
                    item = self._normalize_generic_item(raw_cv, default_source="comic_vine", default_type="comic")
            elif source == SOURCE_INTERNET_ARCHIVE:
                raw_ia = await self._fetch_ia_by_id(raw_id)
                if raw_ia:
                    item = self._normalize_generic_item(raw_ia, default_source="internet_archive", default_type="book", is_free=True)
        except Exception as exc:
            logger.warning(
                "External API fetch failed for content_id",
                extra={"content_id": content_id, "error": str(exc)},
            )
            item = None

        if item:
            return item

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content not found: {content_id}",
        )

    def _normalize_gb_item(self, raw: dict[str, Any]) -> dict[str, Any]:
        raw_id = str(raw.get("google_books_id") or raw.get("external_id") or raw.get("id") or "")
        cid = f"gb:{raw_id}" if not raw_id.startswith("gb:") else raw_id
        clean_raw_id = raw_id.replace("gb:", "")

        authors = raw.get("authors") or []
        author = raw.get("author")
        if not author and authors:
            author = authors[0] if isinstance(authors, list) else str(authors)

        raw_cover = (
            raw.get("cover_url")
            or raw.get("thumbnail_url")
            or raw.get("small_thumbnail_url")
            or ""
        )
        optimized_cover = optimize_cover_url(raw_cover) or ""

        genres = raw.get("categories") or raw.get("genres") or []

        return {
            "content_id": cid,
            "external_id": clean_raw_id,
            "external_source": "google_books",
            "title": raw.get("title") or "Unknown Title",
            "author": author or "Unknown Author",
            "authors": authors if isinstance(authors, list) else ([author] if author else []),
            "description": raw.get("description") or "",
            "cover_url": optimized_cover,
            "content_type": "book",
            "is_free": False,
            "free_url": None,
            "genres": genres if isinstance(genres, list) else [str(genres)],
            "source": "google_books",
            "published_date": str(raw.get("published_date") or ""),
        }

    def _normalize_generic_item(
        self,
        raw: dict[str, Any],
        default_source: str,
        default_type: str = "book",
        is_free: bool = False,
    ) -> dict[str, Any]:
        prefix = "cv" if default_source == "comic_vine" else ("ia" if default_source == "internet_archive" else "gb")
        
        # Raw identifier extraction
        raw_id = str(
            raw.get("external_id")
            or raw.get("id")
            or raw.get("google_books_id")
            or ""
        ).replace("ia_", "").replace("cv:", "").replace("gb:", "")

        cid = str(raw.get("content_id") or (f"{prefix}:{raw_id}" if raw_id else ""))

        authors = raw.get("authors") or []
        author = raw.get("author")
        if not author and authors:
            author = authors[0] if isinstance(authors, list) else str(authors)

        raw_cover = (
            raw.get("cover_url")
            or raw.get("cover_image")
            or raw.get("thumbnail_url")
            or raw.get("cover_url_large")
            or ""
        )
        optimized_cover = optimize_cover_url(raw_cover) or ""

        ctype = raw.get("content_type") or default_type
        if default_source == "comic_vine":
            ctype = "comic"

        free_flag = bool(raw.get("is_free", is_free))
        if default_source == "internet_archive":
            free_flag = True

        free_link = raw.get("free_url") or raw.get("read_url") or raw.get("detail_url")
        if default_source == "internet_archive" and not free_link and raw_id:
            free_link = f"https://archive.org/details/{raw_id}"

        return {
            "content_id": cid,
            "external_id": raw_id,
            "external_source": default_source,
            "title": raw.get("title") or "Unknown Title",
            "author": author or "Unknown Author",
            "authors": authors if isinstance(authors, list) else ([author] if author else []),
            "description": raw.get("description") or "",
            "cover_url": optimized_cover,
            "content_type": ctype,
            "is_free": free_flag,
            "free_url": free_link if free_flag else None,
            "genres": raw.get("genres") or raw.get("subjects") or [],
            "source": default_source,
            "published_date": str(raw.get("published_date") or ""),
        }

    async def _fetch_cv_by_id(self, raw_id: str) -> dict[str, Any] | None:
        for method_name in ("get_comic", "get_by_id", "get_volume", "get_issue"):
            raw_method = getattr(self._cv_client, method_name, None)
            if callable(raw_method):
                try:
                    fn = cast(AsyncCallable, raw_method)
                    res = await fn(raw_id)  # pyright: ignore[reportGeneralTypeIssues]
                    if res and isinstance(res, dict):
                        return res
                except Exception:
                    pass
        return None

    async def _fetch_ia_by_id(self, raw_id: str) -> dict[str, Any] | None:
        for method_name in ("get_item", "get_by_id", "get_book_details", "get_details"):
            raw_method = getattr(self._ia_client, method_name, None)
            if callable(raw_method):
                try:
                    fn = cast(AsyncCallable, raw_method)
                    res = await fn(raw_id)  # pyright: ignore[reportGeneralTypeIssues]
                    if res and isinstance(res, dict):
                        return res
                except Exception:
                    pass
        return None

    async def _search_cv(self, query: str, limit: int) -> list[dict[str, Any]]:
        for method_name in ("search_comics", "search", "search_volumes", "search_issues"):
            raw_method = getattr(self._cv_client, method_name, None)
            if callable(raw_method):
                try:
                    fn = cast(AsyncCallable, raw_method)
                    try:
                        res = await fn(query, limit=limit)  # pyright: ignore[reportGeneralTypeIssues]
                    except TypeError:
                        try:
                            res = await fn(query, max_results=limit)  # pyright: ignore[reportGeneralTypeIssues]
                        except TypeError:
                            res = await fn(query)  # pyright: ignore[reportGeneralTypeIssues]
                    if isinstance(res, list):
                        return res
                except Exception:
                    pass
        return []

    async def _search_ia(self, query: str, limit: int) -> list[dict[str, Any]]:
        for method_name in ("search_free_books", "search_books", "search", "search_items"):
            raw_method = getattr(self._ia_client, method_name, None)
            if callable(raw_method):
                try:
                    fn = cast(AsyncCallable, raw_method)
                    try:
                        res = await fn(query, limit=limit)  # pyright: ignore[reportGeneralTypeIssues]
                    except TypeError:
                        try:
                            res = await fn(query, max_results=limit)  # pyright: ignore[reportGeneralTypeIssues]
                        except TypeError:
                            res = await fn(query)  # pyright: ignore[reportGeneralTypeIssues]
                    if isinstance(res, list):
                        return res
                except Exception:
                    pass
        return []

    async def search(
        self,
        query: str,
        limit: int = 20,
        sources: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        from src.api.routes.collections import _CATALOG_SEED

        results: list[dict[str, Any]] = []
        seen_cids: set[str] = set()

        q_clean = query.strip().lower()

        # 1. Local catalog seed search
        if q_clean:
            for seed in _CATALOG_SEED:
                cid = str(seed.get("content_id") or seed.get("id") or "")
                title = str(seed.get("title") or "").lower()
                author = str(seed.get("author") or "").lower()
                genres = [str(g).lower() for g in seed.get("genres", [])]

                if (
                    q_clean in title
                    or q_clean in author
                    or any(q_clean in g for g in genres)
                ):
                    if cid and cid not in seen_cids:
                        seen_cids.add(cid)
                        results.append(self._normalize_generic_item(
                            seed,
                            default_source=seed.get("source", "google_books"),
                            default_type=seed.get("content_type", "book"),
                            is_free=bool(seed.get("is_free", False)),
                        ))

        # 2. Concurrently fetch external sources (Google Books, Comic Vine, Internet Archive)
        per_source_limit = max(5, limit // 2)

        async def _fetch_gb():
            try:
                gb_res = await self._gb_client.search(query, max_results=per_source_limit)
                return [self._normalize_gb_item(item) for item in (gb_res or [])]
            except Exception as exc:
                logger.warning("Google Books search error", extra={"error": str(exc)})
                return []

        async def _fetch_cv():
            try:
                cv_res = await self._search_cv(query, limit=per_source_limit)
                return [
                    self._normalize_generic_item(item, default_source="comic_vine", default_type="comic")
                    for item in (cv_res or [])
                ]
            except Exception as exc:
                logger.warning("Comic Vine search error", extra={"error": str(exc)})
                return []

        async def _fetch_ia():
            try:
                ia_res = await self._search_ia(query, limit=per_source_limit)
                return [
                    self._normalize_generic_item(item, default_source="internet_archive", default_type="book", is_free=True)
                    for item in (ia_res or [])
                ]
            except Exception as exc:
                logger.warning("Internet Archive search error", extra={"error": str(exc)})
                return []

        # Run external searches in parallel
        gb_items, cv_items, ia_items = await asyncio.gather(
            _fetch_gb(),
            _fetch_cv(),
            _fetch_ia(),
            return_exceptions=True,
        )

        # Merge external items round-robin style (1 book, 1 comic, 1 free book)
        external_lists = [
            list(gb_items) if isinstance(gb_items, list) else [],
            list(cv_items) if isinstance(cv_items, list) else [],
            list(ia_items) if isinstance(ia_items, list) else [],
        ]

        max_len = max((len(l) for l in external_lists), default=0)
        for i in range(max_len):
            for lst in external_lists:
                if i < len(lst):
                    item = lst[i]
                    cid = item.get("content_id")
                    if cid and cid not in seen_cids:
                        seen_cids.add(cid)
                        results.append(item)

        return results[:limit]