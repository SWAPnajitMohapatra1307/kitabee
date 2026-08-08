"""Tests for HybridEngine."""

from __future__ import annotations

from typing import Any

from src.ml import HybridEngine, Personalizer


class FakeVectorizer:
    def __init__(self, similar_map: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.similar_map = similar_map or {}
        self.fit_calls: list[list[dict[str, Any]]] = []

    def fit(self, items: list[dict[str, Any]]) -> None:
        self.fit_calls.append(list(items))

    def similar(self, content_id: str, top_n: int = 10) -> list[dict[str, Any]]:
        return list(self.similar_map.get(str(content_id), []))[:top_n]


class ExplodingVectorizer(FakeVectorizer):
    def similar(self, content_id: str, top_n: int = 10) -> list[dict[str, Any]]:
        raise ValueError("boom")


class FakeCollaborative:
    def __init__(self, recommendations: dict[str, list[str]] | None = None) -> None:
        self.recommendations = recommendations or {}
        self.fit_calls: list[list[dict[str, Any]]] = []

    def fit(self, ratings: list[dict[str, Any]]) -> None:
        self.fit_calls.append(list(ratings))

    def recommend(
        self,
        user_id: str,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        exclude = {str(item_id) for item_id in (exclude_ids or [])}
        return [
            item_id
            for item_id in self.recommendations.get(str(user_id), [])[:n]
            if str(item_id) not in exclude
        ]


class ExplodingCollaborative(FakeCollaborative):
    def recommend(
        self,
        user_id: str,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        raise RuntimeError("boom")


class OldSignatureCollaborative(FakeCollaborative):
    def recommend(self, user_id: str, n: int = 10) -> list[str]:
        return list(self.recommendations.get(str(user_id), []))[:n]


class FakeNeural:
    def __init__(
        self,
        recommendations: dict[str, list[str]] | None = None,
        similar_items_map: dict[str, list[str]] | None = None,
    ) -> None:
        self.recommendations = recommendations or {}
        self.similar_items_map = similar_items_map or {}
        self.fit_calls: list[list[dict[str, Any]]] = []

    def fit(self, ratings: list[dict[str, Any]]) -> None:
        self.fit_calls.append(list(ratings))

    def recommend(
        self,
        user_id: str,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        exclude = {str(item_id) for item_id in (exclude_ids or [])}
        return [
            item_id
            for item_id in self.recommendations.get(str(user_id), [])[:n]
            if str(item_id) not in exclude
        ]

    def get_similar_items(self, content_id: str, n: int = 10) -> list[str]:
        return list(self.similar_items_map.get(str(content_id), []))[:n]


class ExplodingNeural(FakeNeural):
    def recommend(
        self,
        user_id: str,
        n: int = 10,
        exclude_ids: list[str] | None = None,
    ) -> list[str]:
        raise RuntimeError("boom")

    def get_similar_items(self, content_id: str, n: int = 10) -> list[str]:
        raise RuntimeError("boom")


class ReversingPersonalizer(Personalizer):
    def rank(
        self,
        candidate_ids: list[str],
        user_ratings: list[dict],
        content_metadata: list[dict],
    ) -> list[str]:
        return list(reversed(candidate_ids))


def _metadata() -> list[dict[str, Any]]:
    return [
        {
            "content_id": "b1",
            "title": "Dune",
            "genre": "sci-fi",
            "mood": "dark",
            "source": "gb_1",
        },
        {
            "content_id": "b2",
            "title": "Neuromancer",
            "genre": "sci-fi",
            "mood": "dark",
            "source": "gb_2",
        },
        {
            "content_id": "b3",
            "title": "Foundation",
            "genre": "sci-fi",
            "mood": "epic",
            "source": "gb_3",
        },
        {
            "content_id": "cv_4",
            "title": "Saga Vol. 1",
            "genre": "sci-fi",
            "mood": "adventurous",
            "source": "cv_4",
        },
        {
            "content_id": "b5",
            "title": "Pride and Prejudice",
            "genre": "romance",
            "mood": "warm",
            "source": "gb_5",
        },
    ]


def _ratings() -> list[dict[str, Any]]:
    return [
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b5", "rating": 2.0},
    ]


def test_fit_returns_self() -> None:
    vectorizer = FakeVectorizer()
    collaborative = FakeCollaborative()
    neural = FakeNeural()

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
    )

    items = _metadata()
    ratings = _ratings()

    result = engine.fit(items, ratings)

    assert result is engine
    assert engine.is_fitted is True
    assert vectorizer.fit_calls == [items]
    assert collaborative.fit_calls == [ratings]
    assert neural.fit_calls == [ratings]


def test_fit_with_no_items_or_ratings() -> None:
    vectorizer = FakeVectorizer()
    collaborative = FakeCollaborative()
    neural = FakeNeural()

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
    )

    engine.fit([], [])

    assert engine.is_fitted is True
    assert vectorizer.fit_calls == []
    assert collaborative.fit_calls == []
    assert neural.fit_calls == []


def test_recommend_returns_empty_when_no_metadata() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.recommend(user_id="u1", user_ratings=[], content_metadata=[], n=10)

    assert result == []


def test_recommend_returns_empty_when_n_not_positive() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=0,
    )

    assert result == []


def test_recommend_combines_all_signals() -> None:
    vectorizer = FakeVectorizer(
        similar_map={
            "b1": [
                {"content_id": "b2", "score": 0.9, "rank": 1},
                {"content_id": "b3", "score": 0.8, "rank": 2},
            ]
        }
    )
    collaborative = FakeCollaborative(
        recommendations={"u1": ["cv_4", "b3", "b2", "b1"]}
    )
    neural = FakeNeural(
        recommendations={"u1": ["b3", "cv_4", "b2", "b1"]}
    )

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
        personalizer=Personalizer(),
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result == ["b2", "b3", "cv_4"]


def test_recommend_excludes_rated_and_explicit_ids() -> None:
    vectorizer = FakeVectorizer(
        similar_map={
            "b1": [
                {"content_id": "b2", "score": 0.9, "rank": 1},
                {"content_id": "b5", "score": 0.8, "rank": 2},
            ]
        }
    )
    collaborative = FakeCollaborative(
        recommendations={"u1": ["b1", "b2", "b3", "b5", "cv_4"]}
    )
    neural = FakeNeural(
        recommendations={"u1": ["b1", "b2", "b3", "cv_4"]}
    )

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=10,
        exclude_ids=["b3"],
    )

    assert "b1" not in result
    assert "b5" not in result
    assert "b3" not in result
    assert result == ["b2", "cv_4"]


def test_recommend_falls_back_to_unseen_metadata_order() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=10,
    )

    assert result == ["b2", "b3", "cv_4"]


def test_recommend_uses_metadata_from_fit_when_not_passed() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )
    engine.fit(_metadata(), _ratings())

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        n=10,
    )

    assert result == ["b2", "b3", "cv_4"]


def test_recommend_handles_vectorizer_failure() -> None:
    collaborative = FakeCollaborative(recommendations={"u1": ["b3", "b2"]})
    neural = FakeNeural(recommendations={"u1": ["cv_4", "b2"]})

    engine = HybridEngine(
        vectorizer=ExplodingVectorizer(),
        collaborative=collaborative,
        neural=neural,
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result == ["b2", "b3", "cv_4"]


def test_recommend_handles_recommender_failure() -> None:
    vectorizer = FakeVectorizer(
        similar_map={"b1": [{"content_id": "b2", "score": 0.9, "rank": 1}]}
    )

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=ExplodingCollaborative(),
        neural=ExplodingNeural(),
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result == ["b2", "b3", "cv_4"]


def test_recommend_supports_old_recommender_signature() -> None:
    collaborative = OldSignatureCollaborative(recommendations={"u1": ["b2", "b3"]})
    neural = FakeNeural(recommendations={"u1": ["cv_4", "b2"]})

    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=collaborative,
        neural=neural,
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result == ["b2", "cv_4", "b3"]


def test_recommend_uses_personalizer_for_final_order() -> None:
    vectorizer = FakeVectorizer(
        similar_map={
            "b1": [
                {"content_id": "b2", "score": 0.9, "rank": 1},
                {"content_id": "b3", "score": 0.8, "rank": 2},
            ]
        }
    )
    collaborative = FakeCollaborative(recommendations={"u1": ["cv_4"]})
    neural = FakeNeural(recommendations={"u1": []})

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
        personalizer=ReversingPersonalizer(),
    )

    result = engine.recommend(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result == ["cv_4", "b3", "b2"]


def test_build_because_you_loved_returns_none_without_metadata() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=[],
        n=5,
    )

    assert result is None


def test_build_because_you_loved_returns_none_without_ratings() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=[],
        content_metadata=_metadata(),
        n=5,
    )

    assert result is None


def test_build_because_you_loved_returns_none_when_n_not_positive() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=0,
    )

    assert result is None


def test_build_because_you_loved_builds_row() -> None:
    vectorizer = FakeVectorizer(
        similar_map={
            "b1": [
                {"content_id": "b2", "score": 0.95, "rank": 1},
                {"content_id": "b3", "score": 0.85, "rank": 2},
            ]
        }
    )
    collaborative = FakeCollaborative(recommendations={"u1": ["cv_4", "b2"]})
    neural = FakeNeural(similar_items_map={"b1": ["b3", "cv_4", "b2"]})

    engine = HybridEngine(
        vectorizer=vectorizer,
        collaborative=collaborative,
        neural=neural,
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result is not None
    assert result["label"] == "Because you loved Dune"
    assert result["anchor"] == "Dune"
    assert result["items"] == ["b2", "b3", "cv_4"]


def test_build_because_you_loved_falls_back_to_unseen_items() -> None:
    engine = HybridEngine(
        vectorizer=FakeVectorizer(),
        collaborative=FakeCollaborative(),
        neural=FakeNeural(),
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result is not None
    assert result["items"] == ["b2", "b3", "cv_4"]


def test_build_because_you_loved_handles_failures() -> None:
    engine = HybridEngine(
        vectorizer=ExplodingVectorizer(),
        collaborative=ExplodingCollaborative(),
        neural=ExplodingNeural(),
    )

    result = engine.build_because_you_loved(
        user_id="u1",
        user_ratings=_ratings(),
        content_metadata=_metadata(),
        n=3,
    )

    assert result is not None
    assert result["label"] == "Because you loved Dune"
    assert result["items"] == ["b2", "b3", "cv_4"]


def test_import_from_ml_package() -> None:
    from src.ml import HybridEngine as ImportedHybridEngine

    assert ImportedHybridEngine is HybridEngine