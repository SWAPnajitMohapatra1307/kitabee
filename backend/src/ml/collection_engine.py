from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, TypedDict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from src.ml.mood_detector import MoodDetector


class CollectionDict(TypedDict):
    id: str
    title: str
    mood: str
    items: List[str]
    item_count: int


TITLE_TEMPLATES: Dict[str, List[str]] = {
    "dark": [
        "Into the Darkness",
        "Grim but Brilliant",
        "Not for the Faint of Heart",
        "The Dark Side of the Page",
        "Brutal, Beautiful, Unforgettable",
        "Where Light Fears to Go",
    ],
    "adventurous": [
        "Epic Worlds Built From Scratch",
        "Strap In, It's Going to Be Wild",
        "Heroes Who Refused to Stay Home",
        "The Quest Begins Here",
        "For Those Who Crave the Unknown",
        "Big Adventures, Bigger Stakes",
    ],
    "romantic": [
        "Love in Every Page",
        "For the Hopeless Romantics",
        "Hearts on the Line",
        "When Love Gets Complicated",
        "Stories That Believe in Love",
        "Tender, Messy, Real",
    ],
    "funny": [
        "Seriously Though, These Are Funny",
        "Read This, Feel Better",
        "Wit Sharp Enough to Cut",
        "Comics and Books That Actually Make You Laugh",
        "The Lighter Side of Everything",
        "No Tragedy Here, Promise",
    ],
    "mysterious": [
        "You Won't See It Coming",
        "Clues, Lies, and Brilliant Minds",
        "The Truth Is in Here Somewhere",
        "For People Who Notice Everything",
        "Stay Up Late, Can't Put It Down",
        "Everyone Is a Suspect",
    ],
    "inspiring": [
        "Real People, Real Extraordinary Lives",
        "Stories That Actually Change You",
        "Against All Odds",
        "Because Someone Did It First",
        "The Fuel You Did Not Know You Needed",
        "Rise, Fall, Rise Again",
    ],
    "educational": [
        "Smarter After Every Page",
        "The World Explained, Finally",
        "Big Ideas, Readable Prose",
        "What They Should Have Taught in School",
        "For the Perpetually Curious",
        "Facts That Feel Like Stories",
    ],
    "fantastical": [
        "Worlds You Will Never Want to Leave",
        "Magic Is Just the Beginning",
        "Reality Is Overrated",
        "For Those Who Believe in the Impossible",
        "Beyond the Edge of the Map",
        "Where Anything Can Happen",
    ],
}

SPECIAL_COLLECTIONS = {
    "free": "Free to Read Right Now",
    "new": "New This Week",
}


class CollectionEngine:
    """
    Clusters content into Netflix-style themed collections using KMeans
    on TF-IDF vectors, with mood labels from MoodDetector.
    Works for both books and comics.
    """

    def __init__(self, n_clusters: int = 8, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._mood_detector = MoodDetector()
        self._vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words="english",
        )
        self._kmeans: Optional[KMeans] = None
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def fit(self, items: List[Dict]) -> None:
        """
        Fits the TF-IDF vectorizer and KMeans on the provided items.
        """
        if not items:
            raise ValueError("Cannot fit on empty item list.")

        n = len(items)
        k = min(self.n_clusters, n)

        corpus = [self._build_corpus_text(item) for item in items]

        matrix = self._vectorizer.fit_transform(corpus)

        self._kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
        self._kmeans.fit(matrix)
        self._is_fitted = True

    def get_collections(self, items: List[Dict]) -> List[CollectionDict]:
        """
        Returns mood-labeled, Netflix-titled collections from items.
        Includes mood-based clusters plus special collections.
        """
        self._require_fitted()

        if not items:
            return []

        corpus = [self._build_corpus_text(item) for item in items]
        matrix = self._vectorizer.transform(corpus)
        labels = self._kmeans.predict(matrix)

        clusters: Dict[int, List[Dict]] = {}
        for item, label in zip(items, labels):
            clusters.setdefault(int(label), []).append(item)

        collections: List[CollectionDict] = []

        for cluster_id, cluster_items in clusters.items():
            mood = self._dominant_mood(cluster_items)
            title = self._pick_title(mood, cluster_ids=[
                item.get("id", "") for item in cluster_items
            ])
            content_ids = [
                str(item["id"]) for item in cluster_items if item.get("id")
            ]
            collection: CollectionDict = {
                "id": f"{mood}-{cluster_id:03d}",
                "title": title,
                "mood": mood,
                "items": content_ids,
                "item_count": len(content_ids),
            }
            collections.append(collection)

        special = self._build_special_collections(items)
        collections.extend(special)

        return collections

    def get_special_collections(self, items: List[Dict]) -> List[CollectionDict]:
        """
        Returns only the special (non-mood-clustered) collections.
        Does not require fit.
        """
        return self._build_special_collections(items)

    def _require_fitted(self) -> None:
        if not self._is_fitted:
            raise RuntimeError(
                "CollectionEngine must be fitted before calling get_collections. "
                "Call fit(items) first."
            )

    def _build_corpus_text(self, item: Dict) -> str:
        parts: List[str] = []

        for field in ["title", "description"]:
            value = item.get(field)
            if isinstance(value, str):
                parts.append(value.lower())

        for field in ["genres", "categories", "subjects"]:
            value = item.get(field)
            if isinstance(value, list):
                parts.extend(str(v).lower() for v in value)
                parts.extend(str(v).lower() for v in value)

        return " ".join(parts) if parts else "unknown"

    def _dominant_mood(self, items: List[Dict]) -> str:
        moods = self._mood_detector.detect_batch(items)
        if not moods:
            return MoodDetector.DEFAULT_MOOD
        return max(set(moods), key=moods.count)

    def _pick_title(self, mood: str, cluster_ids: List[str]) -> str:
        templates = TITLE_TEMPLATES.get(mood, TITLE_TEMPLATES["fantastical"])
        fingerprint = "".join(sorted(cluster_ids)).encode()
        index = int(hashlib.md5(fingerprint).hexdigest(), 16) % len(templates)
        return templates[index]

    def _build_special_collections(self, items: List[Dict]) -> List[CollectionDict]:
        collections: List[CollectionDict] = []

        free_items = [
            item for item in items
            if item.get("source") == "internet_archive"
            or item.get("is_public_domain") is True
        ]
        if free_items:
            collections.append({
                "id": "special-free",
                "title": SPECIAL_COLLECTIONS["free"],
                "mood": "educational",
                "items": [str(i["id"]) for i in free_items if i.get("id")],
                "item_count": len(free_items),
            })

        new_items = [
            item for item in items
            if self._is_recent(item.get("published_date"))
        ]
        if new_items:
            collections.append({
                "id": "special-new",
                "title": SPECIAL_COLLECTIONS["new"],
                "mood": "fantastical",
                "items": [str(i["id"]) for i in new_items if i.get("id")],
                "item_count": len(new_items),
            })

        return collections

    def _is_recent(self, published_date: Optional[str]) -> bool:
        if not published_date:
            return False
        try:
            year = int(str(published_date)[:4])
            return year >= 2023
        except (ValueError, TypeError):
            return False