"""A2 Autonomous Trader v0 finance-quant-owned account/session primitives."""

from .account import AccountInvariantError, VirtualAccountStore
from .authority import AuthorityError, PromotionReceipt, assert_unattended_paper_authorized
from .risk import RiskDecision, gate_order_intent
from .session import SessionJournal, SessionReceipt, SessionReceiptError, build_session_receipt

__all__ = [
    "AccountInvariantError",
    "AuthorityError",
    "PromotionReceipt",
    "RiskDecision",
    "SessionJournal",
    "SessionReceipt",
    "SessionReceiptError",
    "VirtualAccountStore",
    "assert_unattended_paper_authorized",
    "build_session_receipt",
    "gate_order_intent",
]
