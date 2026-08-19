"""Demo/test task handlers. Deterministic, seeded, no external state."""
from __future__ import annotations

import os
import time
from typing import Tuple

from .contracts import WorkOrder


def run(work_order: WorkOrder) -> Tuple[dict, dict]:
    return {"attempt": float(work_order.seeds[0]) * 0.0 + 1.0}, {}


def sleep(work_order: WorkOrder) -> Tuple[dict, dict]:
    params = dict(work_order.input_refs)
    seconds = float(params.get("sleep_s", "5"))
    time.sleep(seconds)
    return {"slept": seconds}, {}


def boom(work_order: WorkOrder) -> Tuple[dict, dict]:
    raise RuntimeError("intentional test failure")


def env_probe(work_order: WorkOrder) -> Tuple[dict, dict]:
    """Reports which forbidden handles are visible; used by authority tests."""
    forbidden = [v for v in ("FQ_EXPERIMENT_LEDGER_URI", "FQ_PROMOTION_API",
                             "FQ_SEALED_STORE", "MLFLOW_TRACKING_URI",
                             "FQ_ATTEMPT_LEDGER_PATH") if v in os.environ]
    return {"forbidden_visible": float(len(forbidden))}, {"visible": ",".join(sorted(forbidden))}
