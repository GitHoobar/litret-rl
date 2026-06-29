"""
Lightweight, dependency-free helpers for working with time windows.

This module intentionally has no third-party dependencies so it can be used
(and tested) in isolation from the Redis caching layer.
"""

from typing import List, Tuple


def chunk_ranges(total: int, size: int) -> List[Tuple[int, int]]:
    """
    Divide the half-open interval ``[0, total)`` into consecutive
    ``(start, end)`` windows of at most ``size`` units each.

    The windows tile the entire interval with no gaps or overlaps, so the
    ``end`` of the final window always equals ``total`` and the window lengths
    sum to ``total``.

    Args:
        total: Total length of the interval (must be >= 0).
        size: Maximum length of each window (must be positive).

    Returns:
        A list of ``(start, end)`` tuples covering ``[0, total)`` in order.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if total < 0:
        raise ValueError("total must be non-negative")

    windows = []
    num_windows = total // size
    for n in range(num_windows):
        start = n * size
        windows.append((start, start + size))
    return windows
