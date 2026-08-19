from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_lean_replay_stage_is_a_first_class_task_type():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("lean_replay", (("replay_id", ("raw-v0", "splitadj-v0")), ("fold_id", ("k1",)))),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.expected_attempt_ids) == 2
    assert all(wo.task_type == "lean_replay" for wo in manifest.work_orders)
