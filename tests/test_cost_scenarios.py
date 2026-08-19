from finance_quant.execution.scenarios import evaluate_cost_scenarios


def test_cost_scenarios_are_named_and_stress_is_worse():
    out = evaluate_cost_scenarios(0.1, 1.0)
    assert set(out) == {"c-free", "c-stress2x"}
    assert out["c-free"] > out["c-stress2x"]
