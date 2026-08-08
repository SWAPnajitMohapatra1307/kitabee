"""Tests for CollectionService."""

from __future__ import annotations

from typing import Any

import pytest

from src.services.collection_service import CollectionService


class FakeCollectionEngine:
    def __init__(
        self,
        collections: list[dict[str, Any]] | None = None,
        specials: list[dict[str, Any]] | None = None,
    ) -> None:
        self._collections = collections or []
        self._specials = specials or []
        self.fit_called = False

    def fit(self, items: list[dict[str, Any]]) -> None:
        self.fit_called = True

    def get_collections(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return list(self._collections)

    def get_special_collections(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return list(self._specials)


class ExplodingCollectionEngine(FakeCollectionEngine):
    def fit(self, items: list[dict[str, Any]]) -> None:
        raise RuntimeError("boom")

    def get_collections(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise RuntimeError("boom")

    def get_special_collections(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise RuntimeError("boom")


class FakeHybridEngine:
    def __init__(
        self,
        recommendations: list[str] | None = None,
        because_row: dict[str, Any] | None = None,
    ) -> None:
        self._recommendations = recommendations or []
        self._because_row = because_row

    def recommend(self, **kwargs: Any) -> list[str]:
        return list(self._recommendations)

    def build_because_you_loved(self, **kwargs: Any) -> dict[str, Any] | None:
        return self._because_row


class ExplodingHybridEngine(FakeHybridEngine):
    def recommend(self, **kwargs: Any) -> list[str]:
        raise RuntimeError("boom")

    def build_because_you_loved(self, **kwargs: Any) -> dict[str, Any] | None:
        raise RuntimeError("boom")


class FakePersonalizer:
    def filter_by_preference(
        self,
        items: list[dict[str, Any]],
        preference: str,
    ) -> list[dict[str, Any]]:
        return list(items)

    def rank(
        self,
        candidate_ids: list[str],
        user_ratings: list[dict[str, Any]],
        content_metadata: list[dict[str, Any]],
    ) -> list[str]:
        return list(candidate_ids)


def _catalog(n: int = 10) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i in range(1, n + 1):
        items.append({
            "id": f"b{i}",
            "title": f"Book {i}",
            "genre": "sci-fi" if i % 2 == 0 else "fantasy",
            "mood": "dark" if i % 3 == 0 else "warm",
            "source": "gb",
        })
    return items


def _ratings() -> list[dict[str, Any]]:
    return [
        {"user_id": "u1", "content_id": "b1", "rating": 5.0},
        {"user_id": "u1", "content_id": "b2", "rating": 3.0},
    ]


def _cluster_collections() -> list[dict[str, Any]]:
    return [
        {
            "id": "dark-000",
            "title": "Shadows of the Mind",
            "mood": "dark",
            "items": ["b1", "b3", "b5"],
            "item_count": 3,
        },
        {
            "id": "warm-001",
            "title": "Feel-Good Reads",
            "mood": "warm",
            "items": ["b2", "b4"],
            "item_count": 2,
        },
    ]


def _special_collections() -> list[dict[str, Any]]:
    return [
        {
            "id": "special-free",
            "title": "Free to Read Right Now",
            "mood": "educational",
            "items": ["b7", "b8"],
            "item_count": 2,
        },
    ]


def _because_row() -> dict[str, Any]:
    return {
        "label": "Because you loved Book 1",
        "anchor": "Book 1",
        "items": ["b3", "b5", "b7"],
    }


def test_returns_list() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=_catalog())
    assert isinstance(result, list)


def test_empty_catalog_returns_empty() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=[])
    assert result == []


def test_cluster_rows_included() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=_special_collections(),
        ),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=_catalog(), n_collections=10)
    ids = [row["id"] for row in result]
    assert "dark-000" in ids
    assert "warm-001" in ids


def test_special_rows_included() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=_special_collections(),
        ),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=_catalog(), n_collections=10)
    ids = [row["id"] for row in result]
    assert "special-free" in ids


def test_because_you_loved_row_included() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(because_row=_because_row()),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert "personal-because" in ids
    because = next(r for r in result if r["id"] == "personal-because")
    assert because["title"] == "Because you loved Book 1"


def test_because_row_not_included_without_user() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(because_row=_because_row()),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id=None,
        user_ratings=_ratings(),
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert "personal-because" not in ids


def test_because_row_not_included_without_ratings() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(because_row=_because_row()),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=[],
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert "personal-because" not in ids


def test_personalized_row_included() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(recommendations=["b3", "b5"]),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert "personal-picked" in ids
    picked = next(r for r in result if r["id"] == "personal-picked")
    assert picked["title"] == "Picked for You"
    assert picked["items"] == ["b3", "b5"]


def test_personalized_row_not_included_without_user() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(recommendations=["b3"]),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert "personal-picked" not in ids


def test_n_collections_limits_output() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=_special_collections(),
        ),
        hybrid_engine=FakeHybridEngine(
            recommendations=["b3"],
            because_row=_because_row(),
        ),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=2,
    )
    assert len(result) <= 2


def test_row_limit_caps_items() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=[{
                "id": "big-row",
                "title": "Big",
                "mood": "warm",
                "items": [f"b{i}" for i in range(1, 50)],
                "item_count": 49,
            }],
        ),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        row_limit=5,
        n_collections=10,
    )
    for row in result:
        assert len(row["items"]) <= 5


def test_each_row_has_required_keys() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=_special_collections(),
        ),
        hybrid_engine=FakeHybridEngine(
            recommendations=["b3"],
            because_row=_because_row(),
        ),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=10,
    )
    required_keys = {"id", "title", "mood", "items", "item_count"}
    for row in result:
        assert required_keys.issubset(row.keys()), f"Missing keys in {row}"


def test_no_duplicate_row_ids() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=_special_collections(),
        ),
        hybrid_engine=FakeHybridEngine(
            recommendations=["b3"],
            because_row=_because_row(),
        ),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=10,
    )
    ids = [row["id"] for row in result]
    assert len(ids) == len(set(ids))


def test_handles_collection_engine_failure() -> None:
    service = CollectionService(
        collection_engine=ExplodingCollectionEngine(),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=_catalog(), n_collections=10)
    assert isinstance(result, list)


def test_handles_hybrid_engine_failure() -> None:
    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=ExplodingHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(
        catalog=_catalog(),
        user_id="u1",
        user_ratings=_ratings(),
        n_collections=10,
    )
    assert isinstance(result, list)
    ids = [row["id"] for row in result]
    assert "personal-because" not in ids
    assert "personal-picked" not in ids


def test_small_catalog_skips_clustering() -> None:
    small = _catalog(n=3)
    specials = _special_collections()

    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
            specials=specials,
        ),
        hybrid_engine=FakeHybridEngine(),
        personalizer=FakePersonalizer(),
    )
    result = service.build_home_screen(catalog=small, n_collections=10)
    ids = [row["id"] for row in result]
    assert "dark-000" not in ids
    assert "warm-001" not in ids


def test_content_preference_filter_passed_through() -> None:
    filter_log: list[str] = []

    class TrackingPersonalizer(FakePersonalizer):
        def filter_by_preference(
            self,
            items: list[dict[str, Any]],
            preference: str,
        ) -> list[dict[str, Any]]:
            filter_log.append(preference)
            return list(items)

    service = CollectionService(
        collection_engine=FakeCollectionEngine(
            collections=_cluster_collections(),
        ),
        hybrid_engine=FakeHybridEngine(),
        personalizer=TrackingPersonalizer(),
    )
    service.build_home_screen(
        catalog=_catalog(),
        content_preference="comics",
        n_collections=10,
    )
    assert "comics" in filter_log