"""A2 non-widening adapter around the existing mechanical risk veto."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto

from .strategy import PortfolioIntent


@dataclass(frozen=True)
class RiskDecision:
    status: str
    requested_notional: float
    approved_notional: float
    reason: str | None


@dataclass(frozen=True)
class GatedIntent:
    decision: RiskDecision
    approved_intent: PortfolioIntent | None
    risk_hash: str


def _hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def gate_order_intent(
    state: PortfolioState,
    intent: OrderIntent,
    limits: RiskLimits = RiskLimits(),
) -> RiskDecision:
    if intent.side not in {"buy", "sell"}:
        raise ValueError("side must be buy or sell")
    if intent.notional < 0:
        raise ValueError("notional must be non-negative")
    try:
        veto(state, intent, limits)
    except RiskVeto as exc:
        return RiskDecision(
            status="REJECTED",
            requested_notional=float(intent.notional),
            approved_notional=0.0,
            reason=str(exc),
        )
    return RiskDecision(
        status="APPROVED",
        requested_notional=float(intent.notional),
        approved_notional=float(intent.notional),
        reason=None,
    )


def gate_portfolio_intent(
    state: PortfolioState,
    intent: PortfolioIntent,
    limits: RiskLimits = RiskLimits(),
) -> GatedIntent:
    try:
        requested = float(intent.risk_notional)
    except ValueError as exc:
        raise ValueError("risk_notional must be numeric") from exc
    decision = gate_order_intent(
        state,
        OrderIntent(notional=requested, side=intent.side.lower()),
        limits,
    )
    approved = intent if decision.status == "APPROVED" else None
    risk_hash = _hash(
        {
            "state": asdict(state),
            "limits": asdict(limits),
            "intent": asdict(intent),
            "decision": asdict(decision),
        }
    )
    return GatedIntent(decision=decision, approved_intent=approved, risk_hash=risk_hash)
