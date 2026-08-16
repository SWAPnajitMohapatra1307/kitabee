from __future__ import annotations

import random
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
        "Stories That Left a Mark",
        "No Happy Endings Here",
        "The Ones That Haunt You",
        "Darkness Done Right",
        "Bleak Never Looked This Good",
        "For Those Who Like It Heavy",
        "When the Story Goes Somewhere Real",
        "The Kind of Dark You Can't Look Away From",
        "Uncomfortable Truths, Brilliant Writing",
        "Beautiful and Devastating",
        "Read These in Daylight",
        "They Will Wreck You in the Best Way",
        "Heavy. Necessary. Brilliant.",
        "Not Okay — But Worth It",
    ],
    "adventurous": [
        "Epic Worlds Built From Scratch",
        "Strap In, It's Going to Be Wild",
        "Heroes Who Refused to Stay Home",
        "The Quest Begins Here",
        "For Those Who Crave the Unknown",
        "Big Adventures, Bigger Stakes",
        "Worlds Worth Getting Lost In",
        "Run. Fight. Survive.",
        "The Map Ends Here — Go Anyway",
        "Pack Your Bags for Somewhere Impossible",
        "Action First, Questions Later",
        "Because the Real World Is Boring",
        "The Adventure You Needed Today",
        "When Stakes Are Life or Death",
        "Buckle Up",
        "No Turning Back Now",
        "Pages That Move at Full Speed",
        "Bold, Breathless, Brilliant",
        "The Road Goes On Forever",
        "Go Somewhere You've Never Been",
    ],
    "romantic": [
        "Love in Every Page",
        "For the Hopeless Romantics",
        "Hearts on the Line",
        "When Love Gets Complicated",
        "Stories That Believe in Love",
        "Tender, Messy, Real",
        "Fall in Love All Over Again",
        "The Slow Burn Collection",
        "When Two People Change Each Other",
        "Love Letters to the Genre",
        "Swoon-Worthy From Page One",
        "Feelings You Did Not Ask For",
        "Stay Up Late for These",
        "The Kind of Love That Hurts Good",
        "For When You Want to Feel Everything",
        "Devastating in the Best Way",
        "Romance Done Right",
        "Will They Won't They — They Will",
        "Because Love Is Complicated",
        "Heartfelt. Honest. Unforgettable.",
    ],
    "funny": [
        "Seriously Though, These Are Funny",
        "Read This, Feel Better",
        "Wit Sharp Enough to Cut",
        "Comics and Books That Actually Make You Laugh",
        "The Lighter Side of Everything",
        "No Tragedy Here, Promise",
        "Laugh Out Loud, No Really",
        "Absurd in All the Right Ways",
        "Smart Funny Is the Best Funny",
        "Books That Got Banned for Being Too Good",
        "The Antidote to a Bad Week",
        "Ridiculous. Brilliant. Both.",
        "For When You Need to Laugh",
        "Chaos Energy, Excellent Results",
        "Funny Because It's True",
        "Comedy That Respects Your Intelligence",
        "The Kind of Book That Makes You Snort",
        "Life Is Absurd — Lean Into It",
        "Reading With a Grin",
        "Sharp, Silly, and Surprisingly Deep",
    ],
    "mysterious": [
        "You Won't See It Coming",
        "Clues, Lies, and Brilliant Minds",
        "The Truth Is in Here Somewhere",
        "For People Who Notice Everything",
        "Stay Up Late, Can't Put It Down",
        "Everyone Is a Suspect",
        "Nothing Is What It Seems",
        "The Puzzle Box Collection",
        "One More Chapter. Just One More.",
        "Trust No One",
        "The Answer Is Always Worse Than You Think",
        "For Readers Who Pay Attention",
        "Hidden in Plain Sight",
        "The Whodunit Hall of Fame",
        "Unreliable Narrators Welcome",
        "Twists That Actually Work",
        "Dark Secrets, Brilliant Reveals",
        "Keep the Lights On",
        "The Slow Unravelling",
        "Questions With Devastating Answers",
    ],
    "inspiring": [
        "Real People, Real Extraordinary Lives",
        "Stories That Actually Change You",
        "Against All Odds",
        "Because Someone Did It First",
        "The Fuel You Did Not Know You Needed",
        "Rise, Fall, Rise Again",
        "For When You Need to Believe Again",
        "Proof That People Are Capable of Anything",
        "The Human Spirit Does Not Quit",
        "Read These When Life Gets Hard",
        "Ordinary People, Extraordinary Courage",
        "They Said It Couldn't Be Done",
        "The Books That Built People",
        "Resilience on Every Page",
        "Stories That Make You Want to Do Something",
        "You Will Finish These Differently Than You Started",
        "Purpose, Grit, and the Long Game",
        "For the Days When You Need a Push",
        "Quietly Life-Changing",
        "The Ones That Stick With You Forever",
    ],
    "educational": [
        "Smarter After Every Page",
        "The World Explained, Finally",
        "Big Ideas, Readable Prose",
        "What They Should Have Taught in School",
        "For the Perpetually Curious",
        "Facts That Feel Like Stories",
        "Mind-Expanding Reads",
        "The Kind of Non-Fiction You Actually Finish",
        "Because Knowledge Is the Best Hobby",
        "Everything You Thought You Knew Is Wrong",
        "Ideas That Rewired Brains",
        "The Curious Person's Essential Library",
        "Science, History, and Everything in Between",
        "Dense With Ideas, Easy to Read",
        "For Readers Who Ask Why",
        "The Books Experts Recommend",
        "Fascinating From the First Page",
        "The Big Picture Collection",
        "Understanding the World One Book at a Time",
        "Sharp Minds, Clear Prose",
    ],
    "fantastical": [
        "Worlds You Will Never Want to Leave",
        "Magic Is Just the Beginning",
        "Reality Is Overrated",
        "For Those Who Believe in the Impossible",
        "Beyond the Edge of the Map",
        "Where Anything Can Happen",
        "Impossible Things Done Beautifully",
        "Stories With No Ceiling",
        "Magic Systems Worth Learning",
        "For the Part of You That Never Stopped Believing",
        "The Imagination Has No Limits Here",
        "When the Rules of Reality Don't Apply",
        "Wonder on Every Page",
        "Built From Pure Imagination",
        "The Escapist's Essential Library",
        "Far Away and Absolutely Worth It",
        "Once You Enter You Won't Come Back",
        "Dragons, Gods, and Impossible Journeys",
        "Fantastical and Completely Believable",
        "The Best Kind of Not Real",
    ],
    "thoughtful": [
        "Slow Burn, Deep Burn",
        "Books That Stay With You",
        "For When You Want to Feel Something",
        "Quiet Stories, Loud Impact",
        "Read Slowly, Think Long",
        "The Kind of Book You Reread",
        "Sit With These for a While",
        "Meaning Hidden in Plain Sight",
        "Beneath the Surface Is Everything",
        "The Ones That Ask the Big Questions",
        "Literature That Respects You",
        "For Readers Who Like to Think",
        "Stories That Demand Something Back",
        "Carefully Constructed, Deeply Felt",
        "The Quiet Ones That Hit Hardest",
        "For the Long Evening Read",
        "Pages Worth Returning To",
        "Subtle and Devastating",
        "Writing That Makes You Stop and Think",
        "The Considered Life in Book Form",
    ],
    "epic": [
        "Legends in Every Chapter",
        "Built for the Long Haul",
        "Stories Too Big for One World",
        "When the Stakes Are Everything",
        "Empires, Heroes, and Impossible Odds",
        "The Epic Shelf",
        "Doorstoppers Worth Every Page",
        "World-Building at Its Finest",
        "The Kind of Series You Live Inside",
        "Civilisations Rise and Fall Here",
        "For Those Who Want to Be Consumed",
        "Scope That Takes Your Breath Away",
        "When One Book Is Never Enough",
        "Big Books, Bigger Ideas",
        "The Grand Narrative Collection",
        "Mythology in the Making",
        "Stories That Earn Their Length",
        "For Readers Who Want Everything",
        "The Long Game — Worth Every Hour",
        "Monumental. Magnificent. Essential.",
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

    def __init__(self, n_clusters: int = 16) -> None:
        self.n_clusters = n_clusters
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

        self._kmeans = KMeans(n_clusters=k, n_init=10)
        self._kmeans.fit(matrix)
        self._is_fitted = True

    def get_collections(self, items: List[Dict]) -> List[CollectionDict]:
        """
        Returns mood-labeled, Netflix-titled collections from items.
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
            title = self._pick_title(mood)
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

    def _pick_title(self, mood: str) -> str:
        templates = TITLE_TEMPLATES.get(mood, TITLE_TEMPLATES["fantastical"])
        return random.choice(templates)

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