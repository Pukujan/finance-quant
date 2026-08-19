import pytest

from finance_quant.acceptance.ladder import Ladder, ProtocolError


def test_ladder_happy_path():
    l = Ladder()
    l.seal("alpha")
    l.run()
    l.score()
    l.review()
    assert l.no_authority_before_review()
    l.paper_approve()
    assert l.authority["alpha"] == 1
    l.tiny_live()
    assert l.state == "TINY_LIVE"


def test_no_authority_before_review():
    l = Ladder()
    l.seal("alpha")
    l.run()
    l.score()
    assert l.no_authority_before_review()


def test_duplicate_authority_rejected():
    l = Ladder()
    l.seal("alpha")
    l.run(); l.score(); l.review(); l.paper_approve()
    l.reset()
    l.seal("alpha")
    l.run(); l.score(); l.review()
    with pytest.raises(ProtocolError, match="duplicate authority"):
        l.paper_approve()


def test_invalid_transition_run_from_idle():
    l = Ladder()
    with pytest.raises(ProtocolError):
        l.run()


def test_reset_returns_to_idle():
    l = Ladder()
    l.seal("alpha")
    l.run(); l.score(); l.review(); l.paper_approve()
    l.reset()
    assert l.state == "IDLE"
    assert l.current == ""
    l.seal("beta")
    assert l.state == "SEALED"
