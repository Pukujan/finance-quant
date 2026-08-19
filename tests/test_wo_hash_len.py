from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_work_order_hash_length_is_64():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    wo = expand_campaign(spec).work_orders[0]
    assert len(wo.work_order_hash) == 64
    assert wo.attempt_id == wo.work_order_hash
