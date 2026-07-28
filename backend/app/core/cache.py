"""
Redis Cache Layer
Wraps redis-py with a simple get/set/delete interface.
Falls back gracefully if Redis is not available (development without Redis).
"""
import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    """Lazy Redis connection — returns None if Redis is unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1)
        client.ping()
        _redis_client = client
        logger.info("Redis connected at %s", settings.REDIS_URL)
        return client
    except Exception as e:
        logger.warning("Redis unavailable (%s) — cache disabled", e)
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache. Returns None on miss or error."""
    client = _get_redis()
    if not client:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.warning("Cache get error for key %s: %s", key, e)
        return None


def cache_set(key: str, value: Any, ttl: int = None) -> bool:
    """Set value in cache with optional TTL in seconds."""
    client = _get_redis()
    if not client:
        return False
    try:
        ttl = ttl or settings.CACHE_TTL
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning("Cache set error for key %s: %s", key, e)
        return False


def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    client = _get_redis()
    if not client:
        return False
    try:
        client.delete(key)
        return True
    except Exception as e:
        logger.warning("Cache delete error for key %s: %s", key, e)
        return False


def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern (e.g. 'dashboard:user:*')."""
    client = _get_redis()
    if not client:
        return
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
    except Exception as e:
        logger.warning("Cache delete pattern error: %s", e)


def make_cache_key(*parts) -> str:
    """Build a namespaced cache key: 'spending:part1:part2'."""
    return "spending:" + ":".join(str(p) for p in parts)
