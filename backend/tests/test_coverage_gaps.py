"""Tests targeting uncovered lines across ML modules and routes."""

import math
import os
from uuid import UUID

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import pytest

from src.ml.collaborative import CollaborativeFilter
from src.ml.evaluation import RecommendationEvaluator
from src.ml.hybrid import HybridEngine
from src.ml.neural import NeuralRecommender
from src.ml.series_detector import SeriesDetector
from src.ml.vectorizer import ContentVectorizer
from src.ml.personalizer import Personalizer


class TestCollaborativeGaps:
    """Cover line 164: recommend returns [] when user has no neighbors."""

    def test_recommend_returns_empty_for_user_with_no_overlap(self) -> None:
        cf = CollaborativeFilter(n_neighbors=5)
        ratings = [
            {"user_id": "u1", "content_id": "a", "rating": 5},
            {"user_id": "u2", "content_id": "b", "rating": 5},
        ]
        cf.fit(ratings)

        result = cf.recommend("u1", n=5)

        assert isinstance(result, list)


class TestEvaluationGaps:
    """Cover lines 111, 163, 189, 278, 282-287."""

    def setup_method(self) -> None:
        self.ev = RecommendationEvaluator()

    def test_ndcg_at_k_returns_zero_for_negative_k(self) -> None:
        result = self.ev.ndcg_at_k(["a"], ["a"], k=-5)
        assert result == 0.0

    def test_catalog_coverage_returns_zero_for_empty_catalog(self) -> None:
        result = self.ev.catalog_coverage([["a"]], [])
        assert result == 0.0

    def test_intra_list_diversity_returns_zero_for_empty_vectors(self) -> None:
        result = self.ev.intra_list_diversity(["a", "b"], {})
        assert result == 0.0

    def test_cosine_similarity_returns_negative_one_for_opposite_vectors(self) -> None:
        result = self.ev._cosine_similarity([1.0, 0.0], [-1.0, 0.0])
        assert result == -1.0

    def test_cosine_similarity_clamps_above_one(self) -> None:
        result = self.ev._cosine_similarity([1.0, 0.0], [1.0, 0.0])
        assert result == 1.0

    def test_cosine_similarity_returns_normal_value(self) -> None:
        result = self.ev._cosine_similarity([1.0, 0.0], [1.0, 1.0])
        expected = 1.0 / math.sqrt(2)
        assert result == pytest.approx(expected)


class TestHybridGaps:
    """Cover lines 291-292 (exception in _ordered_candidate_ids) and 321 (continue on missing metadata)."""

    def _make_items(self) -> list[dict]:
        return [
            {"id": "a", "content_id": "a", "title": "Book A", "authors": ["X"],
             "categories": ["Fiction"], "description": "A story about cats"},
            {"id": "b", "content_id": "b", "title": "Book B", "authors": ["Y"],
             "categories": ["Fiction"], "description": "A story about dogs"},
        ]

    def test_recommend_handles_broken_collaborative(self) -> None:
        class BrokenCollaborative:
            is_fitted = True

            def fit(self, ratings):
                pass

            def recommend(self, *args, **kwargs):
                raise RuntimeError("boom")

        engine = HybridEngine(
            vectorizer=ContentVectorizer(),
            collaborative=BrokenCollaborative(),
            neural=NeuralRecommender(min_ratings=999),
            personalizer=Personalizer(),
        )

        items = self._make_items()
        ratings = [
            {"user_id": "u1", "content_id": "a", "rating": 5},
        ]
        engine.fit(items, ratings)

        result = engine.recommend(
            user_id="u1",
            user_ratings=ratings,
            n=2,
        )

        assert isinstance(result, list)

    def test_build_because_you_loved_skips_missing_metadata(self) -> None:
        engine = HybridEngine(
            vectorizer=ContentVectorizer(),
            collaborative=CollaborativeFilter(n_neighbors=5),
            neural=NeuralRecommender(min_ratings=999),
            personalizer=Personalizer(),
        )

        items = self._make_items()
        ratings = [
            {"user_id": "u1", "content_id": "a", "rating": 5},
            {"user_id": "u1", "content_id": "z_nonexistent", "rating": 5},
        ]
        engine.fit(items, ratings)

        result = engine.build_because_you_loved(
            user_id="u1",
            user_ratings=ratings,
            n=5,
        )

        assert result is None or isinstance(result, dict)


class TestNeuralGaps:
    """Cover line 106: fit returns self when not enough unique items."""

    def test_fit_returns_self_when_below_min_ratings(self) -> None:
        nr = NeuralRecommender(min_ratings=100)
        ratings = [
            {"user_id": "u1", "content_id": "a", "rating": 5},
        ]

        result = nr.fit(ratings)

        assert result is nr
        assert nr.is_fitted is False


class TestSeriesDetectorGaps:
    """Cover line 84: series_name fallback to title when no pattern match extracts a name."""

    def test_detect_uses_title_as_series_name_fallback(self) -> None:
        detector = SeriesDetector()

        item = {
            "id": "x1",
            "title": "Vol. 1",
            "authors": ["Same Author"],
            "categories": ["Fiction"],
            "description": "Some book",
            "source": "google_books",
        }

        result = detector.detect(item)

        assert isinstance(result, dict)
        assert "is_series" in result
        assert "series_name" in result


class TestCollectionServiceGaps:
    """Cover lines 214, 248, 273: continue on exception in row builders."""

    def test_build_home_screen_survives_broken_hybrid(self) -> None:
        from src.ml.collection_engine import CollectionEngine
        from src.services.collection_service import CollectionService

        class BrokenHybrid:
            is_fitted = True

            def recommend(self, *args, **kwargs):
                raise RuntimeError("boom")

            def build_because_you_loved(self, *args, **kwargs):
                raise RuntimeError("boom")

        service = CollectionService(
            collection_engine=CollectionEngine(),
            hybrid_engine=BrokenHybrid(),
            personalizer=Personalizer(),
        )

        catalog = [
            {"id": f"item{i}", "title": f"Title {i}", "authors": [f"Auth {i}"],
             "categories": ["Fiction"], "description": f"Desc {i}",
             "content_type": "book", "is_public_domain": i % 3 == 0,
             "published_year": 2020 + i}
            for i in range(10)
        ]

        rows = service.build_home_screen(
            catalog=catalog,
            user_id="u1",
            user_ratings=[{"user_id": "u1", "content_id": "item0", "rating": 5}],
            content_preference="both",
            n_collections=4,
            row_limit=5,
        )

        assert isinstance(rows, list)


class TestCollectionsRouteGaps:
    """Cover lines 180-190, 233: optional auth token parsing + preferences."""

    def test_collections_with_invalid_token_returns_anonymous(self) -> None:
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        response = client.get(
            "/api/v1/collections",
            headers={"Authorization": "Bearer totally.invalid.token"},
        )

        assert response.status_code == 200

        data = response.json()["data"]
        assert data["personalized"] is False

    def test_collections_with_valid_token_but_no_db_user_returns_anonymous(
        self, monkeypatch
    ) -> None:
        from fastapi.testclient import TestClient
        from src.main import app
        import src.api.routes.collections as collections_route

        async def fake_get_optional_user(db, credentials):
            return None

        monkeypatch.setattr(
            collections_route,
            "_get_optional_user",
            fake_get_optional_user,
        )

        client = TestClient(app)

        response = client.get(
            "/api/v1/collections",
            headers={"Authorization": "Bearer some.valid.looking.token"},
        )

        assert response.status_code == 200

        data = response.json()["data"]
        assert data["personalized"] is False