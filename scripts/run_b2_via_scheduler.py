"""Run B2 folds as native WorkOrders through the local scheduler."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.orchestration.backends.local import LocalBackend
from finance_quant.orchestration.contracts import ResourceRequest
from finance_quant.orchestration.fanin import status
from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.retries import RetryPolicy
from finance_quant.orchestration.scheduler import Scheduler
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def main() -> int:
    days = business_days(START, N_DAYS)
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    ir_hash, folds = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[59]))
    tmp = tempfile.mkdtemp(prefix="fq-b2-sched-")
    attempts = AttemptStore(Path(tmp) / "attempts.db")
    spec = CampaignSpec(
        campaign_id="B2-walk-forward",
        dataset_snapshot_id=store.snapshot_pin(),
        code_commit="0" * 40,
        seeds=(0,),
        stages=(StageSpec(
            task_type="finance_quant.orchestration.handlers:run",
            dimensions=(("fold_id", tuple(f.fold_id for f in folds)),),
        ),),
        resource_request=ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20.0, heartbeat_s=0.5),
    )
    manifest = expand_campaign(spec)
    Scheduler(attempts, LocalBackend(), RetryPolicy(max_retries=0)).run_campaign(manifest, parallel=False)
    st = status(attempts, manifest.manifest_hash, manifest.expected_attempt_ids)
    attempts.close()
    print(json.dumps({
        "ir_hash": ir_hash,
        "folds": [f.fold_id for f in folds],
        "complete": st.complete,
        "terminal": st.terminal_count,
        "expected": st.total_expected,
    }, indent=2))
    return 0 if st.complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
