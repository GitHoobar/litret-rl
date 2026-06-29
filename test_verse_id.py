"""
Tests for verse_id.

Golden ids were generated once from the reference SHA-256 implementation and
pinned here so regressions in the id derivation are caught immediately.

Run with: pytest test_verse_id.py
"""

from verse_id import verse_id


# Pinned, known-good ids for representative verses.
GOLDEN = {
    "agnim ile purohitam": "9a59cf0c",
    "dharma kshetre kuru kshetre": "f88574de",
    "tat tvam asi": "b3e6ae4e",
    "satyam eva jayate": "35c2060e",
}


def test_known_ids():
    """Each sample verse must hash to its pinned golden id."""
    for text, expected in GOLDEN.items():
        assert verse_id(text) == expected


def test_id_is_eight_hex_chars():
    """Ids are always 8 lowercase hex characters."""
    vid = verse_id("om")
    assert len(vid) == 8
    assert all(c in "0123456789abcdef" for c in vid)


def test_is_deterministic():
    """The same text always yields the same id."""
    assert verse_id("tat tvam asi") == verse_id("tat tvam asi")
