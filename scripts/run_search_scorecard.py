"""RANDOM vs GP bake-off scorecard. Proposal-only: no promotion, no risk mutation."""
from __future__ import annotations

import json
import statistics
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore
from finance_quant.search.evaluator import evaluate_proposal
from finance_quant.search.gp_lane import evolve
from finance_quant.search.overfit import search_artifact
from finance_quant.search.random_lane import propose


def _histories(store, days):
    rows = store.as_of("bar", SYMBOLS, days[0], days[-1], days[-1])
    by_symbol = {s: [] for s in SYMBOLS}
    for row in rows:
        by_symbol[row.instrument_id].append(row.payload)
    return [h for h in by_symbol.values() if len(h) >= 3]


def _lane_report(name, proposals, histories):
    evals = [evaluate_proposal(p, histories) for p in proposals]
    valid_scores = [e.score for e in evals if e.valid and e.score is not None]
    return {
        "lane": name,
        "n": len(evals),
        "n_valid": len(valid_scores),
        "n_invalid": sum(1 for e in evals if not e.valid),
        "median_score": statistics.median(valid_scores) if valid_scores else None,
        "best_score": max(valid_scores) if valid_scores else None,
        "search_artifact": search_artifact(valid_scores) if len(valid_scores) > 1 else False,
        "authority": "propose_only",
    }


def main() -> int:
    days = business_days(START, N_DAYS)
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    histories = _histories(store, days)
    random_report = _lane_report("random-v0", propose(7, 16), histories)
    gp_report = _lane_report("gp-v0", evolve(4, generations=2, population=8), histories)
    print(json.dumps({
        "arena": "canonical PIT fixture",
        "lanes": [random_report, gp_report],
        "rule": "neither lane may promote; RANDOM is the disgrace floor",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
