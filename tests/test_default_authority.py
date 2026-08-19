from finance_quant.orchestration.fanout import CampaignSpec, StageSpec, expand_campaign
from finance_quant.orchestration.contracts import ResourceRequest, AuthorityClass


def test_default_authority_class_is_research_worker():
    spec = CampaignSpec(
        "c", "snap", "0" * 40, (1,),
        (StageSpec("t", (("fold_id", ("k1",)),)),),
        ResourceRequest(),
    )
    wo = expand_campaign(spec).work_orders[0]
    assert wo.authority_class is AuthorityClass.RESEARCH_WORKER
