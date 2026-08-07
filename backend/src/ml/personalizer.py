"""Personalizer for ranking and presenting recommendations."""

from collections import defaultdict
from typing import Optional


class Personalizer:
    """Ranks candidate content and builds personalized collection rows.

    Combines genre affinity, mood affinity, and rating history
    signals to sort a list of candidate content IDs by predicted
    preference. Also builds 'Because you loved X' rows.
    """

    def __init__(self) -> None:
        """Initialize the Personalizer."""
        pass

    def rank(
        self,
        candidate_ids: list[str],
        user_ratings: list[dict],
        content_metadata: list[dict],
    ) -> list[str]:
        """Rank candidate content IDs by predicted user preference.

        Scoring signal (additive):
        - +2.0 per genre match with a 4+ rated item
        - +1.0 per mood match with a 4+ rated item
        - +0.5 per genre match with any rated item

        Args:
            candidate_ids: Content IDs to rank.
            user_ratings: List of dicts with keys content_id, rating.
            content_metadata: List of dicts with keys content_id,
                and optionally genre, mood, source.

        Returns:
            candidate_ids sorted by score descending.
            Items with no signal retain original order.
        """
        if not candidate_ids:
            return []

        meta_map = {
            str(item["content_id"]): item
            for item in content_metadata
        }

        rated_map = {
            str(r["content_id"]): float(r["rating"])
            for r in user_ratings
        }

        # build affinity sets from rating history
        strong_genres: dict[str, float] = defaultdict(float)
        strong_moods: dict[str, float] = defaultdict(float)
        weak_genres: dict[str, float] = defaultdict(float)

        for content_id, rating in rated_map.items():
            meta = meta_map.get(content_id, {})
            genre = meta.get("genre", "")
            mood = meta.get("mood", "")

            if rating >= 4.0:
                if genre:
                    strong_genres[genre] += 1.0
                if mood:
                    strong_moods[mood] += 1.0
            if genre:
                weak_genres[genre] += 0.5

        scores: dict[str, float] = {}

        for content_id in candidate_ids:
            cid = str(content_id)
            meta = meta_map.get(cid, {})
            genre = meta.get("genre", "")
            mood = meta.get("mood", "")
            score = 0.0

            if genre:
                score += strong_genres.get(genre, 0.0) * 2.0
                score += weak_genres.get(genre, 0.0) * 0.5

            if mood:
                score += strong_moods.get(mood, 0.0) * 1.0

            scores[cid] = score

        return sorted(
            candidate_ids,
            key=lambda cid: scores.get(str(cid), 0.0),
            reverse=True,
        )

    def filter_by_preference(
        self,
        items: list[dict],
        preference: str,
    ) -> list[dict]:
        """Filter items by content type preference.

        Args:
            items: List of dicts, each with a 'source' key.
                Source values starting with 'cv_' are comics.
                All others are treated as books.
            preference: One of 'books', 'comics', or 'both'.

        Returns:
            Filtered list. Returns all items if preference is 'both'
            or unrecognised.
        """
        if preference == "both" or preference not in ("books", "comics"):
            return items

        result = []
        for item in items:
            source = str(item.get("source", ""))
            is_comic = source.startswith("cv_")

            if preference == "comics" and is_comic:
                result.append(item)
            elif preference == "books" and not is_comic:
                result.append(item)

        return result

    def inject_because_you_loved(
        self,
        recommendations: list[str],
        user_ratings: list[dict],
        content_metadata: list[dict],
    ) -> Optional[dict]:
        """Build a 'Because you loved X' collection row.

        Picks the highest-rated item from user_ratings as the anchor.
        Uses recommendations as the row items.

        Args:
            recommendations: Ordered list of content IDs to show.
            user_ratings: List of dicts with keys content_id, rating.
            content_metadata: List of dicts with keys content_id, title.

        Returns:
            Dict with keys label, anchor, items.
            None if user has no ratings or recommendations is empty.
        """
        if not user_ratings or not recommendations:
            return None

        meta_map = {
            str(item["content_id"]): item
            for item in content_metadata
        }

        # find highest rated item
        best = max(user_ratings, key=lambda r: float(r["rating"]))
        anchor_id = str(best["content_id"])
        anchor_meta = meta_map.get(anchor_id, {})
        anchor_title = anchor_meta.get("title", anchor_id)

        return {
            "label": f"Because you loved {anchor_title}",
            "anchor": anchor_title,
            "items": list(recommendations),
        }