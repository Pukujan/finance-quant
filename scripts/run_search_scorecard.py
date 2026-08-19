"""RANDOM vs GP bake-off scorecard. Proposal-only: no promotion, no risk mutation."""
from __future__ import annotations

import json
import statistics
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.labels import next_day_returns
from finance_quant.pit.store import MemoryGoldStore
from finance_quant.search.deflate import benjamini_hochberg, spearman_p_approx
from finance_quant.search.evaluator import evaluate_proposal, rank_ic_for_proposal
from finance_quant.search.gp_lane import evolve
from finance_quant.search.overfit import search_artifact
from finance_quant.search.random_lane import propose


def _histories(store, days):
    rows = store.as_of("bar", SYMBOLS, days[0], days[-1], days[-1])
    by_symbol = {s: [] for s in SYMBOLS}
    for row in rows:
        by_symbol[row.instrument_id].append(row.payload)
    return [h for h in by_symbol.values() if len(h) >= 3]


def _histories_by_symbol(store, days, cutoff):
    rows = store.as_of("bar", SYMBOLS, days[0], cutoff, cutoff)
    by_symbol = {s: [] for s in SYMBOLS}
    for row in rows:
        by_symbol[row.instrument_id].append(row.payload)
    return {s: h for s, h in by_symbol.items() if len(h) >= 3}


def _returns_at_cutoff(store, days, cutoff):
    i = days.index(cutoff)
    label_kt = days[i + 1]
    out = {}
    for s in SYMBOLS:
        series = next_day_returns(store, s, days, label_kt)
        if cutoff in series:
            out[s] = series[cutoff]
    return out


def _lane_report(name, proposals, histories, histories_by_symbol, returns_by_symbol):
    evals = [evaluate_proposal(p, histories) for p in proposals]
    ics = [rank_ic_for_proposal(p, histories_by_symbol, returns_by_symbol) for p in proposals]
    valid_scores = [e.score for e in evals if e.valid and e.score is not None]
    valid_ics = [e.score for e in ics if e.valid and e.score is not None]
    return {
        "lane": name,
        "n": len(evals),
        "n_valid": len(valid_scores),
        "n_invalid": sum(1 for e in evals if not e.valid),
        "median_score": statistics.median(valid_scores) if valid_scores else None,
        "best_score": max(valid_scores) if valid_scores else None,
        "median_rank_ic": statistics.median(valid_ics) if valid_ics else None,
        "best_rank_ic": max(valid_ics) if valid_ics else None,
        "search_artifact": search_artifact(valid_ics) if len(valid_ics) > 1 else False,
        "authority": "propose_only",
        "valid_ics": valid_ics,
        "n_cross_section": len(returns_by_symbol),
    }


def main() -> int:
    days = business_days(START, N_DAYS)
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    histories = _histories(store, days)
    cutoff = days[-2]
    by_symbol = _histories_by_symbol(store, days, cutoff)
    rets = _returns_at_cutoff(store, days, cutoff)
    random_report = _lane_report("random-v0", propose(7, 16), histories, by_symbol, rets)
    gp_report = _lane_report("gp-v0", evolve(4, generations=2, population=8), histories, by_symbol, rets)
    all_ics = random_report.pop("valid_ics") + gp_report.pop("valid_ics")
    n_xs = random_report.pop("n_cross_section")
    gp_report.pop("n_cross_section")
    pvals = [spearman_p_approx(abs(ic), n_xs) for ic in all_ics]
    discoveries = sum(benjamini_hochberg(pvals, alpha=0.05))
    print(json.dumps({
        "arena": "canonical PIT fixture",
        "cutoff": cutoff,
        "n_cross_section": n_xs,
        "bh_alpha": 0.05,
        "bh_discoveries_across_all_lanes": discoveries,
        "lanes": [random_report, gp_report],
        "rule": "neither lane may promote; RANDOM is the disgrace floor; BH is over ALL trials of ALL lanes",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
