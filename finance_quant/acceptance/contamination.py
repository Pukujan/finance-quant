"""Holdout contamination sentinel: suspiciously perfect sealed-vs-unsealed delta is invalid."""
from __future__ import annotations


def contamination_flag(unsealed_score: float, sealed_score: float, threshold: float = 0.5) -> bool:
    """True if sealed performance is implausibly better than unsealed (honey-case)."""
    return (sealed_score - unsealed_score) > threshold
