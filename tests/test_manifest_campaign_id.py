from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_campaign_id_on_manifest():
    spec = CampaignSpec(
        "hello", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).campaign_id == "hello"
