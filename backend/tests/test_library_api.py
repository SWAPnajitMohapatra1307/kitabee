"""Tests for the library API endpoints.

Covers:
    POST   /api/v1/library
    GET    /api/v1/library
    PATCH  /api/v1/library/{content_id}
    DELETE /api/v1/library/{content_id}

content_id uses gb:/cv:/ia: prefix convention.
_resolve_content_id_to_uuid is stubbed for PATCH/DELETE tests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from src.auth.dependencies import get_current_user
from src.api.deps import get_content_router
from src.main import app
import src.api.routes.library as library_route


_KNOWN_CONTENT_ID = "gb:test123"
_KNOWN_CV_ID = "cv:456"
_KNOWN_IA_ID = "ia:pg1342"
_RESOLVED_UUID = uuid4()


def _make_user(**kwargs):
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
    now = datetime.now(timezone.utc)
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "book_id": _RESOLVED_UUID,
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


class StubContentRouter:
    async def search(self, query, limit, sources=None):
        return []
    async def get_by_content_id(self, content_id):
        return None
    async def get_similar(self, content_id, limit):
        return []


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def fake_user():
    return _make_user()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def stub_router():
    return StubContentRouter()


@pytest.fixture()
def stub_resolve(monkeypatch: pytest.MonkeyPatch):
    async def _fake(content_id, service, content_router):
        return _RESOLVED_UUID
    monkeypatch.setattr(library_route, "_resolve_content_id_to_uuid", _fake)


class TestAddBookToLibrary:
    def test_add_book_returns_201(self, client, fake_user, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID, "status": "want_to_read"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "want_to_read"

    def test_add_book_with_all_fields_returns_201(self, client, fake_user, stub_router, monkeypatch):
        item = _make_library_item(
            user_id=fake_user.id,
            status="currently_reading",
            current_page=42,
            total_pages=300,
            notes="Great book",
            is_favorite=True,
        )

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={
                "content_id": _KNOWN_CONTENT_ID,
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

    def test_add_book_duplicate_returns_409(self, client, fake_user, stub_router, monkeypatch):
        from fastapi import HTTPException, status as http_status

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail={
                        "code": "ALREADY_IN_LIBRARY",
                        "message": "This book is already in your library.",
                    },
                )
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID},
        )

        assert response.status_code == 409
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "ALREADY_IN_LIBRARY"

    def test_add_book_no_auth_returns_403(self, client):
        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID},
        )
        assert response.status_code == 403

    def test_add_book_missing_content_id_returns_422(self, client, fake_user, stub_router, monkeypatch):
        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post("/api/v1/library", json={})

        assert response.status_code == 422

    def test_add_book_invalid_status_returns_422(self, client, fake_user, stub_router, monkeypatch):
        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID, "status": "invalid_status"},
        )

        assert response.status_code == 422

    def test_add_book_negative_current_page_returns_422(self, client, fake_user, stub_router, monkeypatch):
        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                pass

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID, "current_page": -1},
        )

        assert response.status_code == 422

    def test_add_book_response_has_envelope(self, client, fake_user, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CONTENT_ID},
        )

        body = response.json()
        assert "success" in body
        assert "data" in body
        assert "meta" in body

    def test_cv_content_id_accepted(self, client, fake_user, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_CV_ID},
        )

        assert response.status_code == 201

    def test_ia_content_id_accepted(self, client, fake_user, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def add_book(self, *, user_id, payload, content_router):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.post(
            "/api/v1/library",
            json={"content_id": _KNOWN_IA_ID},
        )

        assert response.status_code == 201


class TestGetMyLibrary:
    def test_get_library_returns_200(self, client, fake_user, monkeypatch):
        items = [_make_library_item(user_id=fake_user.id) for _ in range(3)]

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return items, 3

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 3
        assert len(body["data"]["results"]) == 3

    def test_get_library_empty_returns_200(self, client, fake_user, monkeypatch):
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] == 0
        assert body["data"]["results"] == []

    def test_get_library_with_status_filter(self, client, fake_user, monkeypatch):
        received = {}

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                received["status"] = status
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library?status=read")

        assert response.status_code == 200
        assert received["status"].value == "read"

    def test_get_library_pagination_params(self, client, fake_user, monkeypatch):
        received = {}

        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                received["limit"] = limit
                received["offset"] = offset
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        client.get("/api/v1/library?limit=10&offset=5")

        assert received["limit"] == 10
        assert received["offset"] == 5

    def test_get_library_no_auth_returns_403(self, client):
        response = client.get("/api/v1/library")
        assert response.status_code == 403

    def test_get_library_invalid_limit_returns_422(self, client, fake_user, monkeypatch):
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library?limit=0")
        assert response.status_code == 422

    def test_get_library_invalid_offset_returns_422(self, client, fake_user, monkeypatch):
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library?offset=-1")
        assert response.status_code == 422

    def test_get_library_response_has_envelope(self, client, fake_user, monkeypatch):
        class StubService:
            async def get_my_library(self, *, user_id, status, limit, offset):
                return [], 0

        app.dependency_overrides[get_current_user] = lambda: fake_user
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.get("/api/v1/library")
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body
        assert "total" in body["data"]
        assert "results" in body["data"]


class TestUpdateLibraryEntry:
    def test_update_entry_returns_200(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        item = _make_library_item(
            user_id=fake_user.id,
            status="currently_reading",
            current_page=50,
        )

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(
            f"/api/v1/library/{_KNOWN_CONTENT_ID}",
            json={"status": "currently_reading", "current_page": 50},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "currently_reading"
        assert body["data"]["current_page"] == 50

    def test_update_entry_not_found_returns_404(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
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
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(
            f"/api/v1/library/{_KNOWN_CONTENT_ID}",
            json={"status": "read"},
        )

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "LIBRARY_ITEM_NOT_FOUND"

    def test_update_entry_no_auth_returns_403(self, client):
        response = client.patch(
            f"/api/v1/library/{_KNOWN_CONTENT_ID}",
            json={"status": "read"},
        )
        assert response.status_code == 403

    def test_update_entry_invalid_status_returns_422(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                pass
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(
            f"/api/v1/library/{_KNOWN_CONTENT_ID}",
            json={"status": "bad_value"},
        )

        assert response.status_code == 422

    def test_update_entry_empty_body_returns_200(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(f"/api/v1/library/{_KNOWN_CONTENT_ID}", json={})

        assert response.status_code == 200

    def test_update_entry_is_favorite_flag(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id, is_favorite=True)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(
            f"/api/v1/library/{_KNOWN_CONTENT_ID}",
            json={"is_favorite": True},
        )

        assert response.status_code == 200
        assert response.json()["data"]["is_favorite"] is True

    def test_update_entry_response_has_envelope(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        item = _make_library_item(user_id=fake_user.id)

        class StubService:
            async def update_entry(self, *, user_id, book_id, payload):
                return item
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.patch(f"/api/v1/library/{_KNOWN_CONTENT_ID}", json={})
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body


class TestRemoveBookFromLibrary:
    def test_remove_book_returns_200(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.delete(f"/api/v1/library/{_KNOWN_CONTENT_ID}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["message"] == "Item removed from library successfully."

    def test_remove_book_not_found_returns_404(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return False
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.delete(f"/api/v1/library/{_KNOWN_CONTENT_ID}")

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "LIBRARY_ITEM_NOT_FOUND"

    def test_remove_book_no_auth_returns_403(self, client):
        response = client.delete(f"/api/v1/library/{_KNOWN_CONTENT_ID}")
        assert response.status_code == 403

    def test_remove_book_response_has_envelope(self, client, fake_user, stub_resolve, stub_router, monkeypatch):
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True
            async def resolve_content_id(self, content_id):
                return _RESOLVED_UUID

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.delete(f"/api/v1/library/{_KNOWN_CONTENT_ID}")
        body = response.json()

        assert "success" in body
        assert "data" in body
        assert "meta" in body

    def test_remove_book_invalid_prefix_returns_400(self, client, fake_user, stub_router, monkeypatch):
        class StubService:
            async def remove_book(self, *, user_id, book_id):
                return True
            async def resolve_content_id(self, content_id):
                return None

        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_content_router] = lambda: stub_router
        monkeypatch.setattr(library_route, "LibraryService", lambda db: StubService())

        response = client.delete("/api/v1/library/xx:badprefix")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_CONTENT_ID"
