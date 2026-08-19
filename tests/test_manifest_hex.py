from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_is_64_hex():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    h = expand_campaign(spec).manifest_hash
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
