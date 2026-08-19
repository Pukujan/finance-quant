from finance_quant.orchestration.fanout import expand_campaign, CampaignSpec, StageSpec
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_stable_across_calls():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k2")),)),),
        ResourceRequest(),
    )
    a, b = expand_campaign(spec), expand_campaign(spec)
    assert a.manifest_hash == b.manifest_hash
    assert a.expected_attempt_ids == b.expected_attempt_ids
