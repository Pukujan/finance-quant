from pathlib import Path
import tempfile

from finance_quant.orchestration.backends.local import LocalBackend
from finance_quant.orchestration.contracts import ResourceRequest
from finance_quant.orchestration.fanin import status
from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.retries import RetryPolicy
from finance_quant.orchestration.scheduler import Scheduler


def test_two_stage_feature_eval_and_lean_replay_completes(tmp_path):
    store = AttemptStore(tmp_path / "attempts.db")
    spec = CampaignSpec(
        "two", "snap", "0" * 40, (7,),
        (
            StageSpec("finance_quant.orchestration.handlers:feature_eval",
                      (("fold_id", ("k1",)),)),
            StageSpec("finance_quant.orchestration.handlers:lean_replay",
                      (("replay_id", ("raw-v0",)), ("fold_id", ("k1",)))),
        ),
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
    )
    manifest = expand_campaign(spec)
    Scheduler(store, LocalBackend(), RetryPolicy(max_retries=0)).run_campaign(manifest, parallel=False)
    st = status(store, manifest.manifest_hash, manifest.expected_attempt_ids)
    store.close()
    assert st.complete
    assert st.terminal_count == 2
