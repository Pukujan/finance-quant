from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_manifest_hash_differs_when_task_type_differs():
    def spec(task: str) -> CampaignSpec:
        return CampaignSpec(
            "c", "snap", "0" * 40, (1,),
            (StageSpec(task, (("fold_id", ("k1",)),)),),
            ResourceRequest(),
        )
    assert expand_campaign(spec("a")).manifest_hash != expand_campaign(spec("b")).manifest_hash
