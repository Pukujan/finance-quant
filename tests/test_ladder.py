from finance_quant.acceptance.ladder import Ladder, ProtocolError
import pytest


def test_ladder_cannot_grant_authority_before_review():
    ladder = Ladder()
    ladder.seal("c1")
    ladder.run()
    ladder.score()
    assert ladder.no_authority_before_review()
    with pytest.raises(ProtocolError):
        ladder.paper_approve()
    ladder.review()
    ladder.paper_approve()
    assert ladder.authority["c1"] == 1
    with pytest.raises(ProtocolError):
        ladder.paper_approve()
