from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_code_commit_copied_to_every_work_order():
    spec = CampaignSpec(
        "c", "snap", "abc" * 10 + "ab", (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2")),)),),
        ResourceRequest(),
    )
    assert all(wo.code_commit == spec.code_commit for wo in expand_campaign(spec).work_orders)
