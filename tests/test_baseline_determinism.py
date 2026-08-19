from finance_quant.baselines.walk_forward import run_walk_forward
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.cross_section import run_buy_and_hold, run_cross_section_rank
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b1_b5_baselines_are_deterministic_on_fixture():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-1]
    a = (
        run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[59])),
        run_momentum(store, SYMBOLS, days, cutoff),
        run_cross_section_rank(store, SYMBOLS, days, cutoff),
        run_buy_and_hold(store, SYMBOLS, days, cutoff),
    )
    b = (
        run_walk_forward(store, SYMBOLS, days, (days[19], days[39], days[59])),
        run_momentum(store, SYMBOLS, days, cutoff),
        run_cross_section_rank(store, SYMBOLS, days, cutoff),
        run_buy_and_hold(store, SYMBOLS, days, cutoff),
    )
    assert a == b
