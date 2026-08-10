"""Tests for content_normalizer.py."""

from __future__ import annotations

from src.services.content_normalizer import (
    PREFIX_CV,
    PREFIX_GB,
    PREFIX_IA,
    SOURCE_COMIC_VINE,
    SOURCE_GOOGLE_BOOKS,
    SOURCE_INTERNET_ARCHIVE,
    get_source_for_prefix,
    make_content_id,
    normalize_any,
    normalize_comic_vine_issue,
    normalize_comic_vine_volume,
    normalize_google_books,
    normalize_internet_archive,
    parse_content_id,
)


class TestMakeContentId:
    def test_builds_google_books_content_id(self):
        assert make_content_id(PREFIX_GB, "ByLKDQAAQBAJ") == "gb:ByLKDQAAQBAJ"

    def test_builds_comic_vine_content_id(self):
        assert make_content_id(PREFIX_CV, 456) == "cv:456"

    def test_builds_internet_archive_content_id(self):
        assert make_content_id(PREFIX_IA, "pg1342") == "ia:pg1342"

    def test_none_raw_id_returns_none(self):
        assert make_content_id(PREFIX_GB, None) is None

    def test_blank_raw_id_returns_none(self):
        assert make_content_id(PREFIX_GB, "   ") is None


class TestParseContentId:
    def test_parses_google_books(self):
        assert parse_content_id("gb:test123") == ("gb", "test123")

    def test_parses_comic_vine(self):
        assert parse_content_id("cv:456") == ("cv", "456")

    def test_parses_internet_archive(self):
        assert parse_content_id("ia:pg1342") == ("ia", "pg1342")

    def test_invalid_prefix_returns_none(self):
        assert parse_content_id("xx:123") is None

    def test_missing_colon_returns_none(self):
        assert parse_content_id("gb123") is None

    def test_empty_raw_id_returns_none(self):
        assert parse_content_id("gb:") is None

    def test_non_string_returns_none(self):
        assert parse_content_id(None) is None


class TestGetSourceForPrefix:
    def test_gb_maps_to_google_books(self):
        assert get_source_for_prefix("gb") == SOURCE_GOOGLE_BOOKS

    def test_cv_maps_to_comic_vine(self):
        assert get_source_for_prefix("cv") == SOURCE_COMIC_VINE

    def test_ia_maps_to_internet_archive(self):
        assert get_source_for_prefix("ia") == SOURCE_INTERNET_ARCHIVE

    def test_unknown_prefix_returns_none(self):
        assert get_source_for_prefix("xx") is None


class TestNormalizeGoogleBooks:
    def _sample(self, **overrides):
        base = {
            "google_books_id": "test123",
            "title": "Dune",
            "authors": ["Frank Herbert"],
            "description": "A sci-fi epic.",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "categories": ["Fiction", "Science Fiction"],
            "language": "en",
            "publisher": "Chilton Books",
            "published_date": "1965",
            "page_count": 412,
            "isbn_10": "0441013597",
            "isbn_13": "9780441013593",
            "average_rating": 4.5,
            "ratings_count": 1000,
        }
        base.update(overrides)
        return base

    def test_returns_content_id(self):
        result = normalize_google_books(self._sample())
        assert result["content_id"] == "gb:test123"

    def test_returns_external_fields(self):
        result = normalize_google_books(self._sample())
        assert result["external_id"] == "test123"
        assert result["external_source"] == SOURCE_GOOGLE_BOOKS
        assert result["source"] == SOURCE_GOOGLE_BOOKS

    def test_returns_joined_author(self):
        result = normalize_google_books(self._sample())
        assert result["author"] == "Frank Herbert"

    def test_returns_authors_list(self):
        result = normalize_google_books(self._sample())
        assert result["authors"] == ["Frank Herbert"]

    def test_is_free_false(self):
        result = normalize_google_books(self._sample())
        assert result["is_free"] is False

    def test_content_type_book(self):
        result = normalize_google_books(self._sample())
        assert result["content_type"] == "book"

    def test_uses_thumbnail_for_cover_fields(self):
        result = normalize_google_books(self._sample())
        assert result["cover_url"] == "https://example.com/thumb.jpg"
        assert result["cover_url_large"] == "https://example.com/thumb.jpg"

    def test_missing_google_books_id_returns_none(self):
        sample = self._sample()
        del sample["google_books_id"]
        assert normalize_google_books(sample) is None

    def test_missing_authors_returns_defaults(self):
        sample = self._sample(authors=None)
        result = normalize_google_books(sample)
        assert result["authors"] == []
        assert result["author"] is None

    def test_missing_language_defaults_to_en(self):
        sample = self._sample(language=None)
        result = normalize_google_books(sample)
        assert result["language"] == "en"

    def test_missing_ratings_count_defaults_to_zero(self):
        sample = self._sample(ratings_count=None)
        result = normalize_google_books(sample)
        assert result["rating_count"] == 0


class TestNormalizeComicVineIssue:
    def _sample(self, **overrides):
        base = {
            "id": "456",
            "title": "Batman: Year One",
            "series": "Batman",
            "issue_number": "404",
            "description": "A dark origin story.",
            "cover_image": "https://example.com/batman.jpg",
            "detail_url": "https://comicvine.gamespot.com/batman/4000-456/",
            "published_date": "1987-03-01",
        }
        base.update(overrides)
        return base

    def test_returns_content_id(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["content_id"] == "cv:456"

    def test_strips_cv_prefix_from_id(self):
        result = normalize_comic_vine_issue(self._sample(id="cv:456"))
        assert result["content_id"] == "cv:456"
        assert result["external_id"] == "456"

    def test_strips_cv_underscore_prefix_from_id(self):
        result = normalize_comic_vine_issue(self._sample(id="cv_456"))
        assert result["content_id"] == "cv:456"
        assert result["external_id"] == "456"

    def test_returns_external_fields(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["external_source"] == SOURCE_COMIC_VINE
        assert result["source"] == SOURCE_COMIC_VINE

    def test_content_type_comic(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["content_type"] == "comic"

    def test_is_free_false(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["is_free"] is False

    def test_free_url_uses_detail_url(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["free_url"] == "https://comicvine.gamespot.com/batman/4000-456/"

    def test_series_order_uses_issue_number(self):
        result = normalize_comic_vine_issue(self._sample())
        assert result["series_order"] == "404"

    def test_missing_title_falls_back_to_series_and_issue_number(self):
        result = normalize_comic_vine_issue(self._sample(title=None))
        assert result["title"] == "Batman #404"

    def test_missing_title_and_issue_falls_back_to_series(self):
        result = normalize_comic_vine_issue(
            self._sample(title=None, issue_number=None)
        )
        assert result["title"] == "Batman"

    def test_missing_everything_falls_back_to_unknown_comic(self):
        result = normalize_comic_vine_issue(
            self._sample(title=None, series=None, issue_number=None)
        )
        assert result["title"] == "Unknown Comic"

    def test_missing_id_returns_none(self):
        sample = self._sample()
        del sample["id"]
        assert normalize_comic_vine_issue(sample) is None


class TestNormalizeComicVineVolume:
    def _sample(self, **overrides):
        base = {
            "id": "789",
            "title": "Saga",
            "description": "Space opera comic.",
            "cover_image": "https://example.com/saga.jpg",
            "detail_url": "https://comicvine.gamespot.com/saga/4050-789/",
            "publisher": "Image Comics",
            "start_year": "2012",
        }
        base.update(overrides)
        return base

    def test_returns_content_id(self):
        result = normalize_comic_vine_volume(self._sample())
        assert result["content_id"] == "cv:789"

    def test_returns_external_fields(self):
        result = normalize_comic_vine_volume(self._sample())
        assert result["external_id"] == "789"
        assert result["external_source"] == SOURCE_COMIC_VINE
        assert result["source"] == SOURCE_COMIC_VINE

    def test_content_type_comic(self):
        result = normalize_comic_vine_volume(self._sample())
        assert result["content_type"] == "comic"

    def test_uses_start_year_as_published_date(self):
        result = normalize_comic_vine_volume(self._sample())
        assert result["published_date"] == "2012"

    def test_missing_title_falls_back_to_unknown_volume(self):
        result = normalize_comic_vine_volume(self._sample(title=None))
        assert result["title"] == "Unknown Volume"

    def test_missing_id_returns_none(self):
        sample = self._sample()
        del sample["id"]
        assert normalize_comic_vine_volume(sample) is None


class TestNormalizeInternetArchive:
    def _sample(self, **overrides):
        base = {
            "id": "pg1342",
            "title": "Pride and Prejudice",
            "authors": ["Jane Austen"],
            "description": "A classic romance.",
            "thumbnail_url": "https://example.com/pp.jpg",
            "read_url": "https://archive.org/details/pg1342",
            "subjects": ["Fiction", "Romance"],
            "language": "en",
            "published_date": "1813",
        }
        base.update(overrides)
        return base

    def test_returns_content_id(self):
        result = normalize_internet_archive(self._sample())
        assert result["content_id"] == "ia:pg1342"

    def test_strips_ia_prefix_from_id(self):
        result = normalize_internet_archive(self._sample(id="ia:pg1342"))
        assert result["content_id"] == "ia:pg1342"
        assert result["external_id"] == "pg1342"

    def test_strips_ia_underscore_prefix_from_id(self):
        result = normalize_internet_archive(self._sample(id="ia_pg1342"))
        assert result["content_id"] == "ia:pg1342"
        assert result["external_id"] == "pg1342"

    def test_returns_external_fields(self):
        result = normalize_internet_archive(self._sample())
        assert result["external_source"] == SOURCE_INTERNET_ARCHIVE
        assert result["source"] == SOURCE_INTERNET_ARCHIVE

    def test_is_free_true(self):
        result = normalize_internet_archive(self._sample())
        assert result["is_free"] is True

    def test_free_url_comes_from_read_url(self):
        result = normalize_internet_archive(self._sample())
        assert result["free_url"] == "https://archive.org/details/pg1342"

    def test_author_is_joined_string(self):
        result = normalize_internet_archive(self._sample())
        assert result["author"] == "Jane Austen"

    def test_authors_list_preserved(self):
        result = normalize_internet_archive(self._sample())
        assert result["authors"] == ["Jane Austen"]

    def test_missing_authors_defaults_empty(self):
        result = normalize_internet_archive(self._sample(authors=None))
        assert result["authors"] == []
        assert result["author"] is None

    def test_missing_language_defaults_to_en(self):
        result = normalize_internet_archive(self._sample(language=None))
        assert result["language"] == "en"

    def test_missing_id_returns_none(self):
        sample = self._sample()
        del sample["id"]
        assert normalize_internet_archive(sample) is None


class TestNormalizeAny:
    def test_dispatches_google_books(self):
        raw = {"google_books_id": "test123", "title": "Dune"}
        result = normalize_any(raw, SOURCE_GOOGLE_BOOKS)
        assert result["content_id"] == "gb:test123"

    def test_dispatches_comic_vine_to_issue_normalizer(self):
        raw = {"id": "456", "title": "Batman"}
        result = normalize_any(raw, SOURCE_COMIC_VINE)
        assert result["content_id"] == "cv:456"

    def test_dispatches_internet_archive(self):
        raw = {"id": "pg1342", "title": "Pride and Prejudice"}
        result = normalize_any(raw, SOURCE_INTERNET_ARCHIVE)
        assert result["content_id"] == "ia:pg1342"

    def test_unknown_source_returns_none(self):
        raw = {"id": "x1", "title": "Unknown"}
        assert normalize_any(raw, "unknown_source") is None
