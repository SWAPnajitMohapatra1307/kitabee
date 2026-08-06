import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
import src.api.routes.series as series_route

# Helpers

def _make_gb_item(book_id="gb_001", title="Dune (Book 1)"):
    return {
        "id": book_id,
        "content_id": book_id,
        "title": title,
        "source": "google_books",
    }


def _make_cv_item(issue_id="cv_42", title="Batman #42"):
    return {
        "id": "42",
        "content_id": issue_id,
        "title": title,
        "source": "comic_vine",
        "volume": {"id": "796", "name": "Batman"},
        "issue_number": "42",
    }


# Fixtures

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# Tests — 404

class TestNotFound:
    async def test_invalid_book_returns_404(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return None
        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)

        async with client as c:
            resp = await c.get("/api/v1/books/invalid_id/series")
        assert resp.status_code == 404


# Tests — Not a Series

class TestNotSeries:
    async def test_non_series_book_returns_null_data(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return {
                "content_id": "gb_001",
                "title": "A Brief History of Time",
                "source": "google_books",
            }
        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"] is None


# Tests — Series Found (Google Books)

class TestGoogleBooksSeries:
    async def test_series_returns_200(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series(item, detection):
            return [
                {"content_id": "gb_000", "title": "Dune", "position": 1, "source": "google_books"},
            ]

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        assert resp.status_code == 200

    async def test_series_response_shape(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series(item, detection):
            return [
                {"content_id": "gb_000", "title": "Dune", "position": 1, "source": "google_books"},
            ]

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        body = resp.json()
        assert body["success"] is True
        data = body["data"]
        assert "series_name" in data
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    async def test_items_have_labels(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series(item, detection):
            return [
                {"content_id": "gb_000", "title": "Dune", "position": 1, "source": "google_books"},
            ]

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        items = resp.json()["data"]["items"]
        for item in items:
            assert "label" in item
            assert item["label"] in (
                "You Are Here",
                "Read This First",
                "Read This Next",
                "Coming Up",
                "Also In This Series",
            )

    async def test_you_are_here_present(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series(item, detection):
            return []

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        items = resp.json()["data"]["items"]
        labels = [i["label"] for i in items]
        assert "You Are Here" in labels


# Tests — Series Found (Comic Vine)

class TestComicVineSeries:
    async def test_comic_series_returns_200(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_cv_item()

        async def fake_series(item, detection):
            return [
                {"content_id": "cv_1", "title": "Batman #1", "position": 1, "source": "comic_vine"},
            ]

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/cv_42/series")

        assert resp.status_code == 200

    async def test_comic_series_name(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_cv_item()

        async def fake_series(item, detection):
            return []

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/cv_42/series")

        data = resp.json()["data"]
        assert data["series_name"] == "Batman"


# Tests — Fetch Failure Graceful Degradation

class TestGracefulDegradation:
    async def test_series_fetch_fails_still_returns_current(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series_fail(item, detection):
            return []

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series_fail)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 1
        assert data["items"][0]["label"] == "You Are Here"

    async def test_success_envelope_always_present(self, client, monkeypatch):
        async def fake_fetch(book_id):
            return _make_gb_item()

        async def fake_series(item, detection):
            return []

        monkeypatch.setattr(series_route, "_fetch_item", fake_fetch)
        monkeypatch.setattr(series_route, "_fetch_series_items", fake_series)

        async with client as c:
            resp = await c.get("/api/v1/books/gb_001/series")

        body = resp.json()
        assert "success" in body
        assert "data" in body
        assert "meta" in body