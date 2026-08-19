from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_campaign_id_copied_onto_work_orders():
    spec = CampaignSpec(
        "camp-9", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].campaign_id == "camp-9"
