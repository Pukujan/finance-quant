from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.labels import next_day_returns
from finance_quant.pit.store import MemoryGoldStore
from finance_quant.search.evaluator import rank_ic_for_proposal
from finance_quant.search.gp_lane import evolve
from finance_quant.search.random_lane import propose
import statistics


def test_random_and_gp_median_rank_ic_are_defined_on_fixture():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    rows = store.as_of("bar", SYMBOLS, days[0], cutoff, cutoff)
    hist = {s: [] for s in SYMBOLS}
    for row in rows:
        hist[row.instrument_id].append(row.payload)
    hist = {s: h for s, h in hist.items() if len(h) >= 3}
    rets = {}
    for s in SYMBOLS:
        series = next_day_returns(store, s, days, days[-1])
        if cutoff in series:
            rets[s] = series[cutoff]
    r_ics = [rank_ic_for_proposal(p, hist, rets).score for p in propose(7, 8)]
    g_ics = [rank_ic_for_proposal(p, hist, rets).score for p in evolve(4, 1, 4)]
    r_ics = [x for x in r_ics if x is not None]
    g_ics = [x for x in g_ics if x is not None]
    assert r_ics and g_ics
    assert all(-1 <= x <= 1 for x in r_ics + g_ics)
    statistics.median(r_ics)
    statistics.median(g_ics)
