import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import success_envelope
from src.database.base import Book
from src.database.crud.book import upsert_book_from_comic_vine, upsert_book_from_google
from src.external.comic_vine import ComicVineClient
from src.external.google_books import GoogleBooksClient
from src.ml import SeriesBuilder, SeriesDetector

router = APIRouter(prefix="/api/v1/books", tags=["series"])

gb_client = GoogleBooksClient()
cv_client = ComicVineClient()
detector = SeriesDetector()
builder = SeriesBuilder()

_GB_COMPANION_KEYWORDS = (
    "guide",
    "handbook",
    "collection",
    "illustrations",
    "illustration",
    "art",
    "year",
    "magical year",
    "spellbook",
    "companion",
    "trivia",
    "wizarding archive",
)

_GB_EDITION_SUFFIX_PATTERNS = (
    r"\s*-\s*gryffindor edition$",
    r"\s*-\s*slytherin edition$",
    r"\s*-\s*hufflepuff edition$",
    r"\s*-\s*ravenclaw edition$",
    r"\s*-\s*the illustrated edition$",
    r"\s*:\s*the illustrated edition$",
    r"\s*-\s*illustrated edition$",
    r"\s*:\s*illustrated edition$",
    r"\s*-\s*\d+(?:st|nd|rd|th)\s+anniversary edition$",
    r"\s*:\s*\d+(?:st|nd|rd|th)\s+anniversary edition$",
)

_HP_TITLE_POSITION_RULES = (
    (1, ("philosopher's stone", "philosophers stone", "sorcerer's stone", "sorcerers stone")),
    (2, ("chamber of secrets",)),
    (3, ("prisoner of azkaban",)),
    (4, ("goblet of fire",)),
    (5, ("order of the phoenix",)),
    (6, ("half-blood prince", "half blood prince")),
    (7, ("deathly hallows",)),
)


@router.get("/{book_id}/series")
async def get_book_series(book_id: str, db: AsyncSession = Depends(get_db)):
    """Return reading order guide for a book or comic series."""
    item = await _fetch_item(book_id, db)

    if not item:
        raise HTTPException(status_code=404, detail="Book or comic not found.")

    detection = detector.detect(item)
    detection = _enrich_detection_with_known_position(item, detection)

    if not detection["is_series"]:
        return success_envelope(data=None)

    series_items = await _fetch_series_items(item, detection)

    result = builder.build(item, series_items, detection)

    return success_envelope(data=result)


async def _fetch_item(book_id: str, db: AsyncSession) -> dict | None:
    """Fetch a single item. DB-first with metadata backfill."""
    if ":" not in book_id:
        return None

    prefix, raw_id = book_id.split(":", 1)

    if prefix == "ia":
        return None

    source_map = {"gb": "google_books", "cv": "comic_vine"}
    if prefix not in source_map:
        return None

    source = source_map[prefix]

    stmt = select(Book).where(
        Book.external_source == source,
        Book.external_id == raw_id,
    )
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()

    if prefix == "gb":
        if _gb_needs_series_backfill(book):
            book = await _backfill_gb_series_info(raw_id, book, db)
        if book is not None:
            return _book_to_detector_dict(book, book_id, source)
        return None

    if prefix == "cv":
        if _cv_needs_series_backfill(book):
            book = await _backfill_cv_series_info(raw_id, book, db)
        if book is not None:
            return _book_to_detector_dict(book, book_id, source)
        return None

    return None


def _gb_needs_series_backfill(book: Book | None) -> bool:
    if book is None:
        return True
    metadata = book.metadata_json or {}
    gb_meta = metadata.get("google_books") if isinstance(metadata, dict) else None
    if not isinstance(gb_meta, dict):
        return True
    return "seriesInfo" not in gb_meta


def _cv_needs_series_backfill(book: Book | None) -> bool:
    if book is None:
        return True
    metadata = book.metadata_json or {}
    cv_meta = metadata.get("comic_vine") if isinstance(metadata, dict) else None
    if not isinstance(cv_meta, dict):
        return True
    return "volume" not in cv_meta


async def _backfill_gb_series_info(
    raw_id: str,
    existing_book: Book | None,
    db: AsyncSession,
) -> Book | None:
    try:
        raw = await gb_client.get_by_id(raw_id)
    except Exception:
        return existing_book

    if raw is None:
        return existing_book

    has_series_info = isinstance(raw.get("series_info"), dict)

    if not has_series_info and existing_book is not None:
        return existing_book

    try:
        refreshed = await upsert_book_from_google(db, raw)
        return refreshed
    except Exception:
        return existing_book


async def _backfill_cv_series_info(
    raw_id: str,
    existing_book: Book | None,
    db: AsyncSession,
) -> Book | None:
    try:
        raw = await cv_client.get_comic(raw_id)
    except Exception:
        return existing_book

    if raw is None:
        return existing_book

    has_volume = isinstance(raw.get("volume"), dict) and raw["volume"].get("id")

    if not has_volume and existing_book is not None:
        return existing_book

    try:
        refreshed = await upsert_book_from_comic_vine(db, raw)
        return refreshed
    except Exception:
        return existing_book


def _book_to_detector_dict(book: Book, content_id: str, source: str) -> dict:
    metadata = book.metadata_json or {}

    out: dict = {
        "content_id": content_id,
        "source": source,
        "title": book.title,
        "authors": book.authors or [],
    }

    if source == "google_books":
        gb_meta = metadata.get("google_books") if isinstance(metadata, dict) else None
        if isinstance(gb_meta, dict) and "seriesInfo" in gb_meta:
            out["seriesInfo"] = gb_meta["seriesInfo"]

    if source == "comic_vine":
        cv_meta = metadata.get("comic_vine") if isinstance(metadata, dict) else None
        if isinstance(cv_meta, dict):
            if "volume" in cv_meta:
                out["volume"] = cv_meta["volume"]
            if "issue_number" in cv_meta:
                out["issue_number"] = cv_meta["issue_number"]

    return out


async def _fetch_series_items(item: dict, detection: dict) -> list[dict]:
    try:
        series_name = detection.get("series_name") or ""
        if not series_name:
            return []

        if item.get("source") == "comic_vine":
            return await _fetch_cv_series_items(item, detection)

        return await _fetch_gb_series_items(item, detection)

    except Exception:
        return []


async def _fetch_cv_series_items(item: dict, detection: dict) -> list[dict]:
    """Fetch exact Comic Vine series items by volume id, not fuzzy search."""
    volume = item.get("volume") or {}
    volume_id = volume.get("id")
    series_name = detection.get("series_name") or ""

    if not volume_id:
        return []

    issues = await cv_client.get_issues_by_volume(volume_id)
    filtered: list[dict] = []

    for issue in issues:
        issue["source"] = "comic_vine"
        raw = issue.get("external_id", "")
        issue["content_id"] = f"cv:{raw}" if raw else ""

        issue_detection = detector.detect(issue)
        if not issue_detection.get("is_series"):
            continue
        if not _same_series(issue_detection, detection):
            continue

        issue["position"] = issue_detection.get("position")

        if not issue.get("title"):
            number = issue.get("issue_number")
            issue["title"] = f"{series_name} #{number}" if number else series_name

        filtered.append(issue)

    return filtered


async def _fetch_gb_series_items(item: dict, detection: dict) -> list[dict]:
    """Fetch Google Books series items via cleaned heuristic search."""
    series_name = detection.get("series_name") or ""
    current_author = _first_author(item)
    current_title = item.get("title") or ""
    current_position = detection.get("position")

    current_key = _canonical_gb_series_member_key(
        series_name=series_name,
        title=current_title,
        position=current_position,
    )

    seen_keys: set[str] = set()
    if current_key:
        seen_keys.add(current_key)

    query = f"{series_name} {current_author}" if current_author else series_name
    results = await gb_client.search(query, max_results=40)

    filtered: list[dict] = []

    for si in results:
        si["source"] = "google_books"
        raw = si.get("google_books_id", "")
        si["content_id"] = f"gb:{raw}" if raw else ""

        title = si.get("title") or ""
        if not title:
            continue

        candidate_author = _first_author(si)
        if current_author and candidate_author:
            if not _same_author(current_author, candidate_author):
                continue

        if _is_probable_gb_companion_book(series_name, title):
            continue

        candidate_detection = detector.detect(si)
        candidate_detection = _enrich_detection_with_known_position(si, candidate_detection)

        if not _same_series(candidate_detection, detection):
            if not _looks_like_gb_series_member(title, series_name):
                continue

        position = candidate_detection.get("position")
        key = _canonical_gb_series_member_key(
            series_name=series_name,
            title=title,
            position=position,
        )

        if key and key in seen_keys:
            continue
        if key:
            seen_keys.add(key)

        si["position"] = position
        filtered.append(si)

    return filtered


def _enrich_detection_with_known_position(item: dict, detection: dict) -> dict:
    """Backfill position from title heuristics when detector found series but no order."""
    if not detection.get("is_series"):
        return detection

    if detection.get("position") is not None:
        return detection

    if item.get("source") != "google_books":
        return detection

    series_name = detection.get("series_name") or ""
    title = item.get("title") or ""
    inferred = _infer_known_gb_series_position(series_name, title)

    if inferred is None:
        return detection

    enriched = dict(detection)
    enriched["position"] = inferred
    enriched["confidence"] = max(float(detection.get("confidence") or 0.0), 0.7)
    return enriched


def _infer_known_gb_series_position(series_name: str, title: str) -> int | None:
    normalized_series = _normalize_text(series_name)
    normalized_title = _normalize_text(title)

    if not normalized_series or not normalized_title:
        return None

    if normalized_series == "harry potter":
        for position, needles in _HP_TITLE_POSITION_RULES:
            if any(needle in normalized_title for needle in needles):
                return position

    match = re.search(r"\bbook\s+(\d+)\b", normalized_title)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None

    return None


def _same_series(left: dict, right: dict) -> bool:
    left_id = left.get("series_id")
    right_id = right.get("series_id")
    if left_id and right_id:
        return str(left_id) == str(right_id)

    left_name = _normalize_text(left.get("series_name"))
    right_name = _normalize_text(right.get("series_name"))
    return bool(left_name and right_name and left_name == right_name)


def _looks_like_gb_series_member(title: str, series_name: str) -> bool:
    normalized_title = _normalize_text(title)
    normalized_series = _normalize_text(series_name)

    if not normalized_title or not normalized_series:
        return False

    if normalized_title.startswith(normalized_series + " and "):
        return True
    if normalized_title.startswith(normalized_series + ":"):
        return True
    if normalized_title.startswith(normalized_series + " - "):
        return True
    if normalized_title.startswith(normalized_series + " book "):
        return True
    if normalized_title.startswith(normalized_series + " #"):
        return True

    return False


def _is_probable_gb_companion_book(series_name: str, title: str) -> bool:
    normalized_series = _normalize_text(series_name)
    normalized_title = _normalize_text(title)

    if not normalized_series or not normalized_title:
        return False

    if normalized_title == normalized_series:
        return True

    if not normalized_title.startswith(normalized_series):
        return False

    return any(keyword in normalized_title for keyword in _GB_COMPANION_KEYWORDS)


def _canonical_gb_series_member_key(
    series_name: str,
    title: str,
    position: int | None,
) -> str | None:
    if position is not None:
        return f"pos:{position}"

    normalized = _clean_gb_title_for_key(title)
    normalized_series = _normalize_text(series_name)

    if not normalized or normalized == normalized_series:
        return None

    return normalized


def _clean_gb_title_for_key(title: str) -> str:
    normalized = _normalize_text(title)

    normalized = re.sub(r"\s*\([^)]*book\s+\d+[^)]*\)$", "", normalized)
    normalized = re.sub(r"\s+by\s+j\.?\s*k\.?\s*rowling$", "", normalized)

    for pattern in _GB_EDITION_SUFFIX_PATTERNS:
        normalized = re.sub(pattern, "", normalized)

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _first_author(item: dict) -> str | None:
    authors = item.get("authors")
    if isinstance(authors, list) and authors:
        first = authors[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    return None


def _same_author(left: str, right: str) -> bool:
    return _normalize_person_name(left) == _normalize_person_name(right)


def _normalize_person_name(value: str | None) -> str:
    if not value:
        return ""
    lowered = value.lower()
    return re.sub(r"[^a-z0-9]", "", lowered)


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().lower())