from finance_quant.orchestration.contracts import ResourceRequest, ResultReceipt, TerminalStatus, WorkOrder
from finance_quant.orchestration.lifecycle import AttemptStore, CommitOutcome


def _wo():
    return WorkOrder(
        campaign_id="c",
        task_type="t",
        dataset_snapshot_id="snap",
        code_commit="0" * 40,
        seeds=(1,),
        manifest_hash="m" * 64,
        resource_request=ResourceRequest(wall_timeout_s=5.0, heartbeat_s=1.0),
    )


def _receipt(wo):
    return ResultReceipt(
        work_order_hash=wo.work_order_hash,
        retry_seq=0,
        terminal_status=TerminalStatus.COMPLETED,
        worker_id="w1",
        backend_id="local",
        started_at=1.0,
        ended_at=2.0,
        environment_hash="e" * 64,
    )


def test_second_identical_receipt_after_terminal_is_invalid(tmp_path):
    store = AttemptStore(tmp_path / "ledger.db")
    wo = _wo()
    store.issue(wo)
    store.mark_queued(wo.work_order_hash)
    store.mark_running(wo.work_order_hash)
    r = _receipt(wo)
    assert store.commit_receipt(r) is CommitOutcome.COMMITTED
    assert store.commit_receipt(r) is CommitOutcome.INVALID
    assert len(store.duplicates()) == 0
    store.close()
