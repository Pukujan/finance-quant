from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_tiny_live_requires_paper_and_cannot_skip_review():
    ladder = Ladder()
    ladder.seal("c1")
    with pytest.raises(ProtocolError):
        ladder.tiny_live()
    ladder.run()
    ladder.score()
    ladder.review()
    ladder.paper_approve()
    ladder.tiny_live()
    assert ladder.state == "TINY_LIVE"
