"""Mechanical risk veto: a pure function of (state, intent). Generated code cannot override it."""
from __future__ import annotations

from dataclasses import dataclass


class RiskVeto(Exception):
    pass


@dataclass(frozen=True)
class PortfolioState:
    gross_exposure: float
    net_exposure: float
    loss: float


@dataclass(frozen=True)
class OrderIntent:
    notional: float
    side: str   # buy | sell


@dataclass(frozen=True)
class RiskLimits:
    max_gross: float = 1.0
    max_net: float = 0.5
    max_loss: float = 0.1


def veto(state: PortfolioState, intent: OrderIntent, limits: RiskLimits = RiskLimits()) -> None:
    signed = intent.notional if intent.side == "buy" else -intent.notional
    next_gross = state.gross_exposure + abs(intent.notional)
    next_net = state.net_exposure + signed
    if next_gross > limits.max_gross + 1e-12:
        raise RiskVeto("gross_exposure")
    if abs(next_net) > limits.max_net + 1e-12:
        raise RiskVeto("net_exposure")
    if state.loss > limits.max_loss + 1e-12:
        raise RiskVeto("loss_limit")
