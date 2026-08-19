from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_baselines_emit_rank_ic_on_interior_cutoffs():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    b3 = run_momentum(store, SYMBOLS, days, cutoff)
    b4 = run_cross_section_rank(store, SYMBOLS, days, cutoff)
    b5 = run_buy_and_hold(store, SYMBOLS, days, cutoff)
    _, folds = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[-2]))
    assert all(isinstance(f.rank_ic, float) for f in folds)
    assert isinstance(b3.rank_ic, float)
    assert isinstance(b4.rank_ic, float)
    assert isinstance(b5.rank_ic, float)
