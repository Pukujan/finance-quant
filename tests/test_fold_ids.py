from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_fold_ids_appear_on_work_orders():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k9", "k8")),)),),
        ResourceRequest(),
    )
    folds = {wo.fold_id for wo in expand_campaign(spec).work_orders}
    assert folds == {"k8", "k9"}
