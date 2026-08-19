from finance_quant.dsl.ir import Field
from finance_quant.search.evaluator import evaluate_proposal
from finance_quant.search.random_lane import Proposal


def test_evaluator_keeps_invalid_proposals_visible():
    proposal = Proposal("test", 1, Field("close"), "p")
    result = evaluate_proposal(proposal, [[{"close": 1.0}]])
    assert result.valid and result.score == 1.0
    assert result.trial_hash
