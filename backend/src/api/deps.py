"""FastAPI dependency providers.

Central location for Depends() providers used across route handlers.
Keeps route files focused on business logic and endpoints.
"""

from __future__ import annotations

from fastapi import Request

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


def get_book_service(request: Request) -> BookService:
    """Return a BookService wired with the shared Google Books client.

    Args:
        request: The current FastAPI request (auto-injected).

    Returns:
        A BookService instance ready to handle route calls.
    """
    return BookService(get_google_books_client(request))