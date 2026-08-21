"""Two-stage campaign: feature_eval then lean_replay. Deterministic, local backend."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Two-stage campaign: feature_eval then lean_replay. Deterministic, local backend."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _build_parser().parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from finance_quant.orchestration.backends.local import LocalBackend
    from finance_quant.orchestration.contracts import ResourceRequest
    from finance_quant.orchestration.fanin import status
    from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
    from finance_quant.orchestration.lifecycle import AttemptStore
    from finance_quant.orchestration.retries import RetryPolicy
    from finance_quant.orchestration.scheduler import Scheduler

    tmp = tempfile.mkdtemp(prefix="fq-two-stage-")
    store = AttemptStore(Path(tmp) / "attempts.db")
    spec = CampaignSpec(
        campaign_id="two-stage",
        dataset_snapshot_id="snap",
        code_commit="0" * 40,
        seeds=(7,),
        stages=(
            StageSpec("finance_quant.orchestration.handlers:feature_eval",
                      (("fold_id", ("k1", "k2")),)),
            StageSpec("finance_quant.orchestration.handlers:lean_replay",
                      (("replay_id", ("raw-v0",)), ("fold_id", ("k1",)))),
        ),
        resource_request=ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
    )
    manifest = expand_campaign(spec)
    Scheduler(store, LocalBackend(), RetryPolicy(max_retries=0)).run_campaign(manifest, parallel=False)
    st = status(store, manifest.manifest_hash, manifest.expected_attempt_ids)
    store.close()
    print(json.dumps({
        "expected": st.total_expected,
        "terminal": st.terminal_count,
        "complete": st.complete,
        "task_types": sorted({wo.task_type.split(":")[-1] for wo in manifest.work_orders}),
    }, indent=2))
    return 0 if st.complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
