"""TF-IDF vectorizer for content-based similarity across books and comics."""

from __future__ import annotations

import logging
import os
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")
VECTORIZER_PATH = "tfidf_vectorizer.pkl"
MATRIX_PATH = "tfidf_matrix.pkl"
IDS_PATH = "content_ids.pkl"

DEFAULT_MAX_FEATURES = 5000
DEFAULT_TOP_N = 10


class ContentVectorizer:
    """
    TF-IDF vectorizer for content-based similarity.

    Designed to be content-type agnostic — works identically for books
    and comics. Callers pass a list of content dicts with standardised
    fields; the vectorizer builds a TF-IDF matrix and returns similar
    items by cosine similarity.

    Usage
    -----
    vectorizer = ContentVectorizer()
    vectorizer.fit(books)          # books is list[dict]
    similar = vectorizer.similar("book_001", top_n=10)
    vectorizer.save()
    vectorizer.load()
    """

    def __init__(self, model_dir: str | None = None) -> None:
        self.model_dir = model_dir or DEFAULT_MODEL_DIR
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._ids: list[str] = []
        self._fitted = False

    # Helpers

    def _build_text(self, item: dict[str, Any]) -> str:
        """
        Combine item metadata into a single text string.

        Genres and categories are repeated to increase their weight
        relative to free-form description text.
        """
        parts: list[str] = []

        title = item.get("title", "")
        if title:
            parts.append(title)

        authors = item.get("authors", [])
        if authors:
            parts.append(" ".join(authors))

        description = item.get("description", "")
        if description:
            parts.append(description)

        genres = item.get("genres", [])
        if genres:
            joined = " ".join(genres)
            parts.append(joined)
            parts.append(joined)

        categories = item.get("categories", [])
        if categories:
            joined = " ".join(categories)
            parts.append(joined)
            parts.append(joined)

        return " ".join(parts).lower().strip()

    def _require_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError(
                "ContentVectorizer is not fitted. Call fit() or load() first."
            )

    # Public API

    def fit(self, items: list[dict[str, Any]]) -> None:
        """
        Fit the TF-IDF matrix from a list of content items.

        Each item must have at minimum an 'id' field. All other fields
        (title, authors, description, genres, categories) are optional
        but improve similarity quality.

        Parameters
        ----------
        items:
            List of content dicts (books or comics).
        """
        if not items:
            raise ValueError("Cannot fit on empty item list.")

        corpus = [self._build_text(item) for item in items]
        self._ids = [str(item["id"]) for item in items]

        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=DEFAULT_MAX_FEATURES,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )

        self._matrix = self._vectorizer.fit_transform(corpus)
        self._fitted = True

        logger.info(
            "ContentVectorizer fitted: %d items, matrix shape %s",
            len(items),
            self._matrix.shape,
        )

    def similar(
        self,
        content_id: str,
        top_n: int = DEFAULT_TOP_N,
    ) -> list[dict[str, Any]]:
        """
        Return the top_n most similar items to content_id.

        Parameters
        ----------
        content_id:
            The id of the item to find neighbours for.
        top_n:
            Number of results to return (excluding the item itself).

        Returns
        -------
        List of dicts with keys: content_id, score, rank.
        Sorted by score descending.
        """
        self._require_fitted()

        if content_id not in self._ids:
            raise ValueError(f"content_id {content_id!r} not found in fitted data.")

        idx = self._ids.index(content_id)
        scores = cosine_similarity(self._matrix[idx], self._matrix).flatten()

        similar_indices = scores.argsort()[::-1]

        results: list[dict[str, Any]] = []
        rank = 1
        for i in similar_indices:
            if self._ids[i] == content_id:
                continue
            results.append(
                {
                    "content_id": self._ids[i],
                    "score": round(float(scores[i]), 6),
                    "rank": rank,
                }
            )
            rank += 1
            if rank > top_n:
                break

        return results

    def get_matrix(self):
        """Return the raw TF-IDF sparse matrix."""
        self._require_fitted()
        return self._matrix

    def get_ids(self) -> list[str]:
        """Return the list of content ids in matrix row order."""
        self._require_fitted()
        return list(self._ids)

    def vocabulary_size(self) -> int:
        """Return the number of features in the fitted vocabulary."""
        self._require_fitted()
        return len(self._vectorizer.vocabulary_)

    # Persistence

    def save(self, model_dir: str | None = None) -> None:
        """
        Persist the fitted vectorizer, matrix, and id list to disk.

        Parameters
        ----------
        model_dir:
            Directory to save models into. Defaults to self.model_dir.
        """
        self._require_fitted()

        target = model_dir or self.model_dir
        os.makedirs(target, exist_ok=True)

        joblib.dump(self._vectorizer, os.path.join(target, VECTORIZER_PATH))
        joblib.dump(self._matrix, os.path.join(target, MATRIX_PATH))
        joblib.dump(self._ids, os.path.join(target, IDS_PATH))

        logger.info("ContentVectorizer saved to %s", target)

    def load(self, model_dir: str | None = None) -> None:
        """
        Load a previously saved vectorizer from disk.

        Parameters
        ----------
        model_dir:
            Directory to load models from. Defaults to self.model_dir.
        """
        target = model_dir or self.model_dir

        vectorizer_path = os.path.join(target, VECTORIZER_PATH)
        matrix_path = os.path.join(target, MATRIX_PATH)
        ids_path = os.path.join(target, IDS_PATH)

        for path in (vectorizer_path, matrix_path, ids_path):
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Model file not found: {path}. Run fit() and save() first."
                )

        self._vectorizer = joblib.load(vectorizer_path)
        self._matrix = joblib.load(matrix_path)
        self._ids = joblib.load(ids_path)
        self._fitted = True

        logger.info(
            "ContentVectorizer loaded from %s, matrix shape %s",
            target,
            self._matrix.shape,
        )

    @property
    def is_fitted(self) -> bool:
        """True if the vectorizer has been fitted or loaded."""
        return self._fitted