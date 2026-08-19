from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b4_rank_and_b5_buy_hold_share_rank_ic_when_signal_is_close():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    b4 = run_cross_section_rank(store, SYMBOLS, days, cutoff)
    b5 = run_buy_and_hold(store, SYMBOLS, days, cutoff)
    assert b4.rank_ic == b5.rank_ic
