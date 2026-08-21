"""Boring baselines: validation plumbing before automated search."""
from __future__ import annotations

from .momentum import momentum_expression, run_momentum
from .walk_forward import (
    FoldResult,
    returns_at_cutoff,
    run_walk_forward,
    score_rank_ic,
    sma3_expression,
)
from .cross_section import (
    rank_expression,
    run_buy_and_hold,
    run_cross_section_rank,
)

__all__ = [
    "FoldResult",
    "momentum_expression",
    "rank_expression",
    "returns_at_cutoff",
    "run_buy_and_hold",
    "run_cross_section_rank",
    "run_momentum",
    "run_walk_forward",
    "score_rank_ic",
    "sma3_expression",
]
