"""Integration tests for authentication API endpoints.

Tests POST /api/v1/auth/register
      POST /api/v1/auth/login
      POST /api/v1/auth/refresh

UserService is stubbed via monkeypatch so no real DB, bcrypt,
or CRUD calls are made. JWT signing uses the real jwt_handler
so token structure is verified correctly.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, AsyncIterator, Optional
from uuid import UUID, uuid4

import httpx
import pytest
from httpx import ASGITransport

from src.auth.jwt_handler import create_access_token, create_refresh_token
from src.main import app


# Constants

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"

ISO_8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$"
)

VALID_REGISTER_PAYLOAD: dict[str, Any] = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "StrongPass123",
}

VALID_LOGIN_PAYLOAD: dict[str, Any] = {
    "email": "test@example.com",
    "password": "StrongPass123",
}


# Stub

class StubUserService:
    """Configurable stand-in for UserService.

    Controls what create_user, authenticate_user, and get_by_id return.
    Set raise_on_create to make create_user raise a ValueError.
    """

    def __init__(self) -> None:
        self.create_user_return: Optional[Any] = None
        self.authenticate_return: Optional[Any] = None
        self.get_by_id_return: Optional[Any] = None
        self.raise_on_create: Optional[str] = None

    async def create_user(self, payload: Any, admin_key: Any = None) -> Any:
        """Stub create_user — raises or returns configured value."""
        if self.raise_on_create is not None:
            raise ValueError(self.raise_on_create)
        assert self.create_user_return is not None
        return self.create_user_return

    async def authenticate_user(self, email: str, password: str) -> Optional[Any]:
        """Stub authenticate_user — returns configured value."""
        return self.authenticate_return

    async def get_by_id(self, user_id: UUID) -> Optional[Any]:
        """Stub get_by_id — returns configured value."""
        return self.get_by_id_return


# Helpers

def _make_user(
    *,
    user_id: Optional[UUID] = None,
    email: str = "test@example.com",
    name: str = "Test User",
    is_superuser: bool = False,
    is_active: bool = True,
) -> Any:
    """Build a fake user object without touching the database.

    Uses SimpleNamespace to avoid SQLAlchemy ORM attribute machinery.
    UserResponse.model_validate reads plain attributes so SimpleNamespace
    works correctly here.
    """
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=user_id or uuid4(),
        email=email,
        name=name,
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


# Fixtures

@pytest.fixture
def stub_service() -> StubUserService:
    """Fresh stub for each test."""
    return StubUserService()


@pytest.fixture
def fake_user() -> Any:
    """Reusable fake active normal user."""
    return _make_user()


@pytest.fixture
async def app_client(
    stub_service: StubUserService,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx AsyncClient with UserService monkeypatched.

    The route does UserService(db) inline, so we replace the class
    itself in the route module namespace with a factory that returns
    our stub regardless of what db session is passed.
    """
    monkeypatch.setattr(
        "src.api.routes.auth.UserService",
        lambda db: stub_service,
    )
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Register happy path

class TestRegisterHappyPath:
    """Successful POST /api/v1/auth/register responses."""

    async def test_returns_201(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        response = await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)
        assert response.status_code == 201

    async def test_success_envelope_shape(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        body = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body

    async def test_data_contains_user_fields(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        data = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()["data"]
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
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        data = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()["data"]
        assert "password" not in data
        assert "password_hash" not in data

    async def test_is_superuser_not_in_response(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        data = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()["data"]
        assert "is_superuser" not in data


# Register validation

class TestRegisterValidation:
    """Pydantic validation failures for POST /api/v1/auth/register."""

    async def test_missing_email_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL, json={"name": "Test", "password": "StrongPass123"}
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_invalid_email_format_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL,
            json={"email": "notanemail", "name": "Test", "password": "StrongPass123"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_missing_name_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL,
            json={"email": "test@example.com", "password": "StrongPass123"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_name_too_short_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL,
            json={"email": "test@example.com", "name": "x", "password": "StrongPass123"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_password_too_short_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL,
            json={"email": "test@example.com", "name": "Test User", "password": "short"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    async def test_missing_password_returns_422(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REGISTER_URL,
            json={"email": "test@example.com", "name": "Test User"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# Register conflict

class TestRegisterConflict:
    """Service-layer errors mapped to HTTP errors for register."""

    async def test_duplicate_email_returns_409(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.raise_on_create = "EMAIL_TAKEN"
        response = await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_TAKEN"

    async def test_password_too_long_returns_400(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.raise_on_create = "PASSWORD_TOO_LONG"
        response = await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_PASSWORD"


# Login happy path

class TestLoginHappyPath:
    """Successful POST /api/v1/auth/login responses."""

    async def test_returns_200(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.authenticate_return = fake_user
        response = await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_response_has_access_token(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.authenticate_return = fake_user
        data = (await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)).json()["data"]
        assert "access_token" in data
        assert len(data["access_token"]) > 0

    async def test_response_has_refresh_token(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.authenticate_return = fake_user
        data = (await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)).json()["data"]
        assert "refresh_token" in data
        assert len(data["refresh_token"]) > 0

    async def test_token_type_is_bearer(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.authenticate_return = fake_user
        data = (await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)).json()["data"]
        assert data["token_type"] == "bearer"


# Login failure

class TestLoginFailure:
    """Failed login attempts."""

    async def test_wrong_password_returns_401(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.authenticate_return = None
        response = await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_unknown_email_returns_401(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.authenticate_return = None
        response = await app_client.post(
            LOGIN_URL,
            json={"email": "nobody@example.com", "password": "StrongPass123"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_error_message_is_generic(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
    ) -> None:
        stub_service.authenticate_return = None
        message = (
            await app_client.post(LOGIN_URL, json=VALID_LOGIN_PAYLOAD)
        ).json()["error"]["message"]
        # Message must not reveal which field failed specifically.
        # Acceptable: "Invalid email or password." (combined, generic)
        # Not acceptable: "Email not found." or "Wrong password."
        lowered = message.lower()
        assert "not found" not in lowered
        assert "wrong password" not in lowered
        assert "incorrect password" not in lowered


# Refresh happy path

class TestRefreshHappyPath:
    """Successful POST /api/v1/auth/refresh responses."""

    async def test_returns_200_with_new_tokens(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.get_by_id_return = fake_user
        refresh_token = create_refresh_token(fake_user.id)
        response = await app_client.post(
            REFRESH_URL, json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_new_access_token_is_valid_jwt(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.get_by_id_return = fake_user
        refresh_token = create_refresh_token(fake_user.id)
        data = (
            await app_client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        ).json()["data"]
        new_access = data["access_token"]
        # Valid JWT has exactly three dot-separated parts
        assert len(new_access.split(".")) == 3

    async def test_token_type_is_bearer(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.get_by_id_return = fake_user
        refresh_token = create_refresh_token(fake_user.id)
        data = (
            await app_client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        ).json()["data"]
        assert data["token_type"] == "bearer"


# Refresh failure

class TestRefreshFailure:
    """Invalid or expired refresh token handling."""

    async def test_garbage_token_returns_401(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        response = await app_client.post(
            REFRESH_URL, json={"refresh_token": "garbage.token.here"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"

    async def test_access_token_used_as_refresh_returns_401(
        self,
        app_client: httpx.AsyncClient,
        fake_user: Any,
    ) -> None:
        access_token = create_access_token(fake_user.id)
        response = await app_client.post(
            REFRESH_URL, json={"refresh_token": access_token}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"

    async def test_user_not_found_returns_401(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.get_by_id_return = None
        refresh_token = create_refresh_token(fake_user.id)
        response = await app_client.post(
            REFRESH_URL, json={"refresh_token": refresh_token}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"

    async def test_inactive_user_returns_401(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        inactive_user = _make_user(is_active=False)
        stub_service.get_by_id_return = inactive_user
        refresh_token = create_refresh_token(fake_user.id)
        response = await app_client.post(
            REFRESH_URL, json={"refresh_token": refresh_token}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"


# Envelope meta

class TestEnvelopeMeta:
    """Meta block present and correct on all responses."""

    async def test_success_meta_has_iso_8601_utc_timestamp(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        meta = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()["meta"]
        assert ISO_8601_UTC_RE.match(meta["timestamp"]) is not None

    async def test_error_meta_has_iso_8601_utc_timestamp(
        self,
        app_client: httpx.AsyncClient,
    ) -> None:
        meta = (await app_client.post(REGISTER_URL, json={})).json()["meta"]
        assert ISO_8601_UTC_RE.match(meta["timestamp"]) is not None

    async def test_meta_has_version_v1(
        self,
        app_client: httpx.AsyncClient,
        stub_service: StubUserService,
        fake_user: Any,
    ) -> None:
        stub_service.create_user_return = fake_user
        meta = (await app_client.post(REGISTER_URL, json=VALID_REGISTER_PAYLOAD)).json()["meta"]
        assert meta["version"] == "v1"