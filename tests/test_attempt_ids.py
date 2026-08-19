from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_expected_attempt_ids_match_work_order_hashes():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2")),)),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert manifest.expected_attempt_ids == tuple(wo.work_order_hash for wo in manifest.work_orders)
