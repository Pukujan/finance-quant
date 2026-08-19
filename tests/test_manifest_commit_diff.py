from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_code_commit_differs():
    def spec(commit: str) -> CampaignSpec:
        return CampaignSpec(
            "c", "snap", commit, (1,),
            (StageSpec("t", (("fold_id", ("k1",)),)),),
            ResourceRequest(),
        )
    assert expand_campaign(spec("a" * 40)).manifest_hash != expand_campaign(spec("b" * 40)).manifest_hash
