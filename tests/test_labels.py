from finance_quant.baselines.walk_forward import sma3_expression
from finance_quant.dsl.interpreter import evaluate
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.labels import next_day_returns, rank_ic
from finance_quant.pit.store import MemoryGoldStore


def test_next_day_return_is_only_defined_when_next_bar_is_known():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    early = next_day_returns(store, "AAA", days, days[10])
    full = next_day_returns(store, "AAA", days, days[-1])
    assert max(early) <= days[10]
    assert len(full) > len(early)
    assert all(d < days[-1] for d in full)


def test_rank_ic_is_zero_when_signals_constant():
    assert rank_ic({"A": 1.0, "B": 1.0}, {"A": 0.1, "B": -0.1}) == 0.0
    assert rank_ic({"A": 1.0, "B": 2.0}, {"A": 0.1, "B": 0.2}) > 0
