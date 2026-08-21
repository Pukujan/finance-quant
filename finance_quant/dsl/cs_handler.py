"""Bitemporal handler bridge for cross-sectional expressions."""
from __future__ import annotations

from typing import Sequence

from .checker import check
from .interpreter import evaluate_cross_section
from .ir import CrossSection, Expr
from ..pit.store import PITStore


def compile_cross_sectional(expr: Expr, store: PITStore, symbols: Sequence[str],
                            days: Sequence[str], cutoff: str) -> dict[str, float]:
    """Evaluate a cross-sectional expression using point-in-time histories."""
    if not isinstance(expr, CrossSection):
        raise ValueError("cross-sectional handler requires a CrossSection expression")
    check(expr)
    if not days:
        return {}
    rows = store.as_of("bar", symbols, days[0], cutoff, cutoff)
    histories = {symbol: [] for symbol in symbols}
    for row in rows:
        histories[row.instrument_id].append(row.payload)
    usable = {symbol: history for symbol, history in histories.items() if history}
    return evaluate_cross_section(expr, usable)
