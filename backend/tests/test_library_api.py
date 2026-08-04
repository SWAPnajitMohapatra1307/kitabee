"""Tests for the library API endpoints.

Covers:
    POST   /api/v1/library
    GET    /api/v1/library
    PATCH  /api/v1/library/{book_id}
    DELETE /api/v1/library/{book_id}
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import httpx
from fastapi.testclient import TestClient

from src.auth.dependencies import get_current_user
from src.main import app


# Helpers


def _make_user(**kwargs):
    """Build a fake ORM user for dependency override."""
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
        **kwargs,
    )


def _make_library_item(**kwargs):
    """Build a fake Library ORM object."""
    now = datetime.now(timezone.utc)
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "book_id": uuid4(),
        "status": "want_to_read",
        "current_page": None,
        "total_pages": None,
        "started_reading_at": None,
        "finished_reading_at": None,
        "notes": None,
        "is_favorite": False,
        "added_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# Fixtures


@pytest.fixture(autouse=True)
def clear_overrides():
    """Clear dependency overrides after every test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def fake_user():
    """Return a standard fake authenticated user."""
    return _make_user()


@pytest.fixture()
def client():
    """Return a synchronous test client."""
    return TestClient(app)


# POST /api/v1/library


class TestAddBookToLibrary:
    """Tests for POST /api/v1/library."""

    def test_add_book_returns_201(self, client, fake_user, monkeypatch):
        """Successful add returns 201 with library item data."""
        book_id = uuid4()
        item = _make_library_item(book_id=book_id, user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={"book_id": str(book_id), "status": "want_to_read"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert str(body["data"]["book_id"]) == str(book_id)
        assert body["data"]["status"] == "want_to_read"

    def test_add_book_with_all_fields_returns_201(self, client, fake_user, monkeypatch):
        """Add with all optional fields returns 201."""
        book_id = uuid4()
        item = _make_library_item(
            book_id=book_id,
            user_id=fake_user.id,
            status="currently_reading",
            current_page=42,
            total_pages=300,
            notes="Great book",
            is_favorite=True,
        )

        class StubService:
            async def add_book(self, *, user_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={
                "book_id": str(book_id),
                "status": "currently_reading",
                "current_page": 42,
                "total_pages": 300,
                "notes": "Great book",
                "is_favorite": True,
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["current_page"] == 42
        assert body["data"]["is_favorite"] is True

    def test_add_book_duplicate_returns_409(self, client, fake_user, monkeypatch):
        """Adding a book already in library returns 409."""
        from fastapi import HTTPException, status as http_status

        book_id = uuid4()

        class StubService:
            async def add_book(self, *, user_id, payload):
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail={
                        "code": "ALREADY_IN_LIBRARY",
                        "message": "This book is already in your library.",
                    },
                )

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={"book_id": str(book_id)},
        )

        assert response.status_code == 409
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "ALREADY_IN_LIBRARY"

    def test_add_book_no_auth_returns_403(self, client):
        """Missing auth returns 403."""
        response = client.post(
            "/api/v1/library",
            json={"book_id": str(uuid4())},
        )
        assert response.status_code == 403

    def test_add_book_missing_book_id_returns_422(self, client, fake_user, monkeypatch):
        """Missing book_id in payload returns 422."""
        class StubService:
            async def add_book(self, *, user_id, payload):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post("/api/v1/library", json={})

        assert response.status_code == 422

    def test_add_book_invalid_status_returns_422(self, client, fake_user, monkeypatch):
        """Invalid status value returns 422."""
        class StubService:
            async def add_book(self, *, user_id, payload):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={"book_id": str(uuid4()), "status": "invalid_status"},
        )

        assert response.status_code == 422

    def test_add_book_negative_current_page_returns_422(self, client, fake_user, monkeypatch):
        """Negative current_page returns 422."""
        class StubService:
            async def add_book(self, *, user_id, payload):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={"book_id": str(uuid4()), "current_page": -1},
        )

        assert response.status_code == 422

    def test_add_book_response_has_envelope(self, client, fake_user, monkeypatch):
        """Response follows success envelope shape."""
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.post(
            "/api/v1/library",
            json={"book_id": str(uuid4())},
        )

        body = response.json()
        assert "success" in body
        assert "data" in body
        assert "meta" in body


# GET /api/v1/library


class TestGetMyLibrary:
    """Tests for GET /api/v1/library."""

    def test_get_library_returns_200(self, client, fake_user, monkeypatch):
        """Returns 200 with paginated library."""
        items = [_make_library_item(user_id=fake_user.id) for _ in range(3)]

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return items, 3

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 3
        assert len(body["data"]["results"]) == 3

    def test_get_library_empty_returns_200(self, client, fake_user, monkeypatch):
        """Empty library returns 200 with zero results."""
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] == 0
        assert body["data"]["results"] == []

    def test_get_library_with_status_filter(self, client, fake_user, monkeypatch):
        """Status query param is passed to service."""
        received = {}

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                received["status"] = status
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library?status=read")

        assert response.status_code == 200
        assert received["status"].value == "read"

    def test_get_library_pagination_params(self, client, fake_user, monkeypatch):
        """Limit and offset are forwarded to service."""
        received = {}

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                received["limit"] = limit
                received["offset"] = offset
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        client.get("/api/v1/library?limit=10&offset=5")

        assert received["limit"] == 10
        assert received["offset"] == 5

    def test_get_library_no_auth_returns_403(self, client):
        """Missing auth returns 403."""
        response = client.get("/api/v1/library")
        assert response.status_code == 403

    def test_get_library_invalid_limit_returns_422(self, client, fake_user, monkeypatch):
        """limit=0 returns 422."""
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library?limit=0")
        assert response.status_code == 422

    def test_get_library_invalid_offset_returns_422(self, client, fake_user, monkeypatch):
        """Negative offset returns 422."""
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library?offset=-1")
        assert response.status_code == 422

    def test_get_library_response_has_envelope(self, client, fake_user, monkeypatch):
        """Response follows success envelope shape."""
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.get("/api/v1/library")
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body
        assert "total" in body["data"]
        assert "results" in body["data"]


# PATCH /api/v1/library/{book_id}


class TestUpdateLibraryEntry:
    """Tests for PATCH /api/v1/library/{book_id}."""

    def test_update_entry_returns_200(self, client, fake_user, monkeypatch):
        """Successful update returns 200 with updated item."""
        book_id = uuid4()
        item = _make_library_item(
            book_id=book_id,
            user_id=fake_user.id,
            status="currently_reading",
            current_page=50,
        )

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(
            f"/api/v1/library/{book_id}",
            json={"status": "currently_reading", "current_page": 50},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "currently_reading"
        assert body["data"]["current_page"] == 50

    def test_update_entry_not_found_returns_404(self, client, fake_user, monkeypatch):
        """Updating a book not in library returns 404."""
        from fastapi import HTTPException, status as http_status

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "LIBRARY_ITEM_NOT_FOUND",
                        "message": "This book is not in your library.",
                    },
                )

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(
            f"/api/v1/library/{uuid4()}",
            json={"status": "read"},
        )

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "LIBRARY_ITEM_NOT_FOUND"

    def test_update_entry_no_auth_returns_403(self, client):
        """Missing auth returns 403."""
        response = client.patch(
            f"/api/v1/library/{uuid4()}",
            json={"status": "read"},
        )
        assert response.status_code == 403

    def test_update_entry_invalid_status_returns_422(self, client, fake_user, monkeypatch):
        """Invalid status value returns 422."""
        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(
            f"/api/v1/library/{uuid4()}",
            json={"status": "bad_value"},
        )

        assert response.status_code == 422

    def test_update_entry_empty_body_returns_200(self, client, fake_user, monkeypatch):
        """Empty body is valid — service returns unchanged item."""
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(f"/api/v1/library/{uuid4()}", json={})

        assert response.status_code == 200

    def test_update_entry_is_favorite_flag(self, client, fake_user, monkeypatch):
        """is_favorite field is accepted and returned."""
        item = _make_library_item(user_id=fake_user.id, is_favorite=True)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(
            f"/api/v1/library/{uuid4()}",
            json={"is_favorite": True},
        )

        assert response.status_code == 200
        assert response.json()["data"]["is_favorite"] is True

    def test_update_entry_response_has_envelope(self, client, fake_user, monkeypatch):
        """Response follows success envelope shape."""
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.patch(f"/api/v1/library/{uuid4()}", json={})
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body


# DELETE /api/v1/library/{book_id}


class TestRemoveBookFromLibrary:
    """Tests for DELETE /api/v1/library/{book_id}."""

    def test_remove_book_returns_200(self, client, fake_user, monkeypatch):
        """Successful removal returns 200 with message."""
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.delete(f"/api/v1/library/{uuid4()}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["message"] == "Book removed from library successfully."

    def test_remove_book_not_found_returns_404(self, client, fake_user, monkeypatch):
        """Removing a book not in library returns 404."""
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return False

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.delete(f"/api/v1/library/{uuid4()}")

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "LIBRARY_ITEM_NOT_FOUND"

    def test_remove_book_no_auth_returns_403(self, client):
        """Missing auth returns 403."""
        response = client.delete(f"/api/v1/library/{uuid4()}")
        assert response.status_code == 403

    def test_remove_book_response_has_envelope(self, client, fake_user, monkeypatch):
        """Response follows success envelope shape."""
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.delete(f"/api/v1/library/{uuid4()}")
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body

    def test_remove_book_invalid_uuid_returns_422(self, client, fake_user, monkeypatch):
        """Non-UUID book_id in path returns 422."""
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(
            "src.api.routes.library.LibraryService", lambda db: StubService()
        )

        response = client.delete("/api/v1/library/not-a-uuid")
        assert response.status_code == 422
