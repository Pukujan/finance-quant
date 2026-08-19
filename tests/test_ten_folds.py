from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_ten_folds_ten_attempts():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", tuple(f"k{i:02d}" for i in range(10))),)),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 10
