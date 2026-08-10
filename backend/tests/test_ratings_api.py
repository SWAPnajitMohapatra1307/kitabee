"""Tests for the ratings API endpoints.

Endpoints covered:
    POST   /api/v1/books/{content_id}/ratings
    GET    /api/v1/books/{content_id}/ratings/me
    DELETE /api/v1/books/{content_id}/ratings/me
    GET    /api/v1/users/me/ratings

content_id uses gb:/cv:/ia: prefix convention.
_resolve_to_book_uuid is stubbed to avoid DB + external API calls.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from src.auth.dependencies import get_current_user
from src.main import app
import src.api.routes.ratings as ratings_route


_KNOWN_CONTENT_ID = "gb:test123"
_KNOWN_CV_ID = "cv:456"
_KNOWN_IA_ID = "ia:pg1342"
_RESOLVED_UUID = uuid4()


@pytest.fixture
def fake_user():
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        password_hash="hashed",
        avatar_url=None,
        bio=None,
        date_of_birth=None,
        onboarding_completed=False,
        email_verified=False,
        is_active=True,
        is_superuser=False,
        last_login_at=None,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def fake_rating(fake_user):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        user_id=fake_user.id,
        book_id=_RESOLVED_UUID,
        rating=4,
        review_title="Great read",
        review_text="Really enjoyed it.",
        is_spoiler=False,
        helpful_count=0,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stub_resolve(monkeypatch: pytest.MonkeyPatch):
    async def _fake_resolve(content_id, content_router, rating_service):
        return _RESOLVED_UUID
    monkeypatch.setattr(ratings_route, "_resolve_to_book_uuid", _fake_resolve)


def _auth(fake_user):
    app.dependency_overrides[get_current_user] = lambda: fake_user


class TestRateBook:
    def test_create_rating_returns_200(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 4, "review_title": "Great read", "review_text": "Really enjoyed it.", "is_spoiler": False},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["rating"] == 4
        assert body["data"]["review_title"] == "Great read"

    def test_create_rating_minimum_fields(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)
        minimal = SimpleNamespace(**vars(fake_rating))
        minimal.rating = 5
        minimal.review_title = None
        minimal.review_text = None

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return minimal
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 5},
            )

        assert resp.status_code == 200
        assert resp.json()["data"]["rating"] == 5

    def test_create_rating_updates_existing(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)
        updated = SimpleNamespace(**vars(fake_rating))
        updated.rating = 2

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return updated
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 2},
            )

        assert resp.status_code == 200
        assert resp.json()["data"]["rating"] == 2

    def test_create_rating_missing_rating_field(self, fake_user, stub_resolve):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"review_text": "No star given"},
            )

        assert resp.status_code == 422
        assert resp.json()["success"] is False

    def test_create_rating_below_minimum(self, fake_user, stub_resolve):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 0},
            )

        assert resp.status_code == 422

    def test_create_rating_above_maximum(self, fake_user, stub_resolve):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 6},
            )

        assert resp.status_code == 422

    def test_create_rating_requires_auth(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 3},
            )

        assert resp.status_code == 403

    def test_create_rating_envelope_shape(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings",
                json={"rating": 4},
            )

        body = resp.json()
        assert "success" in body
        assert "data" in body
        assert "meta" in body

    def test_cv_content_id_accepted(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_CV_ID}/ratings",
                json={"rating": 4},
            )

        assert resp.status_code == 200

    def test_ia_content_id_accepted(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.post(
                f"/api/v1/books/{_KNOWN_IA_ID}/ratings",
                json={"rating": 3},
            )

        assert resp.status_code == 200


class TestGetMyBookRating:
    def test_returns_rating_when_exists(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 200
        assert resp.json()["data"]["rating"] == 4

    def test_returns_404_when_not_rated(self, fake_user, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return None
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "RATING_NOT_FOUND"

    def test_requires_auth(self):
        with TestClient(app) as client:
            resp = client.get(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 403

    def test_response_has_correct_fields(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        data = resp.json()["data"]
        assert "id" in data
        assert "user_id" in data
        assert "book_id" in data
        assert "rating" in data
        assert "helpful_count" in data
        assert "created_at" in data

    def test_spoiler_flag_returned(self, fake_user, fake_rating, stub_resolve, monkeypatch):
        _auth(fake_user)
        fake_rating.is_spoiler = True

        class StubService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return fake_rating
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.json()["data"]["is_spoiler"] is True


class TestDeleteMyBookRating:
    def test_delete_existing_rating(self, fake_user, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def delete_my_rating(self, *, user_id, book_id):
                return True
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.delete(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 200
        assert resp.json()["data"]["message"] == "Rating deleted successfully."

    def test_delete_nonexistent_rating_returns_404(self, fake_user, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def delete_my_rating(self, *, user_id, book_id):
                return False
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.delete(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "RATING_NOT_FOUND"

    def test_delete_requires_auth(self):
        with TestClient(app) as client:
            resp = client.delete(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        assert resp.status_code == 403

    def test_delete_envelope_shape(self, fake_user, stub_resolve, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def delete_my_rating(self, *, user_id, book_id):
                return True
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.delete(f"/api/v1/books/{_KNOWN_CONTENT_ID}/ratings/me")

        body = resp.json()
        assert body["success"] is True
        assert "meta" in body


class TestGetMyRatings:
    def test_returns_paginated_ratings(self, fake_user, fake_rating, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                return [fake_rating], 1

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["rating"] == 4

    def test_returns_empty_list_when_no_ratings(self, fake_user, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                return [], 0

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings")

        data = resp.json()["data"]
        assert data["total"] == 0
        assert data["results"] == []

    def test_pagination_params_passed(self, fake_user, monkeypatch):
        _auth(fake_user)
        captured = {}

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                captured["limit"] = limit
                captured["offset"] = offset
                return [], 0

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            client.get("/api/v1/users/me/ratings?limit=10&offset=5")

        assert captured["limit"] == 10
        assert captured["offset"] == 5

    def test_default_pagination(self, fake_user, monkeypatch):
        _auth(fake_user)
        captured = {}

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                captured["limit"] = limit
                captured["offset"] = offset
                return [], 0

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            client.get("/api/v1/users/me/ratings")

        assert captured["limit"] == 20
        assert captured["offset"] == 0

    def test_requires_auth(self):
        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings")

        assert resp.status_code == 403

    def test_invalid_limit_rejected(self, fake_user):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings?limit=0")

        assert resp.status_code == 422

    def test_limit_above_max_rejected(self, fake_user):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings?limit=101")

        assert resp.status_code == 422

    def test_negative_offset_rejected(self, fake_user):
        _auth(fake_user)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings?offset=-1")

        assert resp.status_code == 422

    def test_envelope_shape(self, fake_user, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                return [], 0

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings")

        body = resp.json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    def test_response_has_pagination_fields(self, fake_user, monkeypatch):
        _auth(fake_user)

        class StubService:
            def __init__(self, db): pass
            async def get_my_ratings(self, *, user_id, limit, offset):
                return [], 0

        monkeypatch.setattr(ratings_route, "RatingService", StubService)

        with TestClient(app) as client:
            resp = client.get("/api/v1/users/me/ratings")

        data = resp.json()["data"]
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "results" in data
