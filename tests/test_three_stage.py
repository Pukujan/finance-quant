from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_three_stage_expansion_is_sum_of_products():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (
            StageSpec("a", (("fold_id", ("k1", "k2")),)),
            StageSpec("b", (("replay_id", ("r1",)),)),
            StageSpec("c", (("cost_policy_version", ("c0", "c1", "c2")),)),
        ),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 6
