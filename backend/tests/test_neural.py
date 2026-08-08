"""Tests for NeuralRecommender."""

from __future__ import annotations

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import keras
import pytest

from src.ml import NeuralRecommender


@pytest.fixture(scope="module")
def ratings() -> list[dict]:
    return [
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 3.0},
        {"user_id": "u1", "content_id": "b3", "rating": 4.0},
        {"user_id": "u2", "content_id": "b1", "rating": 4.0},
        {"user_id": "u2", "content_id": "b3", "rating": 5.0},
        {"user_id": "u2", "content_id": "b4", "rating": 2.0},
        {"user_id": "u3", "content_id": "b2", "rating": 5.0},
        {"user_id": "u3", "content_id": "b4", "rating": 4.0},
    ]


@pytest.fixture(scope="module")
def fitted_model(ratings: list[dict]) -> NeuralRecommender:
    keras.utils.set_random_seed(42)
    model = NeuralRecommender(n_factors=8, epochs=3, batch_size=4)
    model.fit(ratings)
    return model


def test_default_params() -> None:
    model = NeuralRecommender()
    assert model.n_factors == 16
    assert model.epochs == 10
    assert model.batch_size == 32
    assert model.min_ratings == 2


def test_custom_params() -> None:
    model = NeuralRecommender(n_factors=8, epochs=5, batch_size=16, min_ratings=3)
    assert model.n_factors == 8
    assert model.epochs == 5
    assert model.batch_size == 16
    assert model.min_ratings == 3


def test_not_fitted_by_default() -> None:
    model = NeuralRecommender()
    assert model.is_fitted is False


def test_fit_returns_self(ratings: list[dict]) -> None:
    keras.utils.set_random_seed(42)
    model = NeuralRecommender(n_factors=4, epochs=2, batch_size=4)
    result = model.fit(ratings)
    assert result is model


def test_fit_sets_fitted_flag(fitted_model: NeuralRecommender) -> None:
    assert fitted_model.is_fitted is True


def test_fit_too_few_ratings() -> None:
    model = NeuralRecommender(min_ratings=3)
    result = model.fit(
        [
            {"user_id": "u1", "content_id": "b1", "rating": 5.0},
            {"user_id": "u1", "content_id": "b2", "rating": 4.0},
        ]
    )
    assert result is model
    assert model.is_fitted is False


def test_fit_string_coercion() -> None:
    keras.utils.set_random_seed(42)
    model = NeuralRecommender(n_factors=4, epochs=2, batch_size=2)
    model.fit(
        [
            {"user_id": 1, "content_id": 100, "rating": 5.0},
            {"user_id": 2, "content_id": 100, "rating": 3.0},
            {"user_id": 1, "content_id": 101, "rating": 4.0},
        ]
    )
    assert model.is_fitted is True
    assert isinstance(model.score("1", "100"), float)


def test_refit_resets_state(ratings: list[dict]) -> None:
    keras.utils.set_random_seed(42)
    model = NeuralRecommender(n_factors=4, epochs=2, batch_size=4)
    model.fit(ratings)
    assert model.is_fitted is True

    model.fit([{"user_id": "u1", "content_id": "b1", "rating": 5.0}])
    assert model.is_fitted is False


def test_recommend_returns_list(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=3)
    assert isinstance(result, list)


def test_recommend_returns_strings(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=3)
    assert all(isinstance(item, str) for item in result)


def test_recommend_respects_n(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=2)
    assert len(result) <= 2


def test_recommend_unknown_user(fitted_model: NeuralRecommender) -> None:
    assert fitted_model.recommend("u999", n=5) == []


def test_recommend_not_fitted() -> None:
    model = NeuralRecommender()
    assert model.recommend("u1", n=5) == []


def test_recommend_exclude_ids(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=10, exclude_ids=["b1", "b2"])
    assert "b1" not in result
    assert "b2" not in result


def test_recommend_all_excluded_returns_empty(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=10, exclude_ids=["b1", "b2", "b3", "b4"])
    assert result == []


def test_recommend_has_no_duplicates(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=10)
    assert len(result) == len(set(result))


def test_recommend_with_large_n_is_bounded(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.recommend("u1", n=100)
    assert len(result) <= 4


def test_score_returns_float(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.score("u1", "b1")
    assert isinstance(result, float)


def test_score_unknown_user_returns_zero(fitted_model: NeuralRecommender) -> None:
    assert fitted_model.score("u999", "b1") == 0.0


def test_score_unknown_item_returns_zero(fitted_model: NeuralRecommender) -> None:
    assert fitted_model.score("u1", "b999") == 0.0


def test_score_not_fitted_returns_zero() -> None:
    model = NeuralRecommender()
    assert model.score("u1", "b1") == 0.0


def test_get_similar_items_returns_list(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.get_similar_items("b1", n=2)
    assert isinstance(result, list)


def test_get_similar_items_excludes_self(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.get_similar_items("b1", n=10)
    assert "b1" not in result


def test_get_similar_items_respects_n(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.get_similar_items("b1", n=2)
    assert len(result) <= 2


def test_get_similar_items_unknown_item(fitted_model: NeuralRecommender) -> None:
    assert fitted_model.get_similar_items("b999", n=3) == []


def test_get_similar_items_not_fitted() -> None:
    model = NeuralRecommender()
    assert model.get_similar_items("b1", n=3) == []


def test_get_similar_items_has_no_duplicates(fitted_model: NeuralRecommender) -> None:
    result = fitted_model.get_similar_items("b1", n=10)
    assert len(result) == len(set(result))


def test_import_from_ml_package() -> None:
    from src.ml import NeuralRecommender as ImportedNeuralRecommender

    assert ImportedNeuralRecommender is NeuralRecommender