"""Scheduler: issues attempts, dispatches to the backend, commits outcomes, retries.

Single-process, manifest-driven. The scheduler is the SOLE writer to the attempt
ledger (capability SCHEDULER_CORE); workers only emit receipts via the backend.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

from .backends.local import CrashReport, LocalBackend
from .contracts import ResultReceipt, WorkOrder
from .fanout import ExpansionManifest
from .lifecycle import AttemptStore
from .retries import RetryPolicy
from .resources import PoolLimits


class Scheduler:
    def __init__(self, store: AttemptStore, backend: LocalBackend,
                 retry_policy: RetryPolicy = RetryPolicy(),
                 limits: PoolLimits | None = None):
        self.store = store
        self.backend = backend
        self.retry_policy = retry_policy
        self.limits = limits or backend.limits

    def work_order_from_row(self, work_order_json: str) -> WorkOrder:
        from .contracts import AuthorityClass, EgressClass, ResourceRequest
        raw = json.loads(work_order_json)
        return WorkOrder(
            campaign_id=raw["campaign_id"], task_type=raw["task_type"],
            dataset_snapshot_id=raw["dataset_snapshot_id"],
            code_commit=raw["code_commit"], seeds=tuple(raw["seeds"]),
            manifest_hash=raw["manifest_hash"],
            resource_request=ResourceRequest(**raw["resource_request"]),
            factor_hash=raw.get("factor_hash"), model_config_hash=raw.get("model_config_hash"),
            fold_id=raw.get("fold_id"), cost_policy_version=raw.get("cost_policy_version"),
            replay_id=raw.get("replay_id"),
            input_refs=tuple(tuple(p) for p in raw.get("input_refs", [])),
            authority_class=AuthorityClass(raw.get("authority_class", "research_worker")),
            egress_class=EgressClass(raw.get("egress_class", "none")),
        )

    def issue_manifest(self, manifest: ExpansionManifest) -> None:
        self.store.project_manifest(
            manifest.campaign_id, manifest.manifest_hash,
            json.dumps({"attempt_ids": list(manifest.expected_attempt_ids)}),
        )
        for wo in manifest.work_orders:
            self.store.issue(wo)   # invariant 1: rows exist BEFORE any compute

    def _run_one(self, wo: WorkOrder) -> None:
        from .contracts import TerminalStatus

        retries_used = 0
        retry_seq = self.store.next_retry_seq(wo.work_order_hash)
        self.store.issue(wo, retry_seq=retry_seq)
        while True:
            self.store.mark_queued(wo.work_order_hash, retry_seq)
            self.store.mark_running(wo.work_order_hash, retry_seq)
            outcome = self.backend.execute(wo, retry_seq=retry_seq)
            if isinstance(outcome, CrashReport):
                self.store.supervisor_crash(wo.work_order_hash, retry_seq,
                                            outcome.error_class)
                terminal_status = TerminalStatus.CRASHED
            else:
                self.store.commit_receipt(outcome)
                terminal_status = outcome.terminal_status
            if self.retry_policy.should_retry(terminal_status, retries_used):
                retries_used += 1
                retry_seq = self.store.next_retry_seq(wo.work_order_hash)
                self.store.issue(wo, retry_seq=retry_seq)
                if self.retry_policy.backoff_s:
                    time.sleep(self.retry_policy.backoff_s)
                continue
            break

    def run_campaign(self, manifest: ExpansionManifest, parallel: bool = True) -> None:
        self.issue_manifest(manifest)
        if parallel and self.limits.concurrency > 1:
            with ThreadPoolExecutor(max_workers=self.limits.concurrency) as pool:
                list(pool.map(self._run_one, manifest.work_orders))
        else:
            for wo in manifest.work_orders:
                self._run_one(wo)
