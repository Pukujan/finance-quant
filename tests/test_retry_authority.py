from finance_quant.orchestration.contracts import TerminalStatus, WorkOrder, ResourceRequest
from finance_quant.orchestration.lifecycle import AttemptStore, CommitOutcome
from finance_quant.orchestration.contracts import ResultReceipt


FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=30.0, heartbeat_s=0.5)


def _wo() -> WorkOrder:
    return WorkOrder(
        campaign_id="retry", task_type="finance_quant.orchestration.handlers:run",
        dataset_snapshot_id="snap", code_commit="0" * 40, seeds=(1,),
        manifest_hash="m" * 64, resource_request=FAST, fold_id="k1",
    )


def _receipt(wo: WorkOrder, retry_seq: int, acc: float) -> ResultReceipt:
    return ResultReceipt(
        work_order_hash=wo.work_order_hash, retry_seq=retry_seq,
        terminal_status=TerminalStatus.COMPLETED, worker_id="w", backend_id="local",
        started_at=1.0, ended_at=2.0, environment_hash="e", metrics=(("acc", acc),),
    )


def test_retry_cannot_fork_authoritative_result(tmp_path):
    store = AttemptStore(tmp_path / "attempts.db")
    wo = _wo()
    store.issue(wo, 0)
    store.mark_queued(wo.work_order_hash, 0)
    store.mark_running(wo.work_order_hash, 0)
    assert store.commit_receipt(_receipt(wo, 0, 1.0)) is CommitOutcome.COMMITTED
    store.issue(wo, 1)
    store.mark_queued(wo.work_order_hash, 1)
    store.mark_running(wo.work_order_hash, 1)
    assert store.commit_receipt(_receipt(wo, 1, 99.0)) is CommitOutcome.DUPLICATE
    rows = store.authoritative_receipts([wo.work_order_hash])
    assert len(rows) == 1
    assert "99.0" not in rows[0]
    store.close()
