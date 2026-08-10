"""Tests for ContentRouter.

All three external API clients and DB are mocked.
No real HTTP calls, no real DB connections.
"""

from __future__ import annotations

from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.content_router import ContentRouter
from src.services.content_normalizer import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_COMIC_VINE,
    SOURCE_INTERNET_ARCHIVE,
)


def _make_gb_raw(gb_id: str = "test123", title: str = "Dune") -> dict:
    return {
        "google_books_id": gb_id,
        "title": title,
        "authors": ["Frank Herbert"],
        "description": "A sci-fi epic.",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "categories": ["Fiction"],
        "language": "en",
        "publisher": "Chilton",
        "published_date": "1965",
        "page_count": 412,
        "isbn_10": None,
        "isbn_13": None,
        "average_rating": 4.5,
        "ratings_count": 1000,
    }


def _make_cv_raw(cv_id: str = "456", title: str = "Batman") -> dict:
    return {
        "id": cv_id,
        "title": title,
        "series": "Batman",
        "issue_number": "1",
        "description": "Dark knight.",
        "cover_image": "https://example.com/batman.jpg",
        "detail_url": "https://comicvine.gamespot.com/batman/456/",
        "published_date": "1987-03-01",
    }


def _make_ia_raw(ia_id: str = "pg1342", title: str = "Pride and Prejudice") -> dict:
    return {
        "id": ia_id,
        "title": title,
        "authors": ["Jane Austen"],
        "description": "A classic romance.",
        "thumbnail_url": "https://example.com/pp.jpg",
        "read_url": "https://archive.org/details/pg1342",
        "subjects": ["Fiction", "Romance"],
        "language": "en",
        "published_date": "1813",
    }


def _make_router(
    gb_client=None,
    cv_client=None,
    ia_client=None,
    db=None,
) -> ContentRouter:
    gb = gb_client or MagicMock()
    cv = cv_client or MagicMock()
    ia = ia_client or MagicMock()
    db = db or AsyncMock()
    return ContentRouter(
        google_books=gb,
        comic_vine=cv,
        internet_archive=ia,
        db=db,
    )


class TestGetByContentIdGoogleBooks:
    async def test_returns_normalized_gb_item(self, monkeypatch):
        gb = AsyncMock()
        gb.get_by_id.return_value = _make_gb_raw()

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_google",
            AsyncMock(),
        )

        router = _make_router(gb_client=gb)
        result = await router.get_by_content_id("gb:test123")

        assert result is not None
        assert result["content_id"] == "gb:test123"
        assert result["title"] == "Dune"
        assert result["is_free"] is False
        assert result["external_source"] == SOURCE_GOOGLE_BOOKS

    async def test_returns_none_when_api_returns_none(self, monkeypatch):
        gb = AsyncMock()
        gb.get_by_id.return_value = None

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )

        router = _make_router(gb_client=gb)
        result = await router.get_by_content_id("gb:doesnotexist")

        assert result is None

    async def test_returns_db_item_when_cached(self, monkeypatch):
        db_book = MagicMock()
        db_book.external_id = "test123"
        db_book.external_source = SOURCE_GOOGLE_BOOKS
        db_book.title = "Dune"
        db_book.authors = ["Frank Herbert"]
        db_book.description = None
        db_book.cover_url = None
        db_book.cover_url_large = None
        db_book.genres = []
        db_book.language = "en"
        db_book.publisher = None
        db_book.published_year = 1965
        db_book.page_count = None
        db_book.isbn_10 = None
        db_book.isbn_13 = None
        db_book.average_rating = None
        db_book.ratings_count = 0

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=db_book),
        )

        gb = AsyncMock()
        router = _make_router(gb_client=gb)
        result = await router.get_by_content_id("gb:test123")

        assert result is not None
        assert result["content_id"] == "gb:test123"
        gb.get_by_id.assert_not_called()

    async def test_persists_fetched_item(self, monkeypatch):
        gb = AsyncMock()
        gb.get_by_id.return_value = _make_gb_raw()

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        upsert_mock = AsyncMock()
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_google",
            upsert_mock,
        )

        router = _make_router(gb_client=gb)
        await router.get_by_content_id("gb:test123")

        upsert_mock.assert_called_once()


class TestGetByContentIdComicVine:
    async def test_returns_normalized_cv_item(self, monkeypatch):
        cv = AsyncMock()
        cv.get_comic.return_value = _make_cv_raw()

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_comic_vine",
            AsyncMock(),
        )

        router = _make_router(cv_client=cv)
        result = await router.get_by_content_id("cv:456")

        assert result is not None
        assert result["content_id"] == "cv:456"
        assert result["content_type"] == "comic"
        assert result["is_free"] is False
        assert result["external_source"] == SOURCE_COMIC_VINE

    async def test_returns_none_when_cv_api_returns_none(self, monkeypatch):
        cv = AsyncMock()
        cv.get_comic.return_value = None

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )

        router = _make_router(cv_client=cv)
        result = await router.get_by_content_id("cv:doesnotexist")

        assert result is None


class TestGetByContentIdInternetArchive:
    async def test_returns_normalized_ia_item(self, monkeypatch):
        ia = AsyncMock()
        ia.get_item.return_value = _make_ia_raw()

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_internet_archive",
            AsyncMock(),
        )

        router = _make_router(ia_client=ia)
        result = await router.get_by_content_id("ia:pg1342")

        assert result is not None
        assert result["content_id"] == "ia:pg1342"
        assert result["is_free"] is True
        assert result["external_source"] == SOURCE_INTERNET_ARCHIVE

    async def test_free_url_is_set(self, monkeypatch):
        ia = AsyncMock()
        ia.get_item.return_value = _make_ia_raw()

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_internet_archive",
            AsyncMock(),
        )

        router = _make_router(ia_client=ia)
        result = await router.get_by_content_id("ia:pg1342")

        assert result["free_url"] is not None
        assert "pg1342" in result["free_url"]

    async def test_returns_none_when_ia_api_returns_none(self, monkeypatch):
        ia = AsyncMock()
        ia.get_item.return_value = None

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )

        router = _make_router(ia_client=ia)
        result = await router.get_by_content_id("ia:doesnotexist")

        assert result is None


class TestGetByContentIdInvalidPrefix:
    async def test_invalid_prefix_returns_none(self):
        router = _make_router()
        result = await router.get_by_content_id("xx:badid")
        assert result is None

    async def test_no_prefix_returns_none(self):
        router = _make_router()
        result = await router.get_by_content_id("justanid")
        assert result is None


class TestSearch:
    async def test_search_google_books_only(self, monkeypatch):
        gb = AsyncMock()
        gb.search.return_value = [_make_gb_raw("id1", "Dune")]

        router = _make_router(gb_client=gb)
        results = await router.search(
            query="dune",
            limit=5,
            sources=[SOURCE_GOOGLE_BOOKS],
        )

        assert len(results) == 1
        assert results[0]["content_id"] == "gb:id1"
        assert results[0]["external_source"] == SOURCE_GOOGLE_BOOKS

    async def test_search_comic_vine_only(self, monkeypatch):
        cv = AsyncMock()
        cv.search_comics.return_value = [_make_cv_raw("456", "Batman")]

        router = _make_router(cv_client=cv)
        results = await router.search(
            query="batman",
            limit=5,
            sources=[SOURCE_COMIC_VINE],
        )

        assert len(results) == 1
        assert results[0]["content_id"] == "cv:456"
        assert results[0]["content_type"] == "comic"

    async def test_search_internet_archive_only(self, monkeypatch):
        ia = AsyncMock()
        ia.search_free_books.return_value = [_make_ia_raw("pg1342", "Pride and Prejudice")]

        router = _make_router(ia_client=ia)
        results = await router.search(
            query="pride",
            limit=5,
            sources=[SOURCE_INTERNET_ARCHIVE],
        )

        assert len(results) == 1
        assert results[0]["content_id"] == "ia:pg1342"
        assert results[0]["is_free"] is True

    async def test_search_all_sources_combines_results(self):
        gb = AsyncMock()
        gb.search.return_value = [_make_gb_raw("id1", "Dune")]

        cv = AsyncMock()
        cv.search_comics.return_value = [_make_cv_raw("456", "Batman")]

        ia = AsyncMock()
        ia.search_free_books.return_value = [_make_ia_raw("pg1342", "Pride")]

        router = _make_router(gb_client=gb, cv_client=cv, ia_client=ia)
        results = await router.search(query="test", limit=5)

        assert len(results) == 3
        sources = {r["external_source"] for r in results}
        assert sources == {SOURCE_GOOGLE_BOOKS, SOURCE_COMIC_VINE, SOURCE_INTERNET_ARCHIVE}

    async def test_failing_source_does_not_break_others(self):
        gb = AsyncMock()
        gb.search.side_effect = Exception("GB down")

        cv = AsyncMock()
        cv.search_comics.return_value = [_make_cv_raw()]

        ia = AsyncMock()
        ia.search_free_books.return_value = []

        router = _make_router(gb_client=gb, cv_client=cv, ia_client=ia)
        results = await router.search(query="test", limit=5)

        assert len(results) == 1
        assert results[0]["external_source"] == SOURCE_COMIC_VINE

    async def test_empty_results_returns_empty_list(self):
        gb = AsyncMock()
        gb.search.return_value = []
        cv = AsyncMock()
        cv.search_comics.return_value = []
        ia = AsyncMock()
        ia.search_free_books.return_value = []

        router = _make_router(gb_client=gb, cv_client=cv, ia_client=ia)
        results = await router.search(query="nothingmatches", limit=5)

        assert results == []

    async def test_default_sources_includes_all_three(self):
        gb = AsyncMock()
        gb.search.return_value = []
        cv = AsyncMock()
        cv.search_comics.return_value = []
        ia = AsyncMock()
        ia.search_free_books.return_value = []

        router = _make_router(gb_client=gb, cv_client=cv, ia_client=ia)
        await router.search(query="test", limit=5)

        gb.search.assert_called_once()
        cv.search_comics.assert_called_once()
        ia.search_free_books.assert_called_once()


class TestGetSimilar:
    async def test_returns_empty_when_source_not_found(self, monkeypatch):
        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )

        gb = AsyncMock()
        gb.get_by_id.return_value = None

        router = _make_router(gb_client=gb)
        results = await router.get_similar("gb:doesnotexist", limit=5)

        assert results == []

    async def test_gb_similar_excludes_source_item(self, monkeypatch):
        gb = AsyncMock()
        gb.get_by_id.return_value = _make_gb_raw("test123", "Dune")
        gb.search.return_value = [
            _make_gb_raw("test123", "Dune"),
            _make_gb_raw("other1", "Dune Messiah"),
        ]

        monkeypatch.setattr(
            "src.services.content_router.get_book_by_external_id",
            AsyncMock(return_value=None),
        )
        monkeypatch.setattr(
            "src.services.content_router.upsert_book_from_google",
            AsyncMock(),
        )

        router = _make_router(gb_client=gb)
        results = await router.get_similar("gb:test123", limit=5)

        ids = [r["content_id"] for r in results]
        assert "gb:test123" not in ids

    async def test_returns_empty_list_for_invalid_prefix(self):
        router = _make_router()
        results = await router.get_similar("xx:badid", limit=5)
        assert results == []
