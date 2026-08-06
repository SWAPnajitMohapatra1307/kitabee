"""Async client for the Comic Vine API."""

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


BASE_URL = "https://comicvine.gamespot.com/api"

SEARCH_CACHE_TTL_SECONDS = 86400
DETAIL_CACHE_TTL_SECONDS = 86400

TIMEOUT_CONFIG = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

RETRYABLE_STATUSES = frozenset({429, 500, 501, 502, 503, 504})

ISSUE_FIELDS = "id,name,description,image,volume,issue_number,cover_date,site_detail_url"
VOLUME_FIELDS = "id,name,description,image,publisher,count_of_issues,start_year,site_detail_url"

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_DATE_YEAR_RE = re.compile(r"^\d{4}$")
_DATE_YEAR_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
_DATE_FULL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

CV_STATUS_OK = 1


class TransientAPIError(Exception):
    """Raised for retryable HTTP failures from the Comic Vine API."""


class _NotFoundError(Exception):
    """Internal sentinel for 404 responses from the Comic Vine API."""


class ComicVineClient:
    """Async wrapper around the Comic Vine API.

    Handles authentication, retry with exponential backoff, and
    response mapping into the internal comic schema shape.
    """

    def __init__(self) -> None:
        self._api_key: str = settings.comic_vine_api_key
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=TIMEOUT_CONFIG,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
    async def search_comics(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search comic issues and volumes by free-text query.

        Reads from Redis first. On miss, calls the Comic Vine API
        and caches non-empty results with SEARCH_CACHE_TTL_SECONDS.

        Args:
            query: Free-text search string (title, character, series).
            page: Page number for pagination (1-indexed).
            limit: Maximum items to return per page (1-100).

        Returns:
            List of mapped comic dicts. Empty list when API has no items.
        """
        cache_key = f"cv:search:{query.strip().lower()}:{page}:{limit}"

        cached_result = await redis_client.get(cache_key)
        if cached_result is not None:
            logger.info(
                "Comic Vine search cache hit",
                extra={"key": cache_key, "query": query},
            )
            return cached_result

        params: dict[str, Any] = {
            "api_key": self._api_key,
            "format": "json",
            "query": query,
            "resources": "issue,volume",
            "field_list": ISSUE_FIELDS,
            "page": page,
            "limit": limit,
        }
        logger.info(
            "Comic Vine search request",
            extra={"path": "/search/", "params": {"query": query, "page": page, "limit": limit}},
        )
        data = await self._get_json("/search/", params=params)
        if not data:
            return []

        results = data.get("results") or []
        mapped = [self._map_issue(item) for item in results if isinstance(item, dict)]

        if mapped:
            await redis_client.set(cache_key, mapped, ttl_seconds=SEARCH_CACHE_TTL_SECONDS)

        return mapped

    async def get_comic(self, issue_id: str) -> Optional[dict[str, Any]]:
        """Fetch a single comic issue by its Comic Vine issue ID.

        Reads from Redis first. On miss, calls the Comic Vine API
        and caches successful results with DETAIL_CACHE_TTL_SECONDS.
        Never caches None (miss or transient failure).

        Args:
            issue_id: Numeric Comic Vine issue ID (without the 4000- prefix).

        Returns:
            Mapped comic dict, or None when the issue does not exist or
            the API returns a persistent transient error for this issue.
        """
        cache_key = f"cv:issue:{issue_id}"

        cached_result = await redis_client.get(cache_key)
        if cached_result is not None:
            logger.info(
                "Comic Vine issue cache hit",
                extra={"key": cache_key, "issue_id": issue_id},
            )
            return cached_result

        path = f"/issue/4000-{issue_id}/"
        params: dict[str, Any] = {
            "api_key": self._api_key,
            "format": "json",
            "field_list": ISSUE_FIELDS,
        }
        logger.info(
            "Comic Vine issue detail request",
            extra={"path": path, "params": {"issue_id": issue_id}},
        )
        try:
            data = await self._get_json(path, params=params)
        except _NotFoundError:
            return None
        except TransientAPIError:
            logger.warning(
                "Comic Vine returned persistent transient error for issue",
                extra={"issue_id": issue_id},
            )
            return None
        if not data:
            return None

        results = data.get("results")
        if not isinstance(results, dict):
            return None

        mapped = self._map_issue(results)
        await redis_client.set(cache_key, mapped, ttl_seconds=DETAIL_CACHE_TTL_SECONDS)
        return mapped

    async def get_volume(self, volume_id: str) -> Optional[dict[str, Any]]:
        """Fetch a single comic volume (series) by its Comic Vine volume ID.

        Reads from Redis first. On miss, calls the Comic Vine API
        and caches successful results with DETAIL_CACHE_TTL_SECONDS.
        Never caches None (miss or transient failure).

        Args:
            volume_id: Numeric Comic Vine volume ID (without the 4050- prefix).

        Returns:
            Mapped volume dict, or None when the volume does not exist or
            the API returns a persistent transient error for this volume.
        """
        cache_key = f"cv:volume:{volume_id}"

        cached_result = await redis_client.get(cache_key)
        if cached_result is not None:
            logger.info(
                "Comic Vine volume cache hit",
                extra={"key": cache_key, "volume_id": volume_id},
            )
            return cached_result

        path = f"/volume/4050-{volume_id}/"
        params: dict[str, Any] = {
            "api_key": self._api_key,
            "format": "json",
            "field_list": VOLUME_FIELDS,
        }
        logger.info(
            "Comic Vine volume detail request",
            extra={"path": path, "params": {"volume_id": volume_id}},
        )
        try:
            data = await self._get_json(path, params=params)
        except _NotFoundError:
            return None
        except TransientAPIError:
            logger.warning(
                "Comic Vine returned persistent transient error for volume",
                extra={"volume_id": volume_id},
            )
            return None
        if not data:
            return None

        results = data.get("results")
        if not isinstance(results, dict):
            return None

        mapped = self._map_volume(results)
        await redis_client.set(cache_key, mapped, ttl_seconds=DETAIL_CACHE_TTL_SECONDS)
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
                        "Retrying Comic Vine request",
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
            raise _NotFoundError(f"Comic Vine resource not found: {safe_url}")
        if status in RETRYABLE_STATUSES:
            raise TransientAPIError(
                f"Comic Vine retryable status {status} for {safe_url}"
            )
        if 400 <= status < 500:
            logger.error(
                "Comic Vine non-retryable client error",
                extra={"status": status, "url": safe_url},
            )
            response.raise_for_status()

        data = response.json()
        if data.get("status_code") != CV_STATUS_OK:
            logger.error(
                "Comic Vine API-level error",
                extra={"cv_status": data.get("status_code"), "cv_error": data.get("error")},
            )
            raise TransientAPIError(
                f"Comic Vine API error: {data.get('error')} (status {data.get('status_code')})"
            )

        return data

    @staticmethod
    def _clean_text(value: Any) -> Optional[str]:
        """Normalize a free-text field from Comic Vine.

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
        """Normalize a Comic Vine date string to YYYY-MM-DD.

        Accepts year-only, year-month, and full ISO date shapes.
        Pads shorter shapes with 01 day/month. Returns None for
        any other value, including non-strings.

        Args:
            value: Raw date string from the API response.

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
    def _map_issue(raw: dict[str, Any]) -> dict[str, Any]:
        """Map a raw Comic Vine issue into the internal comic schema shape."""
        image = raw.get("image") or {}
        volume = raw.get("volume") or {}

        raw_id = raw.get("id")
        content_id = f"cv_{raw_id}" if raw_id is not None else None

        return {
            "id": content_id,
            "title": ComicVineClient._clean_text(raw.get("name")),
            "description": ComicVineClient._clean_text(raw.get("description")),
            "cover_image": ComicVineClient._clean_text(
                image.get("medium_url") or image.get("original_url")
            ),
            "series": ComicVineClient._clean_text(volume.get("name")),
            "issue_number": ComicVineClient._clean_text(raw.get("issue_number")),
            "published_date": ComicVineClient._clean_date(raw.get("cover_date")),
            "source": "comic_vine",
            "detail_url": ComicVineClient._clean_text(raw.get("site_detail_url")),
        }

    @staticmethod
    def _map_volume(raw: dict[str, Any]) -> dict[str, Any]:
        """Map a raw Comic Vine volume into the internal volume schema shape."""
        image = raw.get("image") or {}
        publisher = raw.get("publisher") or {}

        raw_id = raw.get("id")
        content_id = f"cv_{raw_id}" if raw_id is not None else None

        return {
            "id": content_id,
            "title": ComicVineClient._clean_text(raw.get("name")),
            "description": ComicVineClient._clean_text(raw.get("description")),
            "cover_image": ComicVineClient._clean_text(
                image.get("medium_url") or image.get("original_url")
            ),
            "publisher": ComicVineClient._clean_text(publisher.get("name")),
            "issue_count": raw.get("count_of_issues"),
            "start_year": ComicVineClient._clean_date(raw.get("start_year")),
            "source": "comic_vine",
            "detail_url": ComicVineClient._clean_text(raw.get("site_detail_url")),
        }
