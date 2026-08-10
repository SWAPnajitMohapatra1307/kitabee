"""Async client for the Internet Archive API."""

import logging
import re
from datetime import datetime
from typing import Any, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.cache.redis_client import redis_client

logger = logging.getLogger(__name__)


BASE_URL = "https://archive.org"

SEARCH_CACHE_TTL_SECONDS = 86400
DETAIL_CACHE_TTL_SECONDS = 86400

TIMEOUT_CONFIG = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)

RETRYABLE_STATUSES = frozenset({429, 500, 501, 502, 503, 504})

FORMAT_PRIORITY = ["EPUB", "Text PDF", "DjVu", "CBZ", "CBR"]

_YEAR_RE = re.compile(r"^\d{4}")


class TransientAPIError(Exception):
    """Raised for retryable HTTP failures from the Internet Archive API."""


class InternetArchiveClient:
    """Async wrapper around the Internet Archive public API."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=TIMEOUT_CONFIG,
        )

    async def search_free_books(
        self,
        query: str,
        page: int = 1,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search public domain texts by free-text query."""
        cache_key = f"ia:search:{query.strip().lower()}:{page}:{limit}"

        cached = await redis_client.get(cache_key)
        if cached is not None:
            logger.info(
                "Internet Archive search cache hit",
                extra={"key": cache_key, "query": query},
            )
            return cached

        params = {
            "q": f'(title:{query} OR creator:{query}) AND mediatype:texts',
            "fl[]": "identifier,title,creator,description,subject,date,language,mediatype,licenseurl",
            "sort[]": "downloads desc",
            "rows": limit,
            "page": page,
            "output": "json",
        }

        logger.info(
            "Internet Archive search request",
            extra={"path": "/advancedsearch.php", "params": {"query": query}},
        )

        data = await self._get_json("/advancedsearch.php", params=params)
        docs = (
            data.get("response", {}).get("docs", [])
            if isinstance(data, dict)
            else []
        )

        mapped = [self._map_doc(doc) for doc in docs if isinstance(doc, dict)]

        if mapped:
            await redis_client.set(cache_key, mapped, ttl_seconds=SEARCH_CACHE_TTL_SECONDS)

        return mapped

    async def get_item(self, identifier: str) -> Optional[dict[str, Any]]:
        """Fetch full metadata for an item."""
        cache_key = f"ia:item:{identifier}"

        cached = await redis_client.get(cache_key)
        if cached is not None:
            logger.info(
                "Internet Archive detail cache hit",
                extra={"key": cache_key, "identifier": identifier},
            )
            return cached

        path = f"/metadata/{identifier}"

        logger.info(
            "Internet Archive metadata request",
            extra={"path": path, "identifier": identifier},
        )

        try:
            data = await self._get_json(path, params={})
        except TransientAPIError:
            logger.warning(
                "Internet Archive persistent transient error",
                extra={"identifier": identifier},
            )
            return None

        if not isinstance(data, dict):
            return None

        mapped = self._map_metadata(identifier, data)
        await redis_client.set(cache_key, mapped, ttl_seconds=DETAIL_CACHE_TTL_SECONDS)
        return mapped

    async def get_read_url(self, identifier: str) -> Optional[str]:
        """Return best available readable/downloadable file URL."""
        path = f"/metadata/{identifier}"

        try:
            data = await self._get_json(path, params={})
        except TransientAPIError:
            return None

        files = data.get("files", [])
        if not isinstance(files, list):
            return None

        best = self._select_best_file(files)
        if not best:
            return None

        return f"https://archive.org/download/{identifier}/{best}"

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
                response = await self._client.get(path, params=params)
                return self._handle_response(response)

        raise RuntimeError("unreachable")

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        status = response.status_code
        safe_url = str(response.url).split("?")[0]

        if status in RETRYABLE_STATUSES:
            raise TransientAPIError(
                f"Internet Archive retryable status {status} for {safe_url}"
            )

        if 400 <= status < 500:
            logger.error(
                "Internet Archive client error",
                extra={"status": status, "url": safe_url},
            )
            response.raise_for_status()

        return response.json()

    def _map_doc(self, raw: dict[str, Any]) -> dict[str, Any]:
        identifier = raw.get("identifier")

        return {
            "id": f"ia_{identifier}" if identifier else None,
            "title": raw.get("title"),
            "authors": self._normalize_authors(raw.get("creator")),
            "description": raw.get("description"),
            "subjects": raw.get("subject") if isinstance(raw.get("subject"), list) else [],
            "published_date": raw.get("date"),
            "language": raw.get("language"),
            "mediatype": raw.get("mediatype"),
            "is_public_domain": self._is_public_domain(raw),
            "read_url": None,
            "thumbnail_url": f"https://archive.org/services/img/{identifier}" if identifier else None,
            "source": "internet_archive",
        }

    def _map_metadata(
        self,
        identifier: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        metadata = data.get("metadata", {}) if isinstance(data, dict) else {}

        return {
            "id": f"ia_{identifier}",
            "title": metadata.get("title"),
            "authors": self._normalize_authors(metadata.get("creator")),
            "description": metadata.get("description"),
            "subjects": metadata.get("subject") if isinstance(metadata.get("subject"), list) else [],
            "published_date": metadata.get("date"),
            "language": metadata.get("language"),
            "mediatype": metadata.get("mediatype"),
            "is_public_domain": self._is_public_domain(metadata),
            "read_url": None,
            "thumbnail_url": f"https://archive.org/services/img/{identifier}",
            "source": "internet_archive",
        }

    def _normalize_authors(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [v for v in value if isinstance(v, str)]
        if isinstance(value, str):
            return [value]
        return []

    def _is_public_domain(self, metadata: dict[str, Any]) -> bool:
        license_url = str(metadata.get("licenseurl", "")).lower()
        subject = metadata.get("subject", [])
        subject_text = " ".join(subject).lower() if isinstance(subject, list) else ""

        if "publicdomain" in license_url:
            return True
        if "creativecommons.org/publicdomain" in license_url:
            return True
        if "public domain" in subject_text:
            return True

        date_value = metadata.get("date")
        if isinstance(date_value, str):
            match = _YEAR_RE.match(date_value.strip())
            if match:
                year = int(match.group(0))
                if year < 1928:
                    return True

        return False

    def _select_best_file(self, files: list[dict[str, Any]]) -> Optional[str]:
        for preferred in FORMAT_PRIORITY:
            for file in files:
                if file.get("format") == preferred:
                    return file.get("name")
        return None