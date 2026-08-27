# A2 Autonomous Trader v0 — SDD/PDD

Issue: #16  
Assurance phase: A2  
Property impact: **STRENGTHEN** A1 execution/PIT invariants; add durable account, session, replay, and authority invariants.

## Scope

A2 builds the first deliberately boring local paper-trading vertical slice:

`PIT/replay input -> deterministic baseline strategy -> portfolio intent -> mechanical risk gate -> constrained LEAN execution -> finance-quant virtual account -> immutable SessionReceipt -> typed API/events -> operator evidence view`.

LEAN remains an execution body only for the A1-validated deterministic daily-bar next-eligible-open slice. Finance-quant owns account truth, session lineage, risk policy, authority checks, and evidence. No upstream fork is authorized.

## Authority boundary

Implementation and validation run with trading authority `NONE`. Unattended paper and live capital remain disabled. No brokerage credentials are permitted in A2 build/test paths. A later A2 `HITL_PROMOTION` may authorize unattended local paper only after every conjunctive A2 gate passes; a test, receipt, runtime result, UI action, or agent decision cannot grant that capability.

## Durable virtual account

The local account store is SQLite and uses canonical decimal strings for money/quantity persistence. Authoritative state includes cash, positions, orders, fills, and cash-ledger entries. State transitions are transactional.

A submitted order has an immutable identity, intent identity, session identity, side, quantity, instrument, and created-at timestamp. A fill is accepted only when its order exists in `ACCEPTED` or `PARTIALLY_FILLED`, the instrument matches, fill quantity is positive, fee is non-negative, and cumulative fill quantity does not exceed accepted quantity.

Exact duplicate `fill_id` deliveries are idempotent only when every persisted fill field matches. Reusing a fill identity with different content fails closed. A rejected/invalid fill cannot partially alter cash, positions, orders, fills, or ledger state.

For declared marks, account reconciliation is exact:

`NAV = cash + Σ(position_quantity × declared_mark)`.

Missing marks for non-zero positions fail closed rather than silently valuing at zero.

## Session lineage

Every controlled run emits one immutable `SessionReceipt`. The receipt binds:

- session identity and ordinal;
- parent receipt hash;
- initial and terminal authoritative account-state hashes;
- input, strategy, risk, and execution hashes;
- runtime identity and exact LEAN commit;
- authority observed during the session;
- terminal status.

Receipt identity is SHA-256 over canonical JSON excluding `receipt_hash`. The append-only session journal has no update/delete API.

For adjacent receipts, session `N+1` must satisfy all three:

1. `session_number(N+1) = session_number(N) + 1`;
2. `parent_receipt_hash(N+1) = receipt_hash(N)`;
3. `initial_state_hash(N+1) = terminal_state_hash(N)`.

## Risk non-widening

The A2 adapter around the existing mechanical veto has only two outputs: approve the exact requested notional, or reject to zero. Invalid side/notional inputs fail closed. Neither strategy, agent, API, UI, nor runtime metadata can widen the requested exposure.

## Restart and replay

Reopening the local store must reproduce the same authoritative state hash. Duplicate delivery may not double-apply an order/fill/cash effect. Historical deterministic replay must eventually reproduce the same terminal state and SessionReceipt for identical input/config/runtime pins; the repeated-run gate is at least five independent runs in A2.

## A2 PDD property map

| Property ID | Statement | Severity | Initial public oracle |
| --- | --- | --- | --- |
| FQ-PROP-023 | Virtual-account cash, positions, and declared marks reconcile exactly to NAV. | critical | `tests/test_a2_account.py::test_fq_prop_023_nav_reconciles_exactly` |
| FQ-PROP-024 | No authoritative fill exists without a valid preceding order and cumulative fill never exceeds accepted quantity. | critical | `tests/test_a2_account.py::test_fq_prop_024_fill_requires_order_and_cannot_overfill` |
| FQ-PROP-025 | Session N+1 starts from exactly Session N terminal account state and parent receipt. | critical | `tests/test_a2_session.py::test_fq_prop_025_session_chain_requires_exact_continuity` |
| FQ-PROP-026 | Canonical session receipts and durable account state are deterministic for identical evidence. | high | `tests/test_a2_session.py::test_fq_prop_026_receipt_hash_is_deterministic` |
| FQ-PROP-027 | Risk can approve the exact request or reduce it to zero only; it cannot widen requested exposure. | critical | `tests/test_a2_risk.py::test_fq_prop_027_risk_gate_never_widens` |
| FQ-PROP-028 | Retry/restart/duplicate delivery cannot double-apply authoritative account effects. | critical | `tests/test_a2_account.py::test_fq_prop_028_duplicate_fill_is_idempotent_and_reopen_is_stable` |
| FQ-PROP-029 | Unattended paper execution fails closed unless durable project authority and explicit A2 HITL promotion both authorize it. | critical | `tests/test_a2_authority.py::test_fq_prop_029_current_project_state_cannot_run_unattended_paper` |

These public tests are necessary but not sufficient for A2 completion. A2 still requires hidden acceptance, mutation thresholds, differential/metamorphic coverage, five-run determinism, clean environment, chaos/fault campaigns, session receipt integrity, and explicit HITL promotion.

## First implementation slice

The initial A2 core deliberately stops before LEAN orchestration/API/UI integration. It establishes finance-quant-owned account/session/authority truth first so later adapters cannot become an accidental source of authority. The next slice binds deterministic baseline intents and the pinned LEAN execution receipt into these durable primitives.
