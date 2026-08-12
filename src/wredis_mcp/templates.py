"""Advanced scaffolding templates for professional WRedis development."""


class TemplateGenerator:
    """Provides professional boilerplate for WRedis projects following wisrovi standards."""

    @staticmethod
    def get_supported_types() -> list:
        """Return the list of supported scaffold types."""
        return ["standard", "cache_service", "full_service"]

    @staticmethod
    def get_folders(scaffold_type: str) -> list:
        """Return the folder layout for the requested scaffold type."""
        if scaffold_type == "cache_service":
            return ["config", "cache", "repositories", "tests", ".wredis"]
        if scaffold_type == "full_service":
            return ["config", "cache", "repositories", "tests", "examples", ".wredis", "scripts", ".github/workflows"]
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

        set_store_template = (
            "from wredis.sets import RedisSetManager\n"
            "from config.settings import RedisSettings\n\n\n"
            "class TagStore:\n"
            '    """Tag and membership store backed by Redis sets."""\n\n'
            "    def __init__(self, settings: RedisSettings):\n"
            "        self._manager = RedisSetManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def add_tags(self, key: str, *tags: str, ttl: int = 86400) -> None:\n"
            '        """Add tags to a set."""\n'
            "        self._manager.add_to_set(key, *tags, ttl=ttl)\n\n"
            "    def get_tags(self, key: str) -> set:\n"
            '        """Get all tags for a key."""\n'
            "        return self._manager.get_set_members(key)\n\n"
            "    def has_tag(self, key: str, tag: str) -> bool:\n"
            '        """Check if a tag exists."""\n'
            "        return self._manager.is_member(key, tag)\n\n"
            "    def remove_tag(self, key: str, tag: str) -> None:\n"
            '        """Remove a tag."""\n'
            "        self._manager.remove_from_set(key, tag)\n"
        )

        sortedset_store_template = (
            "from wredis.sortedset import RedisSortedSetManager\n"
            "from config.settings import RedisSettings\n\n\n"
            "class Leaderboard:\n"
            '    """Real-time leaderboard backed by Redis sorted sets."""\n\n'
            "    def __init__(self, settings: RedisSettings):\n"
            "        self._manager = RedisSortedSetManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def add_score(self, key: str, score: float, member: str) -> None:\n"
            '        """Add or update a member score."""\n'
            "        self._manager.add_to_sorted_set(key, score, member)\n\n"
            "    def increment_score(self, key: str, delta: float, member: str) -> None:\n"
            '        """Increment a member score."""\n'
            "        self._manager.increment_score(key, delta, member)\n\n"
            "    def get_top(self, key: str, count: int = 10, with_scores: bool = True) -> list:\n"
            '        """Get top members by score."""\n'
            "        return self._manager.get_sorted_set_reverse(key, with_scores=with_scores)[:count]\n\n"
            "    def get_rank(self, key: str, member: str) -> int | None:\n"
            '        """Get member rank (0-indexed).""" \n'
            "        return self._manager.get_rank(key, member)\n"
        )

        main_template = (
            "from config.settings import RedisSettings\n"
            "from repositories.hash_store import SessionStore\n"
            "from repositories.queue_store import TaskQueue\n"
            "from repositories.stream_store import EventStream\n"
            "from repositories.set_store import TagStore\n"
            "from repositories.sortedset_store import Leaderboard\n\n\n"
            "def run_service():\n"
            '    """Orchestrator: wires every WRedis repository together."""\n'
            "    settings = RedisSettings.from_env()\n\n"
            "    sessions = SessionStore(settings)\n"
            "    tasks = TaskQueue(settings)\n"
            "    events = EventStream(settings)\n"
            "    tags = TagStore(settings)\n"
            "    leaderboard = Leaderboard(settings)\n\n"
            '    sessions.save_session("user:42", {"name": "Alice", "plan": "pro"}, ttl=3600)\n'
            "    print(f\"Session: {sessions.get_session('user:42')}\")\n\n"
            '    tasks.publish({"id": 1, "action": "process_image"})\n'
            '    print(f"Pending tasks: {tasks.length()}")\n\n'
            '    events.emit({"type": "login", "user": "alice"})\n'
            '    print(f"Events: {events.read()}")\n\n'
            '    tags.add_tags("article:1", "python", "redis", "tutorial")\n'
            '    print(f"Tags: {tags.get_tags("article:1")}")\n\n'
            '    leaderboard.add_score("leaderboard", 100, "player1")\n'
            '    leaderboard.add_score("leaderboard", 200, "player2")\n'
            '    print(f"Top: {leaderboard.get_top("leaderboard")}")\n\n\n'
            'if __name__ == "__main__":\n'
            "    run_service()\n"
        )

        test_config_template = (
            "import pytest\n\n\n"
            '@pytest.fixture(scope="session")\n'
            "def redis_settings():\n"
            '    """Redis settings for testing."""\n'
            "    from config.settings import RedisSettings\n"
            '    return RedisSettings(host="localhost", port=6379, db=1)\n\n\n'
            '@pytest.fixture(scope="function")\n'
            "def clean_redis(redis_settings):\n"
            '    """Flush test DB before each test."""\n'
            "    from wredis.sync import BaseManager\n"
            "    m = BaseManager(\n"
            "        host=redis_settings.host,\n"
            "        port=redis_settings.port,\n"
            "        db=redis_settings.db,\n"
            "    )\n"
            '    m._execute("flushdb")\n'
            "    yield\n"
            '    m._execute("flushdb")\n'
        )

        test_hash_store_template = (
            "import pytest\n"
            "from repositories.hash_store import SessionStore\n\n\n"
            "class TestSessionStore:\n"
            '    """Tests for SessionStore repository."""\n\n'
            "    def test_save_and_get_session(self, clean_redis, redis_settings):\n"
            "        store = SessionStore(redis_settings)\n"
            '        store.save_session("user:1", {"name": "Alice", "plan": "pro"}, ttl=3600)\n'
            '        session = store.get_session("user:1")\n'
            "        assert session is not None\n"
            '        assert session["name"] == "Alice"\n'
            '        assert session["plan"] == "pro"\n\n'
            "    def test_get_nonexistent_session(self, clean_redis, redis_settings):\n"
            "        store = SessionStore(redis_settings)\n"
            '        session = store.get_session("user:999")\n'
            "        assert session is None\n\n"
            "    def test_delete_session(self, clean_redis, redis_settings):\n"
            "        store = SessionStore(redis_settings)\n"
            '        store.save_session("user:1", {"name": "Alice"})\n'
            '        store.delete_session("user:1")\n'
            '        assert store.get_session("user:1") is None\n\n'
            "    def test_all_sessions(self, clean_redis, redis_settings):\n"
            "        store = SessionStore(redis_settings)\n"
            '        store.save_session("user:1", {"name": "Alice"})\n'
            '        store.save_session("user:2", {"name": "Bob"})\n'
            "        all_sessions = store.all_sessions()\n"
            "        assert all_sessions is not None\n"
            "        assert len(all_sessions) == 2\n"
        )

        test_queue_store_template = (
            "import pytest\n"
            "from repositories.queue_store import TaskQueue\n\n\n"
            "class TestTaskQueue:\n"
            '    """Tests for TaskQueue repository."""\n\n'
            "    def test_publish_and_length(self, clean_redis, redis_settings):\n"
            "        queue = TaskQueue(redis_settings)\n"
            '        queue.publish({"id": 1, "action": "test"})\n'
            "        assert queue.length() == 1\n\n"
            "    def test_multiple_tasks(self, clean_redis, redis_settings):\n"
            "        queue = TaskQueue(redis_settings)\n"
            "        for i in range(5):\n"
            '            queue.publish({"id": i, "action": "task"})\n'
            "        assert queue.length() == 5\n"
        )

        dockerfile_template = (
            "# Dockerfile for WRedis service\n"
            "FROM python:3.12-slim\n\n"
            "WORKDIR /app\n\n"
            "# Install system dependencies\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
            "    gcc \\\n"
            "    && rm -rf /var/lib/apt/lists/*\n\n"
            "# Install Python dependencies\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n\n"
            "# Copy application code\n"
            "COPY . .\n\n"
            "# Run the service\n"
            'CMD ["python", "main.py"]\n'
        )

        dockerignore_template = (
            "__pycache__\n"
            "*.pyc\n"
            ".pytest_cache\n"
            ".coverage\n"
            "htmlcov\n"
            ".ruff_cache\n"
            ".mypy_cache\n"
            "tests/__pycache__\n"
            "*.db\n"
            "*.log\n"
            ".wredis\n"
            ".agents\n"
            ".git\n"
            ".github\n"
            "Dockerfile\n"
            "docker-compose.yml\n"
            "README.md\n"
        )

        github_ci_template = (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, master]\n"
            "  pull_request:\n"
            "    branches: [main, master]\n\n"
            "jobs:\n"
            "  lint:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n\n"
            "      - name: Set up Python\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n\n"
            "      - name: Install dependencies\n"
            "        run: |\n"
            "          python -m pip install --upgrade pip\n"
            "          pip install ruff\n\n"
            "      - name: Check ruff\n"
            "        run: ruff check src/ tests/ --output-format=github\n\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    strategy:\n"
            "      matrix:\n"
            "        python-version: ['3.10', '3.11', '3.12', '3.13']\n"
            "    services:\n"
            "      redis:\n"
            "        image: redis:7-alpine\n"
            "        ports:\n"
            "          - 6379:6379\n"
            "        options: >-\n"
            '          --health-cmd "redis-cli ping"\n'
            "          --health-interval 10s\n"
            "          --health-timeout 5s\n"
            "          --health-retries 5\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n\n"
            "      - name: Set up Python ${{ matrix.python-version }}\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: ${{ matrix.python-version }}\n\n"
            "      - name: Install dependencies\n"
            "        run: |\n"
            "          python -m pip install --upgrade pip\n"
            '          pip install -e ".[dev]"\n\n'
            "      - name: Run tests\n"
            "        run: pytest tests/ -v --tb=short\n\n"
            "  coverage:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n\n"
            "      - name: Set up Python\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n\n"
            "      - name: Install dependencies\n"
            "        run: |\n"
            "          python -m pip install --upgrade pip\n"
            '          pip install -e ".[dev]" pytest-cov\n\n'
            "      - name: Run tests with coverage\n"
            "        run: pytest tests/ --cov=src --cov-report=xml --cov-report=html\n\n"
            "      - name: Upload coverage\n"
            "        uses: actions/upload-artifact@v4\n"
            "        with:\n"
            "          name: coverage-report\n"
            "          path: htmlcov/\n"
        )

        readme_template = (
            f"# {project_name.upper()}\n\n"
            "Professional Redis-backed architecture built with **wredis**.\n\n"
            "## Architecture\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "    A[main.py] --> B[config/settings.py]\n"
            "    A --> C[repositories/hash_store.py]\n"
            "    A --> D[repositories/queue_store.py]\n"
            "    A --> E[repositories/stream_store.py]\n"
            "    A --> F[repositories/set_store.py]\n"
            "    A --> G[repositories/sortedset_store.py]\n"
            "    A --> H[cache/service.py]\n\n"
            "    C --> I[(Redis: Hash - Sessions)]\n"
            "    D --> J[(Redis: Queue - Tasks)]\n"
            "    E --> K[(Redis: Stream - Events)]\n"
            "    F --> L[(Redis: Set - Tags)]\n"
            "    G --> M[(Redis: SortedSet - Leaderboard)]\n"
            "    H --> N[(Redis: Cache - Decorators)]\n\n"
            "    style I fill:#ff6b6b,stroke:#333\n"
            "    style J fill:#4ecdc4,stroke:#333\n"
            "    style K fill:#ffe66d,stroke:#333\n"
            "    style L fill:#95e1d3,stroke:#333\n"
            "    style M fill:#dda0dd,stroke:#333\n"
            "    style N fill:#98d8c8,stroke:#333\n"
            "```\n\n"
            "## Project Structure\n\n"
            "```\n"
            f"{project_name}/\n"
            "├── config/\n"
            "│   ├── __init__.py\n"
            "│   └── settings.py          # RedisSettings from environment\n"
            "├── cache/\n"
            "│   ├── __init__.py\n"
            "│   └── service.py           # @cache / @async_cache decorators\n"
            "├── repositories/\n"
            "│   ├── __init__.py\n"
            "│   ├── hash_store.py        # SessionStore (Hash)\n"
            "│   ├── queue_store.py       # TaskQueue (Queue)\n"
            "│   ├── stream_store.py      # EventStream (Stream)\n"
            "│   ├── set_store.py         # TagStore (Set)\n"
            "│   └── sortedset_store.py   # Leaderboard (SortedSet)\n"
            "├── tests/\n"
            "│   ├── conftest.py          # Pytest fixtures\n"
            "│   ├── test_hash_store.py\n"
            "│   └── test_queue_store.py\n"
            "├── examples/\n"
            "├── scripts/\n"
            "├── .github/workflows/\n"
            "│   └── ci.yml               # GitHub Actions CI\n"
            "├── main.py                  # Service entrypoint\n"
            "├── requirements.txt\n"
            "├── Dockerfile\n"
            "├── .dockerignore\n"
            "├── wredis.config.json\n"
            "└── README.md\n"
            "```\n\n"
            "## Quick Start\n\n"
            "```bash\n"
            "# Install dependencies\n"
            "pip install -r requirements.txt\n\n"
            "# Run Redis (if not running)\n"
            "docker run -d -p 6379:6379 redis:7-alpine\n\n"
            "# Run the service\n"
            "python main.py\n"
            "```\n\n"
            "## Running Tests\n\n"
            "```bash\n"
            "# Run all tests\n"
            "pytest tests/ -v\n\n"
            "# Run with coverage\n"
            "pytest tests/ --cov=src --cov-report=html\n"
            "```\n\n"
            "## Docker\n\n"
            "```bash\n"
            "docker build -t {project_name} .\n"
            "docker run --network host {project_name}\n"
            "```\n\n"
            "---\n"
            "*Generated by WRedis MCP by **wisrovi***\n"
        )

        blueprints = {
            "requirements.txt": "wredis>=1.0.0\nredis>=5.0.0\npydantic>=2.0.0\n",
            "README.md": readme_template,
            "config/__init__.py": "from .settings import RedisSettings\n",
            "config/settings.py": settings_template,
            "cache/__init__.py": "from .service import expensive_operation, expensive_operation_async\n",
            "cache/service.py": cache_template,
            "repositories/__init__.py": (
                "from .hash_store import SessionStore\n"
                "from .queue_store import TaskQueue\n"
                "from .stream_store import EventStream\n"
                "from .set_store import TagStore\n"
                "from .sortedset_store import Leaderboard\n"
            ),
            "repositories/hash_store.py": hash_store_template,
            "repositories/queue_store.py": queue_store_template,
            "repositories/stream_store.py": stream_store_template,
            "repositories/set_store.py": set_store_template,
            "repositories/sortedset_store.py": sortedset_store_template,
            "main.py": main_template,
            "wredis.config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
            "tests/conftest.py": test_config_template,
            "tests/test_hash_store.py": test_hash_store_template,
            "tests/test_queue_store.py": test_queue_store_template,
            "Dockerfile": dockerfile_template,
            ".dockerignore": dockerignore_template,
            ".github/workflows/ci.yml": github_ci_template,
        }

        if scaffold_type == "cache_service":
            blueprints["requirements.txt"] += "loguru>=0.7.0\n"
        if scaffold_type == "full_service":
            blueprints["requirements.txt"] += "loguru>=0.7.0\npytest>=8.0.0\npytest-cov>=5.0.0\n"

        return blueprints
