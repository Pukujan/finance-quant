from pathlib import Path
import tempfile

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


def test_b2_folds_complete_through_local_scheduler(tmp_path):
    days = business_days(START, N_DAYS)
    gold = MemoryGoldStore()
    for row in generate():
        gold.put(row)
    _, folds = run_walk_forward(gold, SYMBOLS, days, (days[19], days[39], days[59]))
    store = AttemptStore(tmp_path / "attempts.db")
    spec = CampaignSpec(
        "B2", gold.snapshot_pin(), "0" * 40, (0,),
        (StageSpec("finance_quant.orchestration.handlers:run",
                   (("fold_id", tuple(f.fold_id for f in folds)),)),),
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
    )
    manifest = expand_campaign(spec)
    Scheduler(store, LocalBackend(), RetryPolicy(max_retries=0)).run_campaign(manifest, parallel=False)
    st = status(store, manifest.manifest_hash, manifest.expected_attempt_ids)
    store.close()
    assert st.complete
    assert st.terminal_count == 3
