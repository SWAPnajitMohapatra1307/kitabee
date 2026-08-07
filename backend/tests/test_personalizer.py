"""Tests for Personalizer."""

import pytest

from src.ml.personalizer import Personalizer


# Fixtures


@pytest.fixture
def personalizer():
    return Personalizer()


@pytest.fixture
def metadata():
    return [
        {"content_id": "b1", "title": "Dune", "genre": "sci-fi", "mood": "dark"},
        {"content_id": "b2", "title": "Foundation", "genre": "sci-fi", "mood": "educational"},
        {"content_id": "b3", "title": "HP1", "genre": "fantasy", "mood": "adventurous"},
        {"content_id": "b4", "title": "HP2", "genre": "fantasy", "mood": "adventurous"},
        {"content_id": "b5", "title": "Hobbit", "genre": "fantasy", "mood": "adventurous"},
    ]


@pytest.fixture
def user_ratings():
    return [
        {"content_id": "b1", "rating": 5.0},
        {"content_id": "b2", "rating": 4.0},
    ]


# Init tests


def test_personalizer_instantiates():
    p = Personalizer()
    assert p is not None


# rank tests


def test_rank_returns_list(personalizer, metadata, user_ratings):
    result = personalizer.rank(["b3", "b4", "b5"], user_ratings, metadata)
    assert isinstance(result, list)


def test_rank_returns_same_ids(personalizer, metadata, user_ratings):
    candidates = ["b3", "b4", "b5"]
    result = personalizer.rank(candidates, user_ratings, metadata)
    assert set(result) == set(candidates)


def test_rank_prefers_genre_match(personalizer, metadata):
    ratings = [{"content_id": "b1", "rating": 5.0},
               {"content_id": "b2", "rating": 5.0}]
    # b2 is sci-fi, b3 is fantasy — user loves sci-fi
    # b2 already rated, candidates are b3(fantasy) and new sci-fi
    extra_meta = metadata + [
        {"content_id": "b6", "title": "Asimov", "genre": "sci-fi", "mood": "educational"}
    ]
    result = personalizer.rank(["b3", "b6"], ratings, extra_meta)
    assert result[0] == "b6"


def test_rank_empty_candidates_returns_empty(personalizer, metadata, user_ratings):
    result = personalizer.rank([], user_ratings, metadata)
    assert result == []


def test_rank_no_ratings_returns_candidates(personalizer, metadata):
    candidates = ["b1", "b2", "b3"]
    result = personalizer.rank(candidates, [], metadata)
    assert set(result) == set(candidates)


def test_rank_no_metadata_returns_candidates(personalizer, user_ratings):
    candidates = ["b1", "b2", "b3"]
    result = personalizer.rank(candidates, user_ratings, [])
    assert set(result) == set(candidates)


def test_rank_mood_match_adds_score(personalizer, metadata):
    ratings = [{"content_id": "b3", "rating": 5.0},
               {"content_id": "b4", "rating": 5.0}]
    # b5 matches mood=adventurous (same as b3, b4)
    # b2 does not match mood
    result = personalizer.rank(["b2", "b5"], ratings, metadata)
    assert result[0] == "b5"


def test_rank_length_unchanged(personalizer, metadata, user_ratings):
    candidates = ["b3", "b4", "b5"]
    result = personalizer.rank(candidates, user_ratings, metadata)
    assert len(result) == 3


# filter_by_preference tests


def test_filter_both_returns_all(personalizer):
    items = [
        {"source": "gb_123", "title": "Book"},
        {"source": "cv_456", "title": "Comic"},
    ]
    result = personalizer.filter_by_preference(items, "both")
    assert len(result) == 2


def test_filter_books_excludes_comics(personalizer):
    items = [
        {"source": "gb_123", "title": "Book"},
        {"source": "cv_456", "title": "Comic"},
    ]
    result = personalizer.filter_by_preference(items, "books")
    assert len(result) == 1
    assert result[0]["title"] == "Book"


def test_filter_comics_excludes_books(personalizer):
    items = [
        {"source": "gb_123", "title": "Book"},
        {"source": "cv_456", "title": "Comic"},
    ]
    result = personalizer.filter_by_preference(items, "comics")
    assert len(result) == 1
    assert result[0]["title"] == "Comic"


def test_filter_unknown_preference_returns_all(personalizer):
    items = [
        {"source": "gb_123", "title": "Book"},
        {"source": "cv_456", "title": "Comic"},
    ]
    result = personalizer.filter_by_preference(items, "unknown")
    assert len(result) == 2


def test_filter_empty_items_returns_empty(personalizer):
    result = personalizer.filter_by_preference([], "books")
    assert result == []


def test_filter_cv_prefix_detected_as_comic(personalizer):
    items = [{"source": "cv_001", "title": "Batman"}]
    result = personalizer.filter_by_preference(items, "books")
    assert result == []


def test_filter_no_source_key_treated_as_book(personalizer):
    items = [{"title": "Mystery Book"}]
    result = personalizer.filter_by_preference(items, "books")
    assert len(result) == 1


# inject_because_you_loved tests


def test_inject_returns_dict(personalizer, metadata, user_ratings):
    result = personalizer.inject_because_you_loved(
        ["b3", "b4"], user_ratings, metadata
    )
    assert isinstance(result, dict)


def test_inject_returns_none_no_ratings(personalizer, metadata):
    result = personalizer.inject_because_you_loved(["b3"], [], metadata)
    assert result is None


def test_inject_returns_none_no_recommendations(personalizer, metadata, user_ratings):
    result = personalizer.inject_because_you_loved([], user_ratings, metadata)
    assert result is None


def test_inject_anchor_is_highest_rated(personalizer, metadata):
    ratings = [
        {"content_id": "b1", "rating": 5.0},
        {"content_id": "b2", "rating": 2.0},
    ]
    result = personalizer.inject_because_you_loved(["b3"], ratings, metadata)
    assert result["anchor"] == "Dune"


def test_inject_label_contains_anchor(personalizer, metadata, user_ratings):
    result = personalizer.inject_because_you_loved(
        ["b3", "b4"], user_ratings, metadata
    )
    assert "Because you loved" in result["label"]
    assert result["anchor"] in result["label"]


def test_inject_items_match_recommendations(personalizer, metadata, user_ratings):
    recs = ["b3", "b4", "b5"]
    result = personalizer.inject_because_you_loved(recs, user_ratings, metadata)
    assert result["items"] == recs


def test_inject_anchor_fallback_to_id_when_no_title(personalizer):
    ratings = [{"content_id": "b99", "rating": 5.0}]
    result = personalizer.inject_because_you_loved(
        ["b1"], ratings, []
    )
    assert result["anchor"] == "b99"
    assert "b99" in result["label"]


def test_inject_keys_present(personalizer, metadata, user_ratings):
    result = personalizer.inject_because_you_loved(
        ["b3"], user_ratings, metadata
    )
    assert "label" in result
    assert "anchor" in result
    assert "items" in result