from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_cannot_paper_approve_after_reject():
    ladder = Ladder()
    ladder.seal("c1")
    ladder.run()
    ladder.score()
    ladder.reject()
    with pytest.raises(ProtocolError):
        ladder.paper_approve()
