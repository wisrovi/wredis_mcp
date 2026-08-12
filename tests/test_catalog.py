import json
import logging
from unittest import mock
from urllib import request

import pytest

from wredis_mcp.catalog import PatternsCatalog


@pytest.fixture
def catalog():
    with mock.patch.object(PatternsCatalog, "refresh_catalog", return_value=[]):
        return PatternsCatalog()


def test_init_loads_initial_catalog():
    c = PatternsCatalog()
    assert len(c.cached_patterns) == 23
    assert c.cached_patterns[0]["manager"] == "RedisHashManager"


def test_fetch_url_success(catalog):
    payload = [{"name": "hash_session_store"}]
    with mock.patch("urllib.request.urlopen") as mock_urlopen:
        resp = mock.MagicMock()
        resp.status = 200
        resp.read.return_value = json.dumps(payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = resp

        result = catalog._fetch_url("https://example.com/catalog.json")
    assert result == payload


def test_fetch_url_non_200(catalog):
    with mock.patch("urllib.request.urlopen") as mock_urlopen:
        resp = mock.MagicMock()
        resp.status = 404
        mock_urlopen.return_value.__enter__.return_value = resp
        assert catalog._fetch_url("https://example.com/missing.json") == []


def test_fetch_url_exception(catalog, caplog):
    with mock.patch("urllib.request.urlopen", side_effect=request.URLError("boom")), caplog.at_level(logging.WARNING):
        assert catalog._fetch_url("https://example.com/bad.json") == []
    assert "Failed to fetch catalog" in caplog.text


def test_refresh_catalog_merges_sources(catalog):
    official = [{"name": "hash_session_store"}]
    community = [{"name": "community_pattern"}]
    with mock.patch.object(catalog, "_fetch_url", side_effect=[official, community]) as mock_fetch:
        result = catalog.refresh_catalog()
    assert mock_fetch.call_count == 2
    assert len(result) == 2
    assert result[0]["origin"] == "Official"
    assert result[1]["origin"] == "Community"


def test_refresh_catalog_keeps_cache_when_empty(catalog):
    catalog.cached_patterns = [{"name": "keep_me", "origin": "Official"}]
    with mock.patch.object(catalog, "_fetch_url", return_value=[]):
        result = catalog.refresh_catalog()
    assert result == [{"name": "keep_me", "origin": "Official"}]


def test_search_matches_multiple_fields(catalog):
    patterns = [
        {"name": "hash_session_store", "manager": "RedisHashManager", "description": "sessions"},
        {"name": "queue_worker", "manager": "RedisQueueManager", "description": "tasks"},
    ]
    catalog.cached_patterns = patterns
    assert len(catalog.search("hash")) == 1
    assert len(catalog.search("queue")) == 1
    assert catalog.search("manager") == patterns  # matches manager field on both


def test_search_case_insensitive(catalog):
    catalog.cached_patterns = [
        {
            "name": "GEO_NEARBY",
            "manager": "RedisGeoManager",
            "namespace": "wredis.geo",
            "module": "x",
            "description": "d",
            "category": "c",
        }
    ]
    assert len(catalog.search("geo")) == 1
    assert len(catalog.search("GEO")) == 1


def test_search_empty_query_returns_all(catalog):
    catalog.cached_patterns = [{"name": "a"}, {"name": "b"}]
    assert len(catalog.search("")) == 2


def test_search_skips_missing_fields(catalog):
    catalog.cached_patterns = [{"name": "only_name"}, {"manager": "only_manager"}]
    assert len(catalog.search("only")) == 2
    assert catalog.search("nothing_here") == []


def test_search_triggers_refresh_when_empty(catalog):
    catalog.cached_patterns = []
    with mock.patch.object(catalog, "refresh_catalog") as mock_refresh:
        mock_refresh.return_value = [{"name": "fresh", "origin": "Official"}]
        catalog.search("fresh")
    mock_refresh.assert_called_once()
