"""Ledger-backed proposal batch: RANDOM and GP lanes, all trials visible.

Registers every proposal as an ExperimentLedger run (success or invalid),
never silently dropping failures. Lane authority is permanently propose-only.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import SQLiteBitemporalStore
from finance_quant.search.evaluator import evaluate_proposal
from finance_quant.search.gp_lane import evolve
from finance_quant.search.random_lane import propose
from finance_quant.lineage.pack import LocalEvidencePack
from finance_quant.lineage.runs import evidence_commit_for_run


def _histories(store, days):
    rows = store.as_of("bar", SYMBOLS, days[0], days[-1], days[-1])
    by_symbol = {s: [] for s in SYMBOLS}
    for row in rows:
        by_symbol[row.instrument_id].append(row.payload)
    return [h for h in by_symbol.values() if len(h) >= 3]


def main() -> int:
    days = business_days(START, N_DAYS)
    tmp = tempfile.mkdtemp(prefix="fq-search-")
    pit = SQLiteBitemporalStore(Path(tmp) / "pit.db")
    for record in generate():
        pit.put(record)
    histories = _histories(pit, days)
    ledger = ExperimentLedger(Path(tmp) / "runs.db")
    pack = LocalEvidencePack(Path(tmp) / "evidence")
    trials = []
    for proposal in propose(7, 8) + evolve(4, generations=2, population=4):
        ev = evaluate_proposal(proposal, histories)
        spec = RunSpec(
            experiment_id=f"{proposal.lane_id}-{ev.proposal_hash[:8]}",
            code_sha="0" * 40, env_lock_hash="dev-unlocked",
            dataset_manifest_hash=pit.snapshot_pin(),
            feature_ir_hash=ev.proposal_hash, model_config_hash="none",
            seeds=(proposal.seed,), split_policy_ref="fixture-single-cutoff-v0",
            cost_model_ref="not-executed-v0", agent_origin=proposal.lane_id,
        )
        run = ledger.begin(spec)
        if ev.valid:
            done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"score": ev.score or 0.0})
        else:
            done = ledger.finalize(run.run_id, RunStatus.INVALID, error_class=ev.violation_class)
        trials.append({
            "lane": proposal.lane_id, "run_id": done.run_id, "status": done.status.value,
            "valid": ev.valid, "score": ev.score, "violation": ev.violation_class,
        })
        pack.commit(evidence_commit_for_run(done, pit.snapshot_pin(), "SearchTrial"))
    ledger.close()
    pit.close()
    print(json.dumps({
        "n_trials": len(trials),
        "n_valid": sum(1 for t in trials if t["valid"]),
        "n_invalid": sum(1 for t in trials if not t["valid"]),
        "trials": trials,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
