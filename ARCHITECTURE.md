# Architecture Documentation

## System Overview

The Sanskrit Literature Parsing system with Redis caching is designed for high-performance text parsing and data transformation of ancient Indian texts.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Sanskrit Text Parsing System                 │
│                      with Redis Caching Layer                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Input Layer  │
└──────────────┘
      │
      │  ┌─────────────────┐     ┌─────────────────┐
      ├──│ rigveda.txt     │     │ ramayana.txt    │
      ├──│ bhagwvadgita.txt│     │ agnipurana.txt  │
      └──│ garudapurana.txt│     └─────────────────┘
         └─────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│                    Parsing Scripts Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ rigveda.py   │  │ ramayana.py  │  │ agnipurana.py│       │
│  │              │  │              │  │              │       │
│  │ + parse()    │  │ + parse()    │  │ + parse()    │       │
│  │ + extract()  │  │ + extract()  │  │ + extract()  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│                  Redis Caching Layer (NEW!)                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         SanskritParsingCache (redis_cache.py)          │  │
│  │                                                          │  │
│  │  Core Components:                                       │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │ 1. Cache Key Generator (SHA-256 hashing)       │    │  │
│  │  │    Input: verse text → Output: cache_key       │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │ 2. Cache Operations Manager                    │    │  │
│  │  │    - get(key)                                   │    │  │
│  │  │    - set(key, value, ttl)                       │    │  │
│  │  │    - set_batch(items)                           │    │  │
│  │  │    - invalidate(pattern)                        │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │ 3. Performance Monitor                          │    │  │
│  │  │    - Track hits/misses                          │    │  │
│  │  │    - Calculate hit rate                         │    │  │
│  │  │    - Generate statistics                        │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │ 4. Decorator Interface (@cached_parse)         │    │  │
│  │  │    - Automatic caching wrapper                  │    │  │
│  │  │    - Transparent cache integration              │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│                    Redis Server                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Key-Value Store                                      │    │
│  │  ┌─────────────────────────────────────────────┐     │    │
│  │  │ Key: sanskrit_parse:abc123def456            │     │    │
│  │  │ Value: {                                     │     │    │
│  │  │   "quote": "धर्मक्षेत्रे...",              │     │    │
│  │  │   "category": "Epic",                        │     │    │
│  │  │   "book": "Bhagavad Gita",                   │     │    │
│  │  │   "position": "1.1"                          │     │    │
│  │  │ }                                            │     │    │
│  │  │ TTL: 86400 seconds                           │     │    │
│  │  └─────────────────────────────────────────────┘     │    │
│  │                                                        │    │
│  │  Statistics:                                          │    │
│  │  - cache_hits: 1523                                   │    │
│  │  - cache_misses: 342                                  │    │
│  │  - hit_rate: 81.65%                                   │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────┐
│                    Output Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ .jsonl files │  │ Statistics   │  │ HF Datasets  │        │
│  │              │  │              │  │              │        │
│  │ - rigveda    │  │ - Hit rates  │  │ - Upload     │        │
│  │ - ramayana   │  │ - Timings    │  │ - Version    │        │
│  │ - puranas    │  │ - Metrics    │  │ - Share      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

### Without Cache (Original Flow)

```
1. Read source .txt file
2. Parse each verse (regex, string ops)
3. Convert to JSON format
4. Write to .jsonl file

Time per verse: ~10-100ms
```

### With Cache (Optimized Flow)

```
First Run (Cache Population):
1. Read source .txt file
2. For each verse:
   a. Generate cache key (SHA-256)
   b. Check Redis cache
   c. Cache MISS → Parse verse
   d. Store result in Redis
   e. Write to .jsonl file

Time per verse: ~10-100ms (same as without cache)

Subsequent Runs (Cache Utilization):
1. Read source .txt file
2. For each verse:
   a. Generate cache key (SHA-256)
   b. Check Redis cache
   c. Cache HIT → Retrieve from Redis (0.1-1ms)
   d. Write to .jsonl file

Time per verse: ~0.1-1ms (10-100x faster!)
```

## Component Details

### 1. Redis Cache Module (`redis_cache.py`)

**Purpose**: Provide high-performance caching for parsed Sanskrit text data

**Key Classes**:
- `SanskritParsingCache`: Main cache manager class

**Key Methods**:
```python
__init__(host, port, db, password, ttl)  # Initialize connection
get(content)                              # Retrieve cached data
set(content, parsed_data, ttl)           # Store parsed data
set_batch(items)                         # Batch store operation
invalidate(pattern)                      # Clear cache entries
get_stats()                              # Performance metrics
reset_stats()                            # Reset counters
is_enabled()                             # Check availability
```

**Decorator**:
```python
@cached_parse(cache_instance)           # Auto-caching wrapper
```

### 2. Parsing Scripts (Enhanced)

**Enhanced Features**:
- Redis cache integration
- Performance statistics
- Cache hit/miss tracking
- `--no-cache` flag support

**Example**: `parsing_scripts/rigveda.py`
```python
def parse_verses(..., use_cache=True):
    cache = SanskritParsingCache()
    
    for verse in verses:
        # Try cache first
        cached = cache.get(verse)
        if cached:
            use_cached_data(cached)
        else:
            parsed = parse_verse(verse)
            cache.set(verse, parsed)
```

### 3. Redis Server

**Configuration**:
- Host: localhost (default) or custom
- Port: 6379 (default) or custom
- DB: 0 (default)
- TTL: 86400 seconds (24 hours, configurable)

**Data Structure**:
```
Key Format: sanskrit_parse:{content_hash}
Value Format: JSON string (UTF-8)
Expiration: TTL-based automatic cleanup
```

### 4. Configuration Management

**Environment Variables**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional_password
```

**Programmatic**:
```python
cache = SanskritParsingCache(
    host='redis.server.com',
    port=6380,
    password='secret',
    ttl=3600
)
```

## Performance Characteristics

### Cache Operations

| Operation | Time Complexity | Latency |
|-----------|----------------|---------|
| Cache Key Generation | O(n) | <0.1ms |
| Cache GET | O(1) | 0.1-1ms |
| Cache SET | O(1) | 0.1-1ms |
| Batch SET (n items) | O(n) | ~0.1ms per item |
| Invalidate Pattern | O(n) | Varies by key count |

### Parsing Operations

| Operation | Without Cache | With Cache | Speedup |
|-----------|--------------|------------|---------|
| Single verse | 10-100ms | 0.1-1ms | 10-100x |
| 100 verses | 1-10s | 0.01-0.1s | 100x |
| 10,000 verses | 100-1000s | 1-10s | 100x |

### Memory Usage

| Component | Memory Footprint |
|-----------|-----------------|
| Cache module | ~1-5MB |
| Redis per verse | ~0.5-2KB |
| 10,000 verses cached | ~5-20MB |

## Scalability

### Horizontal Scaling
- Redis Cluster support (future)
- Multiple Redis instances
- Load balancing across instances

### Vertical Scaling
- Increase Redis memory allocation
- Optimize TTL based on usage patterns
- Implement cache warming strategies

### Performance Limits
- Single Redis instance: ~100,000 ops/second
- Network latency: <1ms on localhost
- Memory: Limited by Redis configuration

## Security Considerations

### Authentication
- Redis password protection
- Environment variable configuration
- No credentials in code

### Data Privacy
- Cache contains parsed public domain texts
- No sensitive user data
- TTL-based automatic expiration

### Network Security
- Redis on localhost by default
- Firewall rules for remote Redis
- SSL/TLS support (if needed)

## Monitoring & Observability

### Built-in Metrics
```python
stats = cache.get_stats()
# {
#   'enabled': True,
#   'hits': 1523,
#   'misses': 342,
#   'total_requests': 1865,
#   'hit_rate': '81.65%'
# }
```

### Performance Tracking
- Cache hit rate monitoring
- Latency measurements
- Operation counters

### Future Enhancements
- Prometheus metrics export
- Grafana dashboards
- Real-time alerting

## Error Handling

### Graceful Degradation
```
Redis Available    → Use cache (optimal performance)
Redis Unavailable  → Skip cache (still functional)
Redis Error        → Log warning, continue without cache
```

### Automatic Fallback
- Connection failures handled automatically
- No interruption to parsing workflow
- Warning messages for debugging

## Testing Strategy

### Unit Tests (`test_redis_cache.py`)
- Cache initialization
- Basic operations (get/set)
- Batch operations
- Statistics tracking
- Decorator functionality
- Error handling
- Unicode support
- TTL behavior

### Integration Tests
- End-to-end parsing with cache
- Performance benchmarks
- Real-world data scenarios

### Benchmark Suite (`benchmark_cache.py`)
- Performance comparisons
- Multiple scenarios
- Visual performance graphs

## Deployment Options

### Development
```bash
# Local Redis
redis-server
python parsing_scripts/rigveda.py
```

### Docker
```bash
# Docker Compose
docker-compose up -d
python parsing_scripts/rigveda.py
```

### Production
```bash
# Managed Redis (AWS ElastiCache, Redis Cloud, etc.)
export REDIS_HOST=redis.production.com
export REDIS_PASSWORD=secure_password
python parsing_scripts/rigveda.py
```

## Future Architecture Improvements

### Planned Enhancements
1. **Multi-tier Caching**: In-memory LRU cache + Redis
2. **Cache Warming**: Pre-populate cache on startup
3. **Distributed Caching**: Redis Cluster support
4. **Advanced Metrics**: Prometheus/Grafana integration
5. **Cache Compression**: Reduce memory footprint
6. **Smart Invalidation**: Detect source file changes

### Extensibility
- Pluggable cache backends (Redis, Memcached, PostgreSQL)
- Custom cache key strategies
- Configurable serialization formats
- Cache middleware pipeline

---

**Version**: 2.0.0  
**Last Updated**: November 7, 2025  
**Maintainer**: [Your Name]

