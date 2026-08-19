from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_fold_set_differs():
    def spec(folds: tuple[str, ...]) -> CampaignSpec:
        return CampaignSpec(
            "c", "snap", "0" * 40, (1,),
            (StageSpec("t", (("fold_id", folds),)),),
            ResourceRequest(),
        )
    assert expand_campaign(spec(("k1",))).manifest_hash != expand_campaign(spec(("k1", "k2"))).manifest_hash
