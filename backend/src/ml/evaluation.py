"""
ML evaluation metrics for recommendation quality assessment.

Provides precision@k, recall@k, NDCG@k, catalog coverage,
and intra-list diversity measurements.
"""

from __future__ import annotations

import math
from typing import Any


class RecommendationEvaluator:
    """
    Evaluates recommendation quality using standard IR metrics.

    All methods are stateless and accept raw lists with no DB dependency.
    """

    def precision_at_k(
        self,
        recommended: list[str],
        relevant: list[str],
        k: int,
    ) -> float:
        """
        Fraction of top-k recommendations that are relevant.

        Args:
            recommended: Ordered list of recommended item IDs.
            relevant: Ground-truth relevant item IDs.
            k: Cutoff rank.

        Returns:
            Float in [0.0, 1.0].
        """
        if k <= 0:
            return 0.0
        if not recommended or not relevant:
            return 0.0

        top_k = recommended[:k]
        relevant_set = set(relevant)
        hits = sum(1 for item in top_k if item in relevant_set)
        return hits / k

    def recall_at_k(
        self,
        recommended: list[str],
        relevant: list[str],
        k: int,
    ) -> float:
        """
        Fraction of relevant items that appear in top-k recommendations.

        Args:
            recommended: Ordered list of recommended item IDs.
            relevant: Ground-truth relevant item IDs.
            k: Cutoff rank.

        Returns:
            Float in [0.0, 1.0].
        """
        if k <= 0:
            return 0.0
        if not recommended or not relevant:
            return 0.0

        top_k = recommended[:k]
        relevant_set = set(relevant)
        hits = sum(1 for item in top_k if item in relevant_set)
        return hits / len(relevant_set)

    def ndcg_at_k(
        self,
        recommended: list[str],
        relevant: list[str],
        k: int,
    ) -> float:
        """
        Normalized Discounted Cumulative Gain at k.

        Measures ranking quality by rewarding relevant items ranked earlier.

        Args:
            recommended: Ordered list of recommended item IDs.
            relevant: Ground-truth relevant item IDs.
            k: Cutoff rank.

        Returns:
            Float in [0.0, 1.0].
        """
        if k <= 0:
            return 0.0
        if not recommended or not relevant:
            return 0.0

        relevant_set = set(relevant)
        top_k = recommended[:k]

        dcg = 0.0
        for rank, item in enumerate(top_k, start=1):
            if item in relevant_set:
                dcg += 1.0 / math.log2(rank + 1)

        ideal_hits = min(len(relevant_set), k)
        idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))

        if idcg == 0.0:
            return 0.0

        return dcg / idcg

    def catalog_coverage(
        self,
        all_recommendations: list[list[str]],
        catalog: list[str],
    ) -> float:
        """
        Fraction of catalog items that appear in any recommendation list.

        Args:
            all_recommendations: Recommendation lists across users.
            catalog: Full list of available item IDs.

        Returns:
            Float in [0.0, 1.0].
        """
        if not catalog:
            return 0.0
        if not all_recommendations:
            return 0.0

        catalog_set = set(catalog)
        recommended_set: set[str] = set()

        for recs in all_recommendations:
            recommended_set.update(recs)

        covered = recommended_set & catalog_set
        return len(covered) / len(catalog_set)

    def intra_list_diversity(
        self,
        recommended: list[str],
        item_vectors: dict[str, list[float]],
    ) -> float:
        """
        Average pairwise cosine distance between recommended items.

        Higher values mean more diverse recommendations.

        Args:
            recommended: Ordered list of recommended item IDs.
            item_vectors: Mapping from item ID to feature vector.

        Returns:
            Average pairwise cosine distance. Returns 0.0 if fewer than
            2 recommended items have vectors.
        """
        if not recommended or not item_vectors:
            return 0.0

        vectors = [
            item_vectors[item]
            for item in recommended
            if item in item_vectors
        ]

        if len(vectors) < 2:
            return 0.0

        total_distance = 0.0
        pair_count = 0

        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                similarity = self._cosine_similarity(vectors[i], vectors[j])
                distance = 1.0 - similarity

                if math.isclose(distance, 0.0, rel_tol=0.0, abs_tol=1e-12):
                    distance = 0.0

                total_distance += distance
                pair_count += 1

        if pair_count == 0:
            return 0.0

        return total_distance / pair_count

    def evaluate_batch(
        self,
        recommendations: dict[str, list[str]],
        ground_truth: dict[str, list[str]],
        catalog: list[str],
        item_vectors: dict[str, list[float]] | None = None,
        k: int = 10,
    ) -> dict[str, Any]:
        """
        Evaluate recommendation quality across multiple users.

        Args:
            recommendations: Mapping of user_id to recommended item IDs.
            ground_truth: Mapping of user_id to relevant item IDs.
            catalog: Full list of available item IDs.
            item_vectors: Optional mapping of item_id to feature vector.
            k: Cutoff rank for ranking metrics.

        Returns:
            Dict containing aggregate metrics.
        """
        if not recommendations:
            return {
                "mean_precision_at_k": 0.0,
                "mean_recall_at_k": 0.0,
                "mean_ndcg_at_k": 0.0,
                "catalog_coverage": 0.0,
                "mean_diversity": 0.0,
                "k": k,
                "n_users": 0,
            }

        precisions = []
        recalls = []
        ndcgs = []
        diversities = []

        for user_id, recs in recommendations.items():
            relevant = ground_truth.get(user_id, [])
            precisions.append(self.precision_at_k(recs, relevant, k))
            recalls.append(self.recall_at_k(recs, relevant, k))
            ndcgs.append(self.ndcg_at_k(recs, relevant, k))

            if item_vectors:
                diversities.append(self.intra_list_diversity(recs, item_vectors))

        all_recommendations = list(recommendations.values())
        coverage = self.catalog_coverage(all_recommendations, catalog)
        mean_diversity = sum(diversities) / len(diversities) if diversities else 0.0

        return {
            "mean_precision_at_k": sum(precisions) / len(precisions),
            "mean_recall_at_k": sum(recalls) / len(recalls),
            "mean_ndcg_at_k": sum(ndcgs) / len(ndcgs),
            "catalog_coverage": coverage,
            "mean_diversity": mean_diversity,
            "k": k,
            "n_users": len(recommendations),
        }

    def _cosine_similarity(
        self,
        vec_a: list[float],
        vec_b: list[float],
    ) -> float:
        """
        Compute cosine similarity between two vectors.

        Returns 0.0 for zero vectors or mismatched lengths.
        """
        if len(vec_a) != len(vec_b):
            return 0.0

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = dot / (norm_a * norm_b)

        if math.isclose(similarity, 1.0, rel_tol=0.0, abs_tol=1e-12):
            return 1.0
        if math.isclose(similarity, -1.0, rel_tol=0.0, abs_tol=1e-12):
            return -1.0
        if math.isclose(similarity, 0.0, rel_tol=0.0, abs_tol=1e-12):
            return 0.0

        if similarity > 1.0:
            return 1.0
        if similarity < -1.0:
            return -1.0

        return similarity