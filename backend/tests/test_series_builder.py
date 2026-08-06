import pytest
from src.ml.series_builder import SeriesBuilder

# Fixtures

@pytest.fixture
def builder():
    return SeriesBuilder()


@pytest.fixture
def current_item():
    return {
        "content_id": "gb_2",
        "title": "Chamber of Secrets",
    }


@pytest.fixture
def detection():
    return {
        "series_name": "Harry Potter",
        "position": 2,
    }


@pytest.fixture
def series_items():
    return [
        {"content_id": "gb_1", "title": "Sorcerer's Stone", "position": 1},
        {"content_id": "gb_3", "title": "Prisoner of Azkaban", "position": 3},
        {"content_id": "gb_4", "title": "Goblet of Fire", "position": 4},
    ]


# Tests — Output Shape

class TestOutputShape:
    def test_returns_dict(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        assert isinstance(result, dict)

    def test_has_series_name(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        assert result["series_name"] == "Harry Potter"

    def test_has_total(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        assert result["total"] == 4

    def test_has_current_position(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        assert result["current_position"] == 2

    def test_has_items_list(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        assert isinstance(result["items"], list)

    def test_item_has_required_keys(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        for item in result["items"]:
            assert "content_id" in item
            assert "title" in item
            assert "position" in item
            assert "label" in item


# Tests — Labels

class TestLabels:
    def test_current_item_label(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        current = next(i for i in result["items"] if i["content_id"] == "gb_2")
        assert current["label"] == "You Are Here"

    def test_before_label(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        before = next(i for i in result["items"] if i["content_id"] == "gb_1")
        assert before["label"] == "Read This First"

    def test_next_label(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        next_item = next(i for i in result["items"] if i["content_id"] == "gb_3")
        assert next_item["label"] == "Read This Next"

    def test_coming_up_label(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        coming = next(i for i in result["items"] if i["content_id"] == "gb_4")
        assert coming["label"] == "Coming Up"

    def test_unknown_position_label(self, builder):
        current = {"content_id": "gb_a", "title": "Book A"}
        others = [{"content_id": "gb_b", "title": "Book B", "position": None}]
        detection = {"series_name": "Some Series", "position": None}
        result = builder.build(current, others, detection)
        for item in result["items"]:
            assert item["label"] in ("You Are Here", "Also In This Series")


# Tests — Ordering

class TestOrdering:
    def test_items_sorted_by_position(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        positions = [i["position"] for i in result["items"] if i["position"] is not None]
        assert positions == sorted(positions)

    def test_current_in_correct_position(self, builder, current_item, series_items, detection):
        result = builder.build(current_item, series_items, detection)
        positions = [i["position"] for i in result["items"]]
        current_index = next(
            idx for idx, i in enumerate(result["items"])
            if i["content_id"] == "gb_2"
        )
        assert current_index == 1


# Tests — Edge Cases

class TestEdgeCases:
    def test_only_current_item(self, builder, current_item, detection):
        result = builder.build(current_item, [], detection)
        assert result["total"] == 1
        assert result["items"][0]["label"] == "You Are Here"

    def test_deduplication(self, builder, current_item, detection):
        # Current item also appears in series_items — should not be duplicated
        duplicated = [
            {"content_id": "gb_2", "title": "Chamber of Secrets", "position": 2},
            {"content_id": "gb_1", "title": "Sorcerer's Stone", "position": 1},
        ]
        result = builder.build(current_item, duplicated, detection)
        ids = [i["content_id"] for i in result["items"]]
        assert len(ids) == len(set(ids))

    def test_unknown_series_name_fallback(self, builder, current_item):
        detection = {"series_name": None, "position": 1}
        result = builder.build(current_item, [], detection)
        assert result["series_name"] == "Unknown Series"

    def test_comic_items(self, builder):
        current = {"content_id": "cv_42", "title": "Batman #42"}
        others = [
            {"content_id": "cv_1", "title": "Batman #1", "position": 1},
            {"content_id": "cv_43", "title": "Batman #43", "position": 43},
        ]
        detection = {"series_name": "Batman", "position": 42}
        result = builder.build(current, others, detection)
        assert result["series_name"] == "Batman"
        labels = {i["content_id"]: i["label"] for i in result["items"]}
        assert labels["cv_42"] == "You Are Here"
        assert labels["cv_1"] == "Read This First"
        assert labels["cv_43"] == "Read This Next"

    def test_large_gap_is_coming_up(self, builder):
        current = {"content_id": "gb_1", "title": "Book 1"}
        others = [
            {"content_id": "gb_5", "title": "Book 5", "position": 5},
            {"content_id": "gb_10", "title": "Book 10", "position": 10},
        ]
        detection = {"series_name": "Some Series", "position": 1}
        result = builder.build(current, others, detection)
        labels = {i["content_id"]: i["label"] for i in result["items"]}
        assert labels["gb_5"] == "Coming Up"
        assert labels["gb_10"] == "Coming Up"