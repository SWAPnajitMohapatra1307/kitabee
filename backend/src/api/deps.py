"""FastAPI dependency providers.

Central location for Depends() providers used across route handlers.
Keeps route files focused on business logic and endpoints.
"""

from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import AsyncSessionLocal
from src.external.google_books import GoogleBooksClient
from src.services.book_service import BookService


# Public providers

def get_google_books_client(request: Request) -> GoogleBooksClient:
    """Return the shared GoogleBooksClient from app state.

    The client is created once at startup in the lifespan handler
    and stored on app.state to reuse a single httpx.AsyncClient
    connection pool across all requests.

    Args:
        request: The current FastAPI request (auto-injected).

    Returns:
        The shared GoogleBooksClient instance.
    """
    return request.app.state.google_books_client


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a database session for the current request.

    Opens a new AsyncSession at the start of each request and closes
    it when the request completes, whether or not an exception occurred.

    Yields:
        An active AsyncSession bound to the current request lifecycle.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_book_service(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BookService:
    """Return a BookService wired with Google Books client and DB session.

    Args:
        request: The current FastAPI request (auto-injected).
        db: Async database session (injected via get_db).

    Returns:
        A BookService instance ready to handle route calls.
    """
    return BookService(
        google_books=get_google_books_client(request),
        db=db,
    )