"""SQLAlchemy declarative base and model registry.

Importing this module ensures every ORM model is registered with the metadata
used by Alembic for autogenerate support.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in the Kitabee project."""


from src.database.models.user import User  # noqa: E402, F401
from src.database.models.book import Book  # noqa: E402, F401
from src.database.models.rating import Rating  # noqa: E402, F401
from src.database.models.library_item import Library  # noqa: E402, F401
from src.database.models.recommendation import Recommendation  # noqa: E402, F401
from src.database.models.user_preferences import UserPreferences  # noqa: E402, F401
from src.database.models.search_history import SearchHistory  # noqa: E402, F401
