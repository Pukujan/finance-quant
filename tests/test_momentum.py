from finance_quant.baselines.momentum import momentum_expression, run_momentum
from finance_quant.dsl.checker import check
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b3_momentum_is_as_of_and_repeatable():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    first = run_momentum(store, SYMBOLS, days, days[-1])
    second = run_momentum(store, SYMBOLS, days, days[-1])
    assert first == second
    assert first.n_signals == 6
    assert check(momentum_expression()).max_lookahead_days == 0
