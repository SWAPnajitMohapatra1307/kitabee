"""ORM models for the Kitabee project.

Importing this package ensures every model is registered with
``src.database.base.Base.metadata`` so Alembic can detect them during
autogeneration.
"""
from src.database.models.book import Book
from src.database.models.library_item import Library, LibraryStatus
from src.database.models.rating import Rating
from src.database.models.recommendation import Recommendation, RecommendationModelType
from src.database.models.search_history import SearchHistory
from src.database.models.user import User
from src.database.models.user_preferences import UserPreferences

__all__ = [
    "Book",
    "Library",
    "LibraryStatus",
    "Rating",
    "Recommendation",
    "RecommendationModelType",
    "SearchHistory",
    "User",
    "UserPreferences",
]
