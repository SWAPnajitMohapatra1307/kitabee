"""Tests for password hashing and verification."""

import pytest

from src.auth.password import hash_password, verify_password


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hash_password_returns_string(self):
        result = hash_password("Password123")
        assert isinstance(result, str)

    def test_hash_password_starts_with_bcrypt_prefix(self):
        result = hash_password("Password123")
        assert result.startswith("$2b$12$")

    def test_hash_password_different_each_call(self):
        # bcrypt uses random salt — same input produces different hash
        h1 = hash_password("Password123")
        h2 = hash_password("Password123")
        assert h1 != h2

    def test_hash_password_exceeds_72_bytes_raises(self):
        long_password = "A" * 73
        with pytest.raises(ValueError, match="72"):
            hash_password(long_password)

    def test_hash_password_exactly_72_bytes_ok(self):
        password = "A" * 72
        result = hash_password(password)
        assert result.startswith("$2b$")


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verify_password_correct_returns_true(self):
        hashed = hash_password("Password123")
        assert verify_password("Password123", hashed) is True

    def test_verify_password_wrong_returns_false(self):
        hashed = hash_password("Password123")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty_returns_false(self):
        hashed = hash_password("Password123")
        assert verify_password("", hashed) is False

    def test_verify_password_exceeds_72_bytes_returns_false(self):
        hashed = hash_password("Password123")
        long_password = "A" * 73
        assert verify_password(long_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        hashed = hash_password("Password123")
        assert verify_password("password123", hashed) is False