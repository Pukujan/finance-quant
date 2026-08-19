from finance_quant.pit.fixtures import generate


def test_fixture_bar_count_is_symbols_times_days():
    from finance_quant.pit.fixtures import N_DAYS, SYMBOLS
    bars = [r for r in generate() if r.namespace == "bar"]
    assert len(bars) == len(SYMBOLS) * N_DAYS
