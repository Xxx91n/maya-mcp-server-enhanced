"""Intelligent caching layer for scene data.

Provides TTL-based caching with dirty detection. When execute_code
or write_module modifies the scene, the cache is automatically invalidated.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any


logger = logging.getLogger(__name__)


class SceneCache:
    """Scene data intelligent cache with TTL and dirty detection.

    Usage:
        cache = SceneCache(ttl_seconds=5.0)

        # After any scene modification:
        cache.mark_dirty()

        # Get cached or fresh data:
        data = await cache.get_or_fetch("scene_graph", fetch_fn)
    """

    def __init__(self, ttl_seconds: float = 5.0) -> None:
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds
        self._dirty = True  # Must query on first access
        self._hit_count = 0
        self._miss_count = 0

    @property
    def is_dirty(self) -> bool:
        """Whether the cache needs refreshing."""
        return self._dirty

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0

    def mark_dirty(self) -> None:
        """Mark cache as needing refresh.

        Called automatically after execute_code/write_module.
        """
        self._dirty = True
        logger.debug("Scene cache marked dirty")

    def invalidate(self, key: str | None = None) -> None:
        """Invalidate specific or all cached entries.

        Args:
            key: Specific key to invalidate, or None for all.
        """
        if key is None:
            self._cache.clear()
            self._dirty = True
        elif key in self._cache:
            del self._cache[key]
            self._dirty = True

    async def get_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Get data from cache or fetch fresh data.

        Args:
            key: Cache key for this data.
            fetch_fn: Async function that returns fresh data.

        Returns:
            Cached or freshly fetched data.
        """
        now = time.monotonic()

        # Check cache hit
        if not self._dirty and key in self._cache:
            data, ts = self._cache[key]
            if now - ts < self._ttl:
                self._hit_count += 1
                logger.debug(f"Cache hit for '{key}'")
                return data

        # Cache miss - fetch fresh data
        self._miss_count += 1
        logger.debug(f"Cache miss for '{key}', fetching fresh data")
        data = await fetch_fn()
        self._cache[key] = (data, now)
        self._dirty = False
        return data

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": round(self.hit_rate, 3),
            "is_dirty": self._dirty,
            "ttl_seconds": self._ttl,
        }
