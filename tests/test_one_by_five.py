from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_one_by_n_product():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)), ("replay_id", ("r1", "r2", "r3", "r4", "r5")))),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 5
