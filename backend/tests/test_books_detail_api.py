"""Integration tests for book detail and similar content endpoints.

Tests:
    GET /api/v1/books/{content_id}
    GET /api/v1/books/{content_id}/similar

ContentRouter is stubbed via dependency override.
No DB, no Redis, no external API calls.
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

_KNOWN_ID = "gb:ByLKDQAAQBAJ"
_KNOWN_CV_ID = "cv:456"
_KNOWN_IA_ID = "ia:pg1342"
_UNKNOWN_ID = "gb:doesnotexist"

_SOURCE_MAP = {
    "gb": "google_books",
    "cv": "comic_vine",
    "ia": "internet_archive",
}


def _make_item(content_id: str = _KNOWN_ID, title: str = "Sapiens") -> dict:
    prefix, raw_id = content_id.split(":", 1)
    external_source = _SOURCE_MAP[prefix]
    return {
        "content_id": content_id,
        "external_id": raw_id,
        "external_source": external_source,
        "source": external_source,
        "title": title,
        "authors": ["Yuval Noah Harari"],
        "author": "Yuval Noah Harari",
        "cover_url": "https://example.com/cover.jpg",
        "cover_url_large": None,
        "description": "A history of humankind.",
        "content_type": "book",
        "is_free": prefix == "ia",
        "free_url": None,
        "genres": ["History"],
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
        self.detail_return: Optional[dict] = None
        self.similar_return: list[dict] = []
        self.raise_exception: Optional[Exception] = None
        self.last_call: dict[str, Any] = {}

    async def search(
        self,
        query: str,
        limit: int,
        sources: Optional[list[str]] = None,
    ) -> list[dict]:
        return []

    async def get_by_content_id(self, content_id: str) -> Optional[dict]:
        self.last_call = {"method": "get_by_content_id", "content_id": content_id}
        if self.raise_exception:
            raise self.raise_exception
        return self.detail_return

    async def get_similar(self, content_id: str, limit: int) -> list[dict]:
        self.last_call = {"method": "get_similar", "content_id": content_id, "limit": limit}
        if self.raise_exception:
            raise self.raise_exception
        return self.similar_return


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


class TestContentDetailHappyPath:
    async def test_returns_200_with_success_envelope(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_ID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_data_contains_content_item_fields(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_ID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        data = response.json()["data"]
        assert data["content_id"] == _KNOWN_ID
        assert data["external_id"] == "ByLKDQAAQBAJ"
        assert data["external_source"] == "google_books"
        assert data["title"] == "Sapiens"
        assert data["authors"] == ["Yuval Noah Harari"]
        assert data["source"] == "google_books"
        assert data["is_free"] is False

    async def test_cv_item_has_correct_source(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_CV_ID, "Batman")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_CV_ID}")

        data = response.json()["data"]
        assert data["content_id"] == _KNOWN_CV_ID
        assert data["external_source"] == "comic_vine"
        assert data["source"] == "comic_vine"
        assert data["is_free"] is False

    async def test_ia_item_has_is_free_true(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_IA_ID, "Pride and Prejudice")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_IA_ID}")

        data = response.json()["data"]
        assert data["content_id"] == _KNOWN_IA_ID
        assert data["external_source"] == "internet_archive"
        assert data["is_free"] is True

    async def test_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_ID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        assert response.json()["meta"]["version"] == "v1"


class TestContentDetailNotFound:
    async def test_unknown_content_id_returns_404(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_ID}")

        assert response.status_code == 404

    async def test_404_uses_content_not_found_code(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_ID}")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "CONTENT_NOT_FOUND"
        assert _UNKNOWN_ID in body["error"]["message"]

    async def test_invalid_prefix_returns_400(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get("/api/v1/books/xx:badprefix")

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_CONTENT_ID"

    async def test_bare_string_no_prefix_returns_400(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get("/api/v1/books/justanid")

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_CONTENT_ID"


class TestContentDetailUpstreamFailure:
    async def test_upstream_exception_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        assert response.status_code == 503

    async def test_upstream_exception_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


class TestContentDetailRouterWiring:
    async def test_router_receives_correct_content_id(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_ID)

        await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        assert stub_router.last_call["method"] == "get_by_content_id"
        assert stub_router.last_call["content_id"] == _KNOWN_ID


class TestSimilarContentHappyPath:
    async def test_returns_200_with_success_envelope(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.similar_return = [_make_item("gb:similar1", "Homo Deus")]

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_data_contains_list_shape(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.similar_return = [
            _make_item("gb:similar1", "Homo Deus"),
            _make_item("gb:similar2", "21 Lessons"),
        ]

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        data = response.json()["data"]
        assert "total_count" in data
        assert "results" in data
        assert data["total_count"] == 2
        assert len(data["results"]) == 2

    async def test_results_have_content_id_field(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.similar_return = [_make_item("gb:similar1", "Homo Deus")]

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        result = response.json()["data"]["results"][0]
        assert "content_id" in result
        assert result["content_id"] == "gb:similar1"

    async def test_default_limit_is_10(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        assert stub_router.last_call["limit"] == 10

    async def test_empty_similar_returns_200_not_404(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.similar_return = []

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        assert response.status_code == 200
        assert response.json()["data"]["results"] == []


class TestSimilarContentNotFound:
    async def test_invalid_prefix_returns_400(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get("/api/v1/books/xx:badid/similar")

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_CONTENT_ID"


class TestSimilarContentUpstreamFailure:
    async def test_upstream_exception_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        assert response.status_code == 503

    async def test_upstream_exception_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.raise_exception = Exception("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


class TestSimilarContentLimitValidation:
    async def test_limit_below_min_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_ID}/similar", params={"limit": 0}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_above_max_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_ID}/similar", params={"limit": 41}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_at_max_boundary_returns_200(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_ID}/similar", params={"limit": 40}
        )

        assert response.status_code == 200


class TestSimilarContentRouterWiring:
    async def test_router_receives_correct_content_id_and_limit(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        await app_client.get(
            f"/api/v1/books/{_KNOWN_ID}/similar", params={"limit": 5}
        )

        assert stub_router.last_call["method"] == "get_similar"
        assert stub_router.last_call["content_id"] == _KNOWN_ID
        assert stub_router.last_call["limit"] == 5


class TestDetailEnvelopeMeta:
    async def test_success_meta_has_iso_8601_utc_timestamp(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = _make_item(_KNOWN_ID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}")

        timestamp = response.json()["meta"]["timestamp"]
        assert ISO_8601_UTC_RE.match(timestamp) is not None
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None

    async def test_error_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        stub_router.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_ID}")

        assert response.json()["meta"]["version"] == "v1"

    async def test_similar_success_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_router: StubContentRouter,
    ) -> None:
        response = await app_client.get(f"/api/v1/books/{_KNOWN_ID}/similar")

        assert response.json()["meta"]["version"] == "v1"
