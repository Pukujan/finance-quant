from finance_quant.orchestration.fanin import PartialCampaign, deterministic_aggregate, status
from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, ResultReceipt, TerminalStatus, WorkOrder
import pytest

FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=10, heartbeat_s=1)


def test_deterministic_aggregate_raises_on_partial(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, FAST, fold_id="k")
    store.issue(wo)
    with pytest.raises(PartialCampaign):
        deterministic_aggregate(store, "m" * 64, (wo.work_order_hash,))
    st = status(store, "m" * 64, (wo.work_order_hash,))
    assert not st.complete
    store.close()
