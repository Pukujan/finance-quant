from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_walk_forward_mean_rank_ic_is_the_mean_of_interior_folds():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    _, folds = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[-2]))
    mean = sum(f.rank_ic for f in folds) / len(folds)
    assert all(isinstance(f.rank_ic, float) for f in folds)
    assert abs(mean - sum(f.rank_ic for f in folds) / 3) < 1e-12
