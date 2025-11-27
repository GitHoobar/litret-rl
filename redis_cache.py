"""
Redis Caching Layer for Sanskrit Text Parsing Performance Optimization

This module provides a Redis-based caching layer to optimize Sanskrit text parsing operations.
It reduces redundant parsing by caching parsed verse data with configurable TTL.
"""

import json
import hashlib
import redis
from typing import Optional, Dict, Any, List
from functools import wraps
import os


class SanskritParsingCache:
    """
    Redis cache manager for Sanskrit text parsing operations.
    
    Features:
    - Automatic cache key generation based on content hash
    - Configurable TTL (Time To Live) for cached entries
    - Batch caching support for multiple verses
    - Cache invalidation utilities
    - Performance metrics tracking
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: str = None,
        ttl: int = 86400  # 24 hours default
    ):
        """
        Initialize Redis cache connection.
        
        Args:
            host: Redis server hostname (defaults to REDIS_HOST env or 'localhost')
            port: Redis server port (defaults to REDIS_PORT env or 6379)
            db: Redis database number
            password: Redis password (optional, from REDIS_PASSWORD env)
            ttl: Default time-to-live for cached entries in seconds
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.db = db
        self.ttl = ttl
        
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self._cache_enabled = True
        except (redis.ConnectionError, redis.ResponseError) as e:
            print(f"Warning: Redis connection failed: {e}")
            print("Caching disabled. Parsing will proceed without cache.")
            self._cache_enabled = False
            self.redis_client = None
    
    def _generate_cache_key(self, content: str, prefix: str = "sanskrit_parse") -> str:
        """
        Generate a cache key based on content hash.
        
        Args:
            content: The text content to hash
            prefix: Key prefix for namespacing
            
        Returns:
            Cache key string
        """
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        return f"{prefix}:{content_hash}"
    
    def get(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve parsed data from cache.
        
        Args:
            content: The original text content
            
        Returns:
            Cached parsed data or None if not found
        """
        if not self._cache_enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(content)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                # Increment cache hit counter
                self.redis_client.incr("cache_hits")
                return json.loads(cached_data)
            else:
                # Increment cache miss counter
                self.redis_client.incr("cache_misses")
                return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def set(self, content: str, parsed_data: Dict[str, Any], ttl: int = None) -> bool:
        """
        Store parsed data in cache.
        
        Args:
            content: The original text content
            parsed_data: The parsed verse data
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._cache_enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(content)
            serialized_data = json.dumps(parsed_data, ensure_ascii=False)
            ttl = ttl or self.ttl
            
            self.redis_client.setex(cache_key, ttl, serialized_data)
            return True
        except Exception as e:
            print(f"Cache storage error: {e}")
            return False
    
    def set_batch(self, items: List[tuple], ttl: int = None) -> int:
        """
        Store multiple parsed items in cache efficiently using pipeline.
        
        Args:
            items: List of (content, parsed_data) tuples
            ttl: Time-to-live in seconds
            
        Returns:
            Number of items successfully cached
        """
        if not self._cache_enabled:
            return 0
        
        try:
            ttl = ttl or self.ttl
            pipeline = self.redis_client.pipeline()
            
            for content, parsed_data in items:
                cache_key = self._generate_cache_key(content)
                serialized_data = json.dumps(parsed_data, ensure_ascii=False)
                pipeline.setex(cache_key, ttl, serialized_data)
            
            pipeline.execute()
            return len(items)
        except Exception as e:
            print(f"Batch cache storage error: {e}")
            return 0
    
    def invalidate(self, pattern: str = "sanskrit_parse:*") -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Redis key pattern to match
            
        Returns:
            Number of keys deleted
        """
        if not self._cache_enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache hits, misses, and hit rate
        """
        if not self._cache_enabled:
            return {"enabled": False}
        
        try:
            hits = int(self.redis_client.get("cache_hits") or 0)
            misses = int(self.redis_client.get("cache_misses") or 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                "enabled": True,
                "hits": hits,
                "misses": misses,
                "total_requests": total,
                "hit_rate": f"{hit_rate:.2f}%"
            }
        except Exception as e:
            print(f"Stats retrieval error: {e}")
            return {"enabled": True, "error": str(e)}
    
    def reset_stats(self) -> bool:
        """Reset cache statistics counters."""
        if not self._cache_enabled:
            return False
        
        try:
            self.redis_client.set("cache_hits", 0)
            self.redis_client.set("cache_misses", 0)
            return True
        except Exception as e:
            print(f"Stats reset error: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled and working."""
        return self._cache_enabled


def cached_parse(cache_instance: SanskritParsingCache):
    """
    Decorator for caching Sanskrit text parsing functions.
    
    Usage:
        cache = SanskritParsingCache()
        
        @cached_parse(cache)
        def parse_verse(text):
            # parsing logic
            return parsed_data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(text_content, *args, **kwargs):
            if not cache_instance.is_enabled():
                return func(text_content, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_instance.get(text_content)
            if cached_result:
                return cached_result
            
            # Parse and cache the result
            result = func(text_content, *args, **kwargs)
            cache_instance.set(text_content, result)
            return result
        
        return wrapper
    return decorator

