"""End-to-end exit proof for spike #10's Exit criterion:

A B1/B2-style campaign (factor x fold x cost grid) fans out locally, one stage
has a deliberately crashing task, retries are exhausted deterministically, every
attempt lands in a terminal state, failures remain visible, and two independent
runs produce the identical aggregate fingerprint (completion-order independence).

Run: python scripts/demo_exit_campaign.py
Exit code 0 on success; any invariant breach raises.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.orchestration import fanin, fanout
from finance_quant.orchestration.backends.local import LocalBackend
from finance_quant.orchestration.contracts import ResourceRequest
from finance_quant.orchestration.lifecycle import AttemptState, AttemptStore
from finance_quant.orchestration.retries import RetryPolicy
from finance_quant.orchestration.scheduler import Scheduler

FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=30.0, heartbeat_s=0.5)


def run_once(db_path: Path) -> dict:
    store = AttemptStore(db_path)
    scheduler = Scheduler(store, LocalBackend(), RetryPolicy(max_retries=1))
    spec = fanout.CampaignSpec(
        campaign_id="exit-demo",
        dataset_snapshot_id="fixture-snap-v0",
        code_commit="0" * 40,
        seeds=(11, 12),
        stages=(
            fanout.StageSpec(
                task_type="finance_quant.orchestration.handlers:run",
                dimensions=(
                    ("factor_hash", ("f-sma-x", "f-mom-20")),
                    ("fold_id", ("k1", "k2", "k3")),
                    ("cost_policy_version", ("c-free", "c-stress2x")),
                ),
            ),
            fanout.StageSpec(
                task_type="finance_quant.orchestration.handlers:boom",
                dimensions=(("fold_id", ("k9-poison",)),),
            ),
        ),
        resource_request=FAST,
    )
    manifest = fanout.expand_campaign(spec)
    scheduler.run_campaign(manifest, parallel=True)

    st = fanin.status(store, manifest.manifest_hash, manifest.expected_attempt_ids)
    agg = fanin.deterministic_aggregate(
        store, manifest.manifest_hash, manifest.expected_attempt_ids)
    states = store.states(manifest.expected_attempt_ids)
    not_completed = sum(1 for s in states.values()
                        if s in (AttemptState.CRASHED, AttemptState.FAILED))
    result = {
        "manifest_hash": manifest.manifest_hash,
        "expected_attempts": st.total_expected,
        "terminal": st.terminal_count,
        "complete": st.complete,
        "failed_attempts_visible": not_completed,
        "authoritative_results": agg["n_authoritative"],
        "aggregate_fingerprint": agg["fingerprint"],
    }
    store.close()
    return result


def main() -> int:
    # Windows: WAL sidecar files unmap lazily; clean up best-effort afterwards.
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix="fq-exit-demo-"))
    try:
        first = run_once(tmp / "run1.db")
        second = run_once(tmp / "run2.db")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    assert first["complete"] and second["complete"], "campaign must reach full terminality"
    assert first["failed_attempts_visible"] == 1, "poison attempt must stay visible"
    assert first["authoritative_results"] == 12, "12 healthy work orders must aggregate"
    assert first["aggregate_fingerprint"] == second["aggregate_fingerprint"], \
        "completion order must not change the campaign fingerprint"
    print(json.dumps(first, indent=2))
    print("EXIT PROOF OK: failure preserved in lineage, fan-in deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
