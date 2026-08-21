import pandas as pd
import pytest

from scripts.run_b1_b5_phase_b import rank_ic, strategy_signals


def test_rank_ic_is_one_for_perfect_cross_sectional_ordering():
    signals = pd.DataFrame([[1.0, 2.0, 3.0]], columns=["AAA", "BBB", "CCC"])
    returns = pd.DataFrame([[0.01, 0.02, 0.03]], columns=signals.columns)
    assert rank_ic(signals, returns) == 1.0


def test_signals_are_causal_and_have_expected_warmup():
    prices = pd.DataFrame(
        {"AAA": [10.0, 11.0, 12.0, 13.0], "BBB": [20.0, 19.0, 18.0, 17.0]},
        index=pd.date_range("2024-01-01", periods=4),
    )
    sma = strategy_signals("B1-sma3", prices)
    momentum = strategy_signals("B3-momentum", prices)
    assert sma.iloc[:2].isna().all().all()
    assert momentum.iloc[0].isna().all()
    assert sma.loc[sma.index[2], "AAA"] == 12 / 11 - 1
    assert momentum.loc[momentum.index[1], "AAA"] == pytest.approx(0.1)


def test_buy_and_hold_signal_does_not_change_over_time():
    prices = pd.DataFrame({"AAA": [10.0, 11.0], "BBB": [20.0, 18.0]})
    signals = strategy_signals("B5-buy-hold", prices)
    assert signals.iloc[0].to_dict() == signals.iloc[1].to_dict()
    assert signals.iloc[0].to_dict() == {"AAA": 10.0, "BBB": 20.0}
