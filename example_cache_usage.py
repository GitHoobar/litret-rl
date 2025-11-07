#!/usr/bin/env python3
"""
Example demonstrating Redis caching layer for Sanskrit text parsing.

This script shows various ways to use the caching system:
1. Basic cache operations
2. Using the caching decorator
3. Batch caching
4. Performance monitoring
5. Cache management
"""

import time
from redis_cache import SanskritParsingCache, cached_parse


def example_basic_operations():
    """Demonstrate basic cache get/set operations."""
    print("=" * 60)
    print("Example 1: Basic Cache Operations")
    print("=" * 60)
    
    # Initialize cache
    cache = SanskritParsingCache(ttl=3600)  # 1 hour TTL
    
    if not cache.is_enabled():
        print("❌ Redis is not available. Please start Redis server.")
        return
    
    print("✓ Redis connection established\n")
    
    # Sample Sanskrit verse from Bhagavad Gita
    verse_text = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"
    parsed_data = {
        "quote": verse_text,
        "category": "Epic, Mahabharata",
        "book": "Bhagavad Gita",
        "position": "1.1"
    }
    
    # First access - cache miss
    print("1. First access (cache MISS expected):")
    start = time.time()
    result = cache.get(verse_text)
    elapsed = time.time() - start
    print(f"   Result: {result}")
    print(f"   Time: {elapsed*1000:.3f}ms\n")
    
    # Store in cache
    print("2. Storing in cache:")
    cache.set(verse_text, parsed_data)
    print("   ✓ Data cached\n")
    
    # Second access - cache hit
    print("3. Second access (cache HIT expected):")
    start = time.time()
    result = cache.get(verse_text)
    elapsed = time.time() - start
    print(f"   Result: {result}")
    print(f"   Time: {elapsed*1000:.3f}ms")
    print(f"   💡 Cache hit is typically 10-100x faster!\n")


def example_decorator_usage():
    """Demonstrate using the @cached_parse decorator."""
    print("\n" + "=" * 60)
    print("Example 2: Using the Caching Decorator")
    print("=" * 60)
    
    cache = SanskritParsingCache()
    
    if not cache.is_enabled():
        print("❌ Redis is not available.")
        return
    
    @cached_parse(cache)
    def parse_rigveda_verse(text):
        """Simulated parsing function with artificial delay."""
        # Simulate time-consuming parsing
        time.sleep(0.1)  # 100ms parsing time
        
        return {
            "quote": text,
            "category": "Veda, Samhita",
            "book": "Rigveda",
            "position": "Mandala 1, Hymn 1"
        }
    
    verse = "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्"
    
    # First call - will parse and cache
    print("\n1. First call (parses and caches):")
    start = time.time()
    result1 = parse_rigveda_verse(verse)
    elapsed1 = time.time() - start
    print(f"   Time: {elapsed1*1000:.1f}ms")
    print(f"   Result: {result1['quote'][:50]}...")
    
    # Second call - will return from cache
    print("\n2. Second call (returns from cache):")
    start = time.time()
    result2 = parse_rigveda_verse(verse)
    elapsed2 = time.time() - start
    print(f"   Time: {elapsed2*1000:.1f}ms")
    print(f"   Speedup: {elapsed1/elapsed2:.1f}x faster!")


def example_batch_operations():
    """Demonstrate batch caching for multiple verses."""
    print("\n" + "=" * 60)
    print("Example 3: Batch Caching Operations")
    print("=" * 60)
    
    cache = SanskritParsingCache()
    
    if not cache.is_enabled():
        print("❌ Redis is not available.")
        return
    
    # Multiple verses to cache
    verses = [
        ("ॐ भूर्भुवः स्वः", {"quote": "ॐ भूर्भुवः स्वः", "book": "Rigveda", "position": "Gayatri"}),
        ("तत्सवितुर्वरेण्यम्", {"quote": "तत्सवितुर्वरेण्यम्", "book": "Rigveda", "position": "Gayatri"}),
        ("भर्गो देवस्य धीमहि", {"quote": "भर्गो देवस्य धीमहि", "book": "Rigveda", "position": "Gayatri"}),
        ("धियो यो नः प्रचोदयात्", {"quote": "धियो यो नः प्रचोदयात्", "book": "Rigveda", "position": "Gayatri"}),
    ]
    
    print(f"\n1. Batch caching {len(verses)} verses:")
    start = time.time()
    count = cache.set_batch(verses)
    elapsed = time.time() - start
    print(f"   ✓ Cached {count} verses in {elapsed*1000:.1f}ms")
    
    print(f"\n2. Retrieving cached verses:")
    for verse_text, _ in verses:
        result = cache.get(verse_text)
        if result:
            print(f"   ✓ {verse_text[:30]}... (cached)")


def example_performance_stats():
    """Demonstrate cache performance monitoring."""
    print("\n" + "=" * 60)
    print("Example 4: Performance Statistics")
    print("=" * 60)
    
    cache = SanskritParsingCache()
    
    if not cache.is_enabled():
        print("❌ Redis is not available.")
        return
    
    # Reset stats for clean demonstration
    cache.reset_stats()
    print("\n1. Statistics reset\n")
    
    # Perform various cache operations
    test_verses = [
        "वेदाहमेतं पुरुषं महान्तम्",
        "आदित्यवर्णं तमसः परस्तात्",
        "तमेवं विद्वानमृत इह भवति"
    ]
    
    print("2. Performing cache operations:")
    for verse in test_verses:
        # Each verse accessed twice
        cache.get(verse)  # Miss
        cache.set(verse, {"quote": verse, "book": "Vedas"})
        cache.get(verse)  # Hit
        print(f"   Processed: {verse[:40]}...")
    
    # Display statistics
    print("\n3. Cache Statistics:")
    stats = cache.get_stats()
    print(f"   Status: {'Enabled ✓' if stats['enabled'] else 'Disabled ✗'}")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Cache Hits: {stats['hits']}")
    print(f"   Cache Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']}")


def example_cache_management():
    """Demonstrate cache invalidation and management."""
    print("\n" + "=" * 60)
    print("Example 5: Cache Management")
    print("=" * 60)
    
    cache = SanskritParsingCache()
    
    if not cache.is_enabled():
        print("❌ Redis is not available.")
        return
    
    # Add some test data
    test_data = [
        ("Test verse 1", {"data": "test1"}),
        ("Test verse 2", {"data": "test2"}),
        ("Test verse 3", {"data": "test3"}),
    ]
    
    print("\n1. Adding test data to cache:")
    cache.set_batch(test_data)
    print(f"   ✓ Added {len(test_data)} items")
    
    print("\n2. Verifying cached items:")
    for verse, _ in test_data:
        result = cache.get(verse)
        print(f"   {'✓' if result else '✗'} {verse}")
    
    print("\n3. Invalidating cache:")
    deleted = cache.invalidate("sanskrit_parse:*")
    print(f"   ✓ Deleted {deleted} cache entries")
    
    print("\n4. Verifying after invalidation:")
    for verse, _ in test_data:
        result = cache.get(verse)
        print(f"   {'✓' if result else '✗'} {verse} - {'Still cached' if result else 'Cleared'}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Redis Caching Layer Examples")
    print("Sanskrit Text Parsing Performance Optimization")
    print("=" * 60)
    
    try:
        example_basic_operations()
        example_decorator_usage()
        example_batch_operations()
        example_performance_stats()
        example_cache_management()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

