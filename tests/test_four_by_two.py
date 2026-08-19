from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_four_by_two_product():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("a", "b", "c", "d")), ("cost_policy_version", ("x", "y")))),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 8
