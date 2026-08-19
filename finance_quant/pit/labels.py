"""PIT-safe next-day return labels and rank IC.

The label for bar t is close[t+1]/close[t] - 1. It is only knowable at kt >= t+1,
so scoring a signal computed as-of t against that label is a walk-forward check,
not a leakage path: the signal never sees the label at compute time.
"""
from __future__ import annotations

import math
from typing import Sequence

from .store import PITStore


def next_day_returns(store: PITStore, symbol: str, days: Sequence[str], kt_bound: str) -> dict[str, float]:
    rows = store.as_of("bar", [symbol], days[0], days[-1], kt_bound)
    by_vt = {r.vt: float(r.payload["close"]) for r in rows}
    out = {}
    for i, d in enumerate(days[:-1]):
        nxt = days[i + 1]
        if d in by_vt and nxt in by_vt and by_vt[d] != 0:
            out[d] = by_vt[nxt] / by_vt[d] - 1.0
    return out


def rank_ic(signal_by_symbol: dict[str, float], ret_by_symbol: dict[str, float]) -> float:
    keys = sorted(set(signal_by_symbol) & set(ret_by_symbol))
    if len(keys) < 2:
        return 0.0
    sx = [signal_by_symbol[k] for k in keys]
    if max(sx) == min(sx):
        return 0.0
    sy = [ret_by_symbol[k] for k in keys]
    n = len(keys)
    rx = _ranks(sx)
    ry = _ranks(sy)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / n
    vx = sum((a - mx) ** 2 for a in rx) / n
    vy = sum((b - my) ** 2 for b in ry) / n
    if vx == 0 or vy == 0:
        return 0.0
    return cov / math.sqrt(vx * vy)


def _ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: (xs[i], i))
    ranks = [0.0] * len(xs)
    for r, i in enumerate(order, 1):
        ranks[i] = float(r)
    return ranks
