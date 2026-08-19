from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_attempt_ids_are_unique_across_two_stages():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (
            StageSpec("a", (("fold_id", ("k1", "k2")),)),
            StageSpec("b", (("fold_id", ("k1", "k2")),)),
        ),
        ResourceRequest(),
    )
    ids = expand_campaign(spec).expected_attempt_ids
    assert len(ids) == len(set(ids)) == 4
