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
from src.external.comic_vine import ComicVineClient
from src.external.internet_archive import InternetArchiveClient
from src.services.book_service import BookService
from src.services.content_router import ContentRouter


def get_google_books_client(request: Request) -> GoogleBooksClient:
    """Return the shared GoogleBooksClient from app state.

    Args:
        request: The current FastAPI request (auto-injected).

    Returns:
        The shared GoogleBooksClient instance.
    """
    return request.app.state.google_books_client


def get_comic_vine_client(request: Request) -> ComicVineClient:
    """Return the shared ComicVineClient from app state.

    Args:
        request: The current FastAPI request (auto-injected).

    Returns:
        The shared ComicVineClient instance.
    """
    return request.app.state.comic_vine_client


def get_internet_archive_client(request: Request) -> InternetArchiveClient:
    """Return the shared InternetArchiveClient from app state.

    Args:
        request: The current FastAPI request (auto-injected).

    Returns:
        The shared InternetArchiveClient instance.
    """
    return request.app.state.internet_archive_client


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a database session for the current request.

    Commits on success, rolls back on exception, always closes.

    Yields:
        An active AsyncSession bound to the current request lifecycle.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

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


async def get_content_router(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ContentRouter:
    """Return a ContentRouter wired with all three API clients and DB session.

    Args:
        request: The current FastAPI request (auto-injected).
        db: Async database session (injected via get_db).

    Returns:
        A ContentRouter instance ready to dispatch by content_id prefix.
    """
    return ContentRouter(
        google_books=get_google_books_client(request),
        comic_vine=get_comic_vine_client(request),
        internet_archive=get_internet_archive_client(request),
        db=db,
    )