import math
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import pytest

from src.ml.evaluation import RecommendationEvaluator


class TestRecommendationEvaluator:
    def setup_method(self) -> None:
        self.evaluator = RecommendationEvaluator()

    def test_precision_at_k_returns_expected_value(self) -> None:
        recommended = ["a", "b", "c"]
        relevant = ["a", "c", "d"]

        result = self.evaluator.precision_at_k(recommended, relevant, k=3)

        assert result == pytest.approx(2 / 3)

    def test_precision_at_k_penalizes_short_recommendation_list(self) -> None:
        recommended = ["a"]
        relevant = ["a"]

        result = self.evaluator.precision_at_k(recommended, relevant, k=3)

        assert result == pytest.approx(1 / 3)

    def test_precision_at_k_returns_zero_for_non_positive_k(self) -> None:
        result = self.evaluator.precision_at_k(["a", "b"], ["a"], k=0)

        assert result == 0.0

    def test_precision_at_k_returns_zero_for_empty_inputs(self) -> None:
        assert self.evaluator.precision_at_k([], ["a"], k=3) == 0.0
        assert self.evaluator.precision_at_k(["a"], [], k=3) == 0.0

    def test_recall_at_k_returns_expected_value(self) -> None:
        recommended = ["a", "b", "c"]
        relevant = ["a", "c", "d"]

        result = self.evaluator.recall_at_k(recommended, relevant, k=3)

        assert result == pytest.approx(2 / 3)

    def test_recall_at_k_returns_zero_for_non_positive_k(self) -> None:
        result = self.evaluator.recall_at_k(["a", "b"], ["a"], k=-1)

        assert result == 0.0

    def test_recall_at_k_returns_zero_for_empty_inputs(self) -> None:
        assert self.evaluator.recall_at_k([], ["a"], k=3) == 0.0
        assert self.evaluator.recall_at_k(["a"], [], k=3) == 0.0

    def test_ndcg_at_k_returns_one_for_perfect_ranking(self) -> None:
        recommended = ["a", "b", "c"]
        relevant = ["a", "b"]

        result = self.evaluator.ndcg_at_k(recommended, relevant, k=2)

        assert result == 1.0

    def test_ndcg_at_k_returns_expected_value_for_imperfect_ranking(self) -> None:
        recommended = ["x", "a", "b"]
        relevant = ["a", "b"]

        result = self.evaluator.ndcg_at_k(recommended, relevant, k=3)

        expected_dcg = (1 / math.log2(3)) + (1 / math.log2(4))
        expected_idcg = 1 + (1 / math.log2(3))

        assert result == pytest.approx(expected_dcg / expected_idcg)

    def test_ndcg_at_k_returns_zero_when_no_hits(self) -> None:
        recommended = ["x", "y", "z"]
        relevant = ["a", "b"]

        result = self.evaluator.ndcg_at_k(recommended, relevant, k=3)

        assert result == 0.0

    def test_ndcg_at_k_returns_zero_for_invalid_inputs(self) -> None:
        assert self.evaluator.ndcg_at_k(["a"], ["a"], k=0) == 0.0
        assert self.evaluator.ndcg_at_k([], ["a"], k=3) == 0.0
        assert self.evaluator.ndcg_at_k(["a"], [], k=3) == 0.0

    def test_catalog_coverage_returns_expected_value(self) -> None:
        all_recommendations = [["a", "b"], ["b", "c"], ["x"]]
        catalog = ["a", "b", "c", "d"]

        result = self.evaluator.catalog_coverage(all_recommendations, catalog)

        assert result == pytest.approx(3 / 4)

    def test_catalog_coverage_returns_zero_for_empty_inputs(self) -> None:
        assert self.evaluator.catalog_coverage([], ["a", "b"]) == 0.0
        assert self.evaluator.catalog_coverage([["a"]], []) == 0.0

    def test_intra_list_diversity_returns_one_for_orthogonal_vectors(self) -> None:
        recommended = ["a", "b"]
        item_vectors = {
            "a": [1.0, 0.0],
            "b": [0.0, 1.0],
        }

        result = self.evaluator.intra_list_diversity(recommended, item_vectors)

        assert result == 1.0

    def test_intra_list_diversity_returns_zero_for_identical_vectors(self) -> None:
        recommended = ["a", "b"]
        item_vectors = {
            "a": [1.0, 1.0],
            "b": [1.0, 1.0],
        }

        result = self.evaluator.intra_list_diversity(recommended, item_vectors)

        assert result == 0.0

    def test_intra_list_diversity_returns_zero_when_fewer_than_two_vectors_exist(self) -> None:
        recommended = ["a", "b"]
        item_vectors = {
            "a": [1.0, 0.0],
        }

        result = self.evaluator.intra_list_diversity(recommended, item_vectors)

        assert result == 0.0

    def test_evaluate_batch_returns_aggregate_metrics_without_diversity(self) -> None:
        recommendations = {
            "u1": ["a", "b"],
            "u2": ["c", "d"],
        }
        ground_truth = {
            "u1": ["a"],
            "u2": ["x"],
        }
        catalog = ["a", "b", "c", "d", "e"]

        result = self.evaluator.evaluate_batch(
            recommendations=recommendations,
            ground_truth=ground_truth,
            catalog=catalog,
            k=1,
        )

        assert result["mean_precision_at_k"] == 0.5
        assert result["mean_recall_at_k"] == 0.5
        assert result["mean_ndcg_at_k"] == 0.5
        assert result["catalog_coverage"] == pytest.approx(4 / 5)
        assert result["mean_diversity"] == 0.0
        assert result["k"] == 1
        assert result["n_users"] == 2

    def test_evaluate_batch_returns_diversity_when_vectors_provided(self) -> None:
        recommendations = {
            "u1": ["a", "b"],
        }
        ground_truth = {
            "u1": ["a"],
        }
        catalog = ["a", "b", "c"]
        item_vectors = {
            "a": [1.0, 0.0],
            "b": [0.0, 1.0],
        }

        result = self.evaluator.evaluate_batch(
            recommendations=recommendations,
            ground_truth=ground_truth,
            catalog=catalog,
            item_vectors=item_vectors,
            k=1,
        )

        assert result["mean_precision_at_k"] == 1.0
        assert result["mean_recall_at_k"] == 1.0
        assert result["mean_ndcg_at_k"] == 1.0
        assert result["catalog_coverage"] == pytest.approx(2 / 3)
        assert result["mean_diversity"] == 1.0
        assert result["k"] == 1
        assert result["n_users"] == 1

    def test_evaluate_batch_returns_zero_metrics_for_empty_recommendations(self) -> None:
        result = self.evaluator.evaluate_batch(
            recommendations={},
            ground_truth={"u1": ["a"]},
            catalog=["a", "b"],
            k=5,
        )

        assert result == {
            "mean_precision_at_k": 0.0,
            "mean_recall_at_k": 0.0,
            "mean_ndcg_at_k": 0.0,
            "catalog_coverage": 0.0,
            "mean_diversity": 0.0,
            "k": 5,
            "n_users": 0,
        }

    def test_cosine_similarity_returns_zero_for_mismatched_lengths(self) -> None:
        result = self.evaluator._cosine_similarity([1.0, 0.0], [1.0])

        assert result == 0.0

    def test_cosine_similarity_returns_zero_for_zero_vector(self) -> None:
        result = self.evaluator._cosine_similarity([0.0, 0.0], [1.0, 1.0])

        assert result == 0.0

    def test_cosine_similarity_returns_one_for_identical_vectors(self) -> None:
        result = self.evaluator._cosine_similarity([1.0, 2.0], [1.0, 2.0])

        assert result == pytest.approx(1.0)