import pytest
from src.ml.series_detector import SeriesDetector

# Fixtures

@pytest.fixture
def detector():
    return SeriesDetector()


@pytest.fixture
def comic_vine_item():
    return {
        "content_id": "cv_42",
        "title": "Batman #42",
        "source": "comic_vine",
        "volume": {"id": "796", "name": "Batman"},
        "issue_number": "42",
    }


@pytest.fixture
def google_books_series_item():
    return {
        "content_id": "gb_abc",
        "title": "Harry Potter and the Chamber of Secrets",
        "source": "google_books",
        "seriesInfo": {
            "bookDisplayNumber": "2",
            "series": [
                {
                    "seriesId": "hp_series_001",
                    "seriesName": "Harry Potter",
                }
            ],
        },
    }


@pytest.fixture
def title_pattern_item():
    return {
        "content_id": "gb_xyz",
        "title": "The Witcher (Book 2)",
        "source": "google_books",
    }


@pytest.fixture
def keyword_item():
    return {
        "content_id": "gb_saga",
        "title": "The Expanse Saga",
        "source": "google_books",
    }


@pytest.fixture
def non_series_item():
    return {
        "content_id": "gb_none",
        "title": "A Brief History of Time",
        "source": "google_books",
    }


# Tests — Comic Vine Rule 1

class TestComicVineDetection:
    def test_detects_series(self, detector, comic_vine_item):
        result = detector.detect(comic_vine_item)
        assert result["is_series"] is True

    def test_series_name(self, detector, comic_vine_item):
        result = detector.detect(comic_vine_item)
        assert result["series_name"] == "Batman"

    def test_series_id_has_cv_prefix(self, detector, comic_vine_item):
        result = detector.detect(comic_vine_item)
        assert result["series_id"] == "cv_volume_796"

    def test_position_correct(self, detector, comic_vine_item):
        result = detector.detect(comic_vine_item)
        assert result["position"] == 42

    def test_confidence_high(self, detector, comic_vine_item):
        result = detector.detect(comic_vine_item)
        assert result["confidence"] == 0.95

    def test_missing_volume_id_not_detected(self, detector):
        item = {
            "source": "comic_vine",
            "volume": {"name": "Batman"},
            "issue_number": "1",
        }
        result = detector.detect(item)
        assert result["is_series"] is False

    def test_missing_volume_name_not_detected(self, detector):
        item = {
            "source": "comic_vine",
            "volume": {"id": "123"},
            "issue_number": "1",
        }
        result = detector.detect(item)
        assert result["is_series"] is False

    def test_missing_issue_number_lower_confidence(self, detector):
        item = {
            "source": "comic_vine",
            "volume": {"id": "123", "name": "Batman"},
        }
        result = detector.detect(item)
        assert result["is_series"] is True
        assert result["position"] is None
        assert result["confidence"] == 0.9

    def test_float_issue_number_parsed(self, detector):
        item = {
            "source": "comic_vine",
            "volume": {"id": "123", "name": "Batman"},
            "issue_number": "1.0",
        }
        result = detector.detect(item)
        assert result["position"] == 1


# Tests — Google Books Rule 2

class TestGoogleBooksSeriesInfo:
    def test_detects_series(self, detector, google_books_series_item):
        result = detector.detect(google_books_series_item)
        assert result["is_series"] is True

    def test_series_name(self, detector, google_books_series_item):
        result = detector.detect(google_books_series_item)
        assert result["series_name"] == "Harry Potter"

    def test_series_id(self, detector, google_books_series_item):
        result = detector.detect(google_books_series_item)
        assert result["series_id"] == "hp_series_001"

    def test_position(self, detector, google_books_series_item):
        result = detector.detect(google_books_series_item)
        assert result["position"] == 2

    def test_confidence_high(self, detector, google_books_series_item):
        result = detector.detect(google_books_series_item)
        assert result["confidence"] == 0.9

    def test_missing_display_number_lower_confidence(self, detector):
        item = {
            "source": "google_books",
            "seriesInfo": {
                "series": [{"seriesId": "abc", "seriesName": "Dune"}]
            },
        }
        result = detector.detect(item)
        assert result["is_series"] is True
        assert result["position"] is None
        assert result["confidence"] == 0.85

    def test_empty_series_list_not_detected(self, detector):
        item = {
            "source": "google_books",
            "seriesInfo": {"series": []},
        }
        result = detector.detect(item)
        assert result["is_series"] is False

    def test_missing_series_name_not_detected(self, detector):
        item = {
            "source": "google_books",
            "seriesInfo": {
                "series": [{"seriesId": "abc"}]
            },
        }
        result = detector.detect(item)
        assert result["is_series"] is False


# Tests — Title Pattern Rule 3

class TestTitlePatternDetection:
    def test_book_number_detected(self, detector, title_pattern_item):
        result = detector.detect(title_pattern_item)
        assert result["is_series"] is True
        assert result["position"] == 2

    def test_series_name_cleaned(self, detector, title_pattern_item):
        result = detector.detect(title_pattern_item)
        assert "Book 2" not in result["series_name"]

    def test_confidence_medium(self, detector, title_pattern_item):
        result = detector.detect(title_pattern_item)
        assert result["confidence"] == 0.6

    def test_hash_number_pattern(self, detector):
        item = {"title": "Batman #42", "source": "google_books"}
        result = detector.detect(item)
        assert result["is_series"] is True
        assert result["position"] == 42

    def test_volume_pattern(self, detector):
        item = {"title": "Naruto Vol. 3", "source": "google_books"}
        result = detector.detect(item)
        assert result["is_series"] is True
        assert result["position"] == 3

    def test_part_pattern(self, detector):
        item = {"title": "The Dark Tower Part 4", "source": "google_books"}
        result = detector.detect(item)
        assert result["is_series"] is True
        assert result["position"] == 4

    def test_slugified_series_id(self, detector, title_pattern_item):
        result = detector.detect(title_pattern_item)
        assert " " not in result["series_id"]


# Tests — Keyword Rule 4

class TestKeywordDetection:
    def test_saga_keyword(self, detector, keyword_item):
        result = detector.detect(keyword_item)
        assert result["is_series"] is True

    def test_no_position(self, detector, keyword_item):
        result = detector.detect(keyword_item)
        assert result["position"] is None

    def test_confidence_low(self, detector, keyword_item):
        result = detector.detect(keyword_item)
        assert result["confidence"] == 0.4

    def test_chronicles_keyword(self, detector):
        item = {"title": "The Chronicles of Narnia", "source": "google_books"}
        result = detector.detect(item)
        assert result["is_series"] is True

    def test_trilogy_keyword(self, detector):
        item = {"title": "His Dark Materials Trilogy", "source": "google_books"}
        result = detector.detect(item)
        assert result["is_series"] is True


# Tests — No Series

class TestNoSeries:
    def test_non_series_book(self, detector, non_series_item):
        result = detector.detect(non_series_item)
        assert result["is_series"] is False

    def test_confidence_zero(self, detector, non_series_item):
        result = detector.detect(non_series_item)
        assert result["confidence"] == 0.0

    def test_all_none(self, detector, non_series_item):
        result = detector.detect(non_series_item)
        assert result["series_name"] is None
        assert result["series_id"] is None
        assert result["position"] is None

    def test_empty_item(self, detector):
        result = detector.detect({})
        assert result["is_series"] is False

    def test_none_title(self, detector):
        result = detector.detect({"title": None, "source": "google_books"})
        assert result["is_series"] is False