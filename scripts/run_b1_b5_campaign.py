"""Run B1-B5 boring baselines through ExperimentLedger. No search, no promotion."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.walk_forward import run_walk_forward, sma3_expression
from finance_quant.dsl.ir import to_dict
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.orchestration.contracts import content_hash
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import SQLiteBitemporalStore


def main() -> int:
    days = business_days(START, N_DAYS)
    cutoff = days[-1]
    tmp = tempfile.mkdtemp(prefix="fq-b1b5-")
    pit = SQLiteBitemporalStore(Path(tmp) / "pit.db")
    for record in generate():
        pit.put(record)
    ledger = ExperimentLedger(Path(tmp) / "runs.db")
    manifest = pit.snapshot_pin()
    ir_hash, folds = run_walk_forward(pit, SYMBOLS, days, (days[19], days[39], days[59]))
    jobs = [
        ("B1-sma3", ir_hash, folds[-1]),
        ("B3-momentum", content_hash(to_dict(sma3_expression())), run_momentum(pit, SYMBOLS, days, cutoff)),
        ("B4-xs-rank", "xs-rank", run_cross_section_rank(pit, SYMBOLS, days, cutoff)),
        ("B5-buy-hold", "buy-hold", run_buy_and_hold(pit, SYMBOLS, days, cutoff)),
    ]
    recorded = []
    for experiment_id, model_hash, fold in jobs:
        spec = RunSpec(experiment_id, "0" * 40, "dev-unlocked", manifest,
                       ir_hash if experiment_id.startswith("B1") or experiment_id.startswith("B3") else model_hash,
                       model_hash, (0,), "fixture-cutoff-v0", "not-executed-v0")
        run = ledger.begin(spec)
        done = ledger.finalize(run.run_id, RunStatus.SUCCESS,
                               {"n_signals": float(fold.n_signals),
                                "mean_signal": fold.mean_signal,
                                "rank_ic": fold.rank_ic},
                               {"fold": fold.fold_id, "signal": fold.signal_hash})
        recorded.append({"experiment_id": experiment_id, "run_id": done.run_id,
                         "fold": fold.fold_id, "n_signals": fold.n_signals,
                         "rank_ic": fold.rank_ic})
    ledger.close()
    pit.close()
    print(json.dumps({"campaign": "B1-B5", "n_runs": len(recorded), "runs": recorded}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
