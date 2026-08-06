import pytest
from src.ml.mood_detector import MoodDetector


# Fixtures

@pytest.fixture
def detector():
    return MoodDetector()


def _item(title="", description="", genres=None, categories=None, subjects=None):
    return {
        "title": title,
        "description": description,
        "genres": genres or [],
        "categories": categories or [],
        "subjects": subjects or [],
    }


# Constants

class TestConstants:
    def test_has_eight_moods(self, detector):
        assert len(detector.MOOD_KEYWORDS) == 8

    def test_mood_names(self, detector):
        expected = {
            "dark", "adventurous", "romantic", "funny",
            "mysterious", "inspiring", "educational", "fantastical",
        }
        assert set(detector.MOOD_KEYWORDS.keys()) == expected

    def test_each_mood_has_primary_and_secondary(self, detector):
        for mood, groups in detector.MOOD_KEYWORDS.items():
            assert "primary" in groups, f"{mood} missing primary"
            assert "secondary" in groups, f"{mood} missing secondary"

    def test_default_mood_is_fantastical(self, detector):
        assert detector.DEFAULT_MOOD == "fantastical"


# _build_text

class TestBuildText:
    def test_uses_title(self, detector):
        text = detector._build_text({"title": "Hello World"})
        assert "hello world" in text

    def test_uses_description(self, detector):
        text = detector._build_text({"description": "A great adventure"})
        assert "a great adventure" in text

    def test_uses_genres(self, detector):
        text = detector._build_text({"genres": ["Fantasy", "Action"]})
        assert "fantasy" in text
        assert "action" in text

    def test_uses_categories(self, detector):
        text = detector._build_text({"categories": ["Science Fiction"]})
        assert "science fiction" in text

    def test_uses_subjects(self, detector):
        text = detector._build_text({"subjects": ["mythology"]})
        assert "mythology" in text

    def test_lowercases_all(self, detector):
        text = detector._build_text({"title": "DARK GRIM HORROR"})
        assert "dark grim horror" in text

    def test_missing_fields_ignored(self, detector):
        text = detector._build_text({})
        assert text == ""

    def test_none_fields_ignored(self, detector):
        text = detector._build_text({"title": None, "description": None})
        assert text == ""

    def test_non_list_genre_ignored(self, detector):
        text = detector._build_text({"genres": "Fantasy"})
        assert text == ""

    def test_combines_all_fields(self, detector):
        text = detector._build_text({
            "title": "Dark",
            "description": "Grim tale",
            "genres": ["Horror"],
        })
        assert "dark" in text
        assert "grim tale" in text
        assert "horror" in text


# score_all

class TestScoreAll:
    def test_returns_all_eight_moods(self, detector):
        scores = detector.score_all(_item())
        assert set(scores.keys()) == set(detector.MOOD_KEYWORDS.keys())

    def test_primary_keyword_scores_two(self, detector):
        scores = detector.score_all(_item(title="horror"))
        assert scores["dark"] >= 2

    def test_secondary_keyword_scores_one(self, detector):
        scores = detector.score_all(_item(title="noir"))
        assert scores["dark"] >= 1

    def test_multiple_keywords_accumulate(self, detector):
        scores = detector.score_all(_item(title="dark grim horror"))
        assert scores["dark"] >= 6

    def test_empty_item_all_zeros(self, detector):
        scores = detector.score_all(_item())
        assert all(v == 0 for v in scores.values())

    def test_stem_match_works(self, detector):
        scores = detector.score_all(_item(description="mythology and mythological tales"))
        assert scores["fantastical"] >= 2

    def test_motivat_stem_matches_motivation(self, detector):
        scores = detector.score_all(_item(description="a story about motivation"))
        assert scores["inspiring"] >= 2

    def test_scores_are_integers(self, detector):
        scores = detector.score_all(_item(title="adventure"))
        assert all(isinstance(v, int) for v in scores.values())


# detect

class TestDetect:
    def test_dark_content(self, detector):
        item = _item(
            title="A dystopian horror story",
            description="Brutal and grim world after apocalypse",
            genres=["Horror", "Dark Fiction"],
        )
        assert detector.detect(item) == "dark"

    def test_adventurous_content(self, detector):
        item = _item(
            title="The Great Quest",
            description="An epic journey of exploration and battle",
            genres=["Adventure", "Action"],
        )
        assert detector.detect(item) == "adventurous"

    def test_romantic_content(self, detector):
        item = _item(
            title="A Love Story",
            description="Romance, passion, and heartbreak",
            genres=["Romance"],
        )
        assert detector.detect(item) == "romantic"

    def test_funny_content(self, detector):
        item = _item(
            title="The Comedy of Errors",
            description="A hilarious satire full of humor and wit",
            genres=["Comedy"],
        )
        assert detector.detect(item) == "funny"

    def test_mysterious_content(self, detector):
        item = _item(
            title="The Detective",
            description="A mystery thriller with suspense and conspiracy",
            genres=["Mystery", "Thriller"],
        )
        assert detector.detect(item) == "mysterious"

    def test_inspiring_content(self, detector):
        item = _item(
            title="A Memoir of Triumph",
            description="A biography of courage, resilience and hope",
            genres=["Biography", "Memoir"],
        )
        assert detector.detect(item) == "inspiring"

    def test_educational_content(self, detector):
        item = _item(
            title="The Science of Everything",
            description="A nonfiction exploration of philosophy and history",
            genres=["Science", "Nonfiction"],
        )
        assert detector.detect(item) == "educational"

    def test_fantastical_content(self, detector):
        item = _item(
            title="The Dragon Wizard",
            description="Magic and sorcerer in an otherworldly realm",
            genres=["Fantasy"],
        )
        assert detector.detect(item) == "fantastical"

    def test_empty_item_returns_default(self, detector):
        assert detector.detect(_item()) == "fantastical"

    def test_zero_score_returns_default(self, detector):
        item = _item(title="the a is of")
        assert detector.detect(item) == "fantastical"

    def test_genres_contribute_to_detection(self, detector):
        item = _item(genres=["Mystery", "Thriller", "Crime"])
        assert detector.detect(item) == "mysterious"

    def test_subjects_contribute_to_detection(self, detector):
        item = _item(subjects=["magic", "wizard", "dragon", "fantasy"])
        assert detector.detect(item) == "fantastical"

    def test_categories_contribute_to_detection(self, detector):
        item = _item(categories=["science", "history", "nonfiction"])
        assert detector.detect(item) == "educational"


# detect_batch

class TestDetectBatch:
    def test_returns_list_same_length(self, detector):
        items = [
            _item(title="dark horror"),
            _item(title="magic wizard fantasy"),
        ]
        result = detector.detect_batch(items)
        assert len(result) == 2

    def test_correct_moods_per_item(self, detector):
        items = [
            _item(title="horror dystopia dark grim"),
            _item(title="magic wizard dragon fantasy"),
        ]
        result = detector.detect_batch(items)
        assert result[0] == "dark"
        assert result[1] == "fantastical"

    def test_empty_list(self, detector):
        assert detector.detect_batch([]) == []

    def test_single_item(self, detector):
        result = detector.detect_batch([_item(title="adventure quest journey")])
        assert result == ["adventurous"]

    def test_all_empty_items_return_default(self, detector):
        items = [_item(), _item(), _item()]
        result = detector.detect_batch(items)
        assert all(m == "fantastical" for m in result)