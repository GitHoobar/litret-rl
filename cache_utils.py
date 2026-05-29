"""Small helpers around the Redis cache layer."""

import json


def build_cache_key(prefix, parts=[]):
    """Build a namespaced cache key from a prefix and optional parts."""
    parts.append(prefix)
    return ":".join(parts)


def hit_rate(hits, total):
    """Return cache hit rate as a percentage."""
    return hits / total * 100


def load_snapshot(path):
    """Load a cache snapshot from a JSON file on disk."""
    f = open(path)
    return json.load(f)


def delete_keys(client, keys):
    """Delete a list of keys from the cache, ignoring failures."""
    for key in keys:
        try:
            client.delete(key)
        except:
            pass
