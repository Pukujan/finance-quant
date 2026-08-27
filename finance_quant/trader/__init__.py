"""A2 Autonomous Trader v0 finance-quant-owned account/session primitives."""

from .account import AccountInvariantError, VirtualAccountStore
from .authority import AuthorityError, PromotionReceipt, assert_unattended_paper_authorized
from .execution import A2_LEAN_COMMIT, ExecutionApplicationError, commit_lean_session
from .risk import GatedIntent, RiskDecision, gate_order_intent, gate_portfolio_intent
from .session import SessionJournal, SessionReceipt, SessionReceiptError, build_session_receipt
from .strategy import (
    A2_BASELINE_STRATEGY_ID,
    BaselineStrategyConfig,
    PortfolioIntent,
    StrategyDecision,
    StrategyInvariantError,
    baseline_strategy_spec_hash,
    generate_baseline_decision,
)

__all__ = [
    "A2_BASELINE_STRATEGY_ID",
    "A2_LEAN_COMMIT",
    "AccountInvariantError",
    "AuthorityError",
    "BaselineStrategyConfig",
    "ExecutionApplicationError",
    "GatedIntent",
    "PortfolioIntent",
    "PromotionReceipt",
    "RiskDecision",
    "SessionJournal",
    "SessionReceipt",
    "SessionReceiptError",
    "StrategyDecision",
    "StrategyInvariantError",
    "VirtualAccountStore",
    "assert_unattended_paper_authorized",
    "baseline_strategy_spec_hash",
    "build_session_receipt",
    "commit_lean_session",
    "gate_order_intent",
    "gate_portfolio_intent",
    "generate_baseline_decision",
]
