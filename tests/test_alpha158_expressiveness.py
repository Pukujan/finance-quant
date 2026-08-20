from scripts.alpha158_expressiveness import MAJOR_FAMILY_EXAMPLES, report
from finance_quant.dsl.checker import check


def test_alpha158_tier_one_coverage_meets_issue_three_gate():
    coverage = report()
    assert coverage["total_count"] == 158
    assert coverage["percentage"] >= 70


def test_major_alpha_families_are_tier_one_expressible():
    assert all(check(expr).max_lookahead_days == 0 for expr in MAJOR_FAMILY_EXAMPLES.values())
