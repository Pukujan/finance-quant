"""Run B2 across three folds through the native scheduler and ExperimentLedger."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import SQLiteBitemporalStore


def main() -> int:
    days = business_days(START, N_DAYS)
    cutoffs = (days[19], days[39], days[59])
    tmp = tempfile.mkdtemp(prefix="fq-b2-")
    try:
        pit = SQLiteBitemporalStore(Path(tmp) / "pit.db")
        for record in generate(): pit.put(record)
        ir_hash, folds = run_walk_forward(pit, SYMBOLS, days, cutoffs)
        ledger = ExperimentLedger(Path(tmp) / "runs.db")
        result = []
        for fold in folds:
            spec = RunSpec(f"B2-sma3-{fold.fold_id}", "0" * 40, "dev-unlocked",
                           pit.snapshot_pin(), ir_hash, "sma3-v0", (0,),
                           "walk-forward-v0", "not-executed-v0", parent_run_id=None)
            run = ledger.begin(spec)
            done = ledger.finalize(run.run_id, RunStatus.SUCCESS,
                                   {"n_signals": float(fold.n_signals),
                                    "mean_signal": fold.mean_signal},
                                   {"signal": fold.signal_hash, "fold": fold.fold_id})
            result.append({"fold": fold.__dict__, "run_id": done.run_id, "status": done.status.value})
        ledger.close(); pit.close()
    finally:
        # SQLite WAL sidecars can be unmapped lazily on Windows.
        shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"baseline": "B2-sma3-walk-forward", "ir_hash": ir_hash, "folds": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
