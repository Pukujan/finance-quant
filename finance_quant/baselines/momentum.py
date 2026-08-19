"""B3: lagged close-to-close momentum, checker-approved, PIT as-of only."""
from __future__ import annotations

from typing import Sequence

from ..dsl.checker import check
from ..dsl.interpreter import evaluate
from ..dsl.ir import Binary, Field, Lag, to_dict
from ..orchestration.contracts import content_hash
from ..pit.store import PITStore
from .walk_forward import FoldResult, score_rank_ic


def momentum_expression() -> Binary:
    return Binary("sub", Field("close"), Lag(Field("close"), 1))


def run_momentum(store: PITStore, symbols: Sequence[str], days: Sequence[str],
                 cutoff: str) -> FoldResult:
    expr = momentum_expression()
    assert check(expr).max_lookahead_days == 0
    rows = store.as_of("bar", symbols, days[0], cutoff, cutoff)
    history = {s: [] for s in symbols}
    for row in rows:
        history[row.instrument_id].append(row.payload)
    signals = {s: evaluate(expr, h) for s, h in history.items() if len(h) >= 2}
    return FoldResult(
        fold_id="B3-momentum", cutoff=cutoff,
        signal_hash=content_hash(signals), n_signals=len(signals),
        mean_signal=sum(signals.values()) / len(signals) if signals else 0.0,
        rank_ic=score_rank_ic(store, symbols, days, cutoff, signals),
    )
