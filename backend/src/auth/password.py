"""Password hashing and verification using bcrypt."""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt truncates at 72 bytes — enforce this as a hard limit
_MAX_PASSWORD_BYTES = 72


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt (cost factor 12).

    Args:
        plain: The plain text password to hash.

    Returns:
        Bcrypt hash string safe for database storage.

    Raises:
        ValueError: If password exceeds 72 bytes.
    """
    if len(plain.encode("utf-8")) > _MAX_PASSWORD_BYTES:
        raise ValueError("Password must not exceed 72 characters.")
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against a bcrypt hash.

    Args:
        plain: The plain text password to verify.
        hashed: The bcrypt hash to verify against.

    Returns:
        True if password matches, False otherwise.
    """
    if len(plain.encode("utf-8")) > _MAX_PASSWORD_BYTES:
        return False
    return _pwd_context.verify(plain, hashed)