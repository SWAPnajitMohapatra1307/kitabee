"""Tests for FastAPI dependency providers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_book_service, get_db, get_google_books_client
from src.external.google_books import GoogleBooksClient
from src.services.book_service import BookService


def _build_request(client: GoogleBooksClient):
    """Build a minimal request-like object with app.state."""
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                google_books_client=client,
            )
        )
    )


class TestGetGoogleBooksClient:
    def test_returns_client_from_app_state(self):
        mock_client = MagicMock(spec=GoogleBooksClient)
        request = _build_request(mock_client)

        client = get_google_books_client(request)

        assert client is mock_client


class TestGetDb:
    async def test_yields_async_session(self):
        """get_db must yield an AsyncSession instance."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=False)

        with patch("src.api.deps.AsyncSessionLocal", return_value=mock_context):
            gen = get_db()
            session = await gen.__anext__()

        assert session is mock_session

    async def test_session_context_exits_after_yield(self):
        """get_db must exit the session context after yielding."""
        mock_session = MagicMock(spec=AsyncSession)
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=False)

        with patch("src.api.deps.AsyncSessionLocal", return_value=mock_context):
            gen = get_db()
            await gen.__anext__()

            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()

        mock_context.__aexit__.assert_called_once()


class TestGetBookService:
    async def test_returns_book_service_instance(self):
        mock_client = MagicMock(spec=GoogleBooksClient)
        mock_session = MagicMock(spec=AsyncSession)
        request = _build_request(mock_client)

        service = await get_book_service(request=request, db=mock_session)

        assert isinstance(service, BookService)

    async def test_service_receives_google_client_and_db_session(self):
        mock_client = MagicMock(spec=GoogleBooksClient)
        mock_session = MagicMock(spec=AsyncSession)
        request = _build_request(mock_client)

        service = await get_book_service(request=request, db=mock_session)

        assert service._google_books is mock_client
        assert service._db is mock_session
