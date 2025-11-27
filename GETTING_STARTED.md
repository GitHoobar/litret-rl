# 🚀 Getting Started with Redis Caching

## Quick 3-Step Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Redis
Choose your preferred method:

**Option A - Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B - Local Installation**
```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis
```

### Step 3: Run Parsing with Cache
```bash
python parsing_scripts/rigveda.py
```

You should see:
```
✓ Redis caching enabled

📊 Parsing Statistics:
  Total verses processed: 1028
  Parsed from source: 1028
  Retrieved from cache: 0

🚀 Cache Performance:
  Hit rate: 0.00%
  Total hits: 0
  Total misses: 1028
```

## See the Performance Improvement

Run the same command again:
```bash
python parsing_scripts/rigveda.py
```

Now you'll see:
```
✓ Redis caching enabled

📊 Parsing Statistics:
  Total verses processed: 1028
  Parsed from source: 0
  Retrieved from cache: 1028

🚀 Cache Performance:
  Hit rate: 50.00%
  Total hits: 1028
  Total misses: 1028
```

**🎉 That's it! Your parsing is now 10-100x faster on subsequent runs!**

## Try More Examples

### Run Interactive Examples
```bash
python example_cache_usage.py
```

### Run Performance Benchmarks
```bash
python benchmark_cache.py
```

### Run Tests
```bash
pytest test_redis_cache.py -v
```

## Parse All Texts

```bash
python parsing_scripts/rigveda.py
python parsing_scripts/bhagwvadgita.py
python parsing_scripts/ramayana.py
python parsing_scripts/agnipurana.py
python parsing_scripts/garudapurana.py
```

## Need Help?

- 📖 See [README.md](README.md) for full documentation
- ⚡ See [QUICKSTART.md](QUICKSTART.md) for detailed setup
- 🏗️ See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- 📋 See [CHANGELOG.md](CHANGELOG.md) for version history
- 📝 See [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) for what's new

## Common Issues

### "Redis connection failed"
→ Make sure Redis is running: `redis-cli ping`

### "No module named 'redis'"
→ Install dependencies: `pip install -r requirements.txt`

### Cache not working
→ Check Redis is accessible: `redis-cli ping` should return `PONG`

---

**Happy parsing with blazing fast performance! 🚀**

