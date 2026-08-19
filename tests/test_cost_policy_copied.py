from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_cost_policy_copied():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("cost_policy_version", ("c-stress2x",)), ("fold_id", ("k1",)))),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].cost_policy_version == "c-stress2x"
