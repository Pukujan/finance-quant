from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_empty_stages_yield_no_attempts():
    spec = CampaignSpec("c", "snap", "0" * 40, (1,), (), ResourceRequest())
    assert expand_campaign(spec).expected_attempt_ids == ()
