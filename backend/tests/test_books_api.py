"""Integration tests for the book search API.

Tests the GET /api/v1/books/search endpoint contract:
- Request validation (query, limit, offset bounds)
- Success envelope shape
- Error envelope shape
- Upstream failure mapping (TransientAPIError -> 503)

The BookService is stubbed via dependency override. These tests do
not touch Redis, httpx, or the Google Books API. The GoogleBooksClient
behaviour is covered by test_google_books.py.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, AsyncIterator, Optional

import httpx
import pytest
from httpx import ASGITransport

from src.api.deps import get_book_service
from src.external.google_books import TransientAPIError
from src.main import app
from src.schemas.book import BookSearchResponse, BookSearchResult


# Fixtures

class StubBookService:
    """Configurable stand-in for BookService.

    Records the last call arguments so tests can assert on wiring.
    Set `return_value` to control the response, or `raise_exception`
    to make .search() raise.
    """

    def __init__(self) -> None:
        self.return_value: Optional[BookSearchResponse] = None
        self.raise_exception: Optional[Exception] = None
        self.last_call: dict[str, Any] = {}

    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> BookSearchResponse:
        self.last_call = {"query": query, "limit": limit, "offset": offset}
        if self.raise_exception is not None:
            raise self.raise_exception
        if self.return_value is not None:
            return self.return_value
        # Default: empty successful response echoing the request.
        return BookSearchResponse(
            query=query,
            total_count=0,
            limit=limit,
            offset=offset,
            results=[],
        )


@pytest.fixture
def stub_service() -> StubBookService:
    """Yield a fresh stub for each test."""
    return StubBookService()


@pytest.fixture
async def app_client(stub_service: StubBookService) -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx AsyncClient bound to the FastAPI app.

    Overrides get_book_service with the stub for the duration of the
    test, then clears the override on teardown.
    """
    app.dependency_overrides[get_book_service] = lambda: stub_service
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


def _sample_result(google_books_id: str = "abc123", title: str = "Test Book") -> BookSearchResult:
    """Build a minimal valid BookSearchResult for use in stubbed responses."""
    return BookSearchResult(
        google_books_id=google_books_id,
        title=title,
        authors=["Test Author"],
    )


ISO_8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$"
)


# Happy path

class TestSearchHappyPath:
    """Tests for successful GET /api/v1/books/search responses."""

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

    async def test_data_contains_search_response_fields(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get(
            "/api/v1/books/search",
            params={"q": "sapiens", "limit": 15, "offset": 5},
        )

        data = response.json()["data"]
        assert data["query"] == "sapiens"
        assert data["limit"] == 15
        assert data["offset"] == 5
        assert data["total_count"] == 0
        assert data["results"] == []

    async def test_returns_multiple_results_correctly(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.return_value = BookSearchResponse(
            query="sapiens",
            total_count=2,
            limit=20,
            offset=0,
            results=[
                _sample_result("id1", "Sapiens"),
                _sample_result("id2", "Homo Deus"),
            ],
        )

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        data = response.json()["data"]
        assert data["total_count"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["google_books_id"] == "id1"
        assert data["results"][0]["title"] == "Sapiens"
        assert data["results"][1]["google_books_id"] == "id2"
        assert data["results"][1]["title"] == "Homo Deus"

    async def test_empty_results_still_return_200_not_404(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.return_value = BookSearchResponse(
            query="nothingmatches",
            total_count=0,
            limit=20,
            offset=0,
            results=[],
        )

        response = await app_client.get(
            "/api/v1/books/search", params={"q": "nothingmatches"}
        )

        assert response.status_code == 200
        assert response.json()["data"]["results"] == []


# Query validation

class TestSearchQueryValidation:
    """Tests for validation of the `q` query parameter."""

    async def test_missing_query_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search")

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    async def test_query_shorter_than_min_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_query_longer_than_max_returns_422(
        self, app_client: httpx.AsyncClient
    ) -> None:
        too_long = "a" * 201
        response = await app_client.get("/api/v1/books/search", params={"q": too_long})

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
        max_query = "a" * 200
        response = await app_client.get("/api/v1/books/search", params={"q": max_query})

        assert response.status_code == 200

    async def test_validation_error_envelope_contains_details(
        self, app_client: httpx.AsyncClient
    ) -> None:
        response = await app_client.get("/api/v1/books/search", params={"q": "x"})

        error = response.json()["error"]
        assert "details" in error
        assert isinstance(error["details"], list)
        assert len(error["details"]) > 0


# Limit validation

class TestSearchLimitValidation:
    """Tests for validation of the `limit` query parameter."""

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


# Offset validation

class TestSearchOffsetValidation:
    """Tests for validation of the `offset` query parameter."""

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


# Upstream failure

class TestSearchUpstreamFailure:
    """Tests for upstream Google Books API failure handling."""

    async def test_transient_api_error_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream is down")

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        assert response.status_code == 503

    async def test_transient_api_error_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream is down")

        response = await app_client.get("/api/v1/books/search", params={"q": "sapiens"})

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"
        assert isinstance(body["error"]["message"], str)
        assert body["error"]["message"] != ""


# Envelope contract

class TestSearchEnvelopeMeta:
    """Tests for the meta block on both success and error responses."""

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


# Service wiring

class TestSearchServiceIntegration:
    """Tests that request params are correctly wired to BookService."""

    async def test_service_receives_exact_query_string(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        await app_client.get("/api/v1/books/search", params={"q": "the great gatsby"})

        assert stub_service.last_call["query"] == "the great gatsby"

    async def test_service_receives_exact_limit_and_offset(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        await app_client.get(
            "/api/v1/books/search",
            params={"q": "sapiens", "limit": 15, "offset": 10},
        )

        assert stub_service.last_call["limit"] == 15
        assert stub_service.last_call["offset"] == 10