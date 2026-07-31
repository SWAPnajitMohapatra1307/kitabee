"""Async client for the Google Books API."""

import html
import logging
import re
from typing import Any, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.cache.redis_client import redis_client
from src.config import settings

logger = logging.getLogger(__name__)


BASE_URL = "https://www.googleapis.com/books/v1"

SEARCH_CACHE_TTL_SECONDS = 1800
VOLUME_CACHE_TTL_SECONDS = 86400

TIMEOUT_CONFIG = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

RETRYABLE_STATUSES = frozenset({429, 500, 501, 502, 503, 504})

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_DATE_YEAR_RE = re.compile(r"^\d{4}$")
_DATE_YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
_DATE_FULL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TransientAPIError(Exception):
    """Raised for retryable HTTP failures from the Google Books API."""


class _NotFoundError(Exception):
    """Internal sentinel for 404 responses from the Google Books API."""


class GoogleBooksClient:
    """Async wrapper around the public Google Books API.

    Handles authentication, retry with exponential backoff, and
    response mapping into the internal book schema shape.
    """

    def __init__(self) -> None:
        self._api_key: str = settings.google_books_api_key
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=TIMEOUT_CONFIG,
        )

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search volumes by free-text query.

        Reads from Redis first. On miss, calls the Google Books API
        and caches non-empty results with SEARCH_CACHE_TTL_SECONDS.

        Args:
            query: Free-text search string (title, author, ISBN).
            max_results: Maximum items to return (1-40).

        Returns:
            List of mapped book dicts. Empty list when API has no items.
        """
        cache_key = f"gb:search:{query.strip().lower()}:{max_results}"

        cached_result = await redis_client.get(cache_key)
        if cached_result is not None:
            logger.info(
                "Google Books search cache hit",
                extra={"key": cache_key, "query": query},
            )
            return cached_result

        params: dict[str, Any] = {
            "q": query,
            "maxResults": max_results,
            "key": self._api_key,
        }
        logger.info(
            "Google Books search request",
            extra={"path": "/volumes", "params": {"q": query, "maxResults": max_results}},
        )
        data = await self._get_json("/volumes", params=params)
        if not data:
            return []
        items = data.get("items") or []
        mapped = [self._map_volume(item) for item in items if isinstance(item, dict)]

        if mapped:
            await redis_client.set(cache_key, mapped, ttl_seconds=SEARCH_CACHE_TTL_SECONDS)

        return mapped

    async def get_by_id(self, volume_id: str) -> Optional[dict[str, Any]]:
        """Fetch a single volume by its Google Books ID.

        Reads from Redis first. On miss, calls the Google Books API
        and caches successful results with VOLUME_CACHE_TTL_SECONDS.
        Never caches None (miss or transient failure).

        Args:
            volume_id: Google Books volume identifier.

        Returns:
            Mapped book dict, or None when the volume does not exist or
            the API returns a persistent transient error for this volume.
        """
        cache_key = f"gb:volume:{volume_id}"

        cached_result = await redis_client.get(cache_key)
        if cached_result is not None:
            logger.info(
                "Google Books detail cache hit",
                extra={"key": cache_key, "volume_id": volume_id},
            )
            return cached_result

        path = f"/volumes/{volume_id}"
        params: dict[str, Any] = {"key": self._api_key}
        logger.info(
            "Google Books detail request",
            extra={"path": path, "params": {"volume_id": volume_id}},
        )
        try:
            data = await self._get_json(path, params=params)
        except _NotFoundError:
            return None
        except TransientAPIError:
            logger.warning(
                "Google Books returned persistent transient error for volume",
                extra={"volume_id": volume_id},
            )
            return None
        if not data:
            return None

        mapped = self._map_volume(data)
        await redis_client.set(cache_key, mapped, ttl_seconds=VOLUME_CACHE_TTL_SECONDS)
        return mapped

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _get_json(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """GET a JSON response with retry on transient failures."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(
                (
                    httpx.TimeoutException,
                    httpx.ConnectError,
                    httpx.RemoteProtocolError,
                    TransientAPIError,
                )
            ),
            reraise=True,
        ):
            with attempt:
                if attempt.retry_state.attempt_number > 1:
                    logger.warning(
                        "Retrying Google Books request",
                        extra={
                            "path": path,
                            "attempt": attempt.retry_state.attempt_number,
                        },
                    )
                response = await self._client.get(path, params=params)
                return self._handle_response(response)

        raise RuntimeError("unreachable: AsyncRetrying exited without return or raise")

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Inspect a response, raise retryable errors, raise not-found.

        Strips the query string from any URL used in exceptions or logs
        to prevent leaking the API key.
        """
        status = response.status_code
        safe_url = str(response.url).split("?")[0]
        if status == 404:
            raise _NotFoundError(f"Google Books resource not found: {safe_url}")
        if status in RETRYABLE_STATUSES:
            raise TransientAPIError(
                f"Google Books retryable status {status} for {safe_url}"
            )
        if 400 <= status < 500:
            logger.error(
                "Google Books non-retryable client error",
                extra={"status": status, "url": safe_url},
            )
            response.raise_for_status()
        return response.json()

    @staticmethod
    def _clean_text(value: Any) -> Optional[str]:
        """Normalize a free-text field from Google Books.

        Strips HTML tags, unescapes entities, collapses whitespace,
        and trims surrounding spaces. Returns None for missing or
        empty-after-cleaning values.

        Args:
            value: Raw value from the API response.

        Returns:
            Cleaned string, or None when input is missing or empty.
        """
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        if not stripped:
            return None
        without_tags = _HTML_TAG_RE.sub(" ", stripped)
        unescaped = html.unescape(without_tags)
        collapsed = _WHITESPACE_RE.sub(" ", unescaped).strip()
        return collapsed or None

    @staticmethod
    def _clean_date(value: Any) -> Optional[str]:
        """Normalize a Google Books publishedDate to YYYY-MM-DD.

        Accepts year-only, year-month, and full ISO date shapes.
        Pads shorter shapes with 01 day/month. Returns None for
        any other value, including non-strings.

        Args:
            value: Raw publishedDate from the API response.

        Returns:
            Date string in YYYY-MM-DD form, or None.
        """
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        if _DATE_FULL_RE.match(candidate):
            return candidate
        if _DATE_YEAR_MONTH_RE.match(candidate):
            return f"{candidate}-01"
        if _DATE_YEAR_RE.match(candidate):
            return f"{candidate}-01-01"
        return None

    @staticmethod
    def _clean_int(value: Any) -> Optional[int]:
        """Coerce a value to a positive int.

        Rejects booleans, zero, and negatives. Accepts int, float,
        and numeric strings.

        Args:
            value: Raw value from the API response.

        Returns:
            Positive int, or None when value is missing or invalid.
        """
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value if value > 0 else None
        if isinstance(value, float):
            return int(value) if value > 0 else None
        if isinstance(value, str):
            try:
                parsed = int(value.strip())
            except ValueError:
                return None
            return parsed if parsed > 0 else None
        return None

    @staticmethod
    def _clean_float(value: Any) -> Optional[float]:
        """Coerce a value to a positive float.

        Rejects booleans, zero, and negatives. Accepts int, float,
        and numeric strings.

        Args:
            value: Raw value from the API response.

        Returns:
            Positive float, or None when value is missing or invalid.
        """
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            as_float = float(value)
            return as_float if as_float > 0 else None
        if isinstance(value, str):
            try:
                parsed = float(value.strip())
            except ValueError:
                return None
            return parsed if parsed > 0 else None
        return None

    @staticmethod
    def _clean_str_list(value: Any) -> list[str]:
        """Normalize a list-of-strings field from Google Books.

        Filters out non-list inputs and non-string or empty items,
        strips survivors, and deduplicates while preserving order.

        Args:
            value: Raw value from the API response.

        Returns:
            Cleaned list of strings (possibly empty).
        """
        if not isinstance(value, list):
            return []
        seen: set[str] = set()
        result: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            cleaned = item.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            result.append(cleaned)
        return result

    @staticmethod
    def _extract_isbns(identifiers: Any) -> tuple[Optional[str], Optional[str]]:
        """Pull ISBN_10 and ISBN_13 from industryIdentifiers.

        Skips malformed entries. First valid value per type wins.

        Args:
            identifiers: Raw industryIdentifiers from the API response.

        Returns:
            Tuple of (isbn_10, isbn_13); either may be None.
        """
        isbn_10: Optional[str] = None
        isbn_13: Optional[str] = None
        if not isinstance(identifiers, list):
            return isbn_10, isbn_13
        for entry in identifiers:
            if not isinstance(entry, dict):
                continue
            kind = entry.get("type")
            raw_value = entry.get("identifier")
            if not isinstance(raw_value, str):
                continue
            cleaned = raw_value.strip()
            if not cleaned:
                continue
            if kind == "ISBN_10" and isbn_10 is None:
                isbn_10 = cleaned
            elif kind == "ISBN_13" and isbn_13 is None:
                isbn_13 = cleaned
        return isbn_10, isbn_13

    @staticmethod
    def _map_volume(raw: dict[str, Any]) -> dict[str, Any]:
        """Map a raw Google Books volume into the internal schema shape."""
        volume_info = raw.get("volumeInfo") or {}
        image_links = volume_info.get("imageLinks") or {}
        isbn_10, isbn_13 = GoogleBooksClient._extract_isbns(
            volume_info.get("industryIdentifiers")
        )

        return {
            "google_books_id": GoogleBooksClient._clean_text(raw.get("id")),
            "title": GoogleBooksClient._clean_text(volume_info.get("title")),
            "subtitle": GoogleBooksClient._clean_text(volume_info.get("subtitle")),
            "authors": GoogleBooksClient._clean_str_list(volume_info.get("authors")),
            "description": GoogleBooksClient._clean_text(volume_info.get("description")),
            "publisher": GoogleBooksClient._clean_text(volume_info.get("publisher")),
            "published_date": GoogleBooksClient._clean_date(
                volume_info.get("publishedDate")
            ),
            "page_count": GoogleBooksClient._clean_int(volume_info.get("pageCount")),
            "categories": GoogleBooksClient._clean_str_list(
                volume_info.get("categories")
            ),
            "language": GoogleBooksClient._clean_text(volume_info.get("language")),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13,
            "thumbnail_url": GoogleBooksClient._clean_text(image_links.get("thumbnail")),
            "small_thumbnail_url": GoogleBooksClient._clean_text(
                image_links.get("smallThumbnail")
            ),
            "average_rating": GoogleBooksClient._clean_float(
                volume_info.get("averageRating")
            ),
            "ratings_count": GoogleBooksClient._clean_int(
                volume_info.get("ratingsCount")
            ),
            "preview_link": GoogleBooksClient._clean_text(volume_info.get("previewLink")),
            "info_link": GoogleBooksClient._clean_text(volume_info.get("infoLink")),
        }