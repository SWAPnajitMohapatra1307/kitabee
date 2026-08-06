"""Tests for the Internet Archive API client."""

import pytest
import respx
import httpx

from src.external.internet_archive import InternetArchiveClient


# Fixtures

@pytest.fixture
def client():
    return InternetArchiveClient()


def _search_payload(docs: list) -> dict:
    return {
        "responseHeader": {"status": 0, "QTime": 10},
        "response": {
            "numFound": len(docs),
            "start": 0,
            "docs": docs,
        },
    }


def _fake_doc(identifier: str = "moby_dick") -> dict:
    return {
        "identifier": identifier,
        "title": "Moby Dick",
        "creator": "Herman Melville",
        "description": "A story about a whale.",
        "subject": ["fiction", "adventure", "public domain"],
        "date": "1851-01-01",
        "language": "English",
        "mediatype": "texts",
        "licenseurl": "",
    }


def _fake_metadata(identifier: str = "moby_dick") -> dict:
    return {
        "metadata": {
            "identifier": identifier,
            "title": "Moby Dick",
            "creator": "Herman Melville",
            "description": "A story about a whale.",
            "subject": ["fiction", "adventure", "public domain"],
            "date": "1851-01-01",
            "language": "English",
            "mediatype": "texts",
            "licenseurl": "",
        },
        "files": [
            {"name": "mobydick.epub", "format": "EPUB", "size": "204800"},
            {"name": "mobydick.pdf", "format": "Text PDF", "size": "1048576"},
        ],
    }


# search_free_books tests

@pytest.mark.asyncio
@respx.mock
async def test_search_returns_mapped_results(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_doc()]))
    )
    results = await client.search_free_books("moby dick")
    assert len(results) == 1
    assert results[0]["id"] == "ia_moby_dick"
    assert results[0]["source"] == "internet_archive"


@pytest.mark.asyncio
@respx.mock
async def test_search_returns_empty_on_no_docs(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(200, json=_search_payload([]))
    )
    results = await client.search_free_books("xyzzy_nonexistent")
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_search_maps_thumbnail_url(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_doc()]))
    )
    results = await client.search_free_books("moby dick")
    assert results[0]["thumbnail_url"] == "https://archive.org/services/img/moby_dick"


@pytest.mark.asyncio
@respx.mock
async def test_search_maps_authors_string_to_list(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_doc()]))
    )
    results = await client.search_free_books("moby dick")
    assert results[0]["authors"] == ["Herman Melville"]


@pytest.mark.asyncio
@respx.mock
async def test_search_detects_public_domain_via_subject(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(200, json=_search_payload([_fake_doc()]))
    )
    results = await client.search_free_books("moby dick")
    assert results[0]["is_public_domain"] is True


@pytest.mark.asyncio
@respx.mock
async def test_search_500_raises(client):
    respx.get("https://archive.org/advancedsearch.php").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(Exception):
        await client.search_free_books("moby dick")


# get_item tests

@pytest.mark.asyncio
@respx.mock
async def test_get_item_returns_mapped_metadata(client):
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=_fake_metadata())
    )
    result = await client.get_item("moby_dick")
    assert result is not None
    assert result["id"] == "ia_moby_dick"
    assert result["title"] == "Moby Dick"


@pytest.mark.asyncio
@respx.mock
async def test_get_item_returns_none_on_500(client):
    respx.get("https://archive.org/metadata/bad_item").mock(
        return_value=httpx.Response(500)
    )
    result = await client.get_item("bad_item")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_get_item_maps_thumbnail_url(client):
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=_fake_metadata())
    )
    result = await client.get_item("moby_dick")
    assert result["thumbnail_url"] == "https://archive.org/services/img/moby_dick"


@pytest.mark.asyncio
@respx.mock
async def test_get_item_maps_authors_as_list(client):
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=_fake_metadata())
    )
    result = await client.get_item("moby_dick")
    assert result["authors"] == ["Herman Melville"]


@pytest.mark.asyncio
@respx.mock
async def test_get_item_authors_list_input(client):
    data = _fake_metadata()
    data["metadata"]["creator"] = ["Herman Melville", "Co Author"]
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=data)
    )
    result = await client.get_item("moby_dick")
    assert result["authors"] == ["Herman Melville", "Co Author"]


# get_read_url tests

@pytest.mark.asyncio
@respx.mock
async def test_get_read_url_prefers_epub(client):
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=_fake_metadata())
    )
    url = await client.get_read_url("moby_dick")
    assert url == "https://archive.org/download/moby_dick/mobydick.epub"


@pytest.mark.asyncio
@respx.mock
async def test_get_read_url_falls_back_to_pdf(client):
    data = _fake_metadata()
    data["files"] = [{"name": "mobydick.pdf", "format": "Text PDF", "size": "1048576"}]
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=data)
    )
    url = await client.get_read_url("moby_dick")
    assert url == "https://archive.org/download/moby_dick/mobydick.pdf"


@pytest.mark.asyncio
@respx.mock
async def test_get_read_url_returns_none_when_no_readable_file(client):
    data = _fake_metadata()
    data["files"] = [{"name": "cover.jpg", "format": "JPEG", "size": "10000"}]
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=data)
    )
    url = await client.get_read_url("moby_dick")
    assert url is None


@pytest.mark.asyncio
@respx.mock
async def test_get_read_url_returns_none_on_500(client):
    respx.get("https://archive.org/metadata/bad_item").mock(
        return_value=httpx.Response(500)
    )
    url = await client.get_read_url("bad_item")
    assert url is None


@pytest.mark.asyncio
@respx.mock
async def test_get_read_url_cbz_for_comics(client):
    data = _fake_metadata()
    data["files"] = [{"name": "batman.cbz", "format": "CBZ", "size": "5000000"}]
    respx.get("https://archive.org/metadata/moby_dick").mock(
        return_value=httpx.Response(200, json=data)
    )
    url = await client.get_read_url("moby_dick")
    assert url == "https://archive.org/download/moby_dick/batman.cbz"


# is_public_domain tests

def test_public_domain_via_subject(client):
    metadata = {"subject": ["fiction", "public domain"], "licenseurl": ""}
    assert client._is_public_domain(metadata) is True


def test_public_domain_via_license_url(client):
    metadata = {
        "subject": [],
        "licenseurl": "https://creativecommons.org/publicdomain/zero/1.0/",
    }
    assert client._is_public_domain(metadata) is True


def test_public_domain_via_old_date(client):
    metadata = {"subject": [], "licenseurl": "", "date": "1851-01-01"}
    assert client._is_public_domain(metadata) is True


def test_not_public_domain_modern_book(client):
    metadata = {"subject": ["fiction"], "licenseurl": "", "date": "2020-01-01"}
    assert client._is_public_domain(metadata) is False


def test_public_domain_year_boundary_1927(client):
    metadata = {"subject": [], "licenseurl": "", "date": "1927-01-01"}
    assert client._is_public_domain(metadata) is True


def test_not_public_domain_year_boundary_1928(client):
    metadata = {"subject": [], "licenseurl": "", "date": "1928-01-01"}
    assert client._is_public_domain(metadata) is False


def test_public_domain_licenseurl_contains_publicdomain(client):
    metadata = {"subject": [], "licenseurl": "https://example.com/publicdomain"}
    assert client._is_public_domain(metadata) is True


# _normalize_authors tests

def test_normalize_authors_string(client):
    assert client._normalize_authors("Tolkien") == ["Tolkien"]


def test_normalize_authors_list(client):
    assert client._normalize_authors(["Tolkien", "Lewis"]) == ["Tolkien", "Lewis"]


def test_normalize_authors_none(client):
    assert client._normalize_authors(None) == []


def test_normalize_authors_filters_non_strings(client):
    assert client._normalize_authors(["Tolkien", 123, None]) == ["Tolkien"]


# _select_best_file tests

def test_select_best_file_epub_wins(client):
    files = [
        {"name": "book.pdf", "format": "Text PDF"},
        {"name": "book.epub", "format": "EPUB"},
    ]
    assert client._select_best_file(files) == "book.epub"


def test_select_best_file_pdf_when_no_epub(client):
    files = [{"name": "book.pdf", "format": "Text PDF"}]
    assert client._select_best_file(files) == "book.pdf"


def test_select_best_file_cbz_for_comics(client):
    files = [{"name": "comic.cbz", "format": "CBZ"}]
    assert client._select_best_file(files) == "comic.cbz"


def test_select_best_file_none_when_no_match(client):
    files = [{"name": "cover.jpg", "format": "JPEG"}]
    assert client._select_best_file(files) is None


def test_select_best_file_empty_list(client):
    assert client._select_best_file([]) is None