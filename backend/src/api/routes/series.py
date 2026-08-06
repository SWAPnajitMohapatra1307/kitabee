from fastapi import APIRouter, HTTPException
from src.api.response import success_envelope
from src.external.google_books import GoogleBooksClient
from src.external.comic_vine import ComicVineClient
from src.ml import SeriesDetector, SeriesBuilder

router = APIRouter(prefix="/api/v1/books", tags=["series"])

gb_client = GoogleBooksClient()
cv_client = ComicVineClient()
detector = SeriesDetector()
builder = SeriesBuilder()


@router.get("/{book_id}/series")
async def get_book_series(book_id: str):
    """
    Return reading order guide for a book or comic series.
    Works for Google Books (default) and Comic Vine (cv_ prefix).
    """
    item = await _fetch_item(book_id)

    if not item:
        raise HTTPException(status_code=404, detail="Book or comic not found.")

    detection = detector.detect(item)

    if not detection["is_series"]:
        return success_envelope(data=None)

    series_items = await _fetch_series_items(item, detection)

    result = builder.build(item, series_items, detection)

    return success_envelope(data=result)


async def _fetch_item(book_id: str) -> dict | None:
    """Fetch a single item from the correct API based on ID prefix."""
    try:
        if book_id.startswith("cv_"):
            raw_id = book_id.replace("cv_", "", 1)
            item = await cv_client.get_comic(raw_id)
            if item:
                item["source"] = "comic_vine"
                item["content_id"] = book_id
            return item

        item = await gb_client.get_by_id(book_id)
        if item:
            item["source"] = "google_books"
            item["content_id"] = book_id
        return item

    except Exception:
        return None


async def _fetch_series_items(item: dict, detection: dict) -> list[dict]:
    """Fetch other items in the same series from the correct API."""
    try:
        series_name = detection.get("series_name") or ""
        if not series_name:
            return []

        if item.get("source") == "comic_vine":
            issues = await cv_client.search_comics(series_name)
            for issue in issues:
                issue["source"] = "comic_vine"
                issue["content_id"] = f"cv_{issue.get('id', '')}"
            return issues

        results = await gb_client.search(series_name)
        for si in results:
            si["source"] = "google_books"
            si["content_id"] = si.get("id", "")
        return results

    except Exception:
        return []