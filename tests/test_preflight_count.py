from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_expansion_count_is_known_before_execution():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2", "k3")), ("cost_policy_version", ("c0", "c1")))),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.expected_attempt_ids) == 6
    assert len(set(manifest.expected_attempt_ids)) == 6
