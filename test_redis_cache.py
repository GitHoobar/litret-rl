"""
Unit tests for Redis caching layer.

Run with: pytest test_redis_cache.py
"""

import pytest
import time
from redis_cache import SanskritParsingCache, cached_parse


@pytest.fixture
def cache():
    """Create a cache instance for testing."""
    cache = SanskritParsingCache(ttl=60)  # Short TTL for testing
    if cache.is_enabled():
        # Clean up before tests
        cache.invalidate("sanskrit_parse:*")
        cache.reset_stats()
    return cache


@pytest.fixture
def sample_verse():
    """Sample Sanskrit verse for testing."""
    return "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"


@pytest.fixture
def sample_parsed_data():
    """Sample parsed data for testing."""
    return {
        "quote": "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
        "category": "Epic, Mahabharata",
        "book": "Bhagavad Gita",
        "position": "1.1"
    }


class TestCacheInitialization:
    """Test cache initialization and connection."""
    
    def test_cache_creation(self, cache):
        """Test cache instance creation."""
        assert cache is not None
        assert hasattr(cache, 'redis_client')
    
    def test_cache_connection_status(self, cache):
        """Test if cache connection can be checked."""
        status = cache.is_enabled()
        assert isinstance(status, bool)
    
    def test_custom_configuration(self):
        """Test cache with custom configuration."""
        custom_cache = SanskritParsingCache(
            host='localhost',
            port=6379,
            db=1,
            ttl=3600
        )
        assert custom_cache.ttl == 3600
        assert custom_cache.db == 1


class TestBasicCacheOperations:
    """Test basic cache get/set operations."""
    
    def test_cache_miss(self, cache, sample_verse):
        """Test cache miss on first access."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        result = cache.get(sample_verse)
        assert result is None
    
    def test_cache_set_and_get(self, cache, sample_verse, sample_parsed_data):
        """Test storing and retrieving data."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        # Set data
        success = cache.set(sample_verse, sample_parsed_data)
        assert success is True
        
        # Get data
        result = cache.get(sample_verse)
        assert result is not None
        assert result['quote'] == sample_parsed_data['quote']
        assert result['book'] == sample_parsed_data['book']
    
    def test_cache_overwrite(self, cache, sample_verse):
        """Test overwriting existing cache entry."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        data1 = {"quote": sample_verse, "version": 1}
        data2 = {"quote": sample_verse, "version": 2}
        
        cache.set(sample_verse, data1)
        cache.set(sample_verse, data2)
        
        result = cache.get(sample_verse)
        assert result['version'] == 2


class TestBatchOperations:
    """Test batch caching operations."""
    
    def test_batch_set(self, cache):
        """Test batch setting multiple items."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        items = [
            ("verse1", {"quote": "verse1", "book": "test"}),
            ("verse2", {"quote": "verse2", "book": "test"}),
            ("verse3", {"quote": "verse3", "book": "test"}),
        ]
        
        count = cache.set_batch(items)
        assert count == 3
        
        # Verify all items are cached
        for verse, _ in items:
            result = cache.get(verse)
            assert result is not None
    
    def test_batch_set_empty(self, cache):
        """Test batch setting with empty list."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        count = cache.set_batch([])
        assert count == 0


class TestCacheInvalidation:
    """Test cache invalidation operations."""
    
    def test_invalidate_pattern(self, cache):
        """Test invalidating cache entries by pattern."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        # Add some test data
        cache.set("test1", {"data": "test1"})
        cache.set("test2", {"data": "test2"})
        cache.set("test3", {"data": "test3"})
        
        # Invalidate all
        deleted = cache.invalidate("sanskrit_parse:*")
        assert deleted >= 0  # Could be 0 if already deleted
        
        # Verify items are gone
        assert cache.get("test1") is None
        assert cache.get("test2") is None
        assert cache.get("test3") is None


class TestPerformanceStats:
    """Test cache performance statistics."""
    
    def test_initial_stats(self, cache):
        """Test initial statistics state."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        cache.reset_stats()
        stats = cache.get_stats()
        
        assert stats['enabled'] is True
        assert stats['hits'] == 0
        assert stats['misses'] == 0
    
    def test_stats_tracking(self, cache, sample_verse, sample_parsed_data):
        """Test that statistics are tracked correctly."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        cache.reset_stats()
        cache.invalidate("sanskrit_parse:*")
        
        # First access - miss
        cache.get(sample_verse)
        stats1 = cache.get_stats()
        assert stats1['misses'] == 1
        assert stats1['hits'] == 0
        
        # Set data
        cache.set(sample_verse, sample_parsed_data)
        
        # Second access - hit
        cache.get(sample_verse)
        stats2 = cache.get_stats()
        assert stats2['hits'] == 1
        
        # Third access - another hit
        cache.get(sample_verse)
        stats3 = cache.get_stats()
        assert stats3['hits'] == 2
    
    def test_hit_rate_calculation(self, cache):
        """Test hit rate percentage calculation."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        cache.reset_stats()
        cache.invalidate("sanskrit_parse:*")
        
        # Create predictable hit/miss pattern
        verse = "test_verse"
        cache.get(verse)  # Miss
        cache.set(verse, {"data": "test"})
        cache.get(verse)  # Hit
        cache.get(verse)  # Hit
        
        stats = cache.get_stats()
        # 2 hits, 1 miss = 66.67% hit rate
        assert '66.67%' in stats['hit_rate'] or '66.66%' in stats['hit_rate']
    
    def test_reset_stats(self, cache):
        """Test resetting statistics."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        # Generate some stats
        cache.get("dummy")
        
        # Reset
        success = cache.reset_stats()
        assert success is True
        
        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0


class TestCacheDecorator:
    """Test the @cached_parse decorator."""
    
    def test_decorator_basic(self, cache):
        """Test basic decorator functionality."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        cache.invalidate("sanskrit_parse:*")
        call_count = 0
        
        @cached_parse(cache)
        def parse_function(text):
            nonlocal call_count
            call_count += 1
            return {"quote": text, "parsed": True}
        
        verse = "test verse for decorator"
        
        # First call - should execute function
        result1 = parse_function(verse)
        assert call_count == 1
        assert result1['parsed'] is True
        
        # Second call - should use cache
        result2 = parse_function(verse)
        assert call_count == 1  # Function not called again
        assert result2['parsed'] is True
    
    def test_decorator_with_disabled_cache(self):
        """Test decorator behavior when cache is disabled."""
        disabled_cache = SanskritParsingCache(host='invalid_host', port=1)
        call_count = 0
        
        @cached_parse(disabled_cache)
        def parse_function(text):
            nonlocal call_count
            call_count += 1
            return {"quote": text}
        
        verse = "test verse"
        
        # Both calls should execute function since cache is disabled
        parse_function(verse)
        parse_function(verse)
        assert call_count == 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_cache_with_invalid_host(self):
        """Test cache creation with invalid host."""
        cache = SanskritParsingCache(host='invalid_host', port=99999)
        assert cache.is_enabled() is False
    
    def test_cache_disabled_operations(self):
        """Test operations when cache is disabled."""
        cache = SanskritParsingCache(host='invalid_host', port=1)
        
        # All operations should fail gracefully
        assert cache.get("test") is None
        assert cache.set("test", {"data": "test"}) is False
        assert cache.set_batch([("test", {"data": "test"})]) == 0
        assert cache.invalidate("*") == 0
    
    def test_unicode_content(self, cache):
        """Test caching with Unicode Sanskrit text."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        sanskrit_texts = [
            "ॐ भूर्भुवः स्वः",
            "तत्सवितुर्वरेण्यम्",
            "भर्गो देवस्य धीमहि",
            "धियो यो नः प्रचोदयात्"
        ]
        
        for text in sanskrit_texts:
            data = {"quote": text, "language": "Sanskrit"}
            cache.set(text, data)
            result = cache.get(text)
            assert result is not None
            assert result['quote'] == text
    
    def test_large_content(self, cache):
        """Test caching large content."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        # Create large verse (repeat text many times)
        large_verse = "अग्निमीळे पुरोहितं " * 1000
        data = {"quote": large_verse, "size": "large"}
        
        success = cache.set(large_verse, data)
        assert success is True
        
        result = cache.get(large_verse)
        assert result is not None
        assert result['size'] == "large"


class TestCacheKeyGeneration:
    """Test cache key generation."""
    
    def test_same_content_same_key(self, cache):
        """Test that same content generates same key."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        verse = "test verse"
        key1 = cache._generate_cache_key(verse)
        key2 = cache._generate_cache_key(verse)
        
        assert key1 == key2
    
    def test_different_content_different_key(self, cache):
        """Test that different content generates different keys."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        key1 = cache._generate_cache_key("verse1")
        key2 = cache._generate_cache_key("verse2")
        
        assert key1 != key2
    
    def test_key_format(self, cache):
        """Test cache key format."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        key = cache._generate_cache_key("test")
        assert key.startswith("sanskrit_parse:")
        assert len(key.split(":")) == 2


class TestTTL:
    """Test Time-To-Live functionality."""
    
    def test_custom_ttl(self, cache):
        """Test setting custom TTL for cache entries."""
        if not cache.is_enabled():
            pytest.skip("Redis not available")
        
        verse = "ttl_test_verse"
        data = {"quote": verse}
        
        # Set with very short TTL
        cache.set(verse, data, ttl=1)
        
        # Should exist immediately
        result1 = cache.get(verse)
        assert result1 is not None
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        result2 = cache.get(verse)
        assert result2 is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

