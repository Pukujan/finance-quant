from __future__ import annotations

from copy import deepcopy

import pytest

from finance_quant.risk.veto import PortfolioState, RiskLimits
from finance_quant.trader.risk import gate_portfolio_intent
from finance_quant.trader.strategy import (
    BaselineStrategyConfig,
    StrategyInvariantError,
    generate_baseline_decision,
)


def _events():
    return [
        {
            "event_id": "bar-1",
            "instrument_id": "AAA",
            "event_time": "2026-01-01T00:00:00Z",
            "known_at": "2026-01-01T00:00:00Z",
            "sequence": 1,
            "payload": {"open": "9", "close": "10", "liquidity": "10"},
        },
        {
            "event_id": "bar-2",
            "instrument_id": "AAA",
            "event_time": "2026-01-02T00:00:00Z",
            "known_at": "2026-01-02T00:00:00Z",
            "sequence": 2,
            "payload": {"open": "10", "close": "11", "liquidity": "10"},
        },
    ]


def _decision(events=None):
    return generate_baseline_decision(
        _events() if events is None else events,
        session_id="session-1",
        instrument_id="AAA",
        decision_time="2026-01-02T00:00:00Z",
        config=BaselineStrategyConfig(quantity="2", risk_notional="0.1"),
    )


def test_fq_prop_030_future_or_late_known_events_cannot_change_prior_decision():
    baseline = _decision()
    assert baseline.status == "INTENT"
    assert baseline.intent is not None
    assert baseline.intent.side == "BUY"
    assert baseline.intent.quantity == "2"
    assert baseline.source_event_ids == ("bar-1", "bar-2")

    future = _events() + [
        {
            "event_id": "bar-3",
            "instrument_id": "AAA",
            "event_time": "2026-01-03T00:00:00Z",
            "known_at": "2026-01-03T00:00:00Z",
            "sequence": 3,
            "payload": {"open": "11", "close": "1", "liquidity": "10"},
        }
    ]
    assert _decision(future) == baseline

    late_known = _events() + [
        {
            "event_id": "late-bar",
            "instrument_id": "AAA",
            "event_time": "2026-01-01T12:00:00Z",
            "known_at": "2026-01-04T00:00:00Z",
            "sequence": 4,
            "payload": {"open": "10", "close": "100", "liquidity": "10"},
        }
    ]
    assert _decision(late_known) == baseline


def test_strategy_is_order_independent_and_exact_duplicates_are_idempotent():
    baseline = _decision()
    reversed_events = list(reversed(_events()))
    assert _decision(reversed_events) == baseline
    duplicated = _events() + [deepcopy(_events()[0])]
    assert _decision(duplicated) == baseline


def test_conflicting_duplicate_event_identity_fails_closed():
    events = _events()
    conflicting = deepcopy(events[0])
    conflicting["payload"]["close"] = "99"
    events.append(conflicting)
    with pytest.raises(StrategyInvariantError, match="ambiguous duplicate"):
        _decision(events)


def test_flat_or_insufficient_history_produces_no_intent():
    one = _decision(_events()[:1])
    assert one.status == "NO_INTENT"
    assert one.intent is None
    flat_events = _events()
    flat_events[1]["payload"]["close"] = "10"
    flat = _decision(flat_events)
    assert flat.status == "NO_INTENT"
    assert flat.intent is None


def test_risk_gate_binds_strategy_intent_and_never_changes_it():
    decision = _decision()
    assert decision.intent is not None
    state = PortfolioState(gross_exposure=0.0, net_exposure=0.0, loss=0.0)
    limits = RiskLimits(max_gross=1.0, max_net=0.5, max_loss=0.1)
    first = gate_portfolio_intent(state, decision.intent, limits)
    second = gate_portfolio_intent(state, decision.intent, limits)
    assert first == second
    assert first.decision.status == "APPROVED"
    assert first.approved_intent == decision.intent
    assert len(first.risk_hash) == 64

    blocked = gate_portfolio_intent(
        PortfolioState(gross_exposure=1.0, net_exposure=0.0, loss=0.0),
        decision.intent,
        limits,
    )
    assert blocked.decision.status == "REJECTED"
    assert blocked.decision.approved_notional == 0.0
    assert blocked.approved_intent is None
