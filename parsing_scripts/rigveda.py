import json
import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from redis_cache import SanskritParsingCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("Warning: Redis cache module not available. Proceeding without caching.")


def parse_verses(input_path, output_path, category="Veda, Samhita", book="Rigveda", use_cache=True):
    """
    Read a text file of Vedic verses separated by blank lines, each ending with '|| POSITION',
    and write each verse as a JSON object per line in JSONL format. Removes any '|' characters within the verse.
    
    Args:
        input_path: Path to input text file
        output_path: Path to output JSONL file
        category: Category classification for the text
        book: Book name
        use_cache: Enable Redis caching for performance optimization (default: True)
    """
    # Initialize cache if available and enabled
    cache = None
    if use_cache and CACHE_AVAILABLE:
        cache = SanskritParsingCache()
        if cache.is_enabled():
            print(f"✓ Redis caching enabled")
        else:
            cache = None
            print("⚠ Redis caching disabled (connection failed)")
    elif not use_cache:
        print("⚠ Caching explicitly disabled")
    
    cached_count = 0
    parsed_count = 0
    # Read the entire file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove any triple-quote delimiters
    content = content.replace('"""', '')

    # Split into blocks by two or more newlines
    blocks = [blk.strip() for blk in content.split('\n\n') if blk.strip()]

    with open(output_path, 'w', encoding='utf-8') as out:
        for blk in blocks:
            # Skip blocks without the '||' separator
            if '||' not in blk:
                continue
            # Combine multiple lines into a single string
            combined = ' '.join(line.strip() for line in blk.splitlines())
            
            # Try to get from cache first
            record = None
            if cache:
                record = cache.get(combined)
                if record:
                    cached_count += 1
            
            # If not in cache, parse it
            if record is None:
                # Split into quote text and position
                try:
                    quote_part, pos_part = combined.rsplit('||', 1)
                except ValueError:
                    continue  # malformed block

                # Clean up quote and position
                quote = quote_part.replace('|', '').strip()
                position = pos_part.strip()

                record = {
                    "quote": quote,
                    "category": category,
                    "book": book,
                    "position": position
                }
                
                # Store in cache for future use
                if cache:
                    cache.set(combined, record)
                
                parsed_count += 1
            
            # Write as a single JSON line
            out.write(json.dumps(record, ensure_ascii=False) + '\n')


    # Print statistics
    total = cached_count + parsed_count
    print(f"\n📊 Parsing Statistics:")
    print(f"  Total verses processed: {total}")
    print(f"  Parsed from source: {parsed_count}")
    print(f"  Retrieved from cache: {cached_count}")
    
    if cache:
        stats = cache.get_stats()
        if stats.get('enabled'):
            print(f"\n🚀 Cache Performance:")
            print(f"  Hit rate: {stats.get('hit_rate', 'N/A')}")
            print(f"  Total hits: {stats.get('hits', 0)}")
            print(f"  Total misses: {stats.get('misses', 0)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a text file of Vedic verses into JSONL format with Redis caching support."
    )
    parser.add_argument('--input', default="data/rigveda.txt", help="Input text file path")
    parser.add_argument('--output', default="data/rigveda.jsonl", help="Output JSONL file path")
    parser.add_argument('--no-cache', action='store_true', help="Disable Redis caching")
    args = parser.parse_args()
    
    parse_verses(args.input, args.output, use_cache=not args.no_cache)
