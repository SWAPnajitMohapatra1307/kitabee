"""Tests for JWT token creation and verification."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from jose import jwt

from src.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.config import settings


class TestCreateAccessToken:
    """Tests for create_access_token."""

    def test_create_access_token_returns_string(self):
        token = create_access_token(uuid4())
        assert isinstance(token, str)

    def test_create_access_token_contains_user_id(self):
        uid = uuid4()
        token = create_access_token(uid)
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == str(uid)

    def test_create_access_token_type_is_access(self):
        token = create_access_token(uuid4())
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["type"] == "access"

    def test_create_access_token_has_expiry(self):
        token = create_access_token(uuid4())
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "exp" in payload


class TestCreateRefreshToken:
    """Tests for create_refresh_token."""

    def test_create_refresh_token_returns_string(self):
        token = create_refresh_token(uuid4())
        assert isinstance(token, str)

    def test_create_refresh_token_type_is_refresh(self):
        token = create_refresh_token(uuid4())
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["type"] == "refresh"

    def test_create_refresh_token_contains_user_id(self):
        uid = uuid4()
        token = create_refresh_token(uid)
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == str(uid)


class TestVerifyToken:
    """Tests for verify_token."""

    def test_verify_access_token_returns_user_id(self):
        uid = uuid4()
        token = create_access_token(uid)
        result = verify_token(token, "access")
        assert result == str(uid)

    def test_verify_refresh_token_returns_user_id(self):
        uid = uuid4()
        token = create_refresh_token(uid)
        result = verify_token(token, "refresh")
        assert result == str(uid)

    def test_verify_token_wrong_type_returns_none(self):
        token = create_access_token(uuid4())
        assert verify_token(token, "refresh") is None

    def test_verify_token_invalid_string_returns_none(self):
        assert verify_token("not.a.token", "access") is None

    def test_verify_token_empty_string_returns_none(self):
        assert verify_token("", "access") is None

    def test_verify_token_expired_returns_none(self):
        uid = uuid4()
        # Create token that expired 1 hour ago
        expired = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {"sub": str(uid), "exp": expired, "type": "access"}
        token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        assert verify_token(token, "access") is None

    def test_verify_token_wrong_secret_returns_none(self):
        uid = uuid4()
        payload = {
            "sub": str(uid),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(payload, "wrong_secret", algorithm="HS256")
        assert verify_token(token, "access") is None

    def test_verify_token_missing_sub_returns_none(self):
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        assert verify_token(token, "access") is None