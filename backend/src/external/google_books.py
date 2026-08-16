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
    """Async wrapper around the public Google Books API."""

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
        await self._client.aclose()

    async def _get_json(
        self,
        path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
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
    def _extract_series_info(volume_info: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Extract seriesInfo from volumeInfo if present and valid.

        Google Books returns seriesInfo at the volumeInfo level for books
        that are part of a series. Structure:
            {
                "bookDisplayNumber": "1",
                "series": [{"seriesId": "...", "seriesName": "...", "imageUrl": "..."}]
            }

        Returns the raw seriesInfo dict if it contains at least one series
        entry with a seriesName. Returns None otherwise.
        """
        series_info = volume_info.get("seriesInfo")
        if not isinstance(series_info, dict):
            return None
        series_list = series_info.get("series")
        if not isinstance(series_list, list) or not series_list:
            return None
        first = series_list[0]
        if not isinstance(first, dict):
            return None
        if not first.get("seriesName"):
            return None
        return series_info

    @staticmethod
    def _map_volume(raw: dict[str, Any]) -> dict[str, Any]:
        """Map a raw Google Books volume into the internal schema shape."""
        volume_info = raw.get("volumeInfo") or {}
        image_links = volume_info.get("imageLinks") or {}
        isbn_10, isbn_13 = GoogleBooksClient._extract_isbns(
            volume_info.get("industryIdentifiers")
        )
        series_info = GoogleBooksClient._extract_series_info(volume_info)

        mapped: dict[str, Any] = {
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

        if series_info is not None:
            mapped["series_info"] = series_info

        return mapped