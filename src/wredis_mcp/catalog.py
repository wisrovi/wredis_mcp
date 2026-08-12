"""Pattern catalog synchronization with local fallbacks."""

import json
import logging
from contextlib import suppress
from urllib import request

# Use a module-level logger
logger = logging.getLogger(__name__)


class PatternsCatalog:
    """Manages the synchronization of available Redis patterns from the wisrovi SUITE.

    Synchronizes from GitHub just like the VS Code extension (with local fallbacks).
    """

    # URLs synchronized with the wisrovi ecosystem
    OFFICIAL_URL = "https://raw.githubusercontent.com/wisrovi/wredis/main/patterns_catalog.json"
    COMMUNITY_URL = "https://raw.githubusercontent.com/wisrovi/wredis-plugins/main/patterns_catalog.json"

    def __init__(self):
        """Initialize the catalog with hardcoded offline fallbacks."""
        self.cached_patterns = []
        self._load_initial_catalog()

    def _fetch_url(self, url: str) -> list:
        try:
            req = request.Request(url, headers={"User-Agent": "wredis-mcp"})
            with request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001  (any network error falls back to local catalog)
            logger.warning(f"Failed to fetch catalog from {url}: {e}")
        return []

    def refresh_catalog(self) -> list:
        """Fetch latest patterns from both official and community repositories."""
        official = self._fetch_url(self.OFFICIAL_URL)
        community = self._fetch_url(self.COMMUNITY_URL)

        # Merge and mark origin
        all_patterns = []
        for p in official:
            p["origin"] = "Official"
            all_patterns.append(p)
        for p in community:
            p["origin"] = "Community"
            all_patterns.append(p)

        if all_patterns:
            self.cached_patterns = all_patterns
            logger.info(f"Catalog refreshed: {len(self.cached_patterns)} patterns found.")

        return self.cached_patterns

    def search(self, query: str) -> list:
        """Filters cataloged patterns based on a search query keyword."""
        if not self.cached_patterns:
            self.refresh_catalog()

        query_lower = query.lower()
        results = []
        for pattern in self.cached_patterns:
            # Match against multiple fields
            fields = [
                pattern.get("name", ""),
                pattern.get("manager", ""),
                pattern.get("namespace", ""),
                pattern.get("module", ""),
                pattern.get("description", ""),
                pattern.get("category", ""),
            ]
            if any(query_lower in str(f).lower() for f in fields):
                results.append(pattern)
        return results

    def _load_initial_catalog(self):
        """Initial load with hardcoded fallbacks if offline."""
        self.cached_patterns = [
            {
                "name": "hash_session_store",
                "manager": "RedisHashManager",
                "namespace": "wredis.hash",
                "module": "wredis.hash",
                "description": "Store and retrieve typed session/profile records with TTL",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "queue_task_processing",
                "manager": "RedisQueueManager",
                "namespace": "wredis.queue",
                "module": "wredis.queue",
                "description": "Reliable producer/consumer task queue with compression and retries",
                "category": "Messaging",
                "origin": "Official",
            },
            {
                "name": "stream_consumer_groups",
                "manager": "RedisStreamManager",
                "namespace": "wredis.streams",
                "module": "wredis.streams",
                "description": "Event streaming with consumer groups, ACK and replay support",
                "category": "Messaging",
                "origin": "Official",
            },
            {
                "name": "pubsub_fanout",
                "manager": "RedisPubSubManager",
                "namespace": "wredis.pubsub",
                "module": "wredis.pubsub",
                "description": "Low-latency fire-and-forget broadcast across channels",
                "category": "Messaging",
                "origin": "Official",
            },
            {
                "name": "cache_aside_decorator",
                "manager": "@cache / @async_cache",
                "namespace": "wredis.decorators",
                "module": "wredis.decorators",
                "description": "Cache-Aside pattern with hit/miss metrics and TTL management",
                "category": "Caching",
                "origin": "Official",
            },
            {
                "name": "sorted_set_leaderboard",
                "manager": "RedisSortedSetManager",
                "namespace": "wredis.sortedset",
                "module": "wredis.sortedset",
                "description": "Rankings, score ranges and real-time leaderboards",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "set_membership",
                "manager": "RedisSetManager",
                "namespace": "wredis.sets",
                "module": "wredis.sets",
                "description": "Unique memberships, tags and membership checks",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "geo_nearby_search",
                "manager": "RedisGeoManager",
                "namespace": "wredis.geo",
                "module": "wredis.geo",
                "description": "Geolocation storage, distance queries and radius search",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "transaction_atomic_ops",
                "manager": "RedisTransactionManager",
                "namespace": "wredis.transaction",
                "module": "wredis.transaction",
                "description": "Atomic WATCH/MULTI/EXEC operations, SETNX locks and counters",
                "category": "Advanced",
                "origin": "Official",
            },
            {
                "name": "pipeline_batch_ops",
                "manager": "RedisPipelineManager",
                "namespace": "wredis.pipeline",
                "module": "wredis.pipeline",
                "description": "Batch execution of multiple commands with a single round-trip",
                "category": "Advanced",
                "origin": "Official",
            },
            {
                "name": "bitmap_analytics",
                "manager": "RedisBitmapManager",
                "namespace": "wredis.bitmap",
                "module": "wredis.bitmap",
                "description": "Compact bit-level tracking for daily active users and flags",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "hyperloglog_cardinality",
                "manager": "RedisHyperLogLogManager",
                "namespace": "wredis.hyperloglog",
                "module": "wredis.hyperloglog",
                "description": "Probabilistic unique counters with ~0.81% standard error",
                "category": "Data Structures",
                "origin": "Official",
            },
            {
                "name": "sentinel_high_availability",
                "manager": "SentinelRedisManager",
                "namespace": "wredis.ha.sentinel",
                "module": "wredis.ha.sentinel",
                "description": "Automatic failover via Redis Sentinel for master/slave setups",
                "category": "High Availability",
                "origin": "Official",
            },
            {
                "name": "cluster_high_availability",
                "manager": "ClusterRedisManager",
                "namespace": "wredis.ha.cluster",
                "module": "wredis.ha.cluster",
                "description": "Distributed Redis Cluster with automatic hash slot routing and failover",
                "category": "High Availability",
                "origin": "Official",
            },
        ]
        # Attempt an immediate refresh
        with suppress(Exception):
            self.refresh_catalog()
