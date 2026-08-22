"""Diagnose seed cover enrichment."""

from __future__ import annotations

import asyncio
import sys
import traceback
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api.routes.collections import _enrich_item_real, _get_base_catalog
from src.services.content_router import ContentRouter


async def main() -> None:
    try:
        db = AsyncMock()
        mock_google_books = AsyncMock()
        mock_comic_vine = AsyncMock()
        mock_archive = AsyncMock()

        router = ContentRouter(
            google_books=mock_google_books,
            comic_vine=mock_comic_vine,
            internet_archive=mock_archive,
            db=db,
        )

        base = _get_base_catalog()[0]
        print("Seed title:", base.get("title"))
        print("Seed query:", base.get("search_query"))
        print("Before cover:", base.get("cover_url"))

        enriched = await _enrich_item_real(base, router)
        print("After cover:", None if enriched is None else enriched.get("cover_url"))
        print("After keys:", None if enriched is None else list(enriched.keys())[:12])
    except Exception:
        print("--- TRACEBACK ---")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())