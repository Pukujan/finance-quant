from finance_quant.execution.scenarios import evaluate_cost_scenarios


def test_cost_scenarios_include_free_and_stress():
    result = evaluate_cost_scenarios(0.10, 1.0)
    assert "c-free" in result
    assert "c-stress2x" in result
    assert result["c-free"] > result["c-stress2x"]
