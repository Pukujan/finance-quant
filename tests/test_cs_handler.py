from finance_quant.baselines.cross_section import compute_cs_signal, rank_expression
from finance_quant.dsl.cs_handler import compile_cross_sectional
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_cross_section_handler_uses_pit_as_of_histories():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-1]

    signal = compile_cross_sectional(rank_expression(), store, SYMBOLS, days, cutoff)

    assert signal == compute_cs_signal(rank_expression(), store, SYMBOLS, days, cutoff)
    assert set(signal) == set(SYMBOLS)
    assert sorted(signal.values()) == [i / len(SYMBOLS) for i in range(1, len(SYMBOLS) + 1)]
