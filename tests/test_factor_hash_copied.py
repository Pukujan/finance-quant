from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_factor_hash_copied_when_present():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("factor_hash", ("abc",)), ("fold_id", ("k1",)))),),
        ResourceRequest(),
    )
    wo = expand_campaign(spec).work_orders[0]
    assert wo.factor_hash == "abc"
    assert wo.fold_id == "k1"
