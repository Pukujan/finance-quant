from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_seeds_are_copied_onto_every_work_order():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (11, 22),
        (StageSpec("t", (("fold_id", ("k1", "k2")),)),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert all(wo.seeds == (11, 22) for wo in manifest.work_orders)
