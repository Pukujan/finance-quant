from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_two_by_two_by_two_product():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (
            ("fold_id", ("k1", "k2")),
            ("factor_hash", ("f1", "f2")),
            ("model_config_hash", ("m1", "m2")),
        )),),
        ResourceRequest(),
    )
    assert len(expand_campaign(spec).expected_attempt_ids) == 8
