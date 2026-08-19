from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_cannot_score_before_run():
    ladder = Ladder()
    ladder.seal("c1")
    with pytest.raises(ProtocolError):
        ladder.score()
