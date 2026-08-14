import pytest

from wredis_mcp.templates import TemplateGenerator


def test_get_supported_types():
    assert TemplateGenerator.get_supported_types() == [
        "standard",
        "cache_service",
        "full_service",
    ]


def test_get_folders_standard():
    assert TemplateGenerator.get_folders("standard") == [
        "config",
        "cache",
        "repositories",
        "tests",
        ".wredis",
    ]


def test_get_folders_cache_service():
    assert TemplateGenerator.get_folders("cache_service") == [
        "config",
        "cache",
        "repositories",
        "tests",
        ".wredis",
    ]


def test_get_files_blueprint_standard_structure():
    bp = TemplateGenerator.get_files_blueprint("standard", "my_app")
    assert "main.py" in bp
    assert "config/settings.py" in bp
    assert "cache/service.py" in bp
    assert "repositories/hash_store.py" in bp
    assert "repositories/queue_store.py" in bp
    assert "repositories/stream_store.py" in bp
    assert "repositories/__init__.py" in bp
    assert "config/__init__.py" in bp
    assert "cache/__init__.py" in bp
    assert "requirements.txt" in bp
    assert "README.md" in bp
    assert "wredis.config.json" in bp


def test_get_files_blueprint_project_name_interpolated():
    bp = TemplateGenerator.get_files_blueprint("standard", "order_service")
    assert "ORDER_SERVICE" in bp["README.md"]
    assert 'prefix="order_service"' in bp["cache/service.py"]


def test_get_files_blueprint_cache_service_extra_dependency():
    bp_standard = TemplateGenerator.get_files_blueprint("standard", "app")
    bp_cache = TemplateGenerator.get_files_blueprint("cache_service", "app")
    assert "loguru>=0.7.0" not in bp_standard["requirements.txt"]
    assert "loguru>=0.7.0" in bp_cache["requirements.txt"]


def test_get_files_blueprint_content_pieces():
    bp = TemplateGenerator.get_files_blueprint("standard", "app")
    settings = bp["config/settings.py"]
    assert "class RedisSettings" in settings
    assert "from_env" in settings

    hash_store = bp["repositories/hash_store.py"]
    assert "class SessionStore" in hash_store
    assert "create_hash" in hash_store
    assert "delete_hash" in hash_store

    queue_store = bp["repositories/queue_store.py"]
    assert "class TaskQueue" in queue_store
    assert "get_queue_length" in queue_store
    assert "delete_queue" in queue_store

    stream_store = bp["repositories/stream_store.py"]
    assert "class EventStream" in stream_store
    assert "add_to_stream" in stream_store
    assert "delete_stream" in stream_store

    main = bp["main.py"]
    assert "run_service" in main
    assert "RedisSettings.from_env" in main

    service = bp["cache/service.py"]
    assert "@cache" in service
    assert "@async_cache" in service

    init = bp["repositories/__init__.py"]
    assert "SessionStore" in init
    assert "TaskQueue" in init
    assert "EventStream" in init
