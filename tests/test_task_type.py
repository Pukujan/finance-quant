from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_work_order_task_type_matches_stage():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("feature_eval", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].task_type == "feature_eval"
