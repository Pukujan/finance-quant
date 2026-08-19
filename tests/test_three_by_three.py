from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_three_by_three_product():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("a", "b", "c")), ("factor_hash", ("f1", "f2", "f3")))),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 9
