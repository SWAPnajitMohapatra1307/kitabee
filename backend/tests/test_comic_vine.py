"""Tests for the Comic Vine API client."""

import pytest
import respx
import httpx

from src.external.comic_vine import ComicVineClient, TransientAPIError


# Fixtures

@pytest.fixture
def client():
    return ComicVineClient()


def _search_payload(results: list) -> dict:
    return {
        "error": "OK",
        "status_code": 1,
        "number_of_total_results": len(results),
        "number_of_page_results": len(results),
        "results": results,
    }


def _issue_payload(result: dict) -> dict:
    return {
        "error": "OK",
        "status_code": 1,
        "results": result,
    }


def _fake_issue(issue_id: int = 123456) -> dict:
    return {
        "id": issue_id,
        "name": "The Killing Joke",
        "description": "<p>Batman faces the Joker.</p>",
        "image": {
            "medium_url": "https://example.com/cover.jpg",
            "original_url": "https://example.com/cover_orig.jpg",
        },
        "volume": {"id": 4050, "name": "Batman"},
        "issue_number": "1",
        "cover_date": "1988-01-01",
        "site_detail_url": "https://comicvine.gamespot.com/batman/issue/1/",
    }


def _fake_volume(volume_id: int = 4050) -> dict:
    return {
        "id": volume_id,
        "name": "Batman",
        "description": "<p>The ongoing Batman series.</p>",
        "image": {
            "medium_url": "https://example.com/batman.jpg",
            "original_url": "https://example.com/batman_orig.jpg",
        },
        "publisher": {"id": 10, "name": "DC Comics"},
        "count_of_issues": 713,
        "start_year": "1940",
        "site_detail_url": "https://comicvine.gamespot.com/batman/",
    }


# search_comics tests

@pytest.mark.asyncio
@respx.mock
async def test_search_comics_returns_mapped_results(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert len(results) == 1
    assert results[0]["id"] == "cv_123456"
    assert results[0]["source"] == "comic_vine"


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_strips_html_from_description(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert "<p>" not in results[0]["description"]
    assert "Batman faces the Joker." in results[0]["description"]


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_returns_empty_on_no_results(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([]))
    )
    results = await client.search_comics("xyzzy_nonexistent")
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_maps_series_name(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert results[0]["series"] == "Batman"


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_maps_issue_number(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert results[0]["issue_number"] == "1"


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_maps_published_date(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert results[0]["published_date"] == "1988-01-01"


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_maps_cover_image(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    results = await client.search_comics("batman")
    assert results[0]["cover_image"] == "https://example.com/cover.jpg"


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_cv_api_error_raises(client):
    error_payload = {"error": "Invalid API Key", "status_code": 100, "results": []}
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=error_payload)
    )
    with pytest.raises(TransientAPIError):
        await client.search_comics("batman")


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_500_raises(client):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(TransientAPIError):
        await client.search_comics("batman")


@pytest.mark.asyncio
@respx.mock
async def test_search_comics_uses_cache_on_second_call(client, monkeypatch):
    respx.get("https://comicvine.gamespot.com/api/search/").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_issue()]))
    )
    call_count = {"set": 0, "get": 0}
    get_returns = [None, [{"id": "cv_123456"}]]

    async def fake_get(key):
        call_count["get"] += 1
        return get_returns[call_count["get"] - 1]

    async def fake_set(key, value, ttl_seconds=None):
        call_count["set"] += 1

    monkeypatch.setattr("src.external.comic_vine.redis_client.get", fake_get)
    monkeypatch.setattr("src.external.comic_vine.redis_client.set", fake_set)

    await client.search_comics("batman")
    result = await client.search_comics("batman")
    assert result == [{"id": "cv_123456"}]
    assert call_count["set"] == 1
    assert call_count["get"] == 2


# get_comic tests

@pytest.mark.asyncio
@respx.mock
async def test_get_comic_returns_mapped_issue(client):
    respx.get("https://comicvine.gamespot.com/api/issue/4000-123456/").mock(
        return_value=httpx.Response(200, json=_issue_payload(_fake_issue()))
    )
    result = await client.get_comic("123456")
    assert result is not None
    assert result["id"] == "cv_123456"
    assert result["title"] == "The Killing Joke"


@pytest.mark.asyncio
@respx.mock
async def test_get_comic_returns_none_on_404(client):
    respx.get("https://comicvine.gamespot.com/api/issue/4000-999999/").mock(
        return_value=httpx.Response(404)
    )
    result = await client.get_comic("999999")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_comic_returns_none_on_500(client):
    respx.get("https://comicvine.gamespot.com/api/issue/4000-123456/").mock(
        return_value=httpx.Response(500)
    )
    result = await client.get_comic("123456")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_comic_strips_html_description(client):
    respx.get("https://comicvine.gamespot.com/api/issue/4000-123456/").mock(
        return_value=httpx.Response(200, json=_issue_payload(_fake_issue()))
    )
    result = await client.get_comic("123456")
    assert "<p>" not in result["description"]


@pytest.mark.asyncio
@respx.mock
async def test_get_comic_returns_none_when_results_not_dict(client):
    payload = {"error": "OK", "status_code": 1, "results": []}
    respx.get("https://comicvine.gamespot.com/api/issue/4000-123456/").mock(
        return_value=httpx.Response(200, json=payload)
    )
    result = await client.get_comic("123456")
    assert result is None


# get_volume tests

@pytest.mark.asyncio
@respx.mock
async def test_get_volume_returns_mapped_volume(client):
    respx.get("https://comicvine.gamespot.com/api/volume/4050-4050/").mock(
        return_value=httpx.Response(200, json=_issue_payload(_fake_volume()))
    )
    result = await client.get_volume("4050")
    assert result is not None
    assert result["id"] == "cv_4050"
    assert result["title"] == "Batman"
    assert result["publisher"] == "DC Comics"


@pytest.mark.asyncio
@respx.mock
async def test_get_volume_returns_none_on_404(client):
    respx.get("https://comicvine.gamespot.com/api/volume/4050-999999/").mock(
        return_value=httpx.Response(404)
    )
    result = await client.get_volume("999999")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_volume_returns_none_on_500(client):
    respx.get("https://comicvine.gamespot.com/api/volume/4050-4050/").mock(
        return_value=httpx.Response(500)
    )
    result = await client.get_volume("4050")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_volume_maps_issue_count(client):
    respx.get("https://comicvine.gamespot.com/api/volume/4050-4050/").mock(
        return_value=httpx.Response(200, json=_issue_payload(_fake_volume()))
    )
    result = await client.get_volume("4050")
    assert result["issue_count"] == 713


@pytest.mark.asyncio
@respx.mock
async def test_get_volume_strips_html_description(client):
    respx.get("https://comicvine.gamespot.com/api/volume/4050-4050/").mock(
        return_value=httpx.Response(200, json=_issue_payload(_fake_volume()))
    )
    result = await client.get_volume("4050")
    assert "<p>" not in result["description"]


# _map_issue edge cases

def test_map_issue_none_id_gives_none_content_id(client):
    raw = _fake_issue()
    raw["id"] = None
    result = client._map_issue(raw)
    assert result["id"] is None


def test_map_issue_missing_image_gives_none_cover(client):
    raw = _fake_issue()
    raw["image"] = {}
    result = client._map_issue(raw)
    assert result["cover_image"] is None


def test_map_issue_missing_volume_gives_none_series(client):
    raw = _fake_issue()
    raw["volume"] = {}
    result = client._map_issue(raw)
    assert result["series"] is None


def test_map_issue_missing_name_gives_none_title(client):
    raw = _fake_issue()
    raw["name"] = None
    result = client._map_issue(raw)
    assert result["title"] is None


# _map_volume edge cases

def test_map_volume_none_id_gives_none_content_id(client):
    raw = _fake_volume()
    raw["id"] = None
    result = client._map_volume(raw)
    assert result["id"] is None


def test_map_volume_missing_publisher_gives_none(client):
    raw = _fake_volume()
    raw["publisher"] = {}
    result = client._map_volume(raw)
    assert result["publisher"] is None


# _clean_date tests

def test_clean_date_full_iso(client):
    assert client._clean_date("1988-01-01") == "1988-01-01"


def test_clean_date_year_only(client):
    assert client._clean_date("1940") == "1940-01-01"


def test_clean_date_year_month(client):
    assert client._clean_date("1988-01") == "1988-01-01"


def test_clean_date_none_input(client):
    assert client._clean_date(None) is None


def test_clean_date_empty_string(client):
    assert client._clean_date("") is None


def test_clean_date_garbage(client):
    assert client._clean_date("not-a-date") is None


# _clean_text tests

def test_clean_text_strips_html(client):
    assert client._clean_text("<p>Hello <b>world</b></p>") == "Hello world"


def test_clean_text_unescapes_entities(client):
    assert client._clean_text("Batman &amp; Robin") == "Batman & Robin"


def test_clean_text_none_input(client):
    assert client._clean_text(None) is None


def test_clean_text_empty_string(client):
    assert client._clean_text("") is None


def test_clean_text_collapses_whitespace(client):
    assert client._clean_text("hello    world") == "hello world"