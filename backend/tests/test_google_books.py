"""Unit tests for the GoogleBooksClient.

Covers the six pure static helpers, the search and detail endpoints, and
retries on transient failures. External HTTP calls are mocked with respx;
none of these tests hit the network.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from src.external.google_books import (
    BASE_URL,
    GoogleBooksClient,
    TransientAPIError,
)


# ---------------------------------------------------------------------------
# Static helpers
# ---------------------------------------------------------------------------


class TestCleanText:
    """Tests for GoogleBooksClient._clean_text."""

    def test_returns_none_for_none(self) -> None:
        assert GoogleBooksClient._clean_text(None) is None

    def test_returns_none_for_empty_string(self) -> None:
        assert GoogleBooksClient._clean_text("") is None

    def test_returns_none_for_whitespace_only(self) -> None:
        assert GoogleBooksClient._clean_text("   \t\n  ") is None

    @pytest.mark.parametrize("value", [42, 4.5, [], {"a": 1}, True, False])
    def test_returns_none_for_non_string_types(self, value: Any) -> None:
        assert GoogleBooksClient._clean_text(value) is None

    def test_strips_surrounding_whitespace(self) -> None:
        assert GoogleBooksClient._clean_text("  hello  ") == "hello"

    def test_strips_html_tags(self) -> None:
        assert GoogleBooksClient._clean_text("<p>Hello <b>world</b></p>") == "Hello world"

    def test_unescapes_html_entities(self) -> None:
        # &amp; -> &, &#39; -> ', &lt; -> <
        assert GoogleBooksClient._clean_text("Tom &amp; Jerry") == "Tom & Jerry"
        assert GoogleBooksClient._clean_text("it&#39;s fine") == "it's fine"
        assert GoogleBooksClient._clean_text("1 &lt; 2") == "1 < 2"

    def test_collapses_multiple_whitespace(self) -> None:
        assert GoogleBooksClient._clean_text("a   b\t\tc\n\nd") == "a b c d"

    def test_html_and_entities_combined(self) -> None:
        raw = "  <p>Tom &amp; Jerry&#39;s   <i>show</i></p>  "
        assert GoogleBooksClient._clean_text(raw) == "Tom & Jerry's show"


class TestCleanDate:
    """Tests for GoogleBooksClient._clean_date."""

    def test_returns_none_for_none(self) -> None:
        assert GoogleBooksClient._clean_date(None) is None

    def test_returns_none_for_non_string(self) -> None:
        assert GoogleBooksClient._clean_date(2020) is None
        assert GoogleBooksClient._clean_date([2020]) is None

    def test_returns_none_for_garbage_string(self) -> None:
        assert GoogleBooksClient._clean_date("not a date") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert GoogleBooksClient._clean_date("") is None
        assert GoogleBooksClient._clean_date("   ") is None

    def test_year_only_normalized_to_jan_first(self) -> None:
        assert GoogleBooksClient._clean_date("2020") == "2020-01-01"

    def test_year_month_normalized_to_first(self) -> None:
        assert GoogleBooksClient._clean_date("2020-05") == "2020-05-01"

    def test_full_date_preserved(self) -> None:
        assert GoogleBooksClient._clean_date("2020-05-15") == "2020-05-15"

    @pytest.mark.parametrize("bad", ["2020/05", "May 2020", "abcd", "20-05-15"])
    def test_invalid_format_returns_none(self, bad: str) -> None:
        assert GoogleBooksClient._clean_date(bad) is None

    def test_year_month_with_invalid_month_still_pads_to_first(self) -> None:
        # Regex matches shape only; out-of-range months still normalize.
        assert GoogleBooksClient._clean_date("2020-13") == "2020-13-01"


class TestCleanInt:
    """Tests for GoogleBooksClient._clean_int."""

    def test_returns_none_for_none(self) -> None:
        assert GoogleBooksClient._clean_int(None) is None

    def test_returns_none_for_bool_true(self) -> None:
        # bool is a subclass of int; should still be rejected.
        assert GoogleBooksClient._clean_int(True) is None

    def test_returns_none_for_bool_false(self) -> None:
        assert GoogleBooksClient._clean_int(False) is None

    def test_returns_none_for_zero(self) -> None:
        assert GoogleBooksClient._clean_int(0) is None

    def test_returns_none_for_negative(self) -> None:
        assert GoogleBooksClient._clean_int(-5) is None

    def test_positive_int_returned(self) -> None:
        assert GoogleBooksClient._clean_int(42) == 42

    def test_valid_string_coerced(self) -> None:
        assert GoogleBooksClient._clean_int("42") == 42

    def test_invalid_string_returns_none(self) -> None:
        assert GoogleBooksClient._clean_int("abc") is None
        assert GoogleBooksClient._clean_int("") is None
        assert GoogleBooksClient._clean_int("  ") is None

    def test_float_coerced_when_positive(self) -> None:
        assert GoogleBooksClient._clean_int(4.7) == 4

    def test_float_zero_returns_none(self) -> None:
        assert GoogleBooksClient._clean_int(0.0) is None


class TestCleanFloat:
    """Tests for GoogleBooksClient._clean_float."""

    def test_returns_none_for_none(self) -> None:
        assert GoogleBooksClient._clean_float(None) is None

    def test_returns_none_for_bool(self) -> None:
        assert GoogleBooksClient._clean_float(True) is None
        assert GoogleBooksClient._clean_float(False) is None

    def test_returns_none_for_zero(self) -> None:
        assert GoogleBooksClient._clean_float(0) is None
        assert GoogleBooksClient._clean_float(0.0) is None

    def test_returns_none_for_negative(self) -> None:
        assert GoogleBooksClient._clean_float(-1.5) is None

    def test_int_coerced_to_float(self) -> None:
        assert GoogleBooksClient._clean_float(4) == 4.0

    def test_float_returned(self) -> None:
        assert GoogleBooksClient._clean_float(4.5) == 4.5

    def test_valid_string_coerced(self) -> None:
        assert GoogleBooksClient._clean_float("4.5") == 4.5

    def test_invalid_string_returns_none(self) -> None:
        assert GoogleBooksClient._clean_float("abc") is None


class TestCleanStrList:
    """Tests for GoogleBooksClient._clean_str_list."""

    def test_returns_empty_for_none(self) -> None:
        assert GoogleBooksClient._clean_str_list(None) == []

    def test_returns_empty_for_non_list(self) -> None:
        assert GoogleBooksClient._clean_str_list("not a list") == []
        assert GoogleBooksClient._clean_str_list({"a": 1}) == []
        assert GoogleBooksClient._clean_str_list(42) == []

    def test_filters_empty_strings(self) -> None:
        assert GoogleBooksClient._clean_str_list(["a", "", "b"]) == ["a", "b"]

    def test_filters_whitespace_only_strings(self) -> None:
        assert GoogleBooksClient._clean_str_list(["a", "   ", "\t\n", "b"]) == ["a", "b"]

    def test_strips_items(self) -> None:
        assert GoogleBooksClient._clean_str_list(["  a  ", " b"]) == ["a", "b"]

    def test_deduplicates_preserving_order(self) -> None:
        assert GoogleBooksClient._clean_str_list(
            ["Fiction", "Mystery", "Fiction", "Romance", "Mystery"]
        ) == ["Fiction", "Mystery", "Romance"]

    def test_filters_non_string_items(self) -> None:
        assert GoogleBooksClient._clean_str_list(
            ["a", 42, None, "b", [1, 2], {"k": "v"}, "c"]
        ) == ["a", "b", "c"]


class TestExtractIsbns:
    """Tests for GoogleBooksClient._extract_isbns."""

    def test_returns_none_none_for_none(self) -> None:
        assert GoogleBooksClient._extract_isbns(None) == (None, None)

    def test_returns_none_none_for_non_list(self) -> None:
        assert GoogleBooksClient._extract_isbns("not a list") == (None, None)
        assert GoogleBooksClient._extract_isbns({}) == (None, None)

    def test_returns_none_none_for_empty_list(self) -> None:
        assert GoogleBooksClient._extract_isbns([]) == (None, None)

    def test_extracts_isbn_10(self) -> None:
        ids = [{"type": "ISBN_10", "identifier": "0123456789"}]
        assert GoogleBooksClient._extract_isbns(ids) == ("0123456789", None)

    def test_extracts_isbn_13(self) -> None:
        ids = [{"type": "ISBN_13", "identifier": "9780123456786"}]
        assert GoogleBooksClient._extract_isbns(ids) == (None, "9780123456786")

    def test_extracts_both(self) -> None:
        ids = [
            {"type": "ISBN_10", "identifier": "0123456789"},
            {"type": "ISBN_13", "identifier": "9780123456786"},
        ]
        assert GoogleBooksClient._extract_isbns(ids) == ("0123456789", "9780123456786")

    def test_ignores_other_types(self) -> None:
        ids = [
            {"type": "OTHER", "identifier": "ignored"},
            {"type": "ISSN", "identifier": "ignored"},
        ]
        assert GoogleBooksClient._extract_isbns(ids) == (None, None)

    def test_first_valid_wins_for_duplicates(self) -> None:
        ids = [
            {"type": "ISBN_10", "identifier": "1111111111"},
            {"type": "ISBN_10", "identifier": "2222222222"},
        ]
        assert GoogleBooksClient._extract_isbns(ids)[0] == "1111111111"

    def test_strips_identifier_whitespace(self) -> None:
        ids = [{"type": "ISBN_13", "identifier": "  9780123456786  "}]
        assert GoogleBooksClient._extract_isbns(ids) == (None, "9780123456786")

    def test_skips_missing_identifier_field(self) -> None:
        ids = [{"type": "ISBN_10"}, {"type": "ISBN_13", "identifier": "9780123456786"}]
        assert GoogleBooksClient._extract_isbns(ids) == (None, "9780123456786")

    def test_skips_non_dict_items(self) -> None:
        ids = ["not a dict", 42, {"type": "ISBN_10", "identifier": "0123456789"}]
        assert GoogleBooksClient._extract_isbns(ids) == ("0123456789", None)


class TestMapVolume:
    """Tests for GoogleBooksClient._map_volume."""

    def test_maps_all_fields_from_full_response(self, sample_volume: dict[str, Any]) -> None:
        mapped = GoogleBooksClient._map_volume(sample_volume)

        assert mapped["google_books_id"] == "zyTCAlFPjgYC"
        assert mapped["title"] == "The Testing Book & More"
        assert mapped["subtitle"] == "A guide"
        assert mapped["authors"] == ["Jane Doe", "John Smith"]
        assert mapped["description"] == "Hello world Bold ."
        assert mapped["publisher"] == "Acme Press"
        assert mapped["published_date"] == "2020-05-15"
        assert mapped["page_count"] == 320
        assert mapped["categories"] == ["Fiction", "Mystery"]
        assert mapped["language"] == "en"
        assert mapped["isbn_10"] == "0123456789"
        assert mapped["isbn_13"] == "9780123456786"
        assert mapped["thumbnail_url"] == "https://books.google.com/thumb.jpg"
        assert mapped["small_thumbnail_url"] == "https://books/google/small.jpg"
        assert mapped["average_rating"] == 4.25
        assert mapped["ratings_count"] == 1234
        assert mapped["preview_link"] == "https://books.google.com/preview"
        assert mapped["info_link"] == "https://books.google.com/info"

    def test_handles_missing_volume_info(self) -> None:
        raw = {"id": "abc"}
        mapped = GoogleBooksClient._map_volume(raw)

        assert mapped["google_books_id"] == "abc"
        assert mapped["title"] is None
        assert mapped["subtitle"] is None
        assert mapped["authors"] == []
        assert mapped["description"] is None
        assert mapped["publisher"] is None
        assert mapped["published_date"] is None
        assert mapped["page_count"] is None
        assert mapped["categories"] == []
        assert mapped["language"] is None
        assert mapped["isbn_10"] is None
        assert mapped["isbn_13"] is None
        assert mapped["thumbnail_url"] is None
        assert mapped["small_thumbnail_url"] is None
        assert mapped["average_rating"] is None
        assert mapped["ratings_count"] is None
        assert mapped["preview_link"] is None
        assert mapped["info_link"] is None

    def test_handles_missing_image_links(self) -> None:
        raw = {"id": "x", "volumeInfo": {"title": "Hello"}}
        mapped = GoogleBooksClient._map_volume(raw)
        assert mapped["thumbnail_url"] is None
        assert mapped["small_thumbnail_url"] is None
        assert mapped["title"] == "Hello"

    def test_handles_missing_industry_identifiers(self) -> None:
        raw = {"id": "x", "volumeInfo": {"title": "Hello"}}
        mapped = GoogleBooksClient._map_volume(raw)
        assert mapped["isbn_10"] is None
        assert mapped["isbn_13"] is None

    def test_handles_completely_empty_raw(self) -> None:
        mapped = GoogleBooksClient._map_volume({})
        assert mapped["google_books_id"] is None
        assert mapped["title"] is None
        assert mapped["authors"] == []
        assert mapped["categories"] == []


# ---------------------------------------------------------------------------
# Network-backed methods (mocked with respx)
# ---------------------------------------------------------------------------


class TestSearch:
    """Tests for GoogleBooksClient.search."""

    async def test_returns_mapped_books_on_success(
        self, client: GoogleBooksClient, sample_volume: dict[str, Any]
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            mock.get("/volumes").mock(
                return_value=httpx.Response(200, json={"items": [sample_volume]})
            )
            results = await client.search("testing", max_results=5)

        assert len(results) == 1
        assert results[0]["google_books_id"] == "zyTCAlFPjgYC"
        assert results[0]["title"] == "The Testing Book & More"

    async def test_returns_empty_list_when_no_items_key(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            mock.get("/volumes").mock(return_value=httpx.Response(200, json={"totalItems": 0}))
            results = await client.search("noresults")

        assert results == []

    async def test_returns_empty_list_when_items_is_empty_array(
        self, client: GoogleBooksClient
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            mock.get("/volumes").mock(return_value=httpx.Response(200, json={"items": []}))
            results = await client.search("empty")

        assert results == []

    async def test_uses_query_and_max_results_params(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                return_value=httpx.Response(200, json={"items": []})
            )
            await client.search("sapiens", max_results=7)

        assert route.called
        request = route.calls.last.request
        assert request.url.params["q"] == "sapiens"
        assert request.url.params["maxResults"] == "7"

    async def test_api_key_included_in_params(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                return_value=httpx.Response(200, json={"items": []})
            )
            await client.search("anything")

        assert route.calls.last.request.url.params["key"] == client._api_key

    async def test_retries_on_500_then_succeeds(
        self,
        client: GoogleBooksClient,
        sample_volume: dict[str, Any],
        fast_retry: None,
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                side_effect=[
                    httpx.Response(500, json={"error": "boom"}),
                    httpx.Response(200, json={"items": [sample_volume]}),
                ]
            )
            results = await client.search("retry me")

        assert route.call_count == 2
        assert len(results) == 1
        assert results[0]["google_books_id"] == "zyTCAlFPjgYC"

    async def test_retries_on_429_then_succeeds(
        self,
        client: GoogleBooksClient,
        sample_volume: dict[str, Any],
        fast_retry: None,
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                side_effect=[
                    httpx.Response(429, json={"error": "rate limit"}),
                    httpx.Response(200, json={"items": [sample_volume]}),
                ]
            )
            results = await client.search("throttled")

        assert route.call_count == 2
        assert len(results) == 1

    async def test_raises_after_max_retries_on_persistent_500(
        self, client: GoogleBooksClient, fast_retry: None
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                return_value=httpx.Response(500, json={"error": "down"})
            )
            with pytest.raises(TransientAPIError):
                await client.search("flaky")

        assert route.call_count == 3

    async def test_raises_on_400_immediately_no_retry(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                return_value=httpx.Response(400, json={"error": "bad"})
            )
            with pytest.raises(httpx.HTTPStatusError):
                await client.search("bad")

        assert route.call_count == 1

    async def test_retries_on_timeout_exception(
        self,
        client: GoogleBooksClient,
        sample_volume: dict[str, Any],
        fast_retry: None,
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes").mock(
                side_effect=[
                    httpx.TimeoutException("timed out"),
                    httpx.Response(200, json={"items": [sample_volume]}),
                ]
            )
            results = await client.search("timeout test")

        assert route.call_count == 2
        assert len(results) == 1


class TestGetById:
    """Tests for GoogleBooksClient.get_by_id."""

    async def test_returns_mapped_book_on_success(
        self, client: GoogleBooksClient, sample_volume: dict[str, Any]
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            mock.get("/volumes/zyTCAlFPjgYC").mock(
                return_value=httpx.Response(200, json=sample_volume)
            )
            result = await client.get_by_id("zyTCAlFPjgYC")

        assert result is not None
        assert result["google_books_id"] == "zyTCAlFPjgYC"
        assert result["title"] == "The Testing Book & More"

    async def test_returns_none_on_404(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            mock.get("/volumes/missing").mock(
                return_value=httpx.Response(404, json={"error": "not found"})
            )
            result = await client.get_by_id("missing")

        assert result is None

    async def test_retries_on_500_then_succeeds(
        self,
        client: GoogleBooksClient,
        sample_volume: dict[str, Any],
        fast_retry: None,
    ) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes/zyTCAlFPjgYC").mock(
                side_effect=[
                    httpx.Response(500, json={"error": "boom"}),
                    httpx.Response(200, json=sample_volume),
                ]
            )
            result = await client.get_by_id("zyTCAlFPjgYC")

        assert route.call_count == 2
        assert result is not None
        assert result["google_books_id"] == "zyTCAlFPjgYC"

    async def test_raises_on_403_immediately(self, client: GoogleBooksClient) -> None:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.get("/volumes/forbidden").mock(
                return_value=httpx.Response(403, json={"error": "forbidden"})
            )
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_by_id("forbidden")

        assert route.call_count == 1


class TestCloseMethod:
    """Tests for GoogleBooksClient.close."""

    async def test_close_closes_underlying_client(self) -> None:
        instance = GoogleBooksClient()
        # Mark the httpx client as closed before close() to verify behaviour.
        await instance.close()
        assert instance._client.is_closed
