"""Business logic for assembling Netflix-style collection rows."""

from __future__ import annotations

import logging
from typing import Any

from src.ml.collection_engine import CollectionEngine
from src.ml.hybrid import HybridEngine
from src.ml.personalizer import Personalizer

logger = logging.getLogger(__name__)

_MIN_ITEMS_FOR_CLUSTERING = 8
_DEFAULT_ROW_LIMIT = 20
_DEFAULT_COLLECTION_COUNT = 6


class CollectionService:
    """
    Assemble themed collection rows for the home screen.

    Combines:
    - Mood/genre clusters from CollectionEngine
    - Special rows (free, new)
    - Personalized hybrid recommendations
    - 'Because you loved X' row when user has ratings
    """

    def __init__(
        self,
        collection_engine: CollectionEngine | None = None,
        hybrid_engine: HybridEngine | None = None,
        personalizer: Personalizer | None = None,
    ) -> None:
        self._collection_engine = collection_engine or CollectionEngine()
        self._hybrid_engine = hybrid_engine or HybridEngine()
        self._personalizer = personalizer or Personalizer()

    def build_home_screen(
        self,
        catalog: list[dict[str, Any]],
        user_id: str | None = None,
        user_ratings: list[dict[str, Any]] | None = None,
        content_preference: str = "both",
        n_collections: int = _DEFAULT_COLLECTION_COUNT,
        row_limit: int = _DEFAULT_ROW_LIMIT,
    ) -> list[dict[str, Any]]:
        """
        Build a list of themed collection rows for the home screen.

        Parameters
        ----------
        catalog:
            All available content items. Each item must have an 'id' key.
        user_id:
            Current user identifier. None for anonymous users.
        user_ratings:
            User's rating history. Empty list or None for cold start.
        content_preference:
            One of 'books', 'comics', 'both'. Filters personalised rows.
        n_collections:
            Maximum number of collection rows to return.
        row_limit:
            Maximum items per row.

        Returns
        -------
        list[dict]
            Each row has: id, title, mood, items, item_count.
        """
        ratings = list(user_ratings or [])
        filtered_catalog = self._personalizer.filter_by_preference(
            catalog, content_preference
        )

        rows: list[dict[str, Any]] = []
        used_item_ids: set[str] = set()

        because_row = self._build_because_you_loved_row(
            catalog=filtered_catalog,
            user_id=user_id,
            user_ratings=ratings,
            row_limit=row_limit,
        )
        if because_row:
            rows.append(because_row)
            used_item_ids.update(str(i) for i in because_row.get("items", []))

        personalized_row = self._build_personalized_row(
            catalog=filtered_catalog,
            user_id=user_id,
            user_ratings=ratings,
            row_limit=row_limit,
            exclude_ids=used_item_ids,
        )
        if personalized_row:
            rows.append(personalized_row)
            used_item_ids.update(str(i) for i in personalized_row.get("items", []))

        cluster_rows = self._build_cluster_rows(
            catalog=filtered_catalog,
            user_ratings=ratings,
            row_limit=row_limit,
        )
        for row in cluster_rows:
            items = [i for i in row.get("items", []) if str(i) not in used_item_ids]
            if not items:
                continue
            row["items"] = items[:row_limit]
            row["item_count"] = len(row["items"])
            used_item_ids.update(str(i) for i in row["items"])
            rows.append(row)

        special_rows = self._build_special_rows(
            catalog=catalog,
            row_limit=row_limit,
        )
        for row in special_rows:
            items = [i for i in row.get("items", []) if str(i) not in used_item_ids]
            if not items:
                continue
            row["items"] = items[:row_limit]
            row["item_count"] = len(row["items"])
            used_item_ids.update(str(i) for i in row["items"])
            rows.append(row)

        seen_ids: set[str] = set()
        unique_rows: list[dict[str, Any]] = []
        for row in rows:
            row_id = row.get("id", "")
            if row_id and row_id not in seen_ids:
                seen_ids.add(row_id)
                unique_rows.append(row)

        return unique_rows[:n_collections]

    def _build_because_you_loved_row(
        self,
        catalog: list[dict[str, Any]],
        user_id: str | None,
        user_ratings: list[dict[str, Any]],
        row_limit: int,
    ) -> dict[str, Any] | None:
        """Build 'Because you loved X' row using hybrid engine."""
        if not user_id or not user_ratings or not catalog:
            return None

        metadata = self._catalog_to_metadata(catalog)

        try:
            result = self._hybrid_engine.build_because_you_loved(
                user_id=user_id,
                user_ratings=user_ratings,
                content_metadata=metadata,
                n=row_limit,
            )
        except Exception:
            logger.warning("Failed to build because_you_loved row", exc_info=True)
            return None

        if result is None:
            return None

        label = result.get("label", "Because you loved...")
        items = result.get("items", [])

        return {
            "id": "personal-because",
            "title": label,
            "mood": "personal",
            "items": items[:row_limit],
            "item_count": len(items[:row_limit]),
        }

    def _build_personalized_row(
        self,
        catalog: list[dict[str, Any]],
        user_id: str | None,
        user_ratings: list[dict[str, Any]],
        row_limit: int,
        exclude_ids: set[str] | None = None,
    ) -> dict[str, Any] | None:
        """Build a 'Picked for You' row using hybrid recommendations."""
        if not user_id or not user_ratings or not catalog:
            return None

        metadata = self._catalog_to_metadata(catalog)

        try:
            recommended_ids = self._hybrid_engine.recommend(
                user_id=user_id,
                user_ratings=user_ratings,
                content_metadata=metadata,
                n=row_limit * 3,
                exclude_ids=list(exclude_ids) if exclude_ids else None,
            )
        except Exception:
            logger.warning("Failed to build personalized row", exc_info=True)
            return None

        if not recommended_ids:
            return None

        if exclude_ids:
            recommended_ids = [i for i in recommended_ids if i not in exclude_ids]

        recommended_ids = recommended_ids[:row_limit]

        if not recommended_ids:
            return None

        return {
            "id": "personal-picked",
            "title": "Picked for You",
            "mood": "personal",
            "items": recommended_ids,
            "item_count": len(recommended_ids),
        }

    def _build_cluster_rows(
        self,
        catalog: list[dict[str, Any]],
        user_ratings: list[dict[str, Any]],
        row_limit: int,
    ) -> list[dict[str, Any]]:
        """Build mood/genre cluster rows from CollectionEngine."""
        if len(catalog) < _MIN_ITEMS_FOR_CLUSTERING:
            return self._collection_engine.get_special_collections(catalog)

        try:
            self._collection_engine.fit(catalog)
            collections = self._collection_engine.get_collections(catalog)
        except Exception:
            logger.warning("CollectionEngine failed", exc_info=True)
            return []

        rows: list[dict[str, Any]] = []
        for collection in collections:
            items = collection.get("items", [])
            if not items:
                continue

            ranked_items = self._personalizer.rank(
                candidate_ids=items,
                user_ratings=user_ratings,
                content_metadata=self._catalog_to_metadata(catalog),
            )

            rows.append({
                "id": collection.get("id", ""),
                "title": collection.get("title", ""),
                "mood": collection.get("mood", ""),
                "items": ranked_items[:row_limit],
                "item_count": len(ranked_items[:row_limit]),
            })

        return rows

    def _build_special_rows(
        self,
        catalog: list[dict[str, Any]],
        row_limit: int,
    ) -> list[dict[str, Any]]:
        """Build special rows: free to read, new arrivals."""
        try:
            specials = self._collection_engine.get_special_collections(catalog)
        except Exception:
            logger.warning("Failed to build special collections", exc_info=True)
            return []

        rows: list[dict[str, Any]] = []
        for collection in specials:
            items = collection.get("items", [])
            if not items:
                continue
            rows.append({
                "id": collection.get("id", ""),
                "title": collection.get("title", ""),
                "mood": collection.get("mood", ""),
                "items": items[:row_limit],
                "item_count": len(items[:row_limit]),
            })

        return rows

    def _catalog_to_metadata(
        self,
        catalog: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Convert catalog items to Personalizer/HybridEngine metadata format.

        CollectionEngine uses 'id'. Personalizer/Hybrid uses 'content_id'.
        This bridges the two conventions.
        """
        result: list[dict[str, Any]] = []
        for item in catalog:
            item_id = str(item.get("id", item.get("content_id", "")))
            if not item_id:
                continue
            metadata_item = dict(item)
            metadata_item["content_id"] = item_id
            result.append(metadata_item)
        return result