from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_dataset_snapshot_id_copied_to_work_orders():
    spec = CampaignSpec(
        "c", "snap-xyz", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    wo = expand_campaign(spec).work_orders[0]
    assert wo.dataset_snapshot_id == "snap-xyz"
    assert wo.code_commit == "0" * 40
