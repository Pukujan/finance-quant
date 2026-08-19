from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_duplicate_stage_task_types_still_expand():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (
            StageSpec("eval", (("fold_id", ("k1",)),)),
            StageSpec("eval", (("replay_id", ("r1", "r2")),)),
        ),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.expected_attempt_ids) == 3
    assert {wo.task_type for wo in manifest.work_orders} == {"eval"}
