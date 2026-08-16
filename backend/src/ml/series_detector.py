import re
from typing import Any, Dict, Optional


class SeriesDetector:
    RE_PATTERNS = [
        r"\bbook\s+(\d+)",
        r"\bpart\s+(\d+)",
        r"#(\d+)",
        r"\bvol(?:ume)?\.?\s+(\d+)",
    ]

    FRANCHISE_TITLE_PATTERNS = [
        re.compile(
            r"^([A-Z][\w'’.-]+(?:\s+[A-Z][\w'’.-]+)+)\s+and\s+(?:the|a|an)\s+.+$"
        ),
    ]

    SERIES_KEYWORDS = ["chronicles", "saga", "series", "trilogy"]

    def detect(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Detect whether an item belongs to a series."""
        if not item:
            return self._empty()

        source = item.get("source")

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
                    "confidence": 0.95 if position is not None else 0.9,
                }

        series_info = item.get("seriesInfo")
        if isinstance(series_info, dict):
            series_list = series_info.get("series") or []
            display_number = series_info.get("bookDisplayNumber")

            if series_list:
                first_series = series_list[0]
                series_id = first_series.get("seriesId")
                series_name = first_series.get("seriesName")

                if series_name:
                    position = self._parse_display_number(display_number)
                    return {
                        "is_series": True,
                        "series_name": series_name,
                        "series_id": series_id,
                        "position": position,
                        "confidence": 0.9 if position is not None else 0.85,
                    }

        title_detection = self._detect_from_title(item.get("title") or "")
        if title_detection["is_series"]:
            return title_detection

        return self._empty()

    def _detect_from_title(self, title: str) -> Dict[str, Any]:
        """Extract series info from title string patterns."""
        if not title:
            return self._empty()

        for pattern in self.RE_PATTERNS:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                position_val = match.group(1)
                series_name = title[: match.start()].strip()
                if not series_name:
                    series_name = title
                series_name = re.sub(r"[:\-\(]+$", "", series_name).strip()

                return {
                    "is_series": True,
                    "series_name": series_name,
                    "series_id": self._slugify(series_name),
                    "position": self._safe_int(position_val),
                    "confidence": 0.6,
                }

        franchise_detection = self._detect_named_franchise_title(title)
        if franchise_detection is not None:
            return franchise_detection

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

    def _detect_named_franchise_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Heuristic for titles like 'Harry Potter and the ...'."""
        stripped = title.strip()

        for pattern in self.FRANCHISE_TITLE_PATTERNS:
            match = pattern.match(stripped)
            if match:
                series_name = match.group(1).strip()
                if len(series_name.split()) >= 2:
                    return {
                        "is_series": True,
                        "series_name": series_name,
                        "series_id": self._slugify(series_name),
                        "position": None,
                        "confidence": 0.55,
                    }

        return None

    def _empty(self) -> Dict[str, Any]:
        return {
            "is_series": False,
            "series_name": None,
            "series_id": None,
            "position": None,
            "confidence": 0.0,
        }

    def _parse_display_number(self, value: Any) -> Optional[int]:
        return self._safe_int(value)

    def _safe_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None

        try:
            return int(float(value))
        except (TypeError, ValueError):
            pass

        if isinstance(value, str):
            match = re.search(r"(\d+)", value)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None

        return None

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[-\s]+", "_", text)