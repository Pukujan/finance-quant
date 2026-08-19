from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_cannot_review_from_running():
    ladder = Ladder()
    ladder.seal("c1")
    ladder.run()
    with pytest.raises(ProtocolError):
        ladder.review()
