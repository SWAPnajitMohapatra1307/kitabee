"""Integration tests for user profile API endpoints.

Tests GET    /api/v1/users/me
      PATCH  /api/v1/users/me
      DELETE /api/v1/users/me
      PATCH  /api/v1/users/me/password

UserService is stubbed via monkeypatch so no real DB or bcrypt calls
are made. get_current_user is overridden via dependency_overrides so
no real JWT verification occurs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, AsyncIterator, Optional
from uuid import uuid4

import httpx
import pytest
from httpx import ASGITransport

from src.auth.dependencies import get_current_user
from src.main import app


# Constants

ME_URL = "/api/v1/users/me"
PASSWORD_URL = "/api/v1/users/me/password"


# Helpers

def _make_user(
    *,
    is_active: bool = True,
    is_superuser: bool = False,
) -> Any:
    """Build a fake user object using SimpleNamespace.

    Avoids SQLAlchemy ORM attribute machinery. UserResponse.model_validate
    reads plain attributes so SimpleNamespace works correctly.
    """
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
        is_active=is_active,
        is_superuser=is_superuser,
        last_login_at=None,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )


# Stub

class StubUserService:
    """Configurable stand-in for UserService.

    Controls what update_profile and change_password do.
    """

    def __init__(self) -> None:
        self.update_profile_return: Optional[Any] = None
        self.change_password_raise: Optional[str] = None

    async def update_profile(self, user: Any, payload: Any) -> Any:
        """Stub update_profile — returns configured value."""
        if self.update_profile_return is not None:
            return self.update_profile_return
        return user

    async def change_password(
        self,
        user: Any,
        current_password: str,
        new_password: str,
    ) -> None:
        """Stub change_password — raises or returns None."""
        if self.change_password_raise is not None:
            raise ValueError(self.change_password_raise)


# Fixtures

@pytest.fixture
def fake_user() -> Any:
    """Reusable fake active normal user."""
    return _make_user()


@pytest.fixture
def stub_service() -> StubUserService:
    """Fresh stub for each test."""
    return StubUserService()


@pytest.fixture
async def app_client(
    fake_user: Any,
    stub_service: StubUserService,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx AsyncClient with auth and UserService stubbed.

    get_current_user is overridden via dependency_overrides to return
    the fake user without JWT verification.
    UserService is monkeypatched so no DB calls occur.
    """
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr(
        "src.api.routes.users.UserService",
        lambda db: stub_service,
    )

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# GET /api/v1/users/me

class TestGetMe:
    """Tests for GET /api/v1/users/me."""

    async def test_returns_200(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.get(ME_URL)
        assert response.status_code == 200

    async def test_success_envelope_shape(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        body = (await app_client.get(ME_URL)).json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_data_contains_user_fields(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (await app_client.get(ME_URL)).json()["data"]
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "onboarding_completed" in data
        assert "email_verified" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_password_not_in_response(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (await app_client.get(ME_URL)).json()["data"]
        assert "password_hash" not in data
        assert "password" not in data

    async def test_is_superuser_not_in_response(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (await app_client.get(ME_URL)).json()["data"]
        assert "is_superuser" not in data

    async def test_returns_correct_email(
        self,
        app_client: httpx.AsyncClient,
        fake_user: Any,
    ) -> None:
        data = (await app_client.get(ME_URL)).json()["data"]
        assert data["email"] == fake_user.email

    async def test_returns_correct_name(
        self,
        app_client: httpx.AsyncClient,
        fake_user: Any,
    ) -> None:
        data = (await app_client.get(ME_URL)).json()["data"]
        assert data["name"] == fake_user.name

    async def test_unauthenticated_returns_403(self) -> None:
        # No dependency override — real get_current_user runs, no token present.
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(ME_URL)
        assert response.status_code == 403


# PATCH /api/v1/users/me

class TestUpdateMe:
    """Tests for PATCH /api/v1/users/me."""

    async def test_returns_200(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(ME_URL, json={"name": "New Name"})
        assert response.status_code == 200

    async def test_success_envelope_shape(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        body = (await app_client.patch(ME_URL, json={"name": "New Name"})).json()
        assert body["success"] is True
        assert "data" in body

    async def test_updated_name_reflected(
        self,
        app_client: httpx.AsyncClient,
        fake_user: Any,
        stub_service: StubUserService,
    ) -> None:
        updated = _make_user()
        updated.name = "New Name"
        stub_service.update_profile_return = updated
        data = (await app_client.patch(ME_URL, json={"name": "New Name"})).json()["data"]
        assert data["name"] == "New Name"

    async def test_empty_body_returns_200(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        # All fields optional — empty patch is valid, returns unchanged user.
        response = await app_client.patch(ME_URL, json={})
        assert response.status_code == 200

    async def test_name_too_short_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(ME_URL, json={"name": "x"})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_bio_update(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        updated = _make_user()
        updated.bio = "I love books."
        stub_service.update_profile_return = updated
        data = (
            await app_client.patch(ME_URL, json={"bio": "I love books."})
        ).json()["data"]
        assert data["bio"] == "I love books."

    async def test_password_not_in_response(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (await app_client.patch(ME_URL, json={"name": "New Name"})).json()["data"]
        assert "password_hash" not in data

    async def test_is_superuser_not_in_response(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (await app_client.patch(ME_URL, json={"name": "New Name"})).json()["data"]
        assert "is_superuser" not in data

    async def test_unauthenticated_returns_403(self) -> None:
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(ME_URL, json={"name": "New Name"})
        assert response.status_code == 403


# DELETE /api/v1/users/me

class TestDeleteMe:
    """Tests for DELETE /api/v1/users/me."""

    async def test_returns_200(
        self,
        app_client: httpx.AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def _stub_soft_delete(db: Any, user: Any) -> Any:
            return user

        monkeypatch.setattr(
            "src.api.routes.users.soft_delete_user",
            _stub_soft_delete,
        )
        response = await app_client.delete(ME_URL)
        assert response.status_code == 200

    async def test_success_envelope_shape(
        self,
        app_client: httpx.AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def _stub_soft_delete(db: Any, user: Any) -> Any:
            return user

        monkeypatch.setattr(
            "src.api.routes.users.soft_delete_user",
            _stub_soft_delete,
        )
        body = (await app_client.delete(ME_URL)).json()
        assert body["success"] is True
        assert "data" in body

    async def test_response_contains_confirmation_message(
        self,
        app_client: httpx.AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def _stub_soft_delete(db: Any, user: Any) -> Any:
            return user

        monkeypatch.setattr(
            "src.api.routes.users.soft_delete_user",
            _stub_soft_delete,
        )
        data = (await app_client.delete(ME_URL)).json()["data"]
        assert "message" in data

    async def test_unauthenticated_returns_403(self) -> None:
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(ME_URL)
        assert response.status_code == 403


# PATCH /api/v1/users/me/password

class TestChangePassword:
    """Tests for PATCH /api/v1/users/me/password."""

    async def test_returns_200_on_success(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(
            PASSWORD_URL,
            json={
                "current_password": "OldPass123",
                "new_password": "NewPass456",
            },
        )
        assert response.status_code == 200

    async def test_success_envelope_shape(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        body = (
            await app_client.patch(
                PASSWORD_URL,
                json={
                    "current_password": "OldPass123",
                    "new_password": "NewPass456",
                },
            )
        ).json()
        assert body["success"] is True
        assert "data" in body

    async def test_response_contains_confirmation_message(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        data = (
            await app_client.patch(
                PASSWORD_URL,
                json={
                    "current_password": "OldPass123",
                    "new_password": "NewPass456",
                },
            )
        ).json()["data"]
        assert "message" in data

    async def test_wrong_current_password_returns_400(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.change_password_raise = "WRONG_PASSWORD"
        response = await app_client.patch(
            PASSWORD_URL,
            json={
                "current_password": "WrongPass",
                "new_password": "NewPass456",
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "WRONG_PASSWORD"

    async def test_new_password_too_long_returns_400(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.change_password_raise = "PASSWORD_TOO_LONG"
        response = await app_client.patch(
            PASSWORD_URL,
            json={
                "current_password": "OldPass123",
                "new_password": "NewPass456",
            },
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_PASSWORD"

    async def test_missing_current_password_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(
            PASSWORD_URL,
            json={"new_password": "NewPass456"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_missing_new_password_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(
            PASSWORD_URL,
            json={"current_password": "OldPass123"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_new_password_too_short_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.patch(
            PASSWORD_URL,
            json={
                "current_password": "OldPass123",
                "new_password": "short",
            },
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_unauthenticated_returns_403(self) -> None:
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                PASSWORD_URL,
                json={
                    "current_password": "OldPass123",
                    "new_password": "NewPass456",
                },
            )
        assert response.status_code == 403