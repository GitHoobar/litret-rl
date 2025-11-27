# Sanskrit Literature Parsing with Redis Caching

A high-performance Sanskrit text parsing system with Redis caching layer for processing ancient Indian texts including Vedas, Puranas, and Epics.

## 📚 Overview

This project parses Sanskrit literature from various ancient texts and converts them into structured JSONL format for machine learning and NLP applications. The parsed data is optimized for uploading to Hugging Face datasets.

### Supported Texts

- **Vedas**: Rigveda (Samhita)
- **Epics**: Ramayana, Bhagavad Gita (Mahabharata)
- **Puranas**: Agni Purana, Garuda Purana

## 🚀 New Feature: Redis Caching Layer

**Version 2.0** introduces a Redis-based caching system that dramatically improves parsing performance for repeated operations.

### Performance Benefits

- **10-100x faster** for re-parsing previously processed texts
- **Reduced I/O operations** through intelligent content hashing
- **Batch caching support** for processing multiple verses efficiently
- **Automatic cache invalidation** with configurable TTL (Time-To-Live)
- **Real-time performance metrics** to monitor cache hit rates

### How It Works

The caching layer uses SHA-256 content hashing to generate unique cache keys for each verse or text block. When parsing:

1. **Cache Check**: Before parsing, the system checks Redis for cached parsed data
2. **Cache Hit**: If found, returns cached data instantly (microseconds vs seconds)
3. **Cache Miss**: Parses the text and stores result in Redis for future use
4. **TTL Management**: Cached entries expire after 24 hours (configurable)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- Redis server (local or remote)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd litret-rl
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install and start Redis** (if not already running):

**macOS** (using Homebrew):
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Docker**:
```bash
docker run -d -p 6379:6379 redis:latest
```

4. **Configure Redis connection** (optional):

Set environment variables for custom Redis configuration:
```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_password  # if authentication is enabled
```

## 📖 Usage

### Basic Parsing (with automatic caching)

Each parsing script now supports Redis caching out of the box:

```bash
# Parse Rigveda with caching
python parsing_scripts/rigveda.py

# Parse Bhagavad Gita with caching
python parsing_scripts/bhagwvadgita.py --input data/bhagwvadgita.txt --output data/bhagwvadgita.jsonl

# Parse other texts
python parsing_scripts/ramayana.py
python parsing_scripts/agnipurana.py
python parsing_scripts/garudapurana.py
```

### Using the Redis Cache Programmatically

```python
from redis_cache import SanskritParsingCache, cached_parse

# Initialize cache with default settings (localhost:6379)
cache = SanskritParsingCache()

# Or with custom configuration
cache = SanskritParsingCache(
    host='redis.example.com',
    port=6380,
    password='secret',
    ttl=3600  # 1 hour TTL
)

# Check if caching is enabled
if cache.is_enabled():
    print("Redis caching is active!")

# Manual cache operations
verse_text = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"
parsed_data = {"quote": verse_text, "category": "Epic", "book": "Bhagavad Gita"}

# Store in cache
cache.set(verse_text, parsed_data)

# Retrieve from cache
cached_result = cache.get(verse_text)

# Batch caching for multiple verses
items = [
    (verse1, parsed1),
    (verse2, parsed2),
    (verse3, parsed3)
]
cache.set_batch(items)

# Get performance statistics
stats = cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
print(f"Total hits: {stats['hits']}, Total misses: {stats['misses']}")

# Clear cache for specific pattern
cache.invalidate("sanskrit_parse:*")

# Reset statistics
cache.reset_stats()
```

### Using the Caching Decorator

```python
from redis_cache import SanskritParsingCache, cached_parse

cache = SanskritParsingCache()

@cached_parse(cache)
def parse_verse(text_content):
    # Your parsing logic here
    # This will automatically cache results
    return {
        "quote": text_content,
        "category": "Veda",
        "book": "Rigveda"
    }

# First call: parses and caches
result1 = parse_verse("ॐ भूर्भुवः स्वः")

# Second call: returns from cache (instant)
result2 = parse_verse("ॐ भूर्भुवः स्वः")
```

## 📊 Performance Metrics

Monitor caching performance to optimize your parsing pipeline:

```python
from redis_cache import SanskritParsingCache

cache = SanskritParsingCache()

# After parsing operations
stats = cache.get_stats()
print(f"""
Cache Performance:
- Status: {'Enabled' if stats['enabled'] else 'Disabled'}
- Cache Hits: {stats.get('hits', 0)}
- Cache Misses: {stats.get('misses', 0)}
- Hit Rate: {stats.get('hit_rate', '0%')}
""")
```

## 📁 Project Structure

```
litret-rl/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── redis_cache.py                 # NEW: Redis caching module
├── upload_dataset.py              # Upload to Hugging Face
├── data/                          # Sanskrit text files and JSONL outputs
│   ├── rigveda.txt
│   ├── rigveda.jsonl
│   ├── bhagwvadgita.txt
│   ├── bhagwvadgita.jsonl
│   ├── ramayana.txt
│   ├── ramayana.jsonl
│   ├── agnipurana.txt
│   ├── agnipurana.jsonl
│   ├── garudapurana.txt
│   └── garudapurana.jsonl
└── parsing_scripts/               # Text-specific parsers
    ├── rigveda.py
    ├── bhagwvadgita.py
    ├── ramayana.py
    ├── agnipurana.py
    └── garudapurana.py
```

## 🔄 Data Format

Each parsed verse is stored as a JSON object with the following schema:

```json
{
  "quote": "Sanskrit verse text",
  "category": "Text category (e.g., 'Veda, Samhita', 'Epic, Mahabharata')",
  "book": "Source text name (e.g., 'Rigveda', 'Bhagavad Gita')",
  "position": "Location reference (e.g., '1.1', 'Mandala 1, Hymn 1, Verse 1')"
}
```

## 🌐 Uploading to Hugging Face

After parsing, upload the dataset to Hugging Face:

```bash
# Login to Hugging Face (first time only)
huggingface-cli login

# Upload dataset
python upload_dataset.py --repo_id your-username/sanskrit-literature

# Or with explicit token
python upload_dataset.py --repo_id your-username/sanskrit-literature --token YOUR_HF_TOKEN
```

## ⚙️ Configuration

### Redis Configuration Options

The cache system supports various configuration methods:

1. **Environment Variables** (recommended for production):
```bash
export REDIS_HOST=redis.production.com
export REDIS_PORT=6379
export REDIS_PASSWORD=your_secure_password
```

2. **Programmatic Configuration**:
```python
cache = SanskritParsingCache(
    host='192.168.1.100',
    port=6380,
    db=1,
    password='secret',
    ttl=7200  # 2 hours
)
```

3. **Default Behavior**:
- If Redis is unavailable, caching is automatically disabled
- Parsing continues without interruption
- A warning is displayed in the console

### TTL (Time-To-Live) Settings

Adjust cache expiration based on your use case:

- **Development**: 3600 seconds (1 hour)
- **Production**: 86400 seconds (24 hours, default)
- **Long-term**: 604800 seconds (7 days)

## 🧪 Testing

Run tests to verify caching functionality:

```bash
# Install test dependencies
pip install pytest pytest-redis

# Run tests
pytest tests/
```

## 🐛 Troubleshooting

### Redis Connection Issues

**Problem**: `Warning: Redis connection failed`

**Solutions**:
1. Verify Redis is running: `redis-cli ping` (should return `PONG`)
2. Check host/port configuration
3. Verify firewall settings allow Redis port (default 6379)
4. Check authentication credentials if Redis requires password

### Cache Not Working

**Problem**: Cache hit rate is 0% despite repeated parsing

**Solutions**:
1. Verify Redis connection: `cache.is_enabled()` should return `True`
2. Check TTL hasn't expired for your entries
3. Ensure content isn't being modified between parses (affects hash)
4. Verify Redis has sufficient memory: `redis-cli info memory`

### Performance Not Improving

**Problem**: Parsing still slow with cache enabled

**Solutions**:
1. Check cache statistics: `cache.get_stats()`
2. Ensure you're parsing identical content (hashing detects any changes)
3. Verify network latency to Redis server
4. Consider using local Redis for best performance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

[Your License Here]

## 📚 References

- [Rigveda Digital Library](https://example.com)
- [Sanskrit Text Processing](https://example.com)
- [Redis Documentation](https://redis.io/documentation)
- [Hugging Face Datasets](https://huggingface.co/docs/datasets)

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This project focuses on making ancient Sanskrit texts accessible for modern NLP and machine learning applications while respecting the cultural and historical significance of these texts.

