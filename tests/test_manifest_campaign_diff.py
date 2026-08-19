from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_campaign_id_differs():
    kwargs = dict(
        dataset_snapshot_id="snap", code_commit="0" * 40, seeds=(1,),
        stages=(StageSpec("t", (("fold_id", ("k1",)),)),),
        resource_request=ResourceRequest(),
    )
    a = expand_campaign(CampaignSpec(campaign_id="a", **kwargs))
    b = expand_campaign(CampaignSpec(campaign_id="b", **kwargs))
    assert a.manifest_hash != b.manifest_hash
