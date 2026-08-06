from __future__ import annotations

from typing import Dict, List


class MoodDetector:
    """
    Detects high-level content mood from metadata using keyword scoring.
    Works for both books and comics.
    """

    MOOD_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
        "dark": {
            "primary": [
                "dark", "grim", "dystopia", "dystopian", "horror",
                "violence", "brutal", "death", "war", "trauma",
                "psychological", "villain", "sinister", "gritty",
                "apocalypse", "apocalyptic",
            ],
            "secondary": [
                "crime", "conflict", "struggle", "survival",
                "fear", "shadow", "noir",
            ],
        },
        "adventurous": {
            "primary": [
                "adventure", "quest", "journey", "exploration",
                "epic", "action", "hero", "expedition",
                "survival", "battle", "warrior", "legend",
            ],
            "secondary": [
                "travel", "discover", "fight", "mission",
                "challenge", "treasure", "wild",
            ],
        },
        "romantic": {
            "primary": [
                "romance", "love", "relationship", "heart",
                "passion", "desire", "wedding", "marriage",
                "affair", "heartbreak",
            ],
            "secondary": [
                "emotion", "feeling", "connection", "couple",
                "kiss", "longing", "drama",
            ],
        },
        "funny": {
            "primary": [
                "comedy", "humor", "funny", "satire",
                "absurd", "laugh", "wit", "joke",
                "parody", "ridiculous", "hilarious",
            ],
            "secondary": [
                "quirky", "playful", "lighthearted",
                "whimsical", "silly", "sarcasm",
            ],
        },
        "mysterious": {
            "primary": [
                "mystery", "detective", "thriller", "suspense",
                "investigation", "crime", "secret",
                "conspiracy", "whodunit", "spy",
            ],
            "secondary": [
                "clue", "hidden", "puzzle", "shadow",
                "unknown", "danger", "intrigue", "assassin",
            ],
        },
        "inspiring": {
            "primary": [
                "inspire", "biography", "memoir", "triumph",
                "overcome", "resilience", "courage",
                "leadership", "success", "hope", "motivat",
            ],
            "secondary": [
                "journey", "personal", "growth",
                "true story", "faith", "dream", "achieve",
            ],
        },
        "educational": {
            "primary": [
                "science", "history", "philosophy", "nonfiction",
                "research", "factual", "academic",
                "knowledge", "theory", "explain",
            ],
            "secondary": [
                "learn", "study", "discover",
                "culture", "social", "political",
                "economic", "psychology",
            ],
        },
        "fantastical": {
            "primary": [
                "fantasy", "magic", "wizard", "dragon",
                "supernatural", "mytholog", "enchant",
                "sorcerer", "realm", "otherworldly",
                "fairy",
            ],
            "secondary": [
                "myth", "legend", "ancient", "prophecy",
                "mystical", "arcane", "curse", "spell",
            ],
        },
    }

    DEFAULT_MOOD = "fantastical"

    def detect(self, item: Dict) -> str:
        """
        Returns the highest scoring mood label for a single item.
        """
        scores = self.score_all(item)
        best_mood = max(scores, key=scores.get)

        if scores[best_mood] == 0:
            return self.DEFAULT_MOOD

        return best_mood

    def detect_batch(self, items: List[Dict]) -> List[str]:
        """
        Returns mood labels for a list of items.
        """
        return [self.detect(item) for item in items]

    def score_all(self, item: Dict) -> Dict[str, int]:
        """
        Returns raw mood scores for debugging/testing.
        """
        text = self._build_text(item)

        scores: Dict[str, int] = {}

        for mood, groups in self.MOOD_KEYWORDS.items():
            score = 0

            for word in groups["primary"]:
                if word in text:
                    score += 2

            for word in groups["secondary"]:
                if word in text:
                    score += 1

            scores[mood] = score

        return scores

    def _build_text(self, item: Dict) -> str:
        parts: List[str] = []

        for field in ["title", "description"]:
            value = item.get(field)
            if isinstance(value, str):
                parts.append(value.lower())

        for field in ["genres", "categories", "subjects"]:
            value = item.get(field)
            if isinstance(value, list):
                parts.extend(str(v).lower() for v in value)

        return " ".join(parts)