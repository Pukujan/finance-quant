from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_work_order_count_matches_expected_ids():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2", "k3")), ("cost_policy_version", ("c0",)))),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.work_orders) == len(manifest.expected_attempt_ids) == 3
