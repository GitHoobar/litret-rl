"""
Stable short identifiers for verses.

``verse_id`` derives a compact, deterministic 8-character hex identifier for a
piece of text from its SHA-256 digest. The same text always maps to the same
id, which makes the ids convenient as cache keys or de-duplication handles.
"""

import hashlib


def verse_id(text: str) -> str:
    """
    Return an 8-character hexadecimal identifier for ``text``.

    The id is taken from the SHA-256 hex digest of the UTF-8 encoded text, so
    it is stable across runs and processes.

    Args:
        text: The verse (or any string) to identify.

    Returns:
        An 8-character lowercase hex string.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[-8:]
