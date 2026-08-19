"""Agent instruction text cannot widen risk limits. Veto is mechanical."""
from __future__ import annotations

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto


FORBIDDEN_PHRASES = (
    "ignore risk", "override limit", "disable veto", "increase max_gross",
)


def apply_intent_with_instructions(state: PortfolioState, intent: OrderIntent,
                                   instructions: str, limits: RiskLimits = RiskLimits()) -> None:
    lowered = instructions.lower()
    if any(p in lowered for p in FORBIDDEN_PHRASES):
        # Instructions attempting override are ignored; limits stay as-is.
        pass
    veto(state, intent, limits)
