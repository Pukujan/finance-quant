"""Deterministic B2 walk-forward baseline over the canonical PIT fixture.

This is deliberately a boring signal: 3-day moving average, evaluated in three
chronological folds. It tests the full research truth chain, not alpha quality.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..dsl.checker import check
from ..dsl.interpreter import evaluate
from ..dsl.ir import Field, Rolling, to_dict
from ..orchestration.contracts import content_hash
from ..pit.labels import next_day_returns, rank_ic
from ..pit.store import PITStore


@dataclass(frozen=True)
class FoldResult:
    fold_id: str
    cutoff: str
    signal_hash: str
    n_signals: int
    mean_signal: float
    rank_ic: float = 0.0


def sma3_expression() -> Rolling:
    return Rolling("mean", Field("close"), 3)


def run_walk_forward(store: PITStore, symbols: Sequence[str], days: Sequence[str],
                     fold_cutoffs: Sequence[str]) -> tuple[str, list[FoldResult]]:
    """Build each fold strictly AS OF its own cutoff, so later fixture rows cannot leak."""
    expr = sma3_expression()
    cert = check(expr)
    assert cert.max_lookahead_days == 0
    outputs = []
    for fold_no, cutoff in enumerate(fold_cutoffs, 1):
        rows = store.as_of("bar", symbols, days[0], cutoff, cutoff)
        history = {s: [] for s in symbols}
        for row in rows:
            history[row.instrument_id].append(row.payload)
        signals = {s: evaluate(expr, h) for s, h in history.items() if len(h) >= 3}
        outputs.append(FoldResult(
            fold_id=f"B2-F{fold_no}", cutoff=cutoff,
            signal_hash=content_hash(signals), n_signals=len(signals),
            mean_signal=sum(signals.values()) / len(signals),
            rank_ic=score_rank_ic(store, symbols, days, cutoff, signals),
        ))
    return content_hash(to_dict(expr)), outputs


def score_rank_ic(store: PITStore, symbols: Sequence[str], days: Sequence[str],
                  cutoff: str, signals: dict[str, float]) -> float:
    """Score as-of-cutoff signals against next-day returns knowable only after cutoff."""
    try:
        i = list(days).index(cutoff)
    except ValueError:
        return 0.0
    if i + 1 >= len(days):
        return 0.0
    label_kt = days[i + 1]
    rets = {}
    for s in symbols:
        series = next_day_returns(store, s, days, label_kt)
        if cutoff in series:
            rets[s] = series[cutoff]
    return rank_ic(signals, rets)
