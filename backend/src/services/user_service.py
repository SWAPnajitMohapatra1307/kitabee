"""User service — business logic layer for authentication and user management.

Sits between the API route and the database CRUD layer.
Responsibilities:
- Validate email uniqueness before insert.
- Hash passwords before persistence.
- Apply admin_key check to determine superuser status.
- Authenticate users by email and password.
- Update last_login_at on successful login.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.password import hash_password, verify_password
from src.config import settings
from src.database.crud.user import (
    create_user,
    get_by_email,
    get_by_id,
    update_user,
)
from src.database.base import User
from src.schemas.user import UserCreate


logger = logging.getLogger(__name__)


class UserService:
    """Business logic for user registration and authentication.

    Injected with an AsyncSession. Route handlers instantiate one
    per request.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db: Active async SQLAlchemy session for the current request.
        """
        self._db = db

    async def create_user(
        self,
        payload: UserCreate,
        admin_key: str | None = None,
    ) -> User:
        """Register a new user.

        Checks email uniqueness, hashes password, determines superuser
        status from admin_key, and persists the new user.

        Args:
            payload: Validated registration fields (email, name, password).
            admin_key: Optional secret from raw request body. Never from
                       the public schema. Never logged. Never raised on.

        Returns:
            Newly created User ORM instance.

        Raises:
            ValueError: If email is already registered.
            ValueError: If password exceeds 72 bytes.
        """
        email = payload.email.strip().lower()
        name = payload.name.strip()

        existing = await get_by_email(self._db, email)
        if existing is not None:
            logger.info(
                "Registration blocked — email already registered",
                extra={"email": email},
            )
            raise ValueError("EMAIL_TAKEN")

        password_hash = hash_password(payload.password)

        is_superuser = self._check_admin_key(admin_key)

        logger.info(
            "Creating new user",
            extra={"email": email, "is_superuser": is_superuser},
        )

        user = await create_user(
            self._db,
            email=email,
            password_hash=password_hash,
            name=name,
            is_superuser=is_superuser,
        )

        logger.info(
            "User created successfully",
            extra={"user_id": str(user.id)},
        )

        return user

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """Verify credentials and return the matching user.

        Rejects missing, inactive, soft-deleted users.
        Updates last_login_at on success.

        Args:
            email: Email address from login payload.
            password: Plain text password from login payload.

        Returns:
            Authenticated User ORM instance, or None on failure.
        """
        email = email.strip().lower()

        user = await get_by_email(self._db, email)

        if user is None:
            logger.info(
                "Login failed — email not found",
                extra={"email": email},
            )
            return None

        if not user.is_active:
            logger.info(
                "Login failed — account inactive",
                extra={"user_id": str(user.id)},
            )
            return None

        if not verify_password(password, user.password_hash):
            logger.info(
                "Login failed — wrong password",
                extra={"user_id": str(user.id)},
            )
            return None

        user = await update_user(
        self._db,
        user,
        last_login_at=datetime.now(timezone.utc),
         )

        logger.info(
            "Login successful",
            extra={"user_id": str(user.id)},
        )

        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch an active non-deleted user by UUID.

        Used by auth dependency to load user after token verification.

        Args:
            user_id: Internal Kitabee UUID.

        Returns:
            User ORM instance, or None if not found or soft-deleted.
        """
        return await get_by_id(self._db, user_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_admin_key(self, admin_key: str | None) -> bool:
        """Determine superuser status from the provided admin_key.

        Silent fail design:
        - Empty secret in config → always False (disabled).
        - Missing or wrong key → always False.
        - Correct key → True.
        - Never raises, never logs the key value itself.

        Args:
            admin_key: Raw value from request body. May be None.

        Returns:
            True if admin_key matches the non-empty configured secret.
        """
        configured = settings.admin_secret_key
        if not configured:
            return False
        if not admin_key:
            return False
        return admin_key == configured