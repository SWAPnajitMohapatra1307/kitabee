"""Dynamic discovery service for hybrid home feed recommendations.

Queries Google Books and ComicVine APIs based on user taste signals
(anchor books, mood clusters) to expand rows beyond the fixed seed
catalog. All external responses are cached in Redis (24h TTL) and
bounded by strict timeouts so cold starts never block the home screen.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Constants

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
COMICVINE_API_KEY = os.getenv("COMICVINE_API_KEY", "")
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
COMICVINE_SEARCH_URL = "https://comicvine.gamespot.com/api/search/"
CACHE_TTL_SECONDS = 86400
MAX_GOOGLE_RESULTS = 40
MAX_COMICVINE_RESULTS = 20
EXTERNAL_API_TIMEOUT_SECONDS = 2.5

# Query Templates

MOOD_QUERY_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "Mind-Bending Sci-Fi": {
        "books": [
            "subject:science fiction cerebral",
            "subject:hard science fiction",
            "mind bending science fiction twist",
        ],
        "comics": ["science fiction mind bending", "cerebral sci-fi graphic novel"],
    },
    "Dark & Gritty": {
        "books": [
            "subject:noir fiction",
            "dark psychological thriller",
            "gritty crime fiction",
        ],
        "comics": ["dark noir comic", "gritty crime graphic novel"],
    },
    "Epic Fantasy": {
        "books": [
            "subject:epic fantasy",
            "high fantasy adventure",
            "subject:fantasy fiction world building",
        ],
        "comics": ["epic fantasy comic series", "high fantasy graphic novel"],
    },
    "Cozy & Heartwarming": {
        "books": [
            "cozy mystery fiction",
            "heartwarming contemporary fiction",
            "feel good romance novel",
        ],
        "comics": ["slice of life graphic novel", "cozy comic series"],
    },
    "Horror & Dread": {
        "books": [
            "subject:horror fiction",
            "psychological horror novel",
            "supernatural horror",
        ],
        "comics": ["horror comic series", "supernatural horror graphic novel"],
    },
    "Cyberpunk & Dystopia": {
        "books": [
            "subject:cyberpunk fiction",
            "dystopian science fiction",
            "cyberpunk noir",
        ],
        "comics": ["cyberpunk comic", "dystopian graphic novel"],
    },
    "Space Opera": {
        "books": [
            "subject:space opera",
            "interstellar science fiction adventure",
            "galactic empire fiction",
        ],
        "comics": ["space opera comic", "interstellar graphic novel"],
    },
    "Mystery & Suspense": {
        "books": [
            "subject:mystery fiction",
            "suspense thriller novel",
            "detective crime fiction",
        ],
        "comics": ["mystery detective comic", "suspense graphic novel"],
    },
    "Superhero & Action": {
        "books": ["superhero fiction novel", "action adventure fiction"],
        "comics": ["superhero comic series", "action adventure graphic novel"],
    },
    "Literary & Thought-Provoking": {
        "books": [
            "subject:literary fiction",
            "thought provoking contemporary fiction",
            "award winning literary novel",
        ],
        "comics": ["literary graphic novel", "award winning comic"],
    },
    "dark": {
        "books": [
            "dark psychological fiction",
            "subject:dystopia",
            "gritty literary thriller",
        ],
        "comics": ["dark comic series", "gritty graphic novel"],
    },
    "epic": {
        "books": [
            "subject:epic fantasy",
            "epic science fiction",
            "sweeping historical epic",
        ],
        "comics": ["epic comic series", "space opera graphic novel"],
    },
    "adventurous": {
        "books": [
            "adventure fiction",
            "subject:action adventure",
            "quest fantasy novel",
        ],
        "comics": ["adventure comic series", "action graphic novel"],
    },
    "mysterious": {
        "books": [
            "subject:mystery",
            "psychological mystery thriller",
            "detective fiction",
        ],
        "comics": ["mystery comic", "detective graphic novel"],
    },
    "thoughtful": {
        "books": [
            "subject:literary fiction",
            "philosophical fiction",
            "thought provoking novel",
        ],
        "comics": ["literary graphic novel", "philosophical comic"],
    },
    "funny": {
        "books": [
            "subject:humor",
            "comic fantasy novel",
            "satirical fiction",
        ],
        "comics": ["comedy comic series", "humorous graphic novel"],
    },
    "romantic": {
        "books": [
            "subject:romance",
            "romantic literary fiction",
            "contemporary romance novel",
        ],
        "comics": ["romance comic", "romantic graphic novel"],
    },
    "inspiring": {
        "books": [
            "inspiring memoir",
            "uplifting fiction",
            "subject:self-help",
        ],
        "comics": ["inspiring graphic novel", "memoir comic"],
    },
    "educational": {
        "books": [
            "subject:history",
            "popular science nonfiction",
            "subject:psychology",
        ],
        "comics": ["educational comic", "nonfiction graphic novel"],
    },
    "fantastical": {
        "books": [
            "subject:fantasy",
            "magical realism fiction",
            "mythic fantasy novel",
        ],
        "comics": ["fantasy comic series", "mythology graphic novel"],
    },
}

FALLBACK_QUERIES: dict[str, list[str]] = {
    "books": ["subject:fiction bestseller", "subject:popular fiction"],
    "comics": ["popular comic series", "bestselling graphic novel"],
}


# Public API


class DynamicDiscoveryService:
    """Fetches live recommendations from external book and comic APIs."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.http = httpx.AsyncClient(
            timeout=httpx.Timeout(EXTERNAL_API_TIMEOUT_SECONDS, connect=2.0),
            headers={"Accept": "application/json"},
        )

    async def expand_from_anchor(
        self,
        anchor: dict,
        count: int = 10,
        exclude_ids: Optional[set[str]] = None,
    ) -> list[dict]:
        """Discover content related to a user's highly-rated book or comic.

        Builds queries from the anchor's author and genres, then merges
        results from Google Books and ComicVine with deduplication.

        Args:
            anchor: Book dict with title, author, genres, content_type.
            count: Maximum results to return.
            exclude_ids: Content IDs already present in the row.

        Returns:
            List of normalized book/comic dicts matching the anchor.
        """
        exclude_ids = exclude_ids or set()
        queries = self._build_anchor_queries(anchor)

        if not queries:
            return []

        all_results = await self._execute_queries(queries, count)
        return self._deduplicate(all_results, exclude_ids, count)

    async def expand_mood_cluster(
        self,
        mood_label: str,
        content_type: str = "both",
        count: int = 10,
        exclude_ids: Optional[set[str]] = None,
    ) -> list[dict]:
        """Fetch fresh content matching a mood or genre cluster.

        Picks 1-2 random query templates per content type so results
        rotate across 24h cache refresh cycles.

        Args:
            mood_label: Cluster name (e.g. "Dark & Gritty" or "dark").
            content_type: "books", "comics", "book", "comic", or "both".
            count: Maximum results to return.
            exclude_ids: Content IDs already present in the row.

        Returns:
            List of normalized book/comic dicts matching the mood.
        """
        exclude_ids = exclude_ids or set()
        queries = self._build_mood_queries(mood_label, content_type)

        if not queries:
            return []

        all_results = await self._execute_queries(queries, count)
        return self._deduplicate(all_results, exclude_ids, count)

    async def close(self) -> None:
        """Close the HTTP client. Call on app shutdown."""
        await self.http.aclose()

    # Query Builders

    def _build_anchor_queries(self, anchor: dict) -> list[tuple[str, str]]:
        """Build search queries from an anchor book's metadata.

        Author queries are strongest signal, genre queries broaden the
        net, title is a last-resort fallback.
        """
        content_type = (anchor.get("content_type") or "book").lower()
        author = (anchor.get("author") or "").strip()
        genres = anchor.get("genres") or []
        title = (anchor.get("title") or "").strip()
        queries: list[tuple[str, str]] = []

        wants_books = content_type in ("book", "books", "both")
        wants_comics = content_type in ("comic", "comics", "both")

        if author and author.lower() != "unknown":
            if wants_books:
                queries.append((f'inauthor:"{author}"', "books"))
            if wants_comics:
                queries.append((author, "comics"))

        if genres:
            primary_genre = str(genres[0]).strip()
            if primary_genre:
                if wants_books:
                    queries.append((f'subject:"{primary_genre}"', "books"))
                if wants_comics:
                    queries.append((f"{primary_genre} comic", "comics"))

        if not queries and title:
            if wants_books:
                queries.append((title, "books"))
            if wants_comics:
                queries.append((title, "comics"))

        return queries

    def _build_mood_queries(
        self, mood_label: str, content_type: str
    ) -> list[tuple[str, str]]:
        """Select random query templates for a mood cluster.

        Random selection ensures variety across cache refresh cycles
        since each unique query string gets its own 24h cache entry.
        """
        mood_key = (mood_label or "").strip()
        templates = (
            MOOD_QUERY_TEMPLATES.get(mood_key)
            or MOOD_QUERY_TEMPLATES.get(mood_key.lower())
            or FALLBACK_QUERIES
        )

        content_type = (content_type or "both").lower()
        wants_books = content_type in ("book", "books", "both")
        wants_comics = content_type in ("comic", "comics", "both")

        queries: list[tuple[str, str]] = []

        if wants_books and "books" in templates:
            book_options = templates["books"]
            picks = random.sample(book_options, min(2, len(book_options)))
            queries.extend((q, "books") for q in picks)

        if wants_comics and "comics" in templates:
            comic_options = templates["comics"]
            picks = random.sample(comic_options, min(1, len(comic_options)))
            queries.extend((q, "comics") for q in picks)

        return queries

    # Query Execution

    async def _execute_queries(
        self, queries: list[tuple[str, str]], max_per_query: int
    ) -> list[dict]:
        """Run all queries against the appropriate external API."""
        all_results: list[dict] = []

        # Bound fan-out so cold starts stay fast
        limited_queries = queries[:3]

        for query_str, source_type in limited_queries:
            try:
                if source_type == "books":
                    results = await self._query_google_books(
                        query_str, max_per_query
                    )
                else:
                    results = await self._query_comicvine(
                        query_str, max_per_query
                    )
                all_results.extend(results)
            except (httpx.HTTPError, httpx.TimeoutException, asyncio.TimeoutError) as exc:
                logger.warning(
                    "External API query failed",
                    extra={"query": query_str, "error": str(exc)},
                )
            except (ValueError, KeyError, TypeError) as exc:
                logger.warning(
                    "API response parsing failed",
                    extra={"query": query_str, "error": str(exc)},
                )

        return all_results

    def _deduplicate(
        self, items: list[dict], exclude_ids: set[str], limit: int
    ) -> list[dict]:
        """Remove duplicates and already-seen content IDs."""
        seen = {str(x) for x in exclude_ids}
        unique: list[dict] = []

        for item in items:
            cid = str(item.get("content_id") or item.get("id") or "")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            unique.append(item)

        return unique[:limit]

    # External API Clients

    async def _query_google_books(
        self, query: str, max_results: int = 10
    ) -> list[dict]:
        """Query Google Books API with Redis caching and strict timeout."""
        cache_key = self._make_cache_key("gb", query, max_results)
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        if not GOOGLE_BOOKS_API_KEY:
            return []

        params = {
            "q": query,
            "maxResults": min(max_results, MAX_GOOGLE_RESULTS),
            "key": GOOGLE_BOOKS_API_KEY,
            "printType": "books",
            "orderBy": "relevance",
        }

        try:
            resp = await asyncio.wait_for(
                self.http.get(GOOGLE_BOOKS_URL, params=params),
                timeout=EXTERNAL_API_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()

            normalized = [
                book
                for item in data.get("items", [])
                if (book := self._normalize_google_book(item)) is not None
            ]

            await self._set_cache(cache_key, normalized)
            return normalized

        except (
            asyncio.TimeoutError,
            httpx.HTTPError,
            httpx.TimeoutException,
            ValueError,
            KeyError,
            TypeError,
        ) as exc:
            logger.warning(
                "Google Books query timed out or failed",
                extra={"query": query, "error": str(exc)},
            )
            return []

    async def _query_comicvine(
        self, query: str, max_results: int = 10
    ) -> list[dict]:
        """Query ComicVine API with Redis caching and strict timeout."""
        cache_key = self._make_cache_key("cv", query, max_results)
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        if not COMICVINE_API_KEY:
            return []

        params = {
            "query": query,
            "resources": "volume",
            "field_list": "id,name,deck,image,publisher,count_of_issues",
            "api_key": COMICVINE_API_KEY,
            "format": "json",
            "limit": min(max_results, MAX_COMICVINE_RESULTS),
        }

        try:
            resp = await asyncio.wait_for(
                self.http.get(
                    COMICVINE_SEARCH_URL,
                    params=params,
                    headers={"User-Agent": "Kitabee/1.0"},
                ),
                timeout=EXTERNAL_API_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()

            normalized = [
                comic
                for item in data.get("results", [])
                if (comic := self._normalize_comicvine_volume(item)) is not None
            ]

            await self._set_cache(cache_key, normalized)
            return normalized

        except (
            asyncio.TimeoutError,
            httpx.HTTPError,
            httpx.TimeoutException,
            ValueError,
            KeyError,
            TypeError,
        ) as exc:
            logger.warning(
                "ComicVine query timed out or failed",
                extra={"query": query, "error": str(exc)},
            )
            return []

    # Normalizers

    @staticmethod
    def _normalize_google_book(item: dict) -> Optional[dict]:
        """Convert a Google Books volume item to internal Book format."""
        info = item.get("volumeInfo", {})
        title = (info.get("title") or "").strip()
        volume_id = item.get("id", "")

        if not title or not volume_id:
            return None

        authors = info.get("authors", [])
        image_links = info.get("imageLinks", {})
        cover_url = (
            image_links.get("thumbnail")
            or image_links.get("smallThumbnail")
            or ""
        )
        # Google Books sometimes returns http:// URLs
        if cover_url.startswith("http://"):
            cover_url = cover_url.replace("http://", "https://", 1)

        categories = info.get("categories", [])
        genres = [c.split(" / ")[-1].strip() for c in categories[:3]]

        published_year = None
        published_date = info.get("publishedDate", "")
        if published_date and len(published_date) >= 4:
            try:
                published_year = int(published_date[:4])
            except ValueError:
                pass

        return {
            "content_id": f"gb:{volume_id}",
            "id": f"gb:{volume_id}",
            "title": title,
            "author": ", ".join(authors) if authors else "Unknown",
            "cover_url": cover_url,
            "description": (info.get("description") or "")[:500],
            "content_type": "book",
            "genres": genres,
            "mood_cluster": "",
            "is_free": False,
            "free_url": None,
            "published_year": published_year,
            "page_count": info.get("pageCount"),
            "average_rating": info.get("averageRating"),
            "source": "google_books_live",
        }

    @staticmethod
    def _normalize_comicvine_volume(item: dict) -> Optional[dict]:
        """Convert a ComicVine volume result to internal Book format."""
        name = (item.get("name") or "").strip()
        volume_id = item.get("id")

        if not name or not volume_id:
            return None

        image = item.get("image") or {}
        cover_url = (
            image.get("medium_url")
            or image.get("small_url")
            or image.get("thumb_url")
            or ""
        )

        publisher = item.get("publisher") or {}

        return {
            "content_id": f"cv:{volume_id}",
            "id": f"cv:{volume_id}",
            "title": name,
            "author": publisher.get("name") or "Unknown",
            "cover_url": cover_url,
            "description": (item.get("deck") or "")[:500],
            "content_type": "comic",
            "genres": [],
            "mood_cluster": "",
            "is_free": False,
            "free_url": None,
            "published_year": None,
            "page_count": item.get("count_of_issues"),
            "average_rating": None,
            "source": "comicvine_live",
        }

    # Cache Helpers

    @staticmethod
    def _make_cache_key(prefix: str, query: str, max_results: int) -> str:
        """Build a deterministic cache key from query parameters."""
        digest = hashlib.md5(
            f"{query}:{max_results}".encode()
        ).hexdigest()[:12]
        return f"discovery:{prefix}:{digest}"

    async def _get_cache(self, key: str) -> Optional[list[dict]]:
        """Retrieve cached results from Redis. Returns None on miss."""
        if not self.redis:
            return None
        try:
            raw = await self.redis.get(key)
            if raw is None:
                return None
            if isinstance(raw, list):
                return raw
            if isinstance(raw, str):
                return json.loads(raw)
            if isinstance(raw, bytes):
                return json.loads(raw.decode("utf-8"))
        except (
            ConnectionError,
            TimeoutError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            logger.debug(
                "Redis cache read failed",
                extra={"key": key, "error": str(exc)},
            )
        return None

    async def _set_cache(
        self, key: str, data: list[dict], ttl: int = CACHE_TTL_SECONDS
    ) -> None:
        """Store results in Redis with TTL. Fails silently."""
        if not self.redis:
            return
        try:
            payload = json.dumps(data)
            if hasattr(self.redis, "set"):
                # Support both raw redis and custom redis_client wrappers
                try:
                    await self.redis.set(key, payload, ttl_seconds=ttl)
                except TypeError:
                    await self.redis.set(key, payload, ex=ttl)
        except (ConnectionError, TimeoutError, TypeError, ValueError) as exc:
            logger.debug(
                "Redis cache write failed",
                extra={"key": key, "error": str(exc)},
            )