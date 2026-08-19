from finance_quant.orchestration.fanout import StageSpec
import pytest


def test_unknown_expansion_dimension_is_rejected():
    with pytest.raises(ValueError):
        StageSpec("t", (("not_a_dim", ("x",)),))
