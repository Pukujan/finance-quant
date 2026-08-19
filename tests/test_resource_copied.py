from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_resource_request_copied_onto_work_orders():
    rr = ResourceRequest(cpu=2, mem_mb=128, wall_timeout_s=15, heartbeat_s=1)
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        rr,
    )
    wo = expand_campaign(spec).work_orders[0]
    assert wo.resource_request == rr
