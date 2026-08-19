from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_cannot_run_from_idle():
    ladder = Ladder()
    with pytest.raises(ProtocolError):
        ladder.run()
