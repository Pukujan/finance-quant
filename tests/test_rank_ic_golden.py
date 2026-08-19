from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b1_b5_rank_ic_golden_receipt_is_stable():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    _, folds = run_walk_forward(store, SYMBOLS, days, (days[19], days[39], cutoff))
    b3 = run_momentum(store, SYMBOLS, days, cutoff)
    b4 = run_cross_section_rank(store, SYMBOLS, days, cutoff)
    b5 = run_buy_and_hold(store, SYMBOLS, days, cutoff)
    assert [round(f.rank_ic, 6) for f in folds] == [-0.142857, 0.428571, 0.314286]
    assert round(b3.rank_ic, 6) == -0.714286
    assert round(b4.rank_ic, 6) == 0.314286
    assert round(b5.rank_ic, 6) == 0.314286
