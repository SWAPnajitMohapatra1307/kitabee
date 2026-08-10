"""Tests for GET /api/v1/collections.

CollectionService and ContentRouter are both stubbed.
No DB, no Redis, no external API calls.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import src.api.routes.collections as collections_route
from src.api.deps import get_content_router
from src.main import app


ENDPOINT = "/api/v1/collections"

_SOURCE_MAP = {
    "gb": "google_books",
    "cv": "comic_vine",
    "ia": "internet_archive",
}


def _fake_user() -> MagicMock:
    user = MagicMock()
    user.id = "00000000-0000-0000-0000-000000000001"
    user.is_active = True
    return user


def _fake_enriched_item(content_id: str = "gb:test123", title: str = "Test Book") -> dict[str, Any]:
    prefix = content_id.split(":")[0]
    return {
        "content_id": content_id,
        "title": title,
        "author": "Test Author",
        "cover_url": "https://example.com/cover.jpg",
        "content_type": "book",
        "is_free": prefix == "ia",
        "free_url": None,
        "source": _SOURCE_MAP[prefix],
        "description": "A test book.",
        "genres": ["fiction"],
    }


def _fake_rows() -> list[dict[str, Any]]:
    return [
        {
            "id": "dark-000",
            "title": "Shadows of the Mind",
            "mood": "dark",
            "items": ["seed-2", "seed-5"],
            "item_count": 2,
        },
        {
            "id": "free-row",
            "title": "Free to Read Right Now",
            "mood": "educational",
            "items": ["seed-6", "seed-7"],
            "item_count": 2,
        },
    ]


def _fake_enriched_row(row: dict[str, Any]) -> dict[str, Any]:
    items = [
        _fake_enriched_item("gb:item1", "Book One"),
        _fake_enriched_item("gb:item2", "Book Two"),
    ]
    return {
        "id": row["id"],
        "title": row["title"],
        "mood": row["mood"],
        "items": items,
        "item_count": len(items),
    }


class StubContentRouter:
    async def search(self, query: str, limit: int, sources: list[str] | None = None) -> list[dict]:
        prefix_map = {
            "google_books": "gb",
            "comic_vine": "cv",
            "internet_archive": "ia",
        }
        source = (sources or ["google_books"])[0]
        prefix = prefix_map.get(source, "gb")
        raw_id = query.replace(" ", "_")[:20]
        content_id = f"{prefix}:{raw_id}"
        return [_fake_enriched_item(content_id, query)]

    async def get_by_content_id(self, content_id: str) -> dict | None:
        return None

    async def get_similar(self, content_id: str, limit: int) -> list[dict]:
        return []


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stub_content_router() -> StubContentRouter:
    return StubContentRouter()


@pytest.fixture
def mock_service(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    mock.build_home_screen.return_value = _fake_rows()
    monkeypatch.setattr(collections_route, "CollectionService", lambda *a, **kw: mock)
    return mock


@pytest.fixture
def mock_get_ratings(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(return_value=([], 0))
    monkeypatch.setattr(collections_route, "get_ratings_by_user", mock)
    return mock


@pytest.fixture
def mock_get_preferences(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(return_value=None)
    monkeypatch.setattr(collections_route, "get_preferences", mock)
    return mock


@pytest.fixture
def mock_get_by_id(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(return_value=None)
    monkeypatch.setattr(collections_route, "get_by_id", mock)
    return mock


@pytest.fixture
def mock_enrich_row(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    async def _fake(row: dict, content_router: Any) -> dict:
        return _fake_enriched_row(row)
    monkeypatch.setattr(collections_route, "_enrich_row_real", _fake)


@pytest.mark.asyncio
async def test_anonymous_returns_200(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_anonymous_response_shape(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "rows" in body["data"]
    assert "total" in body["data"]
    assert "personalized" in body["data"]


@pytest.mark.asyncio
async def test_anonymous_not_personalized(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    assert response.json()["data"]["personalized"] is False


@pytest.mark.asyncio
async def test_anonymous_collections_is_list(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    assert isinstance(response.json()["data"]["rows"], list)


@pytest.mark.asyncio
async def test_anonymous_total_matches_rows_length(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    data = response.json()["data"]
    assert data["total"] == len(data["rows"])


@pytest.mark.asyncio
async def test_authenticated_personalized_flag(
    mock_service: MagicMock,
    mock_get_preferences: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_user = _fake_user()

    ratings_mock = AsyncMock(
        return_value=([MagicMock(book_id="seed-1", rating=5)], 1)
    )
    monkeypatch.setattr(collections_route, "get_ratings_by_user", ratings_mock)
    monkeypatch.setattr(collections_route, "get_by_id", AsyncMock(return_value=fake_user))

    async def fake_optional_user() -> Any:
        return fake_user

    app.dependency_overrides[collections_route._get_optional_user] = fake_optional_user
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json()["data"]["personalized"] is True


@pytest.mark.asyncio
async def test_n_collections_query_param(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT, params={"n_collections": 3})

    assert response.status_code == 200
    call_kwargs = mock_service.build_home_screen.call_args.kwargs
    assert call_kwargs["n_collections"] == 3


@pytest.mark.asyncio
async def test_row_limit_query_param(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT, params={"row_limit": 5})

    assert response.status_code == 200
    call_kwargs = mock_service.build_home_screen.call_args.kwargs
    assert call_kwargs["row_limit"] == 5


@pytest.mark.asyncio
async def test_n_collections_out_of_range_returns_422(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT, params={"n_collections": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_row_limit_out_of_range_returns_422(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT, params={"row_limit": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_each_row_has_required_keys(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    rows = response.json()["data"]["rows"]
    row_required = {"id", "title", "mood", "items", "item_count"}
    item_required = {"content_id", "title", "author", "cover_url", "content_type", "is_free", "free_url"}

    for row in rows:
        assert row_required.issubset(row.keys())
        assert isinstance(row["items"], list)
        for item in row["items"]:
            assert item_required.issubset(item.keys())


@pytest.mark.asyncio
async def test_service_called_with_catalog(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get(ENDPOINT)

    assert mock_service.build_home_screen.called
    call_kwargs = mock_service.build_home_screen.call_args.kwargs
    assert isinstance(call_kwargs["catalog"], list)
    assert len(call_kwargs["catalog"]) > 0


@pytest.mark.asyncio
async def test_meta_block_present(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    mock_enrich_row: None,
    stub_content_router: StubContentRouter,
) -> None:
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    body = response.json()
    assert "meta" in body
    assert "timestamp" in body["meta"]
    assert "version" in body["meta"]


@pytest.mark.asyncio
async def test_ia_items_have_is_free_true(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
    stub_content_router: StubContentRouter,
) -> None:
    ia_row = {
        "id": "free-row",
        "title": "Free Classics",
        "mood": "educational",
        "items": ["seed-6"],
        "item_count": 1,
    }
    mock_service.build_home_screen.return_value = [ia_row]

    async def _ia_enrich(row: dict, content_router: Any) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "mood": row["mood"],
            "items": [_fake_enriched_item("ia:pg1342", "Pride and Prejudice")],
            "item_count": 1,
        }

    monkeypatch.setattr(collections_route, "_enrich_row_real", _ia_enrich)
    app.dependency_overrides[get_content_router] = lambda: stub_content_router

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(ENDPOINT)

    rows = response.json()["data"]["rows"]
    assert len(rows) == 1
    assert rows[0]["items"][0]["is_free"] is True
    assert rows[0]["items"][0]["content_id"] == "ia:pg1342"
