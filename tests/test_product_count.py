from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_factor_model_fold_product_count():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (
            ("factor_hash", ("f1", "f2")),
            ("model_config_hash", ("m1",)),
            ("fold_id", ("k1", "k2", "k3")),
        )),),
        ResourceRequest(),
    )
    manifest = expand_campaign(spec)
    assert len(manifest.expected_attempt_ids) == 6
