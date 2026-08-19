"""B1 boring baseline: 3-day moving-average signal on the canonical PIT fixture.

This is deliberately not an alpha claim. It proves the first research path uses:
PIT `as_of`, a checker-approved IR artifact, a reproducibility-complete RunSpec,
and an append-only ExperimentLedger record.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.dsl.checker import check
from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling, to_dict
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.orchestration.contracts import content_hash
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import SQLiteBitemporalStore


def main() -> int:
    expression = Rolling("mean", Field("close"), 3)
    certificate = check(expression)
    days = business_days(START, N_DAYS)
    with tempfile.TemporaryDirectory(prefix="fq-b1-") as tmp:
        pit = SQLiteBitemporalStore(Path(tmp) / "pit.db")
        for record in generate(): pit.put(record)
        manifest = pit.snapshot_pin()
        cutoff = days[-1]
        rows = pit.as_of("bar", SYMBOLS, days[0], cutoff, cutoff)
        by_symbol = {s: [] for s in SYMBOLS}
        for row in rows: by_symbol[row.instrument_id].append(row.payload)
        signals = {s: evaluate(expression, h) for s, h in by_symbol.items() if len(h) >= 3}

        ledger = ExperimentLedger(Path(tmp) / "runs.db")
        spec = RunSpec(
            experiment_id="B1-sma3", code_sha="0" * 40, env_lock_hash="dev-unlocked",
            dataset_manifest_hash=manifest,
            feature_ir_hash=content_hash(to_dict(expression)),
            model_config_hash=content_hash({"baseline": "sma3"}), seeds=(0,),
            split_policy_ref="fixture-single-cutoff-v0", cost_model_ref="not-executed-v0",
        )
        run = ledger.begin(spec)
        done = ledger.finalize(run.run_id, RunStatus.SUCCESS,
                               {"n_signals": float(len(signals)), "mean_signal": sum(signals.values()) / len(signals)},
                               {"signals": content_hash(signals)})
        report = {"run_id": done.run_id, "status": done.status.value,
                  "manifest": manifest, "effect": certificate.__dict__, "signals": signals,
                  "metrics": dict(done.metrics)}
        ledger.close(); pit.close()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
