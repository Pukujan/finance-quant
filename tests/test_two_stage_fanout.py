from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_two_stage_expansion_is_the_sum_of_stage_products():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (
            StageSpec("feature_eval", (("fold_id", ("k1", "k2")),)),
            StageSpec("replay", (("replay_id", ("r1", "r2", "r3")),)),
        ),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.expected_attempt_ids) == 5
    types = {wo.task_type for wo in manifest.work_orders}
    assert types == {"feature_eval", "replay"}
