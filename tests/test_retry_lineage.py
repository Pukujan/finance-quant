from finance_quant.orchestration.contracts import ResourceRequest, ResultReceipt, TerminalStatus, WorkOrder
from finance_quant.orchestration.lifecycle import AttemptStore, CommitOutcome


FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=10, heartbeat_s=1)


def test_failed_then_retry_lineage_is_visible(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, FAST, fold_id="k")
    store.issue(wo, 0)
    store.mark_queued(wo.work_order_hash, 0)
    store.mark_running(wo.work_order_hash, 0)
    store.supervisor_crash(wo.work_order_hash, 0, "timeout")
    store.issue(wo, 1)
    store.mark_queued(wo.work_order_hash, 1)
    store.mark_running(wo.work_order_hash, 1)
    receipt = ResultReceipt(wo.work_order_hash, 1, TerminalStatus.COMPLETED, "w", "local", 1.0, 2.0, "e")
    assert store.commit_receipt(receipt) is CommitOutcome.COMMITTED
    assert store.next_retry_seq(wo.work_order_hash) == 2
    store.close()
