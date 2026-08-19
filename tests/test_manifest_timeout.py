from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_resource_timeout_differs():
    def spec(timeout: float) -> CampaignSpec:
        return CampaignSpec(
            "c", "snap", "0" * 40, (1,),
            (StageSpec("t", (("fold_id", ("k1",)),)),),
            ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=timeout, heartbeat_s=1),
        )
    assert expand_campaign(spec(10)).manifest_hash != expand_campaign(spec(20)).manifest_hash
