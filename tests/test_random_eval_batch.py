from finance_quant.search.evaluator import evaluate_proposal
from finance_quant.search.random_lane import propose


def test_random_lane_proposals_evaluate_or_are_marked_invalid():
    histories = [[{"close": 1.0, "volume": 10.0, "open": 1.0, "high": 1.1, "low": 0.9}] * 12]
    results = [evaluate_proposal(p, histories) for p in propose(9, 12)]
    assert results
    assert all(r.trial_hash for r in results)
    assert all(r.valid or r.violation_class for r in results)
