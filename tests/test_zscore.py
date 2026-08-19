from finance_quant.dsl.interpreter import evaluate_cross_section
from finance_quant.dsl.ir import CrossSection, Field


def test_zscore_mean_is_zero_on_symmetric_inputs():
    expr = CrossSection("zscore", Field("close"), "FIXIDX")
    ranks = evaluate_cross_section(expr, {
        "AAA": [{"close": 1.0}],
        "BBB": [{"close": 3.0}],
    })
    mean = sum(ranks.values()) / len(ranks)
    assert abs(mean) < 1e-9
