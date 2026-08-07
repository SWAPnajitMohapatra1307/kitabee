"""Tests for CollaborativeFilter."""

import pytest

from src.ml.collaborative import CollaborativeFilter


# Fixtures


@pytest.fixture
def ratings():
    """Minimal rating dataset with 3 users and 5 items."""
    return [
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 4.0},
        {"user_id": "u1", "content_id": "b3", "rating": 3.0},
        {"user_id": "u2", "content_id": "b1", "rating": 5.0},
        {"user_id": "u2", "content_id": "b2", "rating": 4.0},
        {"user_id": "u2", "content_id": "b4", "rating": 5.0},
        {"user_id": "u3", "content_id": "b5", "rating": 5.0},
        {"user_id": "u3", "content_id": "b4", "rating": 4.0},
    ]


@pytest.fixture
def fitted_filter(ratings):
    """CollaborativeFilter fitted on minimal dataset."""
    cf = CollaborativeFilter(n_neighbors=5)
    cf.fit(ratings)
    return cf


# Init tests


def test_init_default_n_neighbors():
    cf = CollaborativeFilter()
    assert cf._n_neighbors == 5


def test_init_custom_n_neighbors():
    cf = CollaborativeFilter(n_neighbors=3)
    assert cf._n_neighbors == 3


def test_is_fitted_false_before_fit():
    cf = CollaborativeFilter()
    assert cf.is_fitted is False


def test_is_fitted_true_after_fit(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    assert cf.is_fitted is True


# Fit tests


def test_fit_returns_self(ratings):
    cf = CollaborativeFilter()
    result = cf.fit(ratings)
    assert result is cf


def test_fit_empty_data_does_not_crash():
    cf = CollaborativeFilter()
    cf.fit([])
    assert cf.is_fitted is False


def test_fit_builds_user_index(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    assert "u1" in cf._user_index
    assert "u2" in cf._user_index
    assert "u3" in cf._user_index


def test_fit_builds_item_index(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    for book in ["b1", "b2", "b3", "b4", "b5"]:
        assert book in cf._item_index


def test_fit_matrix_shape(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    assert cf._matrix.shape == (3, 5)


def test_fit_matrix_values(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    u1 = cf._user_index["u1"]
    b1 = cf._item_index["b1"]
    assert cf._matrix[u1, b1] == 5.0


def test_fit_user_rated_tracks_items(ratings):
    cf = CollaborativeFilter()
    cf.fit(ratings)
    assert "b1" in cf._user_rated["u1"]
    assert "b2" in cf._user_rated["u1"]
    assert "b3" in cf._user_rated["u1"]


def test_fit_string_coercion():
    cf = CollaborativeFilter()
    cf.fit([{"user_id": 1, "content_id": 100, "rating": 5.0}])
    assert "1" in cf._user_index
    assert "100" in cf._item_index


# find_similar_users tests


def test_find_similar_users_returns_list(fitted_filter):
    result = fitted_filter.find_similar_users("u1")
    assert isinstance(result, list)


def test_find_similar_users_u1_finds_u2(fitted_filter):
    result = fitted_filter.find_similar_users("u1")
    assert "u2" in result


def test_find_similar_users_excludes_self(fitted_filter):
    result = fitted_filter.find_similar_users("u1")
    assert "u1" not in result


def test_find_similar_users_unknown_user_returns_empty(fitted_filter):
    result = fitted_filter.find_similar_users("unknown")
    assert result == []


def test_find_similar_users_not_fitted_returns_empty(ratings):
    cf = CollaborativeFilter()
    result = cf.find_similar_users("u1")
    assert result == []


def test_find_similar_users_respects_n(fitted_filter):
    result = fitted_filter.find_similar_users("u1", n=1)
    assert len(result) <= 1


def test_find_similar_users_zero_similarity_excluded():
    cf = CollaborativeFilter()
    cf.fit([
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 5.0},
        {"user_id": "u2", "content_id": "b3", "rating": 5.0},
        {"user_id": "u2", "content_id": "b4", "rating": 5.0},
    ])
    result = cf.find_similar_users("u1")
    assert "u2" not in result


# recommend tests


def test_recommend_returns_list(fitted_filter):
    result = fitted_filter.recommend("u1")
    assert isinstance(result, list)


def test_recommend_excludes_already_rated(fitted_filter):
    result = fitted_filter.recommend("u1")
    already_rated = {"b1", "b2", "b3"}
    for item in result:
        assert item not in already_rated


def test_recommend_returns_unseen_items(fitted_filter):
    result = fitted_filter.recommend("u1")
    assert "b4" in result


def test_recommend_cold_start_returns_empty():
    cf = CollaborativeFilter()
    cf.fit([
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u2", "content_id": "b1", "rating": 4.0},
        {"user_id": "u2", "content_id": "b2", "rating": 5.0},
    ])
    # u1 has only 1 rating — cold start
    result = cf.recommend("u1")
    assert result == []


def test_recommend_unknown_user_returns_empty(fitted_filter):
    result = fitted_filter.recommend("ghost")
    assert result == []


def test_recommend_not_fitted_returns_empty():
    cf = CollaborativeFilter()
    result = cf.recommend("u1")
    assert result == []


def test_recommend_respects_n(fitted_filter):
    result = fitted_filter.recommend("u1", n=1)
    assert len(result) <= 1


def test_recommend_no_similar_users_returns_empty():
    cf = CollaborativeFilter()
    cf.fit([
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 5.0},
    ])
    # only one user — no similar users possible
    result = cf.recommend("u1")
    assert result == []


def test_recommend_higher_rated_items_ranked_first():
    cf = CollaborativeFilter()
    cf.fit([
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 5.0},
        {"user_id": "u2", "content_id": "b1", "rating": 5.0},
        {"user_id": "u2", "content_id": "b2", "rating": 5.0},
        {"user_id": "u2", "content_id": "b3", "rating": 5.0},
        {"user_id": "u2", "content_id": "b4", "rating": 1.0},
    ])
    result = cf.recommend("u1")
    if "b3" in result and "b4" in result:
        assert result.index("b3") < result.index("b4")