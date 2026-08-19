from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest


def test_replay_id_copied():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("replay_id", ("lean-v0",)), ("fold_id", ("k1",)))),),
        ResourceRequest(),
    )
    assert expand_campaign(spec).work_orders[0].replay_id == "lean-v0"
