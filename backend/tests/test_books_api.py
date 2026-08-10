"""Integration tests for the book search API.

Tests GET /api/v1/books/search with unified content_id system.
ContentRouter is stubbed via dependency override.
No Redis, no httpx, no external API calls.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, AsyncIterator, Optional

import httpx
import pytest
from httpx import ASGITransport

from src.api.deps import get_content_router
from src.main import app


ISO_8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$"
)

_SOURCE_MAP = {
    "gb": "google_books",
    "cv": "comic_vine",
    "ia": "internet_archive",
}


def _make_item(content_id: str = "gb:test123", title: str = "Test Book") -> dict:
    prefix, raw_id = content_id.split(":", 1)
    external_source = _SOURCE_MAP[prefix]
    return {
        "content_id": content_id,
        "external_id": raw_id,
        "external_source": external_source,
        "source": external_source,
        "title": title,
        "authors": ["Test Author"],
        "author": "Test Author",
        "cover_url": None,
        "cover_url_large": None,
        "description": None,
        "content_type": "book",
        "is_free": prefix == "ia",
        "free_url": None,
        "genres": [],
        "language": "en",
        "publisher": None,
        "published_date": None,
        "page_count": None,
        "isbn_10": None,
        "isbn_13": None,
        "average_rating": None,
        "rating_count": 0,
        "series_id": None,
        "series_order": None,
    }


class StubContentRouter:
    def __init__(self) -> None:
        self.search_return: list[dict] = []
        self.raise_exception: Optional[Exception] = None
        self.last_call: dict[str, Any] = {}

    async def search(
        self,
        query: str,
        limit: int,
        sources: Optional[list[str]] = None,
    ) -> list[dict]:
        self.last_call = {"query": query, "limit": limit, "sources": sources}
        if self.raise_exception:
            raise self.raise_exception
        return self.search_return

    async def get_by_content_id(self, content_id: str) -> Optional[dict]:
        return None

    async def get_similar(self, content_id: str, limit: int) -> list[dict]:
        return []


@pytest.fixture
def stub_router() -> StubContentRouter:
    return StubContentRouter()


@pytest.fixture
async def app_client(stub_router: StubContentRouter) -> AsyncIterator[httpx.AsyncClient]:
    app.dependency_overrides[get_content_router] = lambda: stub_router
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


class TestSearchHappyPath:
    async def test_returns_200_with_success_envelope(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_envelope_meta_has_version_v1(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.json()["meta"]["version"] == "v1"

    async def test_data_contains_list_response_fields(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search",
            params={"q": "sapiens", "limit": 15, "offset": 0},
        )

        data = response.json()["data"]
        assert data["total_count"] == 0
        assert data["limit"] == 15
        assert data["offset"] == 0
        assert data["results"] == []

    async def test_returns_multiple_results_correctly(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.search_return = [
            _make_item("gb:id1", "Sapiens"),
            _make_item("gb:id2", "Homo Deus"),
        ]

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        data = response.json()["data"]
        assert data["total_count"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["content_id"] == "gb:id1"
        assert data["results"][0]["title"] == "Sapiens"
        assert data["results"][1]["content_id"] == "gb:id2"

    async def test_ia_results_have_is_free_true(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.search_return = [_make_item("ia:pg1342", "Pride and Prejudice")]

        response = await app_client.get("/api/v1/books/search", params={"q": "pride"})

        result = response.json()["data"]["results"][0]
        assert result["is_free"] is True

    async def test_gb_results_have_is_free_false(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.search_return = [_make_item("gb:test123", "Sapiens")]

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        result = response.json()["data"]["results"][0]
        assert result["is_free"] is False

    async def test_empty_results_return_200_not_404(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "nothingmatches"}
        )

        assert response.status_code == 200
        assert response.json()["data"]["results"] == []


class TestSearchQueryValidation:
    async def test_missing_query_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search")

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_query_shorter_than_min_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_query_longer_than_max_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "a" * 201}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_query_at_min_length_boundary_returns_200(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "ab"})

        assert response.status_code == 200

    async def test_query_at_max_length_boundary_returns_200(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "a" * 200}
        )

        assert response.status_code == 200

    async def test_validation_error_envelope_contains_details(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        error = response.json()["error"]
        assert "details" in error
        assert isinstance(error["details"], list)
        assert len(error["details"]) > 0


class TestSearchLimitValidation:
    async def test_limit_below_min_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "sapiens", "limit": 0}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_above_max_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "sapiens", "limit": 41}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_at_min_boundary_returns_200(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "sapiens", "limit": 1}
        )

        assert response.status_code == 200
        assert response.json()["data"]["limit"] == 1

    async def test_limit_at_max_boundary_returns_200(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "sapiens", "limit": 40}
        )

        assert response.status_code == 200
        assert response.json()["data"]["limit"] == 40

    async def test_default_limit_is_20_when_omitted(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.status_code == 200
        assert response.json()["data"]["limit"] == 20


class TestSearchOffsetValidation:
    async def test_negative_offset_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search", params={"q": "sapiens", "offset": -1}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_default_offset_is_0_when_omitted(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.status_code == 200
        assert response.json()["data"]["offset"] == 0


class TestSearchUpstreamFailure:
    async def test_upstream_exception_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("all sources down")

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.status_code == 503

    async def test_upstream_exception_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("all sources down")

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


class TestSearchEnvelopeMeta:
    async def test_success_meta_has_iso_8601_utc_timestamp(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        timestamp = response.json()["meta"]["timestamp"]
        assert ISO_8601_UTC_RE.match(timestamp) is not None
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None

    async def test_error_meta_has_iso_8601_utc_timestamp(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        timestamp = response.json()["meta"]["timestamp"]
        assert ISO_8601_UTC_RE.match(timestamp) is not None

    async def test_error_meta_has_version_v1(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        assert response.json()["meta"]["version"] == "v1"


class TestSearchRouterWiring:
    async def test_router_receives_exact_query_string(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        await app_client.get("/api/v1/books/search", params={"q": "the great gatsby"})

        assert stub_router.last_call["query"] == "the great gatsby"

    async def test_router_receives_exact_limit(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        await app_client.get(
            "/api/v1/books/search",
            params={"q": "sapiens", "limit": 15},
        )

        assert stub_router.last_call["limit"] == 15
