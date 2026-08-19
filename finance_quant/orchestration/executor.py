"""Worker-side task execution: handler registry + receipt emission.

Handlers are plain callables: (work_order, ctx) -> (metrics dict, artifacts dict).
They never see the store, the ledger, or promotion surfaces (capability by absence).
"""
from __future__ import annotations

import hashlib
import importlib
import os
import platform
import sys
import time
from pathlib import Path
from typing import Callable, Tuple

from .authority import assert_worker_capability
from .contracts import (Artifact, ResultReceipt, TerminalStatus, WorkOrder,
                        content_hash)

Handler = Callable[[WorkOrder], Tuple[dict, dict]]


def resolve_handler(task_type: str) -> Handler:
    """task_type names a dotted callable, e.g. 'finance_quant.tasks.echo:run'."""
    module_name, _, func = task_type.rpartition(":")
    if not module_name or not func:
        raise ValueError(f"task_type '{task_type}' is not 'module:callable'")
    module = importlib.import_module(module_name)
    handler = getattr(module, func)
    if not callable(handler):
        raise ValueError(f"handler '{task_type}' is not callable")
    return handler


def environment_hash() -> str:
    return content_hash({
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
    })


def run_work_order(work_order: WorkOrder, staging_dir: str | Path,
                   worker_id: str, backend_id: str,
                   retry_seq: int = 0) -> ResultReceipt:
    """Executes inside the worker process. Always returns a receipt object
    (the caller serializes it); crashes of the process itself are the
    supervisor's job (they become CRASHED via the ledger, not here)."""
    assert_worker_capability()  # hard gate: forbidden handles kill the worker
    staging = Path(staging_dir)
    artifact_dir = staging / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    status = TerminalStatus.COMPLETED
    error_class = None
    metrics: dict[str, float] = {}
    artifacts: dict[str, bytes] = {}
    try:
        handler = resolve_handler(work_order.task_type)
        metrics, artifacts = handler(work_order)
    except Exception as exc:  # worker-reported failure => FAILED receipt
        status = TerminalStatus.FAILED
        error_class = type(exc).__name__
    ended = time.time()

    manifest_entries = []
    for name, blob in sorted(artifacts.items()):
        payload = blob if isinstance(blob, bytes) else str(blob).encode("utf-8")
        path = artifact_dir / f"{content_hash(name)[:16]}_{os.getpid()}"
        path.write_bytes(payload)
        manifest_entries.append(Artifact(
            ref=str(path.relative_to(staging)),
            sha256=hashlib.sha256(payload).hexdigest(),
            bytes=len(payload),
        ))

    return ResultReceipt(
        work_order_hash=work_order.work_order_hash,
        retry_seq=retry_seq,
        terminal_status=status,
        worker_id=worker_id,
        backend_id=backend_id,
        started_at=started,
        ended_at=ended,
        environment_hash=environment_hash(),
        artifact_manifest=tuple(manifest_entries),
        metrics=tuple((k, float(v)) for k, v in metrics.items()),
        error_class=error_class,
    )
