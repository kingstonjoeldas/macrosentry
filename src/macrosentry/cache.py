"""Caching layer for improved performance."""
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CacheEntry:
    """A single cache entry with TTL."""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl_seconds
        self.hits = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

    def get(self) -> Optional[Any]:
        """Get value if not expired."""
        if self.is_expired():
            return None
        self.hits += 1
        return self.value


class Cache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store a value in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = CacheEntry(value, ttl_seconds)
        logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None

        entry = self.cache[key]
        value = entry.get()

        if value is None:
            # Expired, remove from cache
            del self.cache[key]
            self.stats["misses"] += 1
            return None

        self.stats["hits"] += 1
        logger.debug(f"Cache HIT: {key}")
        return value

    def delete(self, key: str) -> bool:
        """Remove a value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            self.stats["hits"] / total_requests if total_requests > 0 else 0
        )

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 3),
            "evictions": self.stats["evictions"],
            "size": len(self.cache),
            "max_size": self.max_size
        }

    def _evict_oldest(self) -> None:
        """Evict oldest entry when cache is full."""
        if not self.cache:
            return

        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].created_at
        )
        del self.cache[oldest_key]
        self.stats["evictions"] += 1
        logger.debug(f"Cache eviction: {oldest_key}")


class QueryCache:
    """Cache for API/database queries."""

    def __init__(self):
        self._cache = Cache(max_size=500)

    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps(
            {"args": str(args), "kwargs": str(sorted(kwargs.items()))},
            sort_keys=True
        )
        return hashlib.md5(key_data.encode()).hexdigest()

    def cached(self, ttl_seconds: int = 300):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.get_cache_key(*args, **kwargs)
                cached_result = self._cache.get(cache_key)

                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

                result = func(*args, **kwargs)
                self._cache.set(cache_key, result, ttl_seconds)
                logger.debug(f"Cache miss for {func.__name__}, storing result")
                return result

            return wrapper
        return decorator

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        invalidated = 0
        keys_to_delete = [
            k for k in self._cache.cache.keys()
            if pattern in k
        ]
        for key in keys_to_delete:
            self._cache.delete(key)
            invalidated += 1

        logger.info(f"Invalidated {invalidated} cache entries matching '{pattern}'")
        return invalidated

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return self._cache.get_stats()


# Global cache instances
event_cache = Cache(max_size=1000)
query_cache = QueryCache()


def cache_dashboard_data(ttl_seconds: int = 60):
    """Cache decorator for dashboard data."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"dashboard_{func.__name__}"
            cached = query_cache._cache.get(cache_key)

            if cached:
                return cached

            result = func(*args, **kwargs)
            query_cache._cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator
