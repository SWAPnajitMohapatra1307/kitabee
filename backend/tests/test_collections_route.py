"""Tests for GET /api/v1/collections."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

import src.api.routes.collections as collections_route
from src.auth.dependencies import get_current_user
from src.main import app


ENDPOINT = "/api/v1/collections"


def _fake_user() -> MagicMock:
    user = MagicMock()
    user.id = "00000000-0000-0000-0000-000000000001"
    user.is_active = True
    return user


def _fake_rows() -> list[dict[str, Any]]:
    return [
        {
            "id": "dark-000",
            "title": "Shadows of the Mind",
            "mood": "dark",
            "items": ["seed-1", "seed-2"],
            "item_count": 2,
        },
        {
            "id": "special-free",
            "title": "Free to Read Right Now",
            "mood": "educational",
            "items": ["seed-6", "seed-7"],
            "item_count": 2,
        },
    ]


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_service(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    mock.build_home_screen.return_value = _fake_rows()
    monkeypatch.setattr(
        collections_route,
        "CollectionService",
        lambda *a, **kw: mock,
    )
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


@pytest.mark.asyncio
async def test_anonymous_returns_200(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_anonymous_response_shape(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "collections" in body["data"]
    assert "total" in body["data"]
    assert "personalized" in body["data"]


@pytest.mark.asyncio
async def test_anonymous_not_personalized(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    assert response.json()["data"]["personalized"] is False


@pytest.mark.asyncio
async def test_anonymous_collections_is_list(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    data = response.json()["data"]
    assert isinstance(data["collections"], list)


@pytest.mark.asyncio
async def test_anonymous_total_matches_collections_length(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    data = response.json()["data"]
    assert data["total"] == len(data["collections"])


@pytest.mark.asyncio
async def test_authenticated_personalized_flag(
    mock_service: MagicMock,
    mock_get_preferences: AsyncMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_user = _fake_user()

    ratings_mock = AsyncMock(
        return_value=(
            [MagicMock(book_id="seed-1", rating=5)],
            1,
        )
    )
    monkeypatch.setattr(collections_route, "get_ratings_by_user", ratings_mock)
    monkeypatch.setattr(collections_route, "get_by_id", AsyncMock(return_value=fake_user))

    async def fake_optional_user() -> Any:
        return fake_user

    app.dependency_overrides[collections_route._get_optional_user] = fake_optional_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json()["data"]["personalized"] is True

@pytest.mark.asyncio
async def test_n_collections_query_param(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
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
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
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
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT, params={"n_collections": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_row_limit_out_of_range_returns_422(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT, params={"row_limit": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_each_row_has_required_keys(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    rows = response.json()["data"]["collections"]
    required = {"id", "title", "mood", "items", "item_count"}
    for row in rows:
        assert required.issubset(row.keys())


@pytest.mark.asyncio
async def test_service_called_with_catalog(
    mock_service: MagicMock,
    mock_get_ratings: AsyncMock,
    mock_get_preferences: AsyncMock,
    mock_get_by_id: AsyncMock,
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
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
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(ENDPOINT)

    body = response.json()
    assert "meta" in body
    assert "timestamp" in body["meta"]
    assert "version" in body["meta"]