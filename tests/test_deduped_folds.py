from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_unique_attempt_ids_even_with_two_identical_looking_folds_after_dedupe():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1", "k1")),)),),
        ResourceRequest(),
    )
    ids = expand_campaign(spec).expected_attempt_ids
    assert len(ids) == 1
    assert len(set(ids)) == 1
