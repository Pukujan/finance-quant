"""B4/B5 boring baselines: cross-sectional rank and buy-and-hold."""
from __future__ import annotations

from typing import Sequence

from ..dsl.checker import check
from ..dsl.cs_handler import compile_cross_sectional
from ..dsl.ir import CrossSection, Field
from ..orchestration.contracts import content_hash
from ..pit.store import PITStore
from .walk_forward import FoldResult, score_rank_ic


def rank_expression() -> CrossSection:
    return CrossSection("rank", Field("close"), "FIXIDX")


def compute_cs_signal(expr: CrossSection, store: PITStore, symbols: Sequence[str],
                      days: Sequence[str], cutoff: str) -> dict[str, float]:
    return compile_cross_sectional(expr, store, symbols, days, cutoff)


def run_cross_section_rank(store: PITStore, symbols: Sequence[str], days: Sequence[str],
                           cutoff: str) -> FoldResult:
    expr = rank_expression()
    assert check(expr).max_lookahead_days == 0
    ranks = compute_cs_signal(expr, store, symbols, days, cutoff)
    return FoldResult(
        fold_id="B4-xs-rank", cutoff=cutoff,
        signal_hash=content_hash(ranks), n_signals=len(ranks),
        mean_signal=sum(ranks.values()) / len(ranks) if ranks else 0.0,
        rank_ic=score_rank_ic(store, symbols, days, cutoff, ranks),
    )


def run_buy_and_hold(store: PITStore, symbols: Sequence[str], days: Sequence[str],
                     cutoff: str) -> FoldResult:
    rows = store.as_of("bar", symbols, cutoff, cutoff, cutoff)
    closes = {row.instrument_id: float(row.payload["close"]) for row in rows}
    return FoldResult(
        fold_id="B5-buy-hold", cutoff=cutoff,
        signal_hash=content_hash(closes), n_signals=len(closes),
        mean_signal=sum(closes.values()) / len(closes) if closes else 0.0,
        rank_ic=score_rank_ic(store, symbols, days, cutoff, closes),
    )
