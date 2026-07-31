"""Shared fixtures for the test suite."""

from __future__ import annotations

from typing import Any, Iterator

import pytest

from src.external.google_books import GoogleBooksClient


@pytest.fixture
def client() -> Iterator[GoogleBooksClient]:
    """Yield a GoogleBooksClient and close it after the test."""
    instance = GoogleBooksClient()
    try:
        yield instance
    finally:
        # GoogleBooksClient.close is async; tests run under pytest-asyncio auto
        # mode, so we can close here. Import lazily to avoid circular issues.
        import asyncio

        asyncio.run(instance.close())


@pytest.fixture
def sample_volume() -> dict[str, Any]:
    """A realistic Google Books volume payload for reuse across tests."""
    return {
        "id": "zyTCAlFPjgYC",
        "etag": "abc123",
        "selfLink": "https://www.googleapis.com/books/v1/volumes/zyTCAlFPjgYC",
        "volumeInfo": {
            "title": "  The <i>Testing</i> Book &amp; More  ",
            "subtitle": "A guide",
            "authors": ["  Jane Doe ", "John Smith", "Jane Doe", ""],
            "publisher": "Acme Press",
            "publishedDate": "2020-05-15",
            "description": "<p>Hello&nbsp;world</p>   <br/>  <b>Bold</b>.",
            "industryIdentifiers": [
                {"type": "ISBN_10", "identifier": " 0123456789 "},
                {"type": "ISBN_13", "identifier": "9780123456786"},
                {"type": "OTHER", "identifier": "ignored"},
            ],
            "pageCount": 320,
            "categories": ["  Fiction ", "Fiction", "", "", "Mystery"],
            "averageRating": 4.25,
            "ratingsCount": 1234,
            "imageLinks": {
                "thumbnail": "https://books.google.com/thumb.jpg",
                "smallThumbnail": "https://books/google/small.jpg",
            },
            "language": "en",
            "previewLink": "https://books.google.com/preview",
            "infoLink": "https://books.google.com/info",
        },
        "saleInfo": {"country": "US", "saleability": "FOR_SALE"},
        "accessInfo": {"country": "US", "viewability": "PARTIAL"},
    }


@pytest.fixture
def fast_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace tenacity's exponential backoff with a zero-second wait.

    Used so retry-related tests don't sleep between attempts. The client
    imports `wait_exponential` into its module namespace; we swap it there
    so the AsyncRetrying built in `_get_json` sees the patched function.
    """
    from tenacity import wait_fixed

    # `_get_json` evaluates `wait_exponential(multiplier=1, min=1, max=10)`
    # at call time, so patching the `tenacity` symbol is the only patch that
    # reaches the default argument.
    monkeypatch.setattr("tenacity.wait_exponential", wait_fixed(0))
