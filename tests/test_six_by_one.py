from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_six_by_one_product():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", tuple(f"k{i}" for i in range(6))), ("cost_policy_version", ("c0",)))),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 6
