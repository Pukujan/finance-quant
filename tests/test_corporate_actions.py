import pytest

from finance_quant.pit.corporate_actions import apply_split_if_total_return, split_ratio_as_of
from finance_quant.pit.model import BitemporalRecord


def test_raw_mode_preserves_price():
    assert apply_split_if_total_return(100.0, 2.0, "Raw") == 100.0


def test_split_adjusted_mode_divides_by_ratio():
    assert apply_split_if_total_return(100.0, 2.0, "SplitAdjusted") == 50.0


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unknown adjustment mode"):
        apply_split_if_total_return(100.0, 2.0, "TotalReturn")


def test_split_ratio_is_cumulative():
    actions = [
        BitemporalRecord("corporate_action", "CCC", "2024-02-01", "2024-02-01", {"kind": "split", "ratio": 2.0}, "x", 0),
        BitemporalRecord("corporate_action", "CCC", "2024-02-10", "2024-02-10", {"kind": "split", "ratio": 3.0}, "x", 0),
    ]
    assert split_ratio_as_of(actions, "CCC", "2024-02-15", "2024-02-15") == 6.0
    assert split_ratio_as_of(actions, "CCC", "2024-02-05", "2024-02-05") == 2.0
