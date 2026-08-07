"""Collaborative filtering for user-based recommendations."""

from collections import defaultdict
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilter:
    """User-based collaborative filter using cosine similarity.

    Builds a user-item rating matrix from raw rating data,
    finds similar users via cosine similarity, and recommends
    items those users rated highly that the target user has
    not yet rated.
    """

    def __init__(self, n_neighbors: int = 5) -> None:
        """Initialize the collaborative filter.

        Args:
            n_neighbors: Number of similar users to consider
                when generating recommendations.
        """
        self._n_neighbors = n_neighbors
        self._user_index: dict[str, int] = {}
        self._item_index: dict[str, int] = {}
        self._index_to_user: dict[int, str] = {}
        self._index_to_item: dict[int, str] = {}
        self._matrix: Optional[np.ndarray] = None
        self._user_rated: dict[str, set[str]] = defaultdict(set)
        self._fitted = False

    @property
    def is_fitted(self) -> bool:
        """Return True if the model has been fitted."""
        return self._fitted

    def fit(self, ratings_data: list[dict]) -> "CollaborativeFilter":
        """Build the user-item matrix from rating records.

        Args:
            ratings_data: List of dicts, each with keys:
                - user_id (str)
                - content_id (str)
                - rating (float)

        Returns:
            Self, for method chaining.
        """
        if not ratings_data:
            return self

        for record in ratings_data:
            user_id = str(record["user_id"])
            content_id = str(record["content_id"])

            if user_id not in self._user_index:
                idx = len(self._user_index)
                self._user_index[user_id] = idx
                self._index_to_user[idx] = user_id

            if content_id not in self._item_index:
                idx = len(self._item_index)
                self._item_index[content_id] = idx
                self._index_to_item[idx] = content_id

            self._user_rated[user_id].add(content_id)

        n_users = len(self._user_index)
        n_items = len(self._item_index)
        self._matrix = np.zeros((n_users, n_items), dtype=np.float32)

        for record in ratings_data:
            user_id = str(record["user_id"])
            content_id = str(record["content_id"])
            rating = float(record["rating"])
            u = self._user_index[user_id]
            i = self._item_index[content_id]
            self._matrix[u, i] = rating

        self._fitted = True
        return self

    def find_similar_users(self, user_id: str, n: int = 5) -> list[str]:
        """Find users with similar rating patterns.

        Args:
            user_id: Target user ID.
            n: Number of similar users to return.

        Returns:
            List of similar user IDs, most similar first.
            Empty list if user is unknown or model not fitted.
        """
        if not self._fitted:
            return []

        if user_id not in self._user_index:
            return []

        u = self._user_index[user_id]
        user_vector = self._matrix[u].reshape(1, -1)
        similarities = cosine_similarity(user_vector, self._matrix)[0]

        # exclude the user themselves
        similarities[u] = -1.0

        n_users = len(self._user_index)
        k = min(n, n_users - 1)
        top_indices = np.argsort(similarities)[::-1][:k]

        return [
            self._index_to_user[int(i)]
            for i in top_indices
            if similarities[i] > 0.0
        ]

    def recommend(self, user_id: str, n: int = 10) -> list[str]:
        """Recommend content for a user based on similar users.

        Returns items rated highly by similar users that
        the target user has not yet rated.

        Cold start: users with fewer than 2 ratings receive
        an empty list.

        Args:
            user_id: Target user ID.
            n: Number of recommendations to return.

        Returns:
            List of content IDs, highest predicted score first.
            Empty list on cold start or unknown user.
        """
        if not self._fitted:
            return []

        if user_id not in self._user_index:
            return []

        # cold start guard
        if len(self._user_rated[user_id]) < 2:
            return []

        similar_users = self.find_similar_users(user_id, n=self._n_neighbors)
        if not similar_users:
            return []

        already_rated = self._user_rated[user_id]
        scores: dict[str, float] = defaultdict(float)

        for similar_user_id in similar_users:
            su = self._user_index[similar_user_id]
            for content_id, ci in self._item_index.items():
                if content_id in already_rated:
                    continue
                rating = self._matrix[su, ci]
                if rating > 0:
                    scores[content_id] += rating

        if not scores:
            return []

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [content_id for content_id, _ in ranked[:n]]