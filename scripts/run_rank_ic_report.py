"""Report walk-forward rank IC for B1-B5 on the canonical fixture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def main() -> int:
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    _, folds = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], cutoff))
    b3 = run_momentum(store, SYMBOLS, days, cutoff)
    b4 = run_cross_section_rank(store, SYMBOLS, days, cutoff)
    b5 = run_buy_and_hold(store, SYMBOLS, days, cutoff)
    print(json.dumps({
        "cutoff": cutoff,
        "B2_folds": [{"fold": f.fold_id, "rank_ic": f.rank_ic} for f in folds],
        "B2_mean_rank_ic": sum(f.rank_ic for f in folds) / len(folds),
        "B3_rank_ic": b3.rank_ic,
        "B4_rank_ic": b4.rank_ic,
        "B5_rank_ic": b5.rank_ic,
        "note": "labels are next-day returns knowable only after cutoff; not promotion evidence",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
