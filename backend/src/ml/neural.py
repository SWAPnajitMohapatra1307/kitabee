"""
Neural recommender using Keras embedding-based collaborative filtering.

Learns dense user and item embeddings from explicit ratings and predicts
preference scores with a dot product.
"""

from __future__ import annotations

import numpy as np
import keras
from keras import layers


def _build_model(n_users: int, n_items: int, n_factors: int) -> keras.Model:
    """Build and compile the embedding model."""
    user_input = keras.Input(shape=(1,), name="user_input")
    item_input = keras.Input(shape=(1,), name="item_input")

    user_embedding = layers.Embedding(
        input_dim=n_users,
        output_dim=n_factors,
        name="user_embedding",
    )(user_input)
    item_embedding = layers.Embedding(
        input_dim=n_items,
        output_dim=n_factors,
        name="item_embedding",
    )(item_input)

    user_vector = layers.Flatten(name="user_flatten")(user_embedding)
    item_vector = layers.Flatten(name="item_flatten")(item_embedding)

    output = layers.Dot(axes=1, name="dot_product")([user_vector, item_vector])

    model = keras.Model(
        inputs=[user_input, item_input],
        outputs=output,
        name="neural_recommender",
    )
    model.compile(optimizer="adam", loss="mse")
    return model


class NeuralRecommender:
    """
    Embedding-based neural collaborative filtering recommender.

    Parameters
    ----------
    n_factors : int
        Embedding dimension size.
    epochs : int
        Training epochs.
    batch_size : int
        Training batch size.
    min_ratings : int
        Minimum number of ratings required before fitting.
    """

    def __init__(
        self,
        n_factors: int = 16,
        epochs: int = 10,
        batch_size: int = 32,
        min_ratings: int = 2,
    ) -> None:
        self.n_factors = n_factors
        self.epochs = epochs
        self.batch_size = batch_size
        self.min_ratings = min_ratings

        self._model: keras.Model | None = None
        self._user_index: dict[str, int] = {}
        self._item_index: dict[str, int] = {}
        self._item_ids: list[str] = []
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def fit(self, ratings: list[dict]) -> "NeuralRecommender":
        """
        Train the model on ratings data.

        Each rating dict must include user_id, content_id, and rating.
        """
        self._reset_state()

        if len(ratings) < self.min_ratings:
            return self

        user_ids = sorted({str(r["user_id"]) for r in ratings})
        item_ids = sorted({str(r["content_id"]) for r in ratings})

        self._user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
        self._item_index = {item_id: idx for idx, item_id in enumerate(item_ids)}
        self._item_ids = item_ids

        n_users = len(user_ids)
        n_items = len(item_ids)
        n_factors = min(self.n_factors, n_users, n_items)

        if n_factors < 1:
            return self

        self._model = _build_model(n_users, n_items, n_factors)

        user_array = np.array(
            [self._user_index[str(r["user_id"])] for r in ratings],
            dtype=np.int32,
        ).reshape(-1, 1)
        item_array = np.array(
            [self._item_index[str(r["content_id"])] for r in ratings],
            dtype=np.int32,
        ).reshape(-1, 1)
        rating_array = np.array(
            [float(r["rating"]) for r in ratings],
            dtype=np.float32,
        )

        self._model.fit(
            [user_array, item_array],
            rating_array,
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=0,
        )

        self._is_fitted = True
        return self

    def recommend(
        self,
        user_id: str,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        """Return top-n content IDs for the given user."""
        if not self._is_fitted or self._model is None:
            return []

        user_key = str(user_id)
        if user_key not in self._user_index:
            return []

        excluded = {str(item_id) for item_id in (exclude_ids or [])}
        user_idx = self._user_index[user_key]

        user_array = np.full((len(self._item_ids), 1), user_idx, dtype=np.int32)
        item_array = np.arange(len(self._item_ids), dtype=np.int32).reshape(-1, 1)

        scores = self._model.predict([user_array, item_array], verbose=0).flatten()
        ranked_indices = np.argsort(scores)[::-1]

        recommendations: list[str] = []
        for idx in ranked_indices:
            item_id = self._item_ids[idx]
            if item_id in excluded:
                continue
            recommendations.append(item_id)
            if len(recommendations) >= n:
                break

        return recommendations

    def score(self, user_id: str, content_id: str) -> float:
        """Return predicted preference score for a user-item pair."""
        if not self._is_fitted or self._model is None:
            return 0.0

        user_key = str(user_id)
        item_key = str(content_id)

        if user_key not in self._user_index or item_key not in self._item_index:
            return 0.0

        user_array = np.array([[self._user_index[user_key]]], dtype=np.int32)
        item_array = np.array([[self._item_index[item_key]]], dtype=np.int32)

        prediction = self._model.predict([user_array, item_array], verbose=0)
        return float(prediction.flatten()[0])

    def get_similar_items(self, content_id: str, n: int = 10) -> list[str]:
        """Return items most similar to the given item by embedding similarity."""
        if not self._is_fitted or self._model is None:
            return []

        item_key = str(content_id)
        if item_key not in self._item_index:
            return []

        embedding_layer = self._model.get_layer("item_embedding")
        embedding_weights = embedding_layer.get_weights()[0]

        target_vector = embedding_weights[self._item_index[item_key]]
        normalized_weights = embedding_weights / (
            np.linalg.norm(embedding_weights, axis=1, keepdims=True) + 1e-9
        )
        normalized_target = target_vector / (np.linalg.norm(target_vector) + 1e-9)

        scores = normalized_weights @ normalized_target
        ranked_indices = np.argsort(scores)[::-1]

        similar_items: list[str] = []
        for idx in ranked_indices:
            candidate = self._item_ids[idx]
            if candidate == item_key:
                continue
            similar_items.append(candidate)
            if len(similar_items) >= n:
                break

        return similar_items

    def _reset_state(self) -> None:
        """Clear learned model state."""
        self._model = None
        self._user_index = {}
        self._item_index = {}
        self._item_ids = []
        self._is_fitted = False 