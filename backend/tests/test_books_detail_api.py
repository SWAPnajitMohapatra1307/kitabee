"""Integration tests for book detail and similar books endpoints.

Tests the following endpoint contracts:
    GET /api/v1/books/{book_id}
    GET /api/v1/books/{book_id}/similar

BookService is stubbed via dependency override. No DB, no Redis,
no external API calls. Pattern mirrors test_books_api.py (Day 5).
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, AsyncIterator, Optional
from uuid import UUID, uuid4

import httpx
import pytest
from httpx import ASGITransport

from src.api.deps import get_book_service
from src.external.google_books import TransientAPIError
from src.main import app
from src.schemas.book import (
    BookDetailResponse,
    BookSearchResponse,
    BookSearchResult,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ISO_8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$"
)

_KNOWN_UUID = uuid4()
_UNKNOWN_UUID = uuid4()


# ---------------------------------------------------------------------------
# Stub service
# ---------------------------------------------------------------------------

class StubBookService:
    """Configurable stand-in for BookService.

    Covers search, get_by_id, and get_similar so all three endpoints
    can be exercised without real DB or HTTP calls.
    """

    def __init__(self) -> None:
        self.search_return: Optional[BookSearchResponse] = None
        self.detail_return: Optional[BookDetailResponse] = None
        self.similar_return: Optional[BookSearchResponse] = None
        self.raise_exception: Optional[Exception] = None
        self.last_call: dict[str, Any] = {}

    async def search(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> BookSearchResponse:
        self.last_call = {"method": "search", "query": query, "limit": limit, "offset": offset}
        if self.raise_exception:
            raise self.raise_exception
        if self.search_return:
            return self.search_return
        return BookSearchResponse(
            query=query,
            total_count=0,
            limit=limit,
            offset=offset,
            results=[],
        )

    async def get_by_id(self, book_id: UUID) -> Optional[BookDetailResponse]:
        self.last_call = {"method": "get_by_id", "book_id": book_id}
        if self.raise_exception:
            raise self.raise_exception
        return self.detail_return

    async def get_similar(
        self,
        book_id: UUID,
        limit: int,
    ) -> Optional[BookSearchResponse]:
        self.last_call = {"method": "get_similar", "book_id": book_id, "limit": limit}
        if self.raise_exception:
            raise self.raise_exception
        return self.similar_return


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_book_detail(book_id: Optional[UUID] = None) -> BookDetailResponse:
    """Build a minimal valid BookDetailResponse."""
    return BookDetailResponse(
        id=book_id or _KNOWN_UUID,
        external_id="zyTCAlFPjgYC",
        external_source="google_books",
        title="Sapiens",
        subtitle="A Brief History of Humankind",
        authors=["Yuval Noah Harari"],
        description="A history of humankind.",
        publisher="Harper",
        published_year=2014,
        page_count=464,
        genres=["History", "Non-fiction"],
        tags=[],
        language="en",
        isbn_10="0062316095",
        isbn_13="9780062316097",
        cover_url="https://example.com/cover.jpg",
        cover_url_large="https://example.com/cover_large.jpg",
        average_rating=None,
        ratings_count=None,
        kitabee_rating=None,
        kitabee_ratings_count=0,
        metadata_json={},
    )


def _make_search_result(google_books_id: str = "abc123", title: str = "Test Book") -> BookSearchResult:
    """Build a minimal valid BookSearchResult."""
    return BookSearchResult(
        google_books_id=google_books_id,
        title=title,
        authors=["Test Author"],
    )


def _make_similar_response(book_id: UUID, limit: int = 10) -> BookSearchResponse:
    """Build a minimal BookSearchResponse for similar books."""
    return BookSearchResponse(
        query="Yuval Noah Harari History",
        total_count=2,
        limit=limit,
        offset=0,
        results=[
            _make_search_result("similar1", "Homo Deus"),
            _make_search_result("similar2", "21 Lessons"),
        ],
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def stub_service() -> StubBookService:
    """Fresh stub for each test."""
    return StubBookService()


@pytest.fixture
async def app_client(stub_service: StubBookService) -> AsyncIterator[httpx.AsyncClient]:
    """httpx AsyncClient bound to FastAPI app with stubbed BookService."""
    app.dependency_overrides[get_book_service] = lambda: stub_service
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id} — happy path
# ---------------------------------------------------------------------------

class TestBookDetailHappyPath:
    """Successful detail responses."""

    async def test_returns_200_with_success_envelope(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_data_contains_book_detail_fields(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        data = response.json()["data"]
        assert data["id"] == str(_KNOWN_UUID)
        assert data["external_id"] == "zyTCAlFPjgYC"
        assert data["external_source"] == "google_books"
        assert data["title"] == "Sapiens"
        assert data["authors"] == ["Yuval Noah Harari"]
        assert data["published_year"] == 2014
        assert data["genres"] == ["History", "Non-fiction"]

    async def test_data_contains_kitabee_rating_fields(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        data = response.json()["data"]
        assert "kitabee_rating" in data
        assert "kitabee_ratings_count" in data
        assert data["kitabee_ratings_count"] == 0

    async def test_data_contains_metadata_json(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        data = response.json()["data"]
        assert "metadata_json" in data
        assert isinstance(data["metadata_json"], dict)

    async def test_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        assert response.json()["meta"]["version"] == "v1"


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id} — not found
# ---------------------------------------------------------------------------

class TestBookDetailNotFound:
    """404 handling for unknown UUIDs."""

    async def test_unknown_uuid_returns_404(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_UUID}")

        assert response.status_code == 404

    async def test_404_uses_book_not_found_code(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_UUID}")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "BOOK_NOT_FOUND"
        assert isinstance(body["error"]["message"], str)
        assert str(_UNKNOWN_UUID) in body["error"]["message"]

    async def test_invalid_uuid_format_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get("/api/v1/books/not-a-uuid")

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id} — upstream failure
# ---------------------------------------------------------------------------

class TestBookDetailUpstreamFailure:
    """503 handling for upstream API failures."""

    async def test_transient_error_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        assert response.status_code == 503

    async def test_transient_error_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id} — service wiring
# ---------------------------------------------------------------------------

class TestBookDetailServiceWiring:
    """Service receives correct arguments from route."""

    async def test_service_receives_correct_uuid(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        assert stub_service.last_call["method"] == "get_by_id"
        assert stub_service.last_call["book_id"] == _KNOWN_UUID


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id}/similar — happy path
# ---------------------------------------------------------------------------

class TestSimilarBooksHappyPath:
    """Successful similar books responses."""

    async def test_returns_200_with_success_envelope(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body

    async def test_data_contains_search_response_shape(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        data = response.json()["data"]
        assert "query" in data
        assert "total_count" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    async def test_results_exclude_source_book(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        similar = _make_similar_response(_KNOWN_UUID)
        stub_service.similar_return = similar

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        data = response.json()["data"]
        result_ids = [r["google_books_id"] for r in data["results"]]
        assert "zyTCAlFPjgYC" not in result_ids

    async def test_returns_correct_number_of_results(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        data = response.json()["data"]
        assert data["total_count"] == 2
        assert len(data["results"]) == 2

    async def test_default_limit_is_10(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        assert stub_service.last_call["limit"] == 10


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id}/similar — not found
# ---------------------------------------------------------------------------

class TestSimilarBooksNotFound:
    """404 handling when source book UUID is unknown."""

    async def test_unknown_uuid_returns_404(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_UUID}/similar")

        assert response.status_code == 404

    async def test_404_uses_book_not_found_code(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_UUID}/similar")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "BOOK_NOT_FOUND"


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id}/similar — upstream failure
# ---------------------------------------------------------------------------

class TestSimilarBooksUpstreamFailure:
    """503 handling for upstream failures on similar endpoint."""

    async def test_transient_error_returns_503(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        assert response.status_code == 503

    async def test_transient_error_uses_upstream_unavailable_code(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.raise_exception = TransientAPIError("upstream down")

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id}/similar — limit validation
# ---------------------------------------------------------------------------

class TestSimilarBooksLimitValidation:
    """Limit param validation for similar endpoint."""

    async def test_limit_below_min_returns_422(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_UUID}/similar", params={"limit": 0}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_above_max_returns_422(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_UUID}/similar", params={"limit": 41}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_limit_at_max_boundary_returns_200(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID, limit=40)

        response = await app_client.get(
            f"/api/v1/books/{_KNOWN_UUID}/similar", params={"limit": 40}
        )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/books/{book_id}/similar — service wiring
# ---------------------------------------------------------------------------

class TestSimilarBooksServiceWiring:
    """Service receives correct arguments from route."""

    async def test_service_receives_correct_uuid_and_limit(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID, limit=5)

        await app_client.get(
            f"/api/v1/books/{_KNOWN_UUID}/similar", params={"limit": 5}
        )

        assert stub_service.last_call["method"] == "get_similar"
        assert stub_service.last_call["book_id"] == _KNOWN_UUID
        assert stub_service.last_call["limit"] == 5


# ---------------------------------------------------------------------------
# Envelope meta contract
# ---------------------------------------------------------------------------

class TestDetailEnvelopeMeta:
    """Meta block contract for detail and similar endpoints."""

    async def test_success_meta_has_iso_8601_utc_timestamp(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = _make_book_detail(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}")

        timestamp = response.json()["meta"]["timestamp"]
        assert ISO_8601_UTC_RE.match(timestamp) is not None
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None

    async def test_error_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.detail_return = None

        response = await app_client.get(f"/api/v1/books/{_UNKNOWN_UUID}")

        assert response.json()["meta"]["version"] == "v1"

    async def test_similar_success_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubBookService,
    ) -> None:
        stub_service.similar_return = _make_similar_response(_KNOWN_UUID)

        response = await app_client.get(f"/api/v1/books/{_KNOWN_UUID}/similar")

        assert response.json()["meta"]["version"] == "v1"