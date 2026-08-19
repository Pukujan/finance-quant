from finance_quant.dsl.ir import Field
from finance_quant.search.evaluator import rank_ic_for_proposal
from finance_quant.search.random_lane import Proposal


def test_proposal_rank_ic_is_defined_and_bounded():
    proposal = Proposal("test", 1, Field("close"), "p")
    histories = {
        "AAA": [{"close": 1.0}, {"close": 1.1}, {"close": 1.2}],
        "BBB": [{"close": 2.0}, {"close": 1.9}, {"close": 1.8}],
    }
    rets = {"AAA": 0.1, "BBB": -0.1}
    ev = rank_ic_for_proposal(proposal, histories, rets)
    assert ev.valid
    assert ev.score is not None
    assert -1.0 <= ev.score <= 1.0
