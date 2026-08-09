import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

from fastapi.testclient import TestClient

from src.main import app
from src.ml.collection_engine import CollectionEngine
from src.ml.collaborative import CollaborativeFilter
from src.ml.hybrid import HybridEngine
from src.ml.neural import NeuralRecommender
from src.ml.personalizer import Personalizer
from src.ml.vectorizer import ContentVectorizer
from src.services.collection_service import CollectionService


def _build_catalog() -> list[dict]:
    return [
        {
            "id": "b1",
            "title": "Dragon Academy",
            "authors": ["A. Mage"],
            "categories": ["Fantasy"],
            "description": "A young mage enters a dragon school and learns magic with friends.",
            "content_type": "book",
            "is_public_domain": False,
            "published_year": 2024,
        },
        {
            "id": "b2",
            "title": "The Fire Crown",
            "authors": ["A. Mage"],
            "categories": ["Fantasy"],
            "description": "A kingdom at war, ancient magic, dragons, and a reluctant hero.",
            "content_type": "book",
            "is_public_domain": False,
            "published_year": 2023,
        },
        {
            "id": "b3",
            "title": "Sword of Ash",
            "authors": ["B. Knight"],
            "categories": ["Fantasy"],
            "description": "A dark fantasy quest with cursed swords, kingdoms, and epic battles.",
            "content_type": "book",
            "is_public_domain": False,
            "published_year": 2022,
        },
        {
            "id": "b4",
            "title": "Star Voyage",
            "authors": ["C. Nova"],
            "categories": ["Science Fiction"],
            "description": "A crew explores deep space, alien worlds, and distant galaxies.",
            "content_type": "book",
            "is_public_domain": False,
            "published_year": 2024,
        },
        {
            "id": "b5",
            "title": "Orbit Station",
            "authors": ["C. Nova"],
            "categories": ["Science Fiction"],
            "description": "Mystery and survival on a remote station at the edge of the galaxy.",
            "content_type": "book",
            "is_public_domain": False,
            "published_year": 2021,
        },
        {
            "id": "b6",
            "title": "Moon Signal",
            "authors": ["D. Vector"],
            "categories": ["Science Fiction"],
            "description": "Scientists discover a signal from the moon and uncover hidden technology.",
            "content_type": "book",
            "is_public_domain": True,
            "published_year": 1920,
        },
        {
            "id": "c1",
            "title": "Night Mask Vol. 1",
            "authors": ["E. Panel"],
            "categories": ["Comics", "Superhero"],
            "description": "A vigilante fights crime in a neon city with gadgets and shadows.",
            "content_type": "comic",
            "is_public_domain": False,
            "published_year": 2024,
        },
        {
            "id": "c2",
            "title": "Night Mask Vol. 2",
            "authors": ["E. Panel"],
            "categories": ["Comics", "Superhero"],
            "description": "The masked hero faces a new villain in a dark futuristic city.",
            "content_type": "comic",
            "is_public_domain": False,
            "published_year": 2025,
        },
        {
            "id": "c3",
            "title": "Galaxy Squad",
            "authors": ["F. Ink"],
            "categories": ["Comics", "Science Fiction"],
            "description": "A comic adventure with space marines, alien battles, and starships.",
            "content_type": "comic",
            "is_public_domain": False,
            "published_year": 2023,
        },
        {
            "id": "c4",
            "title": "Laugh Street",
            "authors": ["G. Sketch"],
            "categories": ["Comics", "Humor"],
            "description": "A light and funny comic full of jokes, friendships, and chaotic days.",
            "content_type": "comic",
            "is_public_domain": True,
            "published_year": 1915,
        },
    ]


def _build_ratings() -> list[dict]:
    return [
        {"user_id": "u1", "content_id": "b1", "rating": 5},
        {"user_id": "u1", "content_id": "b2", "rating": 4},
        {"user_id": "u1", "content_id": "c1", "rating": 4},
        {"user_id": "u2", "content_id": "b1", "rating": 5},
        {"user_id": "u2", "content_id": "b3", "rating": 4},
        {"user_id": "u2", "content_id": "c1", "rating": 3},
        {"user_id": "u3", "content_id": "b4", "rating": 5},
        {"user_id": "u3", "content_id": "b5", "rating": 4},
        {"user_id": "u3", "content_id": "c3", "rating": 4},
        {"user_id": "u4", "content_id": "b2", "rating": 5},
        {"user_id": "u4", "content_id": "b3", "rating": 4},
        {"user_id": "u4", "content_id": "c2", "rating": 4},
    ]


def _catalog_to_metadata(catalog: list[dict]) -> list[dict]:
    return [{**item, "content_id": item["id"]} for item in catalog]


def _extract_item_ids_from_rows(rows: list[dict]) -> set[str]:
    """Extract item IDs from collection rows, handling both dict and str items."""
    ids: set[str] = set()
    for row in rows:
        for item in row["items"]:
            if isinstance(item, dict):
                ids.add(item["id"])
            else:
                ids.add(str(item))
    return ids


def test_full_ml_pipeline_builds_personalized_home_screen() -> None:
    catalog = _build_catalog()
    ratings = _build_ratings()
    user_ratings = [rating for rating in ratings if rating["user_id"] == "u1"]

    hybrid_engine = HybridEngine(
        vectorizer=ContentVectorizer(),
        collaborative=CollaborativeFilter(),
        neural=NeuralRecommender(
            n_factors=8,
            epochs=1,
            batch_size=8,
            min_ratings=999,
        ),
        personalizer=Personalizer(),
        max_seeds=2,
        similar_per_seed=5,
    )
    hybrid_engine.fit(_catalog_to_metadata(catalog), ratings)

    service = CollectionService(
        collection_engine=CollectionEngine(),
        hybrid_engine=hybrid_engine,
        personalizer=Personalizer(),
    )

    rows = service.build_home_screen(
        catalog=catalog,
        user_id="u1",
        user_ratings=user_ratings,
        content_preference="both",
        n_collections=6,
        row_limit=4,
    )

    assert rows
    assert len(rows) <= 6

    row_ids = [row["id"] for row in rows]
    assert len(row_ids) == len(set(row_ids))

    assert rows[0]["title"].startswith("Because you loved")
    assert any(row["title"] == "Picked for You" for row in rows)

    catalog_ids = {item["id"] for item in catalog}
    recommended_item_ids = _extract_item_ids_from_rows(rows)

    assert recommended_item_ids
    assert recommended_item_ids <= catalog_ids

    for row in rows:
        assert {"id", "title", "items", "item_count"} <= set(row.keys())
        assert len(row["items"]) <= 4
        assert row["item_count"] == len(row["items"])


def test_collections_route_returns_valid_anonymous_envelope() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/collections?n_collections=4&row_limit=5")

    assert response.status_code == 200

    payload = response.json()

    assert payload["success"] is True
    assert "data" in payload
    assert "meta" in payload
    assert payload["meta"]["version"] == "v1"

    data = payload["data"]

    assert {"collections", "total", "personalized"} <= set(data.keys())
    assert isinstance(data["collections"], list)
    assert data["total"] == len(data["collections"])
    assert data["personalized"] is False

    for row in data["collections"]:
        assert {"id", "title", "items", "item_count"} <= set(row.keys())
        assert row["item_count"] == len(row["items"])
        assert len(row["items"]) <= 5