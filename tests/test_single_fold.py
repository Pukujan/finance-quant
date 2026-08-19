from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_single_fold_one_attempt():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 1
