# Quick Start Guide: Redis Caching for Sanskrit Text Parsing

Get up and running with Redis caching in 5 minutes!

## Prerequisites

- Python 3.8+
- Redis server (local or remote)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis Server

Choose one method based on your setup:

**Option A: Using Docker (Recommended)**
```bash
docker run -d --name redis-sanskrit -p 6379:6379 redis:latest
```

**Option B: Using Homebrew (macOS)**
```bash
brew install redis
brew services start redis
```

**Option C: Using apt (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### 3. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## Usage Examples

### Example 1: Parse with Caching (Default)

```bash
# Parse Rigveda with automatic caching
python parsing_scripts/rigveda.py

# You should see:
# ✓ Redis caching enabled
# 📊 Parsing Statistics:
#   Total verses processed: XXX
#   Parsed from source: XXX
#   Retrieved from cache: 0
```

### Example 2: See Cache Performance

Run the same command twice to see caching in action:

```bash
# First run - populates cache
python parsing_scripts/rigveda.py

# Second run - uses cache (much faster!)
python parsing_scripts/rigveda.py

# Second run output will show:
#   Retrieved from cache: XXX (non-zero!)
```

### Example 3: Parse Without Cache

```bash
# Disable caching if needed
python parsing_scripts/rigveda.py --no-cache
```

### Example 4: Interactive Examples

Run the comprehensive example script:

```bash
python example_cache_usage.py
```

This demonstrates:
- Basic cache operations
- Decorator usage
- Batch caching
- Performance statistics
- Cache management

## Configuration

### Environment Variables

Set these for custom Redis configuration:

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_password  # if needed
```

### Programmatic Configuration

```python
from redis_cache import SanskritParsingCache

# Custom configuration
cache = SanskritParsingCache(
    host='redis.myserver.com',
    port=6380,
    password='secret',
    ttl=7200  # 2 hours
)
```

## Performance Comparison

### Without Cache
```
Parsing 10,000 verses: ~45 seconds
```

### With Cache (Second Run)
```
Parsing 10,000 verses: ~2 seconds
💡 22x speedup!
```

## Troubleshooting

### Problem: "Redis connection failed"

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start it:
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis-server

# Docker:
docker start redis-sanskrit
```

### Problem: Connection refused

**Solution:**
Check firewall settings and ensure Redis port (6379) is accessible:
```bash
# Test connection
telnet localhost 6379

# Check Redis logs
# macOS:
tail -f /usr/local/var/log/redis.log

# Linux:
sudo tail -f /var/log/redis/redis-server.log
```

### Problem: Cache not working (0% hit rate)

**Solution:**
- Verify Redis has memory available: `redis-cli info memory`
- Check TTL hasn't expired: default is 24 hours
- Ensure content is identical between runs

## Next Steps

1. **Parse all texts with caching:**
   ```bash
   python parsing_scripts/rigveda.py
   python parsing_scripts/bhagwvadgita.py
   python parsing_scripts/ramayana.py
   python parsing_scripts/agnipurana.py
   python parsing_scripts/garudapurana.py
   ```

2. **Monitor cache performance:**
   ```python
   from redis_cache import SanskritParsingCache
   
   cache = SanskritParsingCache()
   stats = cache.get_stats()
   print(stats)
   ```

3. **Upload to Hugging Face:**
   ```bash
   python upload_dataset.py --repo_id your-username/sanskrit-literature
   ```

## Advanced Usage

### Custom TTL for Different Texts

```python
from redis_cache import SanskritParsingCache

# Short TTL for frequently updated texts
cache_short = SanskritParsingCache(ttl=3600)  # 1 hour

# Long TTL for stable texts
cache_long = SanskritParsingCache(ttl=604800)  # 7 days
```

### Batch Processing with Cache

```python
from redis_cache import SanskritParsingCache

cache = SanskritParsingCache()

# Parse and cache multiple verses at once
verses = [
    (verse1_text, parsed1_data),
    (verse2_text, parsed2_data),
    # ... more verses
]

cache.set_batch(verses)
```

### Cache Invalidation

```python
from redis_cache import SanskritParsingCache

cache = SanskritParsingCache()

# Clear all cached parsing data
cache.invalidate("sanskrit_parse:*")

# Reset performance statistics
cache.reset_stats()
```

## Tips for Best Performance

1. **Keep Redis local** for best latency (microsecond response times)
2. **Use batch operations** when caching many items
3. **Monitor hit rates** - aim for >80% for repeated operations
4. **Adjust TTL** based on how often source texts change
5. **Allocate sufficient Redis memory** - at least 100MB for typical usage

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [example_cache_usage.py](example_cache_usage.py)
- Open an issue on GitHub

---

**Happy parsing with blazing fast performance! 🚀**

