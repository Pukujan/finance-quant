from finance_quant.baselines.cross_section import rank_expression, run_buy_and_hold, run_cross_section_rank
from finance_quant.dsl.checker import check
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b4_and_b5_are_repeatable_and_as_of():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-1]
    assert run_cross_section_rank(store, SYMBOLS, days, cutoff) == run_cross_section_rank(store, SYMBOLS, days, cutoff)
    assert run_buy_and_hold(store, SYMBOLS, days, cutoff) == run_buy_and_hold(store, SYMBOLS, days, cutoff)
    assert check(rank_expression()).requires_universe == "FIXIDX"
    assert run_buy_and_hold(store, SYMBOLS, days, cutoff).n_signals == 6
