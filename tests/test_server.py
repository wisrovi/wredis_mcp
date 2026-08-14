import json
import os
import signal
from unittest import mock

import pytest

from wredis_mcp import server

# --- get_catalog ---


def test_get_catalog_returns_shared_singleton():
    server.get_catalog.cache_clear()
    c1 = server.get_catalog()
    c2 = server.get_catalog()
    assert c1 is c2
    server.get_catalog.cache_clear()


# --- blueprints tool ---


def test_blueprints_contains_all_15_structures():
    text = server.get_wredis_architect_blueprints()
    sections = [
        "=== 1. HASH",
        "=== 2. QUEUE",
        "=== 3. STREAM",
        "=== 4. PUB/SUB",
        "=== 5. SET",
        "=== 6. SORTED SET",
        "=== 7. BITMAP",
        "=== 8. HYPERLOGLOG",
        "=== 9. GEO",
        "=== 10. PIPELINE",
        "=== 11. TRANSACTION",
        "=== 12. CACHE DECORATORS",
        "=== 13. KEY/VALUE",
        "=== 14. HA SENTINEL",
        "=== 15. HA CLUSTER",
    ]
    for s in sections:
        assert s in text
    assert "WREDIS EXPERT BLUEPRINTS" in text
    assert "read/write/update" in text.lower()


# --- search tool ---


def test_search_wredis_pattern_returns_results():
    patterns = [
        {
            "origin": "Official",
            "name": "hash_session_store",
            "manager": "RedisHashManager",
            "module": "wredis.hash",
            "description": "sessions with TTL",
        },
        {
            "origin": "Community",
            "name": "geo_search",
            "manager": "RedisGeoManager",
            "module": "wredis.geo",
            "description": "nearby search",
        },
    ]
    catalog_mock = mock.MagicMock()
    catalog_mock.search.return_value = patterns
    with mock.patch.object(server, "get_catalog", return_value=catalog_mock):
        text = server.search_wredis_pattern("hash")
    assert "hash_session_store" in text
    assert "RedisHashManager" in text
    assert "wredis.hash" in text
    assert "sessions with TTL" in text
    assert "Official" in text
    assert "Community" in text


def test_search_wredis_pattern_no_results():
    catalog_mock = mock.MagicMock()
    catalog_mock.search.return_value = []
    with mock.patch.object(server, "get_catalog", return_value=catalog_mock):
        text = server.search_wredis_pattern("zzz_nope")
    assert "No pattern matching 'zzz_nope' was found" in text
    assert "native WRedis pattern" in text


# --- deploy scaffolding tool ---


def test_deploy_wredis_scaffolding_relative_path_rejected():
    text = server.deploy_wredis_scaffolding("relative/path")
    assert text.startswith("Error:")
    assert "absolute path" in text


def test_deploy_wredis_scaffolding_creates_project(tmp_path):
    target = str(tmp_path / "deployed")
    result = server.deploy_wredis_scaffolding(target, project_name="MyApp", scaffold_type="cache_service")

    assert result.startswith("Success:")
    assert "MyApp" in result
    assert (tmp_path / "deployed" / "main.py").exists()
    assert (tmp_path / "deployed" / "config" / "settings.py").exists()
    assert (tmp_path / "deployed" / "repositories" / "hash_store.py").exists()
    assert (tmp_path / "deployed" / "cache" / "service.py").exists()
    assert (tmp_path / "deployed" / "wredis.config.json").exists()


def test_deploy_wredis_scaffolding_exception_returns_error(tmp_path):
    target = str(tmp_path / "blocked")
    with mock.patch.object(server.TemplateGenerator, "get_folders", side_effect=OSError("disk full")):
        text = server.deploy_wredis_scaffolding(target)
    assert text == "Error: disk full"


def test_deploy_wredis_scaffolding_relative_path_after_abs():
    # relative target_dir returns error even when scaffold_type unsupported
    text = server.deploy_wredis_scaffolding("x", scaffold_type="bogus")
    assert text.startswith("Error:")
    assert "absolute path" in text


# --- validate_redis_connection tool ---


def test_validate_redis_connection_success(tmp_path, monkeypatch):
    with mock.patch("wredis_mcp.server.BaseManager") as mock_base:
        mock_instance = mock.Mock()
        mock_instance.health_check.return_value = True
        mock_instance._execute.side_effect = lambda *args: (
            {"redis_version": "7.0.0", "redis_mode": "standalone"} if args[0] == "info" else "PONG"
        )
        mock_base.return_value = mock_instance

        result = server.validate_redis_connection(host="localhost", port=6379)

    assert "Redis Connection Valid" in result
    assert "localhost:6379" in result
    assert "7.0.0" in result
    assert "standalone" in result
    assert "PONG" in result


def test_validate_redis_connection_failure():
    with mock.patch("wredis_mcp.server.BaseManager", side_effect=ConnectionError("refused")):
        result = server.validate_redis_connection(host="badhost", port=9999)

    assert "Connection Failed" in result
    assert "ConnectionError" in result


# --- generate_from_pattern tool ---


def test_generate_from_pattern_success(tmp_path):
    target = str(tmp_path / "generated")
    with mock.patch.object(server, "get_catalog") as mock_get_catalog:
        mock_catalog = mock.Mock()
        mock_catalog.search.return_value = [
            {
                "name": "hash_session_store",
                "manager": "RedisHashManager",
                "module": "wredis.hash",
                "description": "Session storage",
            }
        ]
        mock_get_catalog.return_value = mock_catalog

        result = server.generate_from_pattern("hash_session_store", target, "TestApp")

    assert result.startswith("Success:")
    assert "TestApp" in result
    assert "hash_session_store" in result
    assert (tmp_path / "generated" / "main.py").exists()
    assert (tmp_path / "generated" / "examples" / "hash_session_store.py").exists()


def test_generate_from_pattern_not_found(tmp_path):
    target = str(tmp_path / "generated")
    with mock.patch.object(server, "get_catalog") as mock_get_catalog:
        mock_catalog = mock.Mock()
        mock_catalog.search.return_value = []
        mock_get_catalog.return_value = mock_catalog

        result = server.generate_from_pattern("nonexistent", target)

    assert result.startswith("Error:")
    assert "not found" in result


def test_generate_from_pattern_relative_path():
    result = server.generate_from_pattern("hash", "relative/path")
    assert result.startswith("Error:")
    assert "absolute path" in result


# --- manual tool ---


def test_manual_contains_guides():
    text = server.get_wredis_architect_manual()
    assert "WREDIS ARCHITECT MANUAL" in text
    assert "PROJECT STRUCTURE RULES" in text
    assert "CORE RULES" in text
    assert "DATA STRUCTURE SELECTION GUIDE" in text
    assert "MODULE MAP" in text
    assert "REFACTORING A MONOLITH TO WREDIS" in text
    assert "mermaid" in text
    assert "Generated by WRedis MCP by wisrovi" in text


# --- CLI run modes ---


def test_run_stdio_uses_stdio_transport():
    with mock.patch.object(server.mcp, "run") as mock_run:
        server.run_stdio()
    mock_run.assert_called_once_with(transport="stdio")


def test_run_sse_uses_sse_transport():
    with mock.patch.object(server.mcp, "run") as mock_run:
        server.run_sse()
    mock_run.assert_called_once_with(transport="sse")


# --- background management ---


def test_start_background_when_already_running(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "PID_FILE", str(tmp_path / "pid"))
    (tmp_path / "pid").write_text("9999")
    with mock.patch("subprocess.Popen") as mock_popen:
        server.start_background()
    mock_popen.assert_not_called()


def test_start_background_launches_process(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "PID_FILE", str(tmp_path / "pid"))
    proc_mock = mock.MagicMock()
    proc_mock.__enter__ = mock.Mock(return_value=proc_mock)
    proc_mock.__exit__ = mock.Mock(return_value=False)
    proc_mock.pid = 4242
    with mock.patch("subprocess.Popen", return_value=proc_mock) as mock_popen:
        server.start_background()
    mock_popen.assert_called_once()
    assert (tmp_path / "pid").read_text() == "4242"


def test_stop_background_when_not_running(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "PID_FILE", str(tmp_path / "nope"))
    with mock.patch("os.kill") as mock_kill:
        server.stop_background()
    mock_kill.assert_not_called()


def test_stop_background_kills_process(tmp_path, monkeypatch):
    pid_file = tmp_path / "pid"
    pid_file.write_text("7777")
    monkeypatch.setattr(server, "PID_FILE", str(pid_file))
    with mock.patch("os.kill") as mock_kill:
        server.stop_background()
    mock_kill.assert_called_once_with(7777, signal.SIGTERM)
    assert not pid_file.exists()


def test_stop_background_process_not_found(tmp_path, monkeypatch):
    pid_file = tmp_path / "pid"
    pid_file.write_text("7777")
    monkeypatch.setattr(server, "PID_FILE", str(pid_file))
    with mock.patch("os.kill", side_effect=ProcessLookupError):
        server.stop_background()
    assert not pid_file.exists()


# --- print_config ---


def _parse_first_json(text: str) -> dict:
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text, idx=text.index("{"))
    return obj


def test_print_config_to_stdout(capsys):
    server.print_config(write_file=False)
    captured = capsys.readouterr()
    data = _parse_first_json(captured.out)
    assert "wredis-mcp" in data["mcpServers"]
    assert data["mcpServers"]["wredis-mcp"]["args"] == [
        "-m",
        "wredis_mcp.server",
        "run",
    ]
    assert "QUICK INSTALL COMMANDS" in captured.out
    assert "gemini mcp add wredis-mcp" in captured.out


def test_print_config_saves_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    server.print_config(write_file=True)
    config_path = tmp_path / ".agents" / "wredis-mcp.json"
    assert config_path.exists()
    data = json.loads(config_path.read_text())
    assert "wredis-mcp" in data["mcpServers"]
    captured = capsys.readouterr()
    assert "Configuration saved to" in captured.out


# --- main CLI entrypoint ---


def test_main_config_saves_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "config"])
    server.main()
    assert (tmp_path / ".agents" / "wredis-mcp.json").exists()


def test_main_config_print_flag(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "config", "--print"])
    server.main()
    captured = capsys.readouterr()
    _parse_first_json(captured.out)  # valid JSON printed to stdout
    assert not (tmp_path / ".agents" / "wredis-mcp.json").exists()


def test_main_run_uses_stdio(monkeypatch):
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "run"])
    with mock.patch.object(server.mcp, "run") as mock_run:
        server.main()
    mock_run.assert_called_once_with(transport="stdio")


def test_main_run_sse(monkeypatch):
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "run-sse"])
    with mock.patch.object(server.mcp, "run") as mock_run:
        server.main()
    mock_run.assert_called_once_with(transport="sse")


def test_main_start(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "PID_FILE", str(tmp_path / "pid"))
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "start"])
    proc_mock = mock.MagicMock()
    proc_mock.__enter__ = mock.Mock(return_value=proc_mock)
    proc_mock.__exit__ = mock.Mock(return_value=False)
    proc_mock.pid = 555
    with mock.patch("subprocess.Popen", return_value=proc_mock):
        server.main()
    assert (tmp_path / "pid").read_text() == "555"


def test_main_stop(monkeypatch, tmp_path):
    pid_file = tmp_path / "pid"
    pid_file.write_text("555")
    monkeypatch.setattr(server, "PID_FILE", str(pid_file))
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "stop"])
    with mock.patch("os.kill"):
        server.main()
    assert not pid_file.exists()


def test_main_help(monkeypatch, capsys):
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp", "help"])
    with mock.patch("argparse.ArgumentParser.print_help") as mock_help:
        server.main()
    mock_help.assert_called_once()


def test_main_default_command_runs_stdio(monkeypatch):
    monkeypatch.setattr(server.sys, "argv", ["wredis-mcp"])
    with mock.patch.object(server.mcp, "run") as mock_run:
        server.main()
    mock_run.assert_called_once_with(transport="stdio")
