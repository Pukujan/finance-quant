from finance_quant.baselines.momentum import run_momentum
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_last_bar_has_no_next_day_label_so_rank_ic_is_zero():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    fold = run_momentum(store, SYMBOLS, days, days[-1])
    assert fold.rank_ic == 0.0
