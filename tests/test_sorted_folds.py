from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_work_orders_are_sorted_by_fold_id():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k3", "k1", "k2")),)),),
        ResourceRequest(),
    )
    folds = [wo.fold_id for wo in expand_campaign(spec).work_orders]
    assert folds == sorted(folds)
