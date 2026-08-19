"""Subprocess entry point: python -m finance_quant.orchestration.worker_main WO_JSON OUT_JSON STAGING

Reads a WorkOrder, runs the handler, writes a ResultReceipt JSON. Exit code is
always 0 for handled outcomes; only true process crashes (or signals) yield nonzero,
which the supervisor maps to CRASHED.
"""
from __future__ import annotations

import dataclasses
import json
import sys
import threading
import time
from pathlib import Path


def _heartbeat(path: Path, interval_s: float, stop: threading.Event) -> None:
    while not stop.is_set():
        path.write_text(str(time.time()))
        stop.wait(interval_s)


def main() -> int:
    from .contracts import (AuthorityClass, EgressClass, ResourceRequest, WorkOrder)
    from .executor import run_work_order

    wo_path, out_path, staging = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    raw = json.loads(Path(wo_path).read_text())
    rr = raw["resource_request"]
    order = WorkOrder(
        campaign_id=raw["campaign_id"],
        task_type=raw["task_type"],
        dataset_snapshot_id=raw["dataset_snapshot_id"],
        code_commit=raw["code_commit"],
        seeds=tuple(raw["seeds"]),
        manifest_hash=raw["manifest_hash"],
        resource_request=ResourceRequest(**rr),
        factor_hash=raw.get("factor_hash"),
        model_config_hash=raw.get("model_config_hash"),
        fold_id=raw.get("fold_id"),
        cost_policy_version=raw.get("cost_policy_version"),
        replay_id=raw.get("replay_id"),
        input_refs=tuple(tuple(p) for p in raw.get("input_refs", [])),
        authority_class=AuthorityClass(raw.get("authority_class", "research_worker")),
        egress_class=EgressClass(raw.get("egress_class", "none")),
    )
    retry_seq = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    stop = threading.Event()
    hb = threading.Thread(target=_heartbeat,
                          args=(staging / "heartbeat", order.resource_request.heartbeat_s, stop),
                          daemon=True)
    hb.start()
    try:
        receipt = run_work_order(order, staging, worker_id=f"local-{Path(staging).name}",
                                 backend_id="local", retry_seq=retry_seq)
    finally:
        stop.set()
    Path(out_path).write_text(json.dumps(dataclasses.asdict(receipt), default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
