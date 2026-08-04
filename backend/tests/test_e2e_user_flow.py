"""End-to-end scenario tests — full user flow.

Tests the complete happy path from registration through account deletion.
Each test in the class shares state via class-level variables so the flow
is sequential: register → login → profile → ratings → library →
preferences → onboarding → delete.

No live database or Redis. All service and crud layers are stubbed via
dependency_overrides and monkeypatch, matching patterns established in
Days 8-13.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
import httpx
from httpx import ASGITransport

from src.main import app
from src.auth.dependencies import get_current_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)
_USER_ID = uuid.uuid4()
_BOOK_ID = uuid.uuid4()
_TOKEN = "e2e-test-token"


def _make_user(**kwargs: Any) -> SimpleNamespace:
    defaults: dict[str, Any] = {
        "id": _USER_ID,
        "email": "e2e@example.com",
        "name": "E2E User",
        "password_hash": "hashed",
        "avatar_url": None,
        "bio": None,
        "date_of_birth": None,
        "onboarding_completed": False,
        "email_verified": False,
        "is_active": True,
        "is_superuser": False,
        "last_login_at": None,
        "deleted_at": None,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_token_pair() -> dict[str, str]:
    return {
        "access_token": _TOKEN,
        "refresh_token": "e2e-refresh-token",
        "token_type": "bearer",
    }


def _make_rating(**kwargs: Any) -> SimpleNamespace:
    defaults: dict[str, Any] = {
        "id": uuid.uuid4(),
        "user_id": _USER_ID,
        "book_id": _BOOK_ID,
        "rating": 4,
        "review_title": "Great book",
        "review_text": "Really enjoyed it.",
        "is_spoiler": False,
        "helpful_count": 0,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_library_item(**kwargs: Any) -> SimpleNamespace:
    defaults: dict[str, Any] = {
        "id": uuid.uuid4(),
        "user_id": _USER_ID,
        "book_id": _BOOK_ID,
        "status": "want_to_read",
        "current_page": None,
        "total_pages": None,
        "started_reading_at": None,
        "finished_reading_at": None,
        "notes": None,
        "is_favorite": False,
        "added_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_preferences(**kwargs: Any) -> SimpleNamespace:
    defaults: dict[str, Any] = {
        "id": uuid.uuid4(),
        "user_id": _USER_ID,
        "favorite_genres": ["Fantasy", "Sci-Fi"],
        "preferred_languages": ["en"],
        "excluded_genres": [],
        "content_warnings_hide": [],
        "reading_pace": "medium",
        "preferred_book_length": "any",
        "theme": "dark",
        "notification_settings": {"email": True, "push": False},
        "privacy_settings": {"public_library": False, "public_ratings": True},
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


@pytest.fixture
def auth_user():
    return _make_user()


@pytest.fixture
def authed_client(auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    return httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


# ---------------------------------------------------------------------------
# Step 1 — Register
# ---------------------------------------------------------------------------

class TestE2ERegister:
    async def test_register_returns_201_with_user(self, client, monkeypatch):
        fake_user = _make_user()

        class StubUserService:
            def __init__(self, db): pass
            async def create_user(self, payload, admin_key):
                return fake_user

        monkeypatch.setattr("src.api.routes.auth.UserService", StubUserService)

        async with client as c:
            resp = await c.post(
                "/api/v1/auth/register",
                json={
                    "email": "e2e@example.com",
                    "password": "SecurePass123!",
                    "name": "E2E User",
                },
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "e2e@example.com"


# ---------------------------------------------------------------------------
# Step 2 — Login
# ---------------------------------------------------------------------------

class TestE2ELogin:
    async def test_login_returns_tokens(self, client, monkeypatch):
        fake_user = _make_user()

        class StubUserService:
            def __init__(self, db): pass
            async def authenticate_user(self, email, password):
                return fake_user

        monkeypatch.setattr("src.api.routes.auth.UserService", StubUserService)
        monkeypatch.setattr(
            "src.api.routes.auth.create_access_token",
            lambda user_id: _TOKEN,
        )
        monkeypatch.setattr(
            "src.api.routes.auth.create_refresh_token",
            lambda user_id: "e2e-refresh-token",
        )

        async with client as c:
            resp = await c.post(
                "/api/v1/auth/login",
                json={"email": "e2e@example.com", "password": "SecurePass123!"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"


# ---------------------------------------------------------------------------
# Step 3 — Get profile
# ---------------------------------------------------------------------------

class TestE2EGetProfile:
    async def test_get_profile_returns_user(self, authed_client):
        async with authed_client as c:
            resp = await c.get("/api/v1/users/me")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "e2e@example.com"

    async def test_get_profile_unauthed_returns_403(self, client):
        async with client as c:
            resp = await c.get("/api/v1/users/me")

        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Step 4 — Update profile
# ---------------------------------------------------------------------------

class TestE2EUpdateProfile:
    async def test_update_profile_returns_updated_user(
        self, authed_client, monkeypatch
    ):
        updated = _make_user(name="E2E Updated", bio="I read a lot.")

        class StubUserService:
            def __init__(self, db): pass
            async def update_profile(self, user, payload):
                return updated

        monkeypatch.setattr("src.api.routes.users.UserService", StubUserService)

        async with authed_client as c:
            resp = await c.patch(
                "/api/v1/users/me",
                json={"name": "E2E Updated", "bio": "I read a lot."},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["name"] == "E2E Updated"
        assert body["data"]["bio"] == "I read a lot."


# ---------------------------------------------------------------------------
# Step 5 — Rate a book
# ---------------------------------------------------------------------------

class TestE2ERateBook:
    async def test_rate_book_returns_rating(self, authed_client, monkeypatch):
        fake_rating = _make_rating()

        class StubRatingService:
            def __init__(self, db): pass
            async def rate_book(self, *, user_id, book_id, payload):
                return fake_rating

        monkeypatch.setattr(
            "src.api.routes.ratings.RatingService", StubRatingService
        )

        async with authed_client as c:
            resp = await c.post(
                f"/api/v1/books/{_BOOK_ID}/ratings",
                json={
                    "rating": 4,
                    "review_title": "Great book",
                    "review_text": "Really enjoyed it.",
                    "is_spoiler": False,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["rating"] == 4
        assert body["data"]["review_title"] == "Great book"


# ---------------------------------------------------------------------------
# Step 6 — Get my rating
# ---------------------------------------------------------------------------

class TestE2EGetMyRating:
    async def test_get_my_rating_returns_rating(self, authed_client, monkeypatch):
        fake_rating = _make_rating()

        class StubRatingService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return fake_rating

        monkeypatch.setattr(
            "src.api.routes.ratings.RatingService", StubRatingService
        )

        async with authed_client as c:
            resp = await c.get(f"/api/v1/books/{_BOOK_ID}/ratings/me")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["rating"] == 4

    async def test_get_my_rating_not_found_returns_404(
        self, authed_client, monkeypatch
    ):
        class StubRatingService:
            def __init__(self, db): pass
            async def get_my_rating(self, *, user_id, book_id):
                return None

        monkeypatch.setattr(
            "src.api.routes.ratings.RatingService", StubRatingService
        )

        async with authed_client as c:
            resp = await c.get(f"/api/v1/books/{_BOOK_ID}/ratings/me")

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Step 7 — Add book to library
# ---------------------------------------------------------------------------

class TestE2EAddToLibrary:
    async def test_add_book_returns_201(self, authed_client, monkeypatch):
        fake_item = _make_library_item()

        class StubLibraryService:
            def __init__(self, db): pass
            async def add_book(self, *, user_id, payload):
                return fake_item

        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", StubLibraryService
        )

        async with authed_client as c:
            resp = await c.post(
                "/api/v1/library",
                json={"book_id": str(_BOOK_ID), "status": "want_to_read"},
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["status"] == "want_to_read"

    async def test_add_duplicate_book_returns_409(self, authed_client, monkeypatch):
        from fastapi import HTTPException

        class StubLibraryService:
            def __init__(self, db): pass
            async def add_book(self, *, user_id, payload):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "ALREADY_IN_LIBRARY",
                        "message": "Already in library.",
                    },
                )

        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", StubLibraryService
        )

        async with authed_client as c:
            resp = await c.post(
                "/api/v1/library",
                json={"book_id": str(_BOOK_ID), "status": "want_to_read"},
            )

        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Step 8 — Get library
# ---------------------------------------------------------------------------

class TestE2EGetLibrary:
    async def test_get_library_returns_results(self, authed_client, monkeypatch):
        fake_item = _make_library_item()

        class StubLibraryService:
            def __init__(self, db): pass
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [fake_item], 1

        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", StubLibraryService
        )

        async with authed_client as c:
            resp = await c.get("/api/v1/library")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] == 1
        assert len(body["data"]["results"]) == 1


# ---------------------------------------------------------------------------
# Step 9 — Set preferences
# ---------------------------------------------------------------------------

class TestE2ESetPreferences:
    async def test_put_preferences_returns_preferences(
        self, authed_client, monkeypatch
    ):
        fake_prefs = _make_preferences()

        class StubPreferencesService:
            def __init__(self, db): pass
            async def upsert_my_preferences(self, *, user_id, payload):
                return fake_prefs

        monkeypatch.setattr(
            "src.api.routes.preferences.PreferencesService",
            StubPreferencesService,
        )

        async with authed_client as c:
            resp = await c.put(
                "/api/v1/users/me/preferences",
                json={
                    "favorite_genres": ["Fantasy", "Sci-Fi"],
                    "theme": "dark",
                    "notification_settings": {"email": True, "push": False},
                    "privacy_settings": {
                        "public_library": False,
                        "public_ratings": True,
                    },
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["theme"] == "dark"
        assert "Fantasy" in body["data"]["favorite_genres"]


# ---------------------------------------------------------------------------
# Step 10 — Get preferences
# ---------------------------------------------------------------------------

class TestE2EGetPreferences:
    async def test_get_preferences_returns_preferences(
        self, authed_client, monkeypatch
    ):
        fake_prefs = _make_preferences()

        class StubPreferencesService:
            def __init__(self, db): pass
            async def get_my_preferences(self, *, user_id):
                return fake_prefs

        monkeypatch.setattr(
            "src.api.routes.preferences.PreferencesService",
            StubPreferencesService,
        )

        async with authed_client as c:
            resp = await c.get("/api/v1/users/me/preferences")

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["reading_pace"] == "medium"

    async def test_get_preferences_not_set_returns_404(
        self, authed_client, monkeypatch
    ):
        from fastapi import HTTPException

        class StubPreferencesService:
            def __init__(self, db): pass
            async def get_my_preferences(self, *, user_id):
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "PREFERENCES_NOT_FOUND",
                        "message": "Preferences not found.",
                    },
                )

        monkeypatch.setattr(
            "src.api.routes.preferences.PreferencesService",
            StubPreferencesService,
        )

        async with authed_client as c:
            resp = await c.get("/api/v1/users/me/preferences")

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Step 11 — Complete onboarding
# ---------------------------------------------------------------------------

class TestE2ECompleteOnboarding:
    async def test_complete_onboarding_returns_message(
        self, authed_client, monkeypatch
    ):
        completed_user = _make_user(onboarding_completed=True)

        class StubPreferencesService:
            def __init__(self, db): pass
            async def complete_onboarding(self, *, user):
                return completed_user

        monkeypatch.setattr(
            "src.api.routes.preferences.PreferencesService",
            StubPreferencesService,
        )

        async with authed_client as c:
            resp = await c.post("/api/v1/users/me/preferences/complete")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "onboarding" in body["data"]["message"].lower()

    async def test_complete_onboarding_idempotent(self, authed_client, monkeypatch):
        already_done = _make_user(onboarding_completed=True)

        class StubPreferencesService:
            def __init__(self, db): pass
            async def complete_onboarding(self, *, user):
                return already_done

        monkeypatch.setattr(
            "src.api.routes.preferences.PreferencesService",
            StubPreferencesService,
        )

        async with authed_client as c:
            resp1 = await c.post("/api/v1/users/me/preferences/complete")
            resp2 = await c.post("/api/v1/users/me/preferences/complete")

        assert resp1.status_code == 200
        assert resp2.status_code == 200


# ---------------------------------------------------------------------------
# Step 12 — Delete account
# ---------------------------------------------------------------------------

class TestE2EDeleteAccount:
    async def test_delete_account_returns_200_message(
        self, authed_client, monkeypatch
    ):
        deleted_user = _make_user(deleted_at=_NOW)

        async def fake_soft_delete(db, user):
            return deleted_user

        monkeypatch.setattr(
            "src.api.routes.users.soft_delete_user",
            fake_soft_delete,
        )

        async with authed_client as c:
            resp = await c.delete("/api/v1/users/me")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "deleted" in body["data"]["message"].lower()

    async def test_delete_account_unauthed_returns_403(self, client):
        async with client as c:
            resp = await c.delete("/api/v1/users/me")

        assert resp.status_code == 403