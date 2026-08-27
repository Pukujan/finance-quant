# A2 Autonomous Trader v0 — SDD/PDD

Issue: #16  
Assurance phase: A2  
Property impact: **STRENGTHEN** A1 execution/PIT invariants; add durable account, strategy, session, replay, and authority invariants.

## Scope

A2 builds the first deliberately boring local paper-trading vertical slice:

`PIT/replay input -> deterministic baseline strategy -> portfolio intent -> mechanical risk gate -> constrained LEAN execution -> finance-quant virtual account -> immutable SessionReceipt -> typed API/events -> operator evidence view`.

LEAN remains an execution body only for the A1-validated deterministic daily-bar next-eligible-open slice. Finance-quant owns account truth, strategy/risk lineage, session lineage, authority checks, and evidence. No upstream fork is authorized.

## Authority boundary

Implementation and validation run with trading authority `NONE`. Unattended paper and live capital remain disabled. No brokerage credentials are permitted in A2 build/test paths. A later A2 `HITL_PROMOTION` may authorize unattended local paper only after every conjunctive A2 gate passes; a test, receipt, runtime result, UI action, or agent decision cannot grant that capability.

## Boring PIT-safe baseline strategy

The A2 decision strategy is `a2-two-close-trend-v1`. It is deliberately simple and carries no model or KG authority. For one instrument at decision instant `t`, it sorts and de-duplicates bar events deterministically, then considers only bars satisfying both `event_time <= t` and `known_at <= t`. From the two latest available closes: rising close -> BUY, falling close -> SELL, flat/insufficient history -> `NO_INTENT`.

Quantity and normalized risk-notional request are fixed configuration. Intent identity, strategy-spec identity, and strategy-decision identity are canonical hashes. Adding an event from the future, or an event whose knowledge time is after `t`, must not change the earlier decision or its strategy hash (`FQ-PROP-030`).

The mechanical risk gate may pass the exact strategy intent or reject it; it never rewrites the intent to a wider exposure. The risk decision and its state/limit/intent inputs receive a deterministic `risk_hash` for SessionReceipt lineage.

## Durable virtual account

The local account store is SQLite and uses canonical decimal strings for money/quantity persistence. Authoritative state includes cash, positions, orders, fills, cash-ledger entries, and authoritative SessionReceipts. State transitions are transactional.

A submitted order has an immutable identity, intent identity, session identity, side, quantity, instrument, and created-at timestamp. A fill is accepted only when its order exists in `ACCEPTED` or `PARTIALLY_FILLED`, the instrument matches, fill quantity is positive, fee is non-negative, and cumulative fill quantity does not exceed accepted quantity.

Exact duplicate order/fill deliveries are idempotent only when their immutable fields match. Reusing an identity with different content fails closed. A rejected/invalid fill cannot partially alter cash, positions, orders, fills, ledger state, or session evidence.

For declared marks, account reconciliation is exact:

`NAV = cash + Σ(position_quantity × declared_mark)`.

Missing marks for non-zero positions fail closed rather than silently valuing at zero.

## Session lineage and atomicity

Every controlled run emits one immutable `SessionReceipt`. The authoritative receipt is committed in the **same SQLite transaction** as the normalized execution effects it describes. If reconciliation, receipt creation, chain validation, or receipt persistence fails, the entire account/session transaction rolls back. This closes the account-commit / receipt-append crash gap for the authoritative path and strengthens `FQ-PROP-028`.

The receipt binds session identity/ordinal, parent receipt hash, initial/terminal account-state hashes, input/strategy/risk/execution hashes, runtime identity and exact LEAN commit, observed authority, and terminal status. Receipt identity is SHA-256 over canonical JSON excluding `receipt_hash`. Authoritative receipts are append-only rows in the account database. `SessionJournal` JSONL is an optional export/evidence surface only; it is never account authority.

For adjacent receipts, `session_number` is contiguous, parent hash equals the prior receipt hash, and initial account state equals the prior terminal state. An exact retry of an already committed `session_id` returns the existing authoritative receipt only when input/strategy/risk/execution/runtime evidence is identical; conflicting reuse fails closed.

## LEAN receipt ingestion

A2 accepts only a normalized receipt that still passes the frozen A1 execution contract, has a valid canonical receipt hash, identifies runtime `lean`, is bound to the exact normalized fixture input hash, and is paired with the A1-selected LEAN source commit `185c691b89f28bd68e48d53c02147415134975f0`.

The initial ingestion slice accepts normalized `ACCEPTED`, `PARTIALLY_FILLED`, and `FILLED` orders for the validated market-order subset. Candidate order/fill identities must retain their deterministic finance-quant semantic form and line up with immutable fixture intents. Unsupported candidate states, corporate-action effects, fault receipts, or ambiguous lineage fail closed rather than being guessed into account state.

Before commit, finance-quant independently recomputes cash/position effects from side, fill quantity, price, and fee, then requires terminal cash, positions, order states, and normalized cash-ledger effects to match the execution receipt exactly.

## Restart and replay

Reopening the local store must reproduce the same authoritative state hash and authoritative receipt chain. Duplicate delivery may not double-apply an order/fill/cash effect. Historical deterministic replay must eventually reproduce the same terminal state and SessionReceipt for identical input/config/runtime pins; the repeated-run gate is at least five independent runs in A2.

## A2 PDD property map

| Property ID | Statement | Severity | Initial public oracle |
| --- | --- | --- | --- |
| FQ-PROP-023 | Virtual-account cash, positions, and declared marks reconcile exactly to NAV. | critical | `tests/test_a2_account.py::test_fq_prop_023_nav_reconciles_exactly` |
| FQ-PROP-024 | No authoritative fill exists without a valid preceding order and cumulative fill never exceeds accepted quantity. | critical | `tests/test_a2_account.py::test_fq_prop_024_fill_requires_order_and_cannot_overfill` |
| FQ-PROP-025 | Session N+1 starts from exactly Session N terminal account state and parent receipt. | critical | `tests/test_a2_session.py::test_fq_prop_025_session_chain_requires_exact_continuity` |
| FQ-PROP-026 | Canonical session receipts and durable account state are deterministic for identical evidence. | high | `tests/test_a2_session.py::test_fq_prop_026_receipt_hash_is_deterministic` |
| FQ-PROP-027 | Risk can approve the exact request or reduce it to zero only; it cannot widen requested exposure. | critical | `tests/test_a2_risk.py::test_fq_prop_027_risk_gate_never_widens` |
| FQ-PROP-028 | Retry/restart/duplicate delivery cannot double-apply authoritative effects; execution effects and receipt commit are atomic. | critical | `tests/test_a2_account.py::test_fq_prop_028_duplicate_fill_is_idempotent_and_reopen_is_stable`, `tests/test_a2_execution_session.py::test_fq_prop_028_session_commit_rolls_back_account_if_receipt_persistence_fails` |
| FQ-PROP-029 | Unattended paper execution fails closed unless durable project authority and explicit A2 HITL promotion both authorize it. | critical | `tests/test_a2_authority.py::test_fq_prop_029_current_project_state_cannot_run_unattended_paper` |
| FQ-PROP-030 | Baseline decisions use only bars legitimately knowable by decision time; future or late-known bars cannot change an earlier decision. | critical | `tests/test_a2_strategy.py::test_fq_prop_030_future_or_late_known_events_cannot_change_prior_decision` |

These public tests are necessary but not sufficient for A2 completion. A2 still requires hidden acceptance, mutation thresholds, differential/metamorphic coverage, five-run determinism, clean environment, chaos/fault campaigns, session receipt integrity, and explicit HITL promotion.

## Current implementation slice

Finance-quant-owned account/session/authority truth now precedes runtime orchestration. The execution-session integration binds a frozen-contract normalized LEAN receipt to that durable truth atomically, and the baseline strategy/risk layer now produces deterministic lineage without future knowledge. The next slice should assemble these pieces into a repeated deterministic controlled campaign and add independent reference differential + fault/replay evidence before API/UI work.
