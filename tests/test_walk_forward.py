from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_walk_forward_is_chronological_and_repeatable():
    store = MemoryGoldStore()
    for row in generate(): store.put(row)
    days = business_days(START, N_DAYS)
    first = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[59]))
    second = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[59]))
    assert first == second
    _, folds = first
    assert [f.n_signals for f in folds] == [6, 6, 6]
    assert [f.cutoff for f in folds] == [days[19], days[39], days[59]]
