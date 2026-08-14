## wredis-mcp WHEN TO USE

Use wredis-mcp when you need:
- Redis caching layer for your application
- Async Redis operations with proper error handling
- Redis cluster management and health checks
- Rate limiting and session storage
- Pub/Sub messaging patterns
- FTS5 full-text search on Redis
- Lua script execution for atomic operations
- Connection pooling and retry logic

### Quick Start
```python
from wredis_mcp.server import validate_redis_connection, generate_from_pattern

# Validate Redis connection health
result = validate_redis_connection(
    host="localhost", port=6379, db=0, password=None
)

# Generate project from pattern
project = generate_from_pattern(
    pattern_name="cache_service", target_dir="/path/to/project"
)
```
