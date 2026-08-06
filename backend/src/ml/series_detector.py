import re
from typing import Any, Dict, Optional


class SeriesDetector:
    # Patterns to catch: "Book 2", "Part 3", "#4", "Volume 5", "Vol. 6"
    # Case insensitive, handles whitespace
    RE_PATTERNS = [
        r"\bbook\s+(\d+)",
        r"\bpart\s+(\d+)",
        r"#(\d+)",
        r"\bvol(?:ume)?\.?\s+(\d+)",
    ]

    # Words that imply a series even without a number
    SERIES_KEYWORDS = ["chronicles", "saga", "series", "trilogy"]

    def detect(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Detect whether an item belongs to a series."""
        if not item:
            return self._empty()

        source = item.get("source")

        # Rule 1 — Comic Vine
        if source == "comic_vine":
            volume = item.get("volume") or {}
            volume_id = volume.get("id")
            volume_name = volume.get("name")
            issue_number = item.get("issue_number")

            if volume_id and volume_name:
                position = self._safe_int(issue_number)
                return {
                    "is_series": True,
                    "series_name": volume_name,
                    "series_id": f"cv_volume_{volume_id}",
                    "position": position,
                    "confidence": 0.95 if position else 0.9,
                }

        # Rule 2 — Google Books seriesInfo
        series_info = item.get("seriesInfo")
        if isinstance(series_info, dict):
            series_list = series_info.get("series") or []
            display_number = series_info.get("bookDisplayNumber")

            if series_list:
                first_series = series_list[0]
                series_id = first_series.get("seriesId")
                series_name = first_series.get("seriesName")

                if series_name:
                    position = self._safe_int(display_number)
                    return {
                        "is_series": True,
                        "series_name": series_name,
                        "series_id": series_id,
                        "position": position,
                        "confidence": 0.9 if position else 0.85,
                    }

        # Rule 3 — Title Pattern Detection (Fallback)
        title_detection = self._detect_from_title(item.get("title") or "")
        if title_detection["is_series"]:
            return title_detection

        return self._empty()

    def _detect_from_title(self, title: str) -> Dict[str, Any]:
        """Extract series info from title string patterns."""
        if not title:
            return self._empty()

        # Try to find position first (Rule 3)
        for pattern in self.RE_PATTERNS:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                position_val = match.group(1)
                # Clean title to get series name (remove the matched part)
                series_name = title[: match.start()].strip()
                # If series_name becomes empty (e.g. title is just "#4"), use original
                if not series_name:
                    series_name = title

                # Remove trailing punctuation like ":" or "-"
                series_name = re.sub(r"[:\-\(]+$", "", series_name).strip()

                return {
                    "is_series": True,
                    "series_name": series_name,
                    "series_id": self._slugify(series_name),
                    "position": self._safe_int(position_val),
                    "confidence": 0.6,
                }

        # Look for keywords without position (Rule 4)
        lower_title = title.lower()
        if any(keyword in lower_title for keyword in self.SERIES_KEYWORDS):
            return {
                "is_series": True,
                "series_name": title,
                "series_id": self._slugify(title),
                "position": None,
                "confidence": 0.4,
            }

        return self._empty()

    def _empty(self) -> Dict[str, Any]:
        return {
            "is_series": False,
            "series_name": None,
            "series_id": None,
            "position": None,
            "confidence": 0.0,
        }

    def _safe_int(self, value: Any) -> Optional[int]:
        try:
            return int(float(value)) # float handle "1.0"
        except (TypeError, ValueError):
            return None

    def _slugify(self, text: str) -> str:
        """Simple slug for series_id when missing."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[-\s]+", "_", text)