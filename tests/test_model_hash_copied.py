from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_model_config_hash_copied():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("model_config_hash", ("lgbm-v0",)), ("fold_id", ("k1",)))),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].model_config_hash == "lgbm-v0"
