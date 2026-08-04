from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException, status

from src.auth.dependencies import get_current_user
from src.main import app


def _make_user(**kwargs):
    now = datetime.now(timezone.utc)
    defaults = {
        "id": uuid4(),
        "email": "test@example.com",
        "name": "Test User",
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
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_preferences(**kwargs):
    now = datetime.now(timezone.utc)
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "favorite_genres": [],
        "preferred_languages": ["en"],
        "excluded_genres": [],
        "content_warnings_hide": [],
        "reading_pace": "medium",
        "preferred_book_length": "any",
        "theme": "system",
        "notification_settings": {"email": False, "push": False},
        "privacy_settings": {"public_library": False, "public_ratings": False},
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_my_preferences_requires_auth():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me/preferences")

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_get_my_preferences_returns_preferences(monkeypatch):
    fake_user = _make_user()
    fake_prefs = _make_preferences(
        user_id=fake_user.id,
        favorite_genres=["fantasy", "mystery"],
        theme="dark",
    )

    class StubPreferencesService:
        async def get_my_preferences(self, *, user_id):
            assert user_id == fake_user.id
            return fake_prefs

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: StubPreferencesService(),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me/preferences")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user_id"] == str(fake_user.id)
    assert body["data"]["favorite_genres"] == ["fantasy", "mystery"]
    assert body["data"]["theme"] == "dark"


@pytest.mark.asyncio
async def test_get_my_preferences_returns_404_when_missing(monkeypatch):
    fake_user = _make_user()

    class StubPreferencesService:
        async def get_my_preferences(self, *, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PREFERENCES_NOT_FOUND",
                    "message": "Preferences not found for this user.",
                },
            )

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: StubPreferencesService(),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me/preferences")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PREFERENCES_NOT_FOUND"


@pytest.mark.asyncio
async def test_put_my_preferences_requires_auth():
    payload = {
        "favorite_genres": ["fantasy"],
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/users/me/preferences", json=payload)

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_put_my_preferences_replaces_preferences(monkeypatch):
    fake_user = _make_user()

    class StubPreferencesService:
        async def upsert_my_preferences(self, *, user_id, payload):
            assert user_id == fake_user.id
            return _make_preferences(
                user_id=user_id,
                **payload.model_dump(),
            )

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: StubPreferencesService(),
    )

    payload = {
        "favorite_genres": ["fantasy", "sci-fi"],
        "preferred_languages": ["en", "hi"],
        "excluded_genres": ["horror"],
        "content_warnings_hide": ["violence"],
        "reading_pace": "fast",
        "preferred_book_length": "long",
        "theme": "dark",
        "notification_settings": {
            "email": True,
            "push": False,
        },
        "privacy_settings": {
            "public_library": True,
            "public_ratings": False,
        },
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/users/me/preferences", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user_id"] == str(fake_user.id)
    assert body["data"]["favorite_genres"] == ["fantasy", "sci-fi"]
    assert body["data"]["preferred_languages"] == ["en", "hi"]
    assert body["data"]["excluded_genres"] == ["horror"]
    assert body["data"]["content_warnings_hide"] == ["violence"]
    assert body["data"]["reading_pace"] == "fast"
    assert body["data"]["preferred_book_length"] == "long"
    assert body["data"]["theme"] == "dark"
    assert body["data"]["notification_settings"] == {
        "email": True,
        "push": False,
    }
    assert body["data"]["privacy_settings"] == {
        "public_library": True,
        "public_ratings": False,
    }


@pytest.mark.asyncio
async def test_put_my_preferences_uses_defaults_for_omitted_fields(monkeypatch):
    fake_user = _make_user()

    class StubPreferencesService:
        async def upsert_my_preferences(self, *, user_id, payload):
            return _make_preferences(
                user_id=user_id,
                **payload.model_dump(),
            )

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: StubPreferencesService(),
    )

    payload = {
        "favorite_genres": ["fantasy"],
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/users/me/preferences", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["favorite_genres"] == ["fantasy"]
    assert body["data"]["preferred_languages"] == ["en"]
    assert body["data"]["excluded_genres"] == []
    assert body["data"]["content_warnings_hide"] == []
    assert body["data"]["reading_pace"] == "medium"
    assert body["data"]["preferred_book_length"] == "any"
    assert body["data"]["theme"] == "system"
    assert body["data"]["notification_settings"] == {
        "email": False,
        "push": False,
    }
    assert body["data"]["privacy_settings"] == {
        "public_library": False,
        "public_ratings": False,
    }


@pytest.mark.asyncio
async def test_put_my_preferences_rejects_invalid_theme(monkeypatch):
    fake_user = _make_user()
    app.dependency_overrides[get_current_user] = lambda: fake_user

    payload = {
        "theme": "blue",
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/users/me/preferences", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_put_my_preferences_rejects_invalid_reading_pace(monkeypatch):
    fake_user = _make_user()
    app.dependency_overrides[get_current_user] = lambda: fake_user

    payload = {
        "reading_pace": "turbo",
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/users/me/preferences", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_post_complete_onboarding_requires_auth():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/users/me/preferences/complete")

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_post_complete_onboarding_marks_user_complete(monkeypatch):
    fake_user = _make_user(onboarding_completed=False)

    class StubPreferencesService:
        def __init__(self):
            self.called_user = None

        async def complete_onboarding(self, *, user):
            self.called_user = user
            return _make_user(id=user.id, onboarding_completed=True)

    stub = StubPreferencesService()

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: stub,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/users/me/preferences/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["message"] == "Onboarding marked as complete."
    assert stub.called_user.id == fake_user.id


@pytest.mark.asyncio
async def test_post_complete_onboarding_is_idempotent(monkeypatch):
    fake_user = _make_user(onboarding_completed=True)

    class StubPreferencesService:
        async def complete_onboarding(self, *, user):
            assert user.id == fake_user.id
            return user

    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.preferences.PreferencesService",
        lambda db: StubPreferencesService(),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/users/me/preferences/complete")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["message"] == "Onboarding marked as complete."