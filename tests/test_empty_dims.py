from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_empty_dimension_values_yield_no_attempts():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ()),)),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert manifest.expected_attempt_ids == ()
