"""V0 local backend: bounded subprocess workers (issue #10).

- one subprocess per attempt, fresh staging dir, sanitized env (capability by absence)
- bounded stdout/stderr capture (file-backed, size-capped on read)
- wall-timeout kill -> CrashReport; heartbeat staleness -> CrashReport
- no shared mutable state between workers: only the read-only repo and the
  worker's own staging dir are touched
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..authority import CapabilityClass, worker_environment
from ..contracts import ResultReceipt, WorkOrder
from ..lifecycle import work_order_to_json
from ..receipts import ContractError, parse_receipt
from ..resources import PoolLimits


@dataclass(frozen=True)
class CrashReport:
    work_order_hash: str
    retry_seq: int
    error_class: str        # timeout | heartbeat_lost | exit_nonzero | malformed_receipt | spawn_error
    detail: str = ""


class LocalBackend:
    """Bounded local-process executor. Deterministic, no services."""

    backend_id = "local"

    def __init__(self, limits: Optional[PoolLimits] = None,
                 capability: CapabilityClass = CapabilityClass.RESEARCH_WORKER,
                 repo_root: Optional[str] = None):
        self.limits = limits or PoolLimits.conservative()
        self.capability = capability
        self.repo_root = repo_root or str(Path(__file__).resolve().parents[3])

    def execute(self, order: WorkOrder, retry_seq: int = 0,
                ) -> ResultReceipt | CrashReport:
        resources = order.resource_request
        staging = Path(tempfile.mkdtemp(prefix=f"fq-{order.work_order_hash[:12]}-{retry_seq}-"))
        wo_file = staging / "work_order.json"
        out_file = staging / "receipt.json"
        wo_file.write_text(work_order_to_json(order))

        env = worker_environment(self.capability)
        env["PYTHONPATH"] = self.repo_root + ";" + env.get("PYTHONPATH", "")

        with open(staging / "stdout.log", "wb") as so, open(staging / "stderr.log", "wb") as se:
            try:
                proc = subprocess.Popen(
                    [sys.executable, "-m", "finance_quant.orchestration.worker_main",
                     str(wo_file), str(out_file), str(staging), str(retry_seq)],
                    cwd=staging, env=env, stdout=so, stderr=se,
                )
            except OSError as exc:
                return CrashReport(order.work_order_hash, retry_seq, "spawn_error", str(exc))

            exit_code = self._supervise(proc, resources.wall_timeout_s,
                                        staging / "heartbeat")

        if exit_code is None:      # killed by supervisor
            return CrashReport(order.work_order_hash, retry_seq,
                               self._crash_reason or "timeout")
        if exit_code != 0:
            detail = self._tail(staging / "stderr.log")
            return CrashReport(order.work_order_hash, retry_seq, "exit_nonzero", detail)
        if not out_file.exists():
            return CrashReport(order.work_order_hash, retry_seq, "malformed_receipt",
                               "worker exited 0 without writing a receipt")
        try:
            return parse_receipt(out_file.read_bytes())
        except ContractError as exc:
            return CrashReport(order.work_order_hash, retry_seq, "malformed_receipt", str(exc))

    _crash_reason: str = "timeout"

    def _supervise(self, proc: subprocess.Popen, timeout_s: float,
                   heartbeat: Path) -> Optional[int]:
        """Returns exit code, or None if the supervisor killed the worker."""
        deadline = time.monotonic() + timeout_s
        hb_deadline = time.monotonic() + max(2 * timeout_s, 5.0)  # heartbeat optional in V0
        while True:
            code = proc.poll()
            if code is not None:
                return code
            now = time.monotonic()
            if now > deadline:
                self._crash_reason = "timeout"
                self._kill_tree(proc)
                return None
            if heartbeat.exists():
                mtime = heartbeat.stat().st_mtime
                if time.time() - mtime > timeout_s:
                    self._crash_reason = "heartbeat_lost"
                    self._kill_tree(proc)
                    return None
            if now > hb_deadline:
                self._crash_reason = "heartbeat_lost"
                self._kill_tree(proc)
                return None
            time.sleep(min(0.05, max(0.01, timeout_s / 20)))

    def _kill_tree(self, proc: subprocess.Popen) -> None:
        try:
            proc.kill()  # V0: worker has no children of its own by contract
        except OSError:
            pass

    def _tail(self, path: Path) -> str:
        cap = self.limits.stdout_stderr_cap_bytes
        try:
            data = path.read_bytes()[-cap:]
        except OSError:
            return ""
        return data.decode("utf-8", errors="replace")
