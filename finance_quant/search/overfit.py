"""Garden-of-forking-paths probe: best-of-N random variants is not promotion evidence."""
from __future__ import annotations

from statistics import median


def search_artifact(scores: list[float], deflated_threshold: float = 0.05) -> bool:
    """True when the best score looks like a search artifact vs the median."""
    if len(scores) < 2:
        return False
    return (max(scores) - median(scores)) < deflated_threshold
