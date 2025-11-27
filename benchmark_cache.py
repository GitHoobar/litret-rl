#!/usr/bin/env python3
"""
Benchmark script to demonstrate Redis caching performance improvements.

This script compares parsing performance with and without caching.
"""

import time
import json
from redis_cache import SanskritParsingCache


def simulate_parsing(text, delay=0.001):
    """
    Simulate text parsing with artificial delay.
    Real parsing involves regex, string operations, etc.
    
    Args:
        text: Text to parse
        delay: Simulated processing time in seconds
    """
    time.sleep(delay)  # Simulate processing time
    
    # Simulate some parsing work
    parts = text.split()
    processed = ' '.join(parts)
    
    return {
        "quote": processed,
        "category": "Benchmark",
        "book": "Test",
        "position": "1.1",
        "word_count": len(parts)
    }


def benchmark_without_cache(verses, iterations=1):
    """Benchmark parsing without caching."""
    print(f"\n{'='*60}")
    print("Benchmark: WITHOUT CACHE")
    print(f"{'='*60}")
    print(f"Verses: {len(verses)}")
    print(f"Iterations: {iterations}")
    
    start_time = time.time()
    
    for iteration in range(iterations):
        for verse in verses:
            parsed_data = simulate_parsing(verse)
    
    elapsed = time.time() - start_time
    total_operations = len(verses) * iterations
    avg_per_operation = elapsed / total_operations
    
    print(f"\nResults:")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Total operations: {total_operations}")
    print(f"  Average per operation: {avg_per_operation*1000:.2f}ms")
    print(f"  Operations per second: {total_operations/elapsed:.1f}")
    
    return elapsed, avg_per_operation


def benchmark_with_cache(verses, iterations=1):
    """Benchmark parsing with Redis caching."""
    print(f"\n{'='*60}")
    print("Benchmark: WITH CACHE")
    print(f"{'='*60}")
    print(f"Verses: {len(verses)}")
    print(f"Iterations: {iterations}")
    
    cache = SanskritParsingCache()
    
    if not cache.is_enabled():
        print("\n❌ Redis not available. Cannot run cache benchmark.")
        return None, None
    
    # Clear cache for clean benchmark
    cache.invalidate("sanskrit_parse:*")
    cache.reset_stats()
    
    print(f"✓ Redis connection established")
    
    start_time = time.time()
    
    for iteration in range(iterations):
        for verse in verses:
            # Try to get from cache
            cached_result = cache.get(verse)
            
            if cached_result is None:
                # Parse and cache
                parsed_data = simulate_parsing(verse)
                cache.set(verse, parsed_data)
            else:
                # Use cached data
                parsed_data = cached_result
    
    elapsed = time.time() - start_time
    total_operations = len(verses) * iterations
    avg_per_operation = elapsed / total_operations
    
    # Get cache statistics
    stats = cache.get_stats()
    
    print(f"\nResults:")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Total operations: {total_operations}")
    print(f"  Average per operation: {avg_per_operation*1000:.2f}ms")
    print(f"  Operations per second: {total_operations/elapsed:.1f}")
    
    print(f"\nCache Statistics:")
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']}")
    
    return elapsed, avg_per_operation


def compare_performance(verses, iterations=1):
    """Compare performance with and without cache."""
    print(f"\n{'#'*60}")
    print("# REDIS CACHE PERFORMANCE COMPARISON")
    print(f"{'#'*60}")
    
    # Run without cache
    time_no_cache, avg_no_cache = benchmark_without_cache(verses, iterations)
    
    # Run with cache
    time_with_cache, avg_with_cache = benchmark_with_cache(verses, iterations)
    
    if time_with_cache is None:
        print("\n⚠️  Could not complete cache benchmark (Redis unavailable)")
        return
    
    # Calculate improvements
    time_improvement = time_no_cache / time_with_cache
    avg_improvement = avg_no_cache / avg_with_cache
    time_saved = time_no_cache - time_with_cache
    
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    print(f"\nWithout Cache:")
    print(f"  Total time: {time_no_cache:.3f}s")
    print(f"  Avg per operation: {avg_no_cache*1000:.2f}ms")
    
    print(f"\nWith Cache:")
    print(f"  Total time: {time_with_cache:.3f}s")
    print(f"  Avg per operation: {avg_with_cache*1000:.2f}ms")
    
    print(f"\n🚀 Performance Improvement:")
    print(f"  Speedup: {time_improvement:.1f}x faster")
    print(f"  Time saved: {time_saved:.3f}s ({time_saved/time_no_cache*100:.1f}%)")
    print(f"  Per-operation improvement: {avg_improvement:.1f}x")
    
    # Visual representation
    print(f"\n📊 Visual Comparison:")
    bar_no_cache = '█' * int(time_no_cache * 10)
    bar_with_cache = '█' * max(1, int(time_with_cache * 10))
    
    print(f"  Without Cache: {bar_no_cache} {time_no_cache:.2f}s")
    print(f"  With Cache:    {bar_with_cache} {time_with_cache:.2f}s")


def main():
    """Run benchmarks with different scenarios."""
    
    # Sample Sanskrit verses for benchmarking
    sample_verses = [
        "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्",
        "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
        "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यम्",
        "वेदाहमेतं पुरुषं महान्तमादित्यवर्णं तमसः परस्तात्",
        "तमेवं विद्वानमृत इह भवति नान्यः पन्था विद्यतेऽयनाय",
        "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत",
        "अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्",
        "परित्राणाय साधूनां विनाशाय च दुष्कृताम्",
        "धर्मसंस्थापनार्थाय सम्भवामि युगे युगे",
        "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज",
    ]
    
    print("\n" + "="*60)
    print("SANSKRIT TEXT PARSING - REDIS CACHE BENCHMARK")
    print("="*60)
    
    # Scenario 1: Small dataset, multiple iterations
    print("\n" + "#"*60)
    print("# Scenario 1: Small Dataset (10 verses), Multiple Iterations (5)")
    print("#"*60)
    compare_performance(sample_verses[:10], iterations=5)
    
    # Scenario 2: Larger dataset, fewer iterations
    print("\n\n" + "#"*60)
    print("# Scenario 2: Larger Dataset (50 verses), Single Iteration")
    print("#"*60)
    extended_verses = sample_verses * 5  # 50 verses
    compare_performance(extended_verses, iterations=1)
    
    # Scenario 3: Real-world simulation
    print("\n\n" + "#"*60)
    print("# Scenario 3: Real-world Simulation (100 verses, 3 iterations)")
    print("#"*60)
    real_world_verses = sample_verses * 10  # 100 verses
    compare_performance(real_world_verses, iterations=3)
    
    print("\n" + "="*60)
    print("✓ Benchmark completed!")
    print("="*60)
    
    print("\n💡 Key Takeaways:")
    print("  1. First iteration shows cache population (slower)")
    print("  2. Subsequent iterations benefit from cache (much faster)")
    print("  3. Larger datasets show greater relative improvement")
    print("  4. Real-world parsing is typically slower, making cache even more valuable")
    print("\n")


if __name__ == "__main__":
    main()

