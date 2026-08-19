from finance_quant.baselines.cross_section import run_buy_and_hold
from finance_quant.baselines.walk_forward import returns_at_cutoff
from finance_quant.execution.costs import SCENARIOS, only_works_at_zero_fees
from finance_quant.pit.cost_labels import rank_ic_with_costs
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_buy_hold_cost_adjusted_ic_is_bounded():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    fold = run_buy_and_hold(store, SYMBOLS, days, cutoff)
    rets = returns_at_cutoff(store, SYMBOLS, days, cutoff)
    # Reconstruct a close-based signal from n_signals sanity; IC with costs stays in [-1, 1].
    signals = {s: float(i) for i, s in enumerate(SYMBOLS)}
    ic = rank_ic_with_costs(signals, rets, 1.0, SCENARIOS[1])
    assert -1.0 <= ic <= 1.0
    assert only_works_at_zero_fees(0.001, 2.0) is True
