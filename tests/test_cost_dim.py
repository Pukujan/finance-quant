from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_cost_policy_dimension_multiplies_attempts():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2")), ("cost_policy_version", ("c-free", "c-stress2x")))),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 4
