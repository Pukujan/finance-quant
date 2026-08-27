"""A2 non-widening adapter around the existing mechanical risk veto."""
from __future__ import annotations

from dataclasses import dataclass

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto


@dataclass(frozen=True)
class RiskDecision:
    status: str
    requested_notional: float
    approved_notional: float
    reason: str | None


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
