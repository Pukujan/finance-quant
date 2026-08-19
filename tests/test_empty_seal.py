from finance_quant.acceptance.seal import merkle_root
import pytest


def test_empty_sealed_suite_is_rejected():
    with pytest.raises(ValueError):
        merkle_root([])
