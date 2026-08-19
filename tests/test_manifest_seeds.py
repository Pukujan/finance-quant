from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_seeds_differ():
    kwargs = dict(
        campaign_id="c", dataset_snapshot_id="snap", code_commit="0" * 40,
        stages=(StageSpec("t", (("fold_id", ("k1",)),)),),
        resource_request=ResourceRequest(),
    )
    a = expand_campaign(CampaignSpec(seeds=(1,), **kwargs))
    b = expand_campaign(CampaignSpec(seeds=(2,), **kwargs))
    assert a.manifest_hash != b.manifest_hash
