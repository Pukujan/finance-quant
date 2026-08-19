from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_nine_folds_nine_attempts():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", tuple(f"k{i}" for i in range(9))),)),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 9
