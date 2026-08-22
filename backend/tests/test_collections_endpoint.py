"""Integration test for home screen collections endpoint and dynamic discovery."""

from __future__ import annotations

import asyncio
import sys
import traceback
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Ensure backend root is on sys.path when run as a script
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api.routes.collections import get_collections


async def test_get_collections_anonymous_returns_success() -> None:
    """Verify anonymous user collections route returns themed rows."""
    request = MagicMock()
    db = AsyncMock()

    # Mock ContentRouter dependencies
    mock_google_books = AsyncMock()
    mock_comic_vine = AsyncMock()
    mock_archive = AsyncMock()

    from src.services.content_router import ContentRouter

    content_router = ContentRouter(
        google_books=mock_google_books,
        comic_vine=mock_comic_vine,
        internet_archive=mock_archive,
        db=db,
    )

    response = await get_collections(
        request=request,
        n_collections=20,
        row_limit=20,
        current_user=None,
        db=db,
        content_router=content_router,
    )

    assert response["success"] is True
    assert "rows" in response["data"]
    assert isinstance(response["data"]["rows"], list)
    print(f"\nSUCCESS: Returned {response['data']['total']} collection rows")


async def main() -> None:
    try:
        await test_get_collections_anonymous_returns_success()
    except Exception:
        print("\n--- TRACEBACK ERROR START ---")
        traceback.print_exc()
        print("--- TRACEBACK ERROR END ---\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())