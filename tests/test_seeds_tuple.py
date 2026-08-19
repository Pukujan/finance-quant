from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_work_order_seeds_tuple_preserved():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (3, 5, 7),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].seeds == (3, 5, 7)
