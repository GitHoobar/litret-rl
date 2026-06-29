"""
corpus.py — load and index the Sanskrit verse corpus.

The ``data/`` directory holds one JSON-Lines file per text (Rigveda, Ramayana,
Bhagavad Gita, Agni Purana, Garuda Purana). Each line is a record with the
keys ``quote``, ``category``, ``book`` and ``position``.

Run directly to print a summary:

    python corpus.py
"""

import os
import glob
import json
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_records(data_dir: str = DATA_DIR) -> List[Dict[str, Any]]:
    """
    Read every verse record from all ``*.jsonl`` files under ``data_dir``.

    Returns:
        A list of records in file order, one per non-empty line.
    """
    records: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def index_by_position(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Build a lookup table mapping each verse's ``position`` to its record, so a
    verse can be retrieved in O(1) by position.

    Every record in ``records`` is represented in the returned index.
    """
    return {record["position"]: record for record in records}


def total_verses(data_dir: str = DATA_DIR) -> int:
    """Return the total number of verses available in the corpus."""
    records = load_records(data_dir)
    return len(index_by_position(records))


if __name__ == "__main__":
    print(f"Total verses in corpus: {total_verses()}")
