"""
Redis caching utilities for the application.
Handles caching of user data, analytics, and other frequently accessed resources.
"""

import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager for application-wide caching."""
    
    _instance = None
    _redis_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance
    
    async def initialize(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection."""
        try:
            import aioredis
            self._redis_client = await aioredis.create_redis_pool(redis_url)
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}. Falling back to in-memory cache.")
            self._redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis_client:
            return None
        
        try:
            value = await self._redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (time to live in seconds)."""
        if not self._redis_client:
            return False
        
        try:
            await self._redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._redis_client:
            return False
        
        try:
            await self._redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        if not self._redis_client:
            return 0
        
        try:
            keys = await self._redis_client.keys(pattern)
            if keys:
                await self._redis_client.delete(*keys)
            return len(keys) if keys else 0
        except Exception as e:
            logger.warning(f"Cache clear pattern failed for pattern {pattern}: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection."""
        if self._redis_client:
            self._redis_client.close()
            await self._redis_client.wait_closed()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching async function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key
            args_str = cache_key(*args[1:], **kwargs)  # Skip 'self' or 'db'
            full_key = f"{key_prefix}:{func.__name__}:{args_str}" if key_prefix else f"{func.__name__}:{args_str}"
            
            # Try to get from cache
            cached_result = await cache.get(full_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {full_key}")
                return cached_result
            
            # Call function if not cached
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(full_key, result, ttl)
            logger.debug(f"Cached result for {full_key}")
            
            return result
        
        return wrapper
    return decorator


# Cache key prefixes
CACHE_PREFIXES = {
    "user": "user",
    "workspace": "workspace",
    "analytics": "analytics",
    "leads": "leads",
    "conversations": "conversations",
    "documents": "documents",
    "workflows": "workflows",
}
