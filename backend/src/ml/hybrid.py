"""Hybrid recommendation engine combining multiple recommendation signals."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.ml.collaborative import CollaborativeFilter
from src.ml.neural import NeuralRecommender
from src.ml.personalizer import Personalizer
from src.ml.vectorizer import ContentVectorizer


class HybridEngine:
    """
    Blend content-based, collaborative, and neural recommendations.

    The engine accumulates scores from:
    - Content similarity around a user's highly rated items
    - Collaborative filtering recommendations
    - Neural recommender recommendations

    Final ordering is refined by the Personalizer.
    """

    def __init__(
        self,
        vectorizer: ContentVectorizer | None = None,
        collaborative: CollaborativeFilter | None = None,
        neural: NeuralRecommender | None = None,
        personalizer: Personalizer | None = None,
        content_weight: float = 1.0,
        collaborative_weight: float = 0.7,
        neural_weight: float = 0.7,
        max_seeds: int = 3,
        similar_per_seed: int = 10,
    ) -> None:
        self.vectorizer = vectorizer or ContentVectorizer()
        self.collaborative = collaborative or CollaborativeFilter()
        self.neural = neural or NeuralRecommender()
        self.personalizer = personalizer or Personalizer()

        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        self.neural_weight = neural_weight
        self.max_seeds = max_seeds
        self.similar_per_seed = similar_per_seed

        self._content_metadata: list[dict[str, Any]] = []
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        """Return whether fit() has been called."""
        return self._is_fitted

    def fit(
        self,
        items: list[dict[str, Any]],
        ratings: list[dict[str, Any]],
    ) -> "HybridEngine":
        """
        Fit underlying recommenders and store metadata.

        Parameters
        ----------
        items:
            Content metadata items used by the vectorizer.
        ratings:
            Explicit user ratings used by collaborative and neural models.
        """
        self._content_metadata = list(items or [])

        if items:
            self.vectorizer.fit(items)

        if ratings:
            self.collaborative.fit(ratings)
            self.neural.fit(ratings)

        self._is_fitted = True
        return self

    def recommend(
        self,
        user_id: str,
        user_ratings: list[dict[str, Any]] | None,
        content_metadata: list[dict[str, Any]] | None = None,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        """
        Return hybrid recommendations for a user.

        Parameters
        ----------
        user_id:
            User identifier.
        user_ratings:
            User rating history.
        content_metadata:
            Metadata for all available content.
            If omitted, metadata passed to fit() is used.
        n:
            Number of recommendations to return.
        exclude_ids:
            Additional content IDs to exclude.

        Returns
        -------
        list[str]
            Ranked content IDs.
        """
        metadata = self._resolve_metadata(content_metadata)
        if not metadata or n <= 0:
            return []

        ratings = list(user_ratings or [])
        excluded = {str(item_id) for item_id in (exclude_ids or [])}
        excluded.update(str(r["content_id"]) for r in ratings)

        combined_scores: dict[str, float] = defaultdict(float)
        limit = max(n * 2, self.similar_per_seed)

        for rating in self._top_seed_ratings(ratings):
            seed_id = str(rating["content_id"])
            seed_weight = max(float(rating["rating"]) - 3.0, 0.0)

            for result in self._safe_content_similar(seed_id, limit):
                candidate_id = str(result.get("content_id", ""))
                if not candidate_id or candidate_id in excluded:
                    continue

                similarity_score = float(result.get("score", 0.0))
                combined_scores[candidate_id] += (
                    self.content_weight * seed_weight * similarity_score
                )

        collaborative_ids = self._safe_recommend(
            recommender=self.collaborative,
            user_id=str(user_id),
            n=limit,
            exclude_ids=list(excluded),
        )
        self._add_ranked_scores(
            combined_scores,
            collaborative_ids,
            self.collaborative_weight,
            excluded,
        )

        neural_ids = self._safe_recommend(
            recommender=self.neural,
            user_id=str(user_id),
            n=limit,
            exclude_ids=list(excluded),
        )
        self._add_ranked_scores(
            combined_scores,
            neural_ids,
            self.neural_weight,
            excluded,
        )

        candidate_ids = self._ordered_candidate_ids(
            combined_scores,
            metadata,
            excluded,
        )

        ranked_ids = self.personalizer.rank(candidate_ids, ratings, metadata)
        return ranked_ids[:n]

    def build_because_you_loved(
        self,
        user_id: str,
        user_ratings: list[dict[str, Any]] | None,
        content_metadata: list[dict[str, Any]] | None = None,
        n: int = 10,
    ) -> dict[str, Any] | None:
        """
        Build a 'Because you loved X' row.

        Uses the user's highest-rated item as the anchor and blends
        content/neural/collaborative candidates around it.
        """
        metadata = self._resolve_metadata(content_metadata)
        ratings = list(user_ratings or [])

        if not metadata or not ratings or n <= 0:
            return None

        best_rating = max(ratings, key=lambda item: float(item["rating"]))
        anchor_id = str(best_rating["content_id"])

        excluded = {str(r["content_id"]) for r in ratings}
        combined_scores: dict[str, float] = defaultdict(float)
        limit = max(n * 2, self.similar_per_seed)

        for result in self._safe_content_similar(anchor_id, limit):
            candidate_id = str(result.get("content_id", ""))
            if not candidate_id or candidate_id in excluded:
                continue

            similarity_score = float(result.get("score", 0.0))
            combined_scores[candidate_id] += self.content_weight * similarity_score

        similar_neural_ids = self._safe_similar_items(anchor_id, limit)
        self._add_ranked_scores(
            combined_scores,
            similar_neural_ids,
            self.neural_weight,
            excluded,
        )

        collaborative_ids = self._safe_recommend(
            recommender=self.collaborative,
            user_id=str(user_id),
            n=limit,
            exclude_ids=list(excluded),
        )
        self._add_ranked_scores(
            combined_scores,
            collaborative_ids,
            self.collaborative_weight * 0.5,
            excluded,
        )

        candidate_ids = self._ordered_candidate_ids(
            combined_scores,
            metadata,
            excluded,
        )

        ranked_ids = self.personalizer.rank(candidate_ids, ratings, metadata)[:n]
        return self.personalizer.inject_because_you_loved(
            ranked_ids,
            ratings,
            metadata,
        )

    def _resolve_metadata(
        self,
        content_metadata: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        """Use provided metadata or fall back to metadata stored during fit()."""
        if content_metadata is None:
            return list(self._content_metadata)
        return list(content_metadata)

    def _top_seed_ratings(
        self,
        ratings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return the user's strongest ratings for content-based seeding."""
        strong_ratings = [
            rating
            for rating in ratings
            if float(rating["rating"]) >= 4.0
        ]
        return sorted(
            strong_ratings,
            key=lambda item: float(item["rating"]),
            reverse=True,
        )[: self.max_seeds]

    def _safe_content_similar(
        self,
        content_id: str,
        top_n: int,
    ) -> list[dict[str, Any]]:
        """Safely query content similarity results."""
        try:
            return list(self.vectorizer.similar(content_id, top_n=top_n))
        except Exception:
            return []

    def _safe_recommend(
        self,
        recommender: Any,
        user_id: str,
        n: int,
        exclude_ids: list[str],
    ) -> list[str]:
        """Safely query recommender.recommend() across slight signature differences."""
        try:
            result = recommender.recommend(user_id, n=n, exclude_ids=exclude_ids)
        except TypeError:
            try:
                result = recommender.recommend(user_id, n=n)
            except Exception:
                return []
        except Exception:
            return []

        return [str(item_id) for item_id in result]

    def _safe_similar_items(
        self,
        content_id: str,
        n: int,
    ) -> list[str]:
        """Safely query neural item-to-item similarity."""
        try:
            result = self.neural.get_similar_items(content_id, n=n)
        except Exception:
            return []
        return [str(item_id) for item_id in result]

    def _add_ranked_scores(
        self,
        combined_scores: dict[str, float],
        ranked_ids: list[str],
        weight: float,
        excluded: set[str],
    ) -> None:
        """Add decayed rank-based scores into the combined score map."""
        for rank, content_id in enumerate(ranked_ids, start=1):
            candidate_id = str(content_id)
            if not candidate_id or candidate_id in excluded:
                continue
            combined_scores[candidate_id] += weight / rank

    def _ordered_candidate_ids(
        self,
        combined_scores: dict[str, float],
        metadata: list[dict[str, Any]],
        excluded: set[str],
    ) -> list[str]:
        """Return scored candidates first, then unseen fallback items."""
        ranked_ids = [
            content_id
            for content_id, _ in sorted(
                combined_scores.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]

        seen = set(ranked_ids)
        for content_id in self._unseen_content_ids(metadata, excluded):
            if content_id not in seen:
                ranked_ids.append(content_id)
                seen.add(content_id)

        return ranked_ids

    def _unseen_content_ids(
        self,
        metadata: list[dict[str, Any]],
        excluded: set[str],
    ) -> list[str]:
        """Return unseen content IDs from metadata, preserving input order."""
        seen: set[str] = set()
        result: list[str] = []

        for item in metadata:
            content_id = str(item.get("content_id", ""))
            if not content_id or content_id in excluded or content_id in seen:
                continue
            seen.add(content_id)
            result.append(content_id)

        return result