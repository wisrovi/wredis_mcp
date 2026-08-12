"""Advanced scaffolding templates for professional WRedis development."""


class TemplateGenerator:
    """Provides professional boilerplate for WRedis projects following wisrovi standards."""

    @staticmethod
    def get_supported_types() -> list:
        """Return the list of supported scaffold types."""
        return ["standard", "cache_service"]

    @staticmethod
    def get_folders(scaffold_type: str) -> list:
        """Return the folder layout for the requested scaffold type."""
        if scaffold_type == "cache_service":
            return ["config", "cache", "repositories", "tests", ".wredis"]
        return ["config", "cache", "repositories", "tests", ".wredis"]

    @staticmethod
    def get_files_blueprint(scaffold_type: str, project_name: str = "wredis_project") -> dict:
        """Return filenames and their professional template content."""
        settings_template = (
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class RedisSettings:\n"
            '    """Centralized connection settings for every WRedis manager."""\n'
            '    host: str = "localhost"\n'
            "    port: int = 6379\n"
            "    db: int = 0\n"
            "    password: str | None = None\n"
            "    verbose: bool = False\n\n"
            "    @classmethod\n"
            '    def from_env(cls) -> "RedisSettings":\n'
            '        """Build settings from environment variables with sane defaults."""\n'
            "        import os\n"
            "        return cls(\n"
            '            host=os.getenv("REDIS_HOST", "localhost"),\n'
            '            port=int(os.getenv("REDIS_PORT", "6379")),\n'
            '            db=int(os.getenv("REDIS_DB", "0")),\n'
            '            password=os.getenv("REDIS_PASSWORD"),\n'
            "        )\n"
        )

        cache_template = (  # noqa: UP032  (braces are literal in the template)
            "from wredis.decorators import cache, async_cache\n"
            "from wredis._exceptions import CacheError\n\n"
            "# Cache-Aside pattern: results are stored in Redis for TTL seconds.\n"
            '@cache(ttl=300, prefix="{name}")\n'
            "def expensive_operation(user_id: str) -> dict:\n"
            '    """Expensive computation cached for 5 minutes."""\n'
            '    return {{"user_id": user_id, "result": "computed"}}\n\n\n'
            '@async_cache(ttl=300, prefix="{name}")\n'
            "async def expensive_operation_async(user_id: str) -> dict:\n"
            '    """Async variant of the cached operation."""\n'
            '    return {{"user_id": user_id, "result": "computed_async"}}\n'
        ).format(name=project_name)

        hash_store_template = (
            "from wredis.hash import RedisHashManager\n"
            "from config.settings import RedisSettings\n\n\n"
            "class SessionStore:\n"
            '    """Typed session storage backed by a Redis hash."""\n\n'
            "    def __init__(self, settings: RedisSettings):\n"
            "        self._manager = RedisHashManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def save_session(self, session_id: str, data: dict, ttl: int = 3600) -> None:\n"
            '        """Persist a session with an optional TTL."""\n'
            '        self._manager.create_hash("sessions", session_id, data, ttl=ttl)\n\n'
            "    def get_session(self, session_id: str) -> dict | str | None:\n"
            '        """Retrieve a stored session."""\n'
            '        return self._manager.read_hash("sessions", session_id)\n\n'
            "    def all_sessions(self) -> dict | None:\n"
            '        """List every stored session."""\n'
            '        return self._manager.read_all_hash("sessions")\n\n'
            "    def delete_session(self, session_id: str) -> None:\n"
            '        """Remove a session field."""\n'
            '        self._manager.delete_hash_field("sessions", session_id)\n'
        )

        queue_store_template = (
            "from wredis.queue import RedisQueueManager\n"
            "from config.settings import RedisSettings\n\n\n"
            "class TaskQueue:\n"
            '    """Reliable background task queue backed by WRedis."""\n\n'
            "    def __init__(self, settings: RedisSettings, poll_interval: int = 1):\n"
            "        self._manager = RedisQueueManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            poll_interval=poll_interval,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def publish(self, task: dict, ttl: int = -1) -> None:\n"
            '        """Enqueue a task for the workers."""\n'
            '        self._manager.publish("tasks", task, ttl=ttl)\n\n'
            "    def length(self) -> int:\n"
            '        """Number of pending tasks."""\n'
            '        return self._manager.get_queue_length("tasks")\n\n'
            "    def worker(self, handler):\n"
            '        """Register a handler and return the manager to start() it."""\n'
            '        self._manager.on_message("tasks")(handler)\n'
            "        return self._manager\n"
        )

        stream_store_template = (
            "from wredis.streams import RedisStreamManager\n"
            "from config.settings import RedisSettings\n\n\n"
            "class EventStream:\n"
            '    """Event pipeline with consumer groups and replay support."""\n\n'
            "    def __init__(self, settings: RedisSettings):\n"
            "        self._manager = RedisStreamManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def emit(self, event: dict, ttl: int | None = None) -> str | None:\n"
            '        """Append an event to the stream."""\n'
            '        return self._manager.add_to_stream("events", event, ttl=ttl)\n\n'
            "    def consume(self, group_name: str, consumer_name: str, handler):\n"
            '        """Register a consumer-group handler."""\n'
            '        self._manager.on_message("events", group_name, consumer_name)(handler)\n'
            "        return self._manager\n\n"
            "    def read(self, count: int = 10) -> list:\n"
            '        """Read recent events without a registered consumer."""\n'
            '        return self._manager.read_from_stream("events", count=count)\n'
        )

        main_template = (
            "from config.settings import RedisSettings\n"
            "from repositories.hash_store import SessionStore\n"
            "from repositories.queue_store import TaskQueue\n"
            "from repositories.stream_store import EventStream\n\n\n"
            "def run_service():\n"
            '    """Orchestrator: wires every WRedis repository together."""\n'
            "    settings = RedisSettings.from_env()\n\n"
            "    sessions = SessionStore(settings)\n"
            "    tasks = TaskQueue(settings)\n"
            "    events = EventStream(settings)\n\n"
            '    sessions.save_session("user:42", {"name": "Alice", "plan": "pro"}, ttl=3600)\n'
            "    print(f\"Session: {sessions.get_session('user:42')}\")\n\n"
            '    tasks.publish({"id": 1, "action": "process_image"})\n'
            '    print(f"Pending tasks: {tasks.length()}")\n\n'
            '    events.emit({"type": "login", "user": "alice"})\n'
            '    print(f"Events: {events.read()}")\n\n\n'
            'if __name__ == "__main__":\n'
            "    run_service()\n"
        )

        blueprints = {
            "requirements.txt": "wredis>=1.0.0\nredis>=5.0.0\npydantic>=2.0.0\n",
            "README.md": (
                f"# {project_name.upper()}\n\n"
                "Professional Redis-backed architecture built with **wredis**.\n\n"
                "---\n*Generated by WRedis MCP by **wisrovi***\n"
            ),
            "config/__init__.py": "from .settings import RedisSettings\n",
            "config/settings.py": settings_template,
            "cache/__init__.py": "from .service import expensive_operation, expensive_operation_async\n",
            "cache/service.py": cache_template,
            "repositories/__init__.py": (
                "from .hash_store import SessionStore\n"
                "from .queue_store import TaskQueue\n"
                "from .stream_store import EventStream\n"
            ),
            "repositories/hash_store.py": hash_store_template,
            "repositories/queue_store.py": queue_store_template,
            "repositories/stream_store.py": stream_store_template,
            "main.py": main_template,
            "wredis.config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
        }

        if scaffold_type == "cache_service":
            blueprints["requirements.txt"] += "loguru>=0.7.0\n"

        return blueprints
