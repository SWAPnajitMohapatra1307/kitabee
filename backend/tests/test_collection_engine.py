import pytest
from src.ml.collection_engine import CollectionEngine, TITLE_TEMPLATES, SPECIAL_COLLECTIONS


# Fixtures

@pytest.fixture
def engine():
    return CollectionEngine(n_clusters=3, random_state=42)


@pytest.fixture
def dark_item():
    return {
        "id": "book_001",
        "title": "Dark Dystopia",
        "description": "A brutal grim horror story of war and trauma",
        "genres": ["Horror", "Dark Fiction"],
        "categories": [],
        "subjects": [],
    }


@pytest.fixture
def adventure_item():
    return {
        "id": "book_002",
        "title": "Epic Quest",
        "description": "An adventurous journey of exploration and battle",
        "genres": ["Adventure", "Action"],
        "categories": [],
        "subjects": [],
    }


@pytest.fixture
def fantasy_item():
    return {
        "id": "book_003",
        "title": "The Dragon Wizard",
        "description": "Magic and sorcery in a fantastical realm",
        "genres": ["Fantasy"],
        "categories": [],
        "subjects": [],
    }


@pytest.fixture
def free_item():
    return {
        "id": "ia_moby_dick",
        "title": "Moby Dick",
        "description": "Classic nautical adventure",
        "genres": [],
        "categories": [],
        "subjects": [],
        "source": "internet_archive",
        "is_public_domain": True,
    }


@pytest.fixture
def new_item():
    return {
        "id": "book_new",
        "title": "Brand New Book",
        "description": "A very recent publication",
        "genres": ["Fiction"],
        "categories": [],
        "subjects": [],
        "published_date": "2024-01-15",
    }


@pytest.fixture
def sample_items(dark_item, adventure_item, fantasy_item):
    return [dark_item, adventure_item, fantasy_item]


# Constants

class TestConstants:
    def test_title_templates_has_eight_moods(self):
        assert len(TITLE_TEMPLATES) == 8

    def test_each_mood_has_six_templates(self):
        for mood, templates in TITLE_TEMPLATES.items():
            assert len(templates) == 6, f"{mood} does not have 6 templates"

    def test_all_templates_are_strings(self):
        for mood, templates in TITLE_TEMPLATES.items():
            for t in templates:
                assert isinstance(t, str), f"{mood} has non-string template"

    def test_special_collections_keys(self):
        assert "free" in SPECIAL_COLLECTIONS
        assert "new" in SPECIAL_COLLECTIONS

    def test_special_collection_titles_are_strings(self):
        for title in SPECIAL_COLLECTIONS.values():
            assert isinstance(title, str)


# Init

class TestInit:
    def test_default_n_clusters(self):
        engine = CollectionEngine()
        assert engine.n_clusters == 8

    def test_custom_n_clusters(self):
        engine = CollectionEngine(n_clusters=4)
        assert engine.n_clusters == 4

    def test_not_fitted_on_init(self, engine):
        assert engine.is_fitted is False

    def test_random_state_stored(self):
        engine = CollectionEngine(random_state=99)
        assert engine.random_state == 99


# fit

class TestFit:
    def test_fit_sets_is_fitted(self, engine, sample_items):
        engine.fit(sample_items)
        assert engine.is_fitted is True

    def test_fit_empty_raises(self, engine):
        with pytest.raises(ValueError, match="empty"):
            engine.fit([])

    def test_fit_single_item(self, engine, dark_item):
        engine.fit([dark_item])
        assert engine.is_fitted is True

    def test_fit_k_capped_at_n(self, dark_item, adventure_item):
        engine = CollectionEngine(n_clusters=10, random_state=42)
        engine.fit([dark_item, adventure_item])
        assert engine.is_fitted is True

    def test_fit_idempotent(self, engine, sample_items):
        engine.fit(sample_items)
        engine.fit(sample_items)
        assert engine.is_fitted is True


# _require_fitted

class TestRequireFitted:
    def test_get_collections_before_fit_raises(self, engine, sample_items):
        with pytest.raises(RuntimeError, match="fitted"):
            engine.get_collections(sample_items)

    def test_get_collections_after_fit_does_not_raise(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        assert isinstance(result, list)


# _build_corpus_text

class TestBuildCorpusText:
    def test_uses_title(self, engine, dark_item):
        text = engine._build_corpus_text(dark_item)
        assert "dark" in text

    def test_uses_description(self, engine, dark_item):
        text = engine._build_corpus_text(dark_item)
        assert "brutal" in text

    def test_uses_genres(self, engine, dark_item):
        text = engine._build_corpus_text(dark_item)
        assert "horror" in text

    def test_empty_item_returns_unknown(self, engine):
        text = engine._build_corpus_text({})
        assert text == "unknown"

    def test_genres_repeated_twice(self, engine):
        item = {"genres": ["fantasy"]}
        text = engine._build_corpus_text(item)
        assert text.count("fantasy") == 2

    def test_categories_repeated_twice(self, engine):
        item = {"categories": ["science"]}
        text = engine._build_corpus_text(item)
        assert text.count("science") == 2


# _dominant_mood

class TestDominantMood:
    def test_majority_mood_wins(self, engine):
        items = [
            {"title": "dark horror grim"},
            {"title": "dark dystopia brutal"},
            {"title": "magic wizard fantasy"},
        ]
        mood = engine._dominant_mood(items)
        assert mood == "dark"

    def test_empty_items_returns_default(self, engine):
        mood = engine._dominant_mood([])
        assert mood == "fantastical"

    def test_single_item_mood(self, engine, dark_item):
        mood = engine._dominant_mood([dark_item])
        assert mood == "dark"


# _pick_title

class TestPickTitle:
    def test_returns_string(self, engine):
        title = engine._pick_title("dark", ["id1", "id2"])
        assert isinstance(title, str)

    def test_title_in_templates(self, engine):
        title = engine._pick_title("dark", ["id1", "id2"])
        assert title in TITLE_TEMPLATES["dark"]

    def test_deterministic_same_ids(self, engine):
        t1 = engine._pick_title("fantastical", ["a", "b", "c"])
        t2 = engine._pick_title("fantastical", ["a", "b", "c"])
        assert t1 == t2

    def test_unknown_mood_falls_back_to_fantastical(self, engine):
        title = engine._pick_title("nonexistent_mood", ["id1"])
        assert title in TITLE_TEMPLATES["fantastical"]

    def test_different_ids_may_pick_different_title(self, engine):
        titles = set()
        for i in range(20):
            ids = [f"item_{i}_{j}" for j in range(5)]
            titles.add(engine._pick_title("dark", ids))
        assert len(titles) >= 2


# _is_recent

class TestIsRecent:
    def test_recent_year_true(self, engine):
        assert engine._is_recent("2024-01-01") is True

    def test_year_2023_true(self, engine):
        assert engine._is_recent("2023") is True

    def test_old_year_false(self, engine):
        assert engine._is_recent("1985") is False

    def test_none_false(self, engine):
        assert engine._is_recent(None) is False

    def test_empty_string_false(self, engine):
        assert engine._is_recent("") is False

    def test_invalid_string_false(self, engine):
        assert engine._is_recent("not-a-date") is False

    def test_year_2022_false(self, engine):
        assert engine._is_recent("2022-06-15") is False


# _build_special_collections

class TestBuildSpecialCollections:
    def test_free_collection_from_internet_archive(self, engine, free_item):
        result = engine._build_special_collections([free_item])
        ids = [c["id"] for c in result]
        assert "special-free" in ids

    def test_free_collection_from_is_public_domain(self, engine):
        item = {"id": "old_book", "is_public_domain": True}
        result = engine._build_special_collections([item])
        ids = [c["id"] for c in result]
        assert "special-free" in ids

    def test_no_free_collection_if_no_free_items(self, engine, dark_item):
        result = engine._build_special_collections([dark_item])
        ids = [c["id"] for c in result]
        assert "special-free" not in ids

    def test_new_collection_from_recent_date(self, engine, new_item):
        result = engine._build_special_collections([new_item])
        ids = [c["id"] for c in result]
        assert "special-new" in ids

    def test_no_new_collection_if_no_recent_items(self, engine, dark_item):
        result = engine._build_special_collections([dark_item])
        ids = [c["id"] for c in result]
        assert "special-new" not in ids

    def test_free_collection_title(self, engine, free_item):
        result = engine._build_special_collections([free_item])
        free = next(c for c in result if c["id"] == "special-free")
        assert free["title"] == "Free to Read Right Now"

    def test_new_collection_title(self, engine, new_item):
        result = engine._build_special_collections([new_item])
        new = next(c for c in result if c["id"] == "special-new")
        assert new["title"] == "New This Week"

    def test_free_collection_item_ids(self, engine, free_item):
        result = engine._build_special_collections([free_item])
        free = next(c for c in result if c["id"] == "special-free")
        assert "ia_moby_dick" in free["items"]

    def test_empty_items(self, engine):
        result = engine._build_special_collections([])
        assert result == []


# get_collections

class TestGetCollections:
    def test_returns_list(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        assert isinstance(result, list)

    def test_each_collection_has_required_keys(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        for col in result:
            assert "id" in col
            assert "title" in col
            assert "mood" in col
            assert "items" in col
            assert "item_count" in col

    def test_item_count_matches_items_length(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        for col in result:
            assert col["item_count"] == len(col["items"])

    def test_all_input_ids_present_in_some_collection(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        all_ids = set()
        for col in result:
            if not col["id"].startswith("special-"):
                all_ids.update(col["items"])
        input_ids = {item["id"] for item in sample_items}
        assert input_ids == all_ids

    def test_mood_is_valid_mood_label(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        valid_moods = set(TITLE_TEMPLATES.keys())
        for col in result:
            assert col["mood"] in valid_moods

    def test_title_is_string(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        for col in result:
            assert isinstance(col["title"], str)
            assert len(col["title"]) > 0

    def test_collection_id_format(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        for col in result:
            assert isinstance(col["id"], str)

    def test_empty_items_returns_empty(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections([])
        assert result == []

    def test_includes_special_collections_when_applicable(
        self, engine, sample_items, free_item, new_item
    ):
        all_items = sample_items + [free_item, new_item]
        engine.fit(all_items)
        result = engine.get_collections(all_items)
        ids = [c["id"] for c in result]
        assert "special-free" in ids
        assert "special-new" in ids

    def test_no_special_collections_when_not_applicable(self, engine, sample_items):
        engine.fit(sample_items)
        result = engine.get_collections(sample_items)
        ids = [c["id"] for c in result]
        assert "special-free" not in ids
        assert "special-new" not in ids


# get_special_collections

class TestGetSpecialCollections:
    def test_does_not_require_fit(self, engine, free_item):
        result = engine.get_special_collections([free_item])
        assert isinstance(result, list)

    def test_returns_free_collection(self, engine, free_item):
        result = engine.get_special_collections([free_item])
        ids = [c["id"] for c in result]
        assert "special-free" in ids

    def test_returns_new_collection(self, engine, new_item):
        result = engine.get_special_collections([new_item])
        ids = [c["id"] for c in result]
        assert "special-new" in ids

    def test_empty_returns_empty(self, engine):
        result = engine.get_special_collections([])
        assert result == []