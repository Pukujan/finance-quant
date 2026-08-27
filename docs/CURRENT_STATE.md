# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A2_AWAITING_HITL assurance=A2 active_issue=16 -->

## Active direction

The active master plan is issue **#12 — OSS-first autonomous trader + visual research console**. A1 / issue **#15** is complete. A2 / issue **#16 — Autonomous Trader v0** has completed its public implementation/assurance work and genuine one-shot hidden acceptance. It is now waiting only on the required explicit `HITL_PROMOTION` decision.

## Runtime and capability

- Primary runtime: **LEAN** commit `185c691b89f28bd68e48d53c02147415134975f0`
- Runtime disposition: **ADOPT_WITH_CONSTRAINTS** for the validated deterministic daily-bar next-eligible-open slice
- Finance-quant SQLite account/order/fill truth: implemented
- Atomic SessionReceipt lineage and exact replay: implemented
- Deterministic PIT-safe baseline + mechanical non-widening risk gate: implemented
- Read-only operator evidence surface: implemented
- Five-run clean LEAN determinism: PASS
- Five-run multi-session restart/replay determinism: PASS
- Stateful/property, metamorphic, mutation, differential, clean-environment, and chaos/fault public gates: PASS

## A2 frozen evaluation and hidden acceptance

Frozen public evaluation SHA: `1ecc470cd6e0e23bf1d439f51e4e2c39674f02c4`.
Candidate artifact SHA-256: `446fdc1a0c87db3a6a2ab4e94fab3d7e9f8fd389cc41676be12c3803b1f2d093`.
Pinned LEAN commit: `185c691b89f28bd68e48d53c02147415134975f0`.

The authorized private runner reported one completed isolated A2 sealed run:

- case set: `A2-ISSUE-16-PRIVATE-V1`
- scorer package SHA-256: `223ddbd0eb679b6e968639a96033b305a1e853366221f62543cdbd74b771fcb0`
- evaluator: `a2-private-evaluator-v1`, SHA-256 `1ef08ed11d6fa493d57ea70b9e57784d2fcbf10b1ea0d45d3955b4b2c4a65cc4`
- sealed bundle SHA-256: `bf711753f3ce2ce6047d854fbf8a6e2ec0c790a52d5f49c2d7d997c013a69a4c`
- seal use: `1 / 1` consumed
- status: `pass`
- aggregate metrics: `conformant=1.0`, `evaluated=1.0`
- failure classes: none

Canonical public evidence is stored at `docs/acceptance/A2_ISSUE_16_SEAL_RECORD.json` and `docs/acceptance/A2_ISSUE_16_SAFE_ACCEPTANCE_RECEIPT.json`. Recomputing the seven-field SealRecord commitment with the frozen public hashing rule yields `327a07323e55c3762ec2b04650f8c7d1f792fa8e210a2adc2583cea7a42c1f86`, exactly matching the receipt. The receipt is bound to the exact frozen candidate and satisfies the frozen A2 public verifier rules.

No exact hidden cases, labels, expected outputs, IDs, traces, counts, or oracle internals are stored publicly.

## Authority

- Trading authority: **NONE**
- Unattended paper: **DISABLED**
- Live capital: **DISABLED**
- Frontend authority: **OPERATOR_ONLY**

A passing hidden receipt does not itself grant capability authority. A2 remains `IN_PROGRESS` until the required explicit human `HITL_PROMOTION` is durably recorded.

## Next exact action

Obtain the human owner's explicit approve/reject decision for A2 unattended local paper operation. If approved, transition only the constrained local-paper capability from `NONE` to `PAPER`, preserve `live_capital_enabled=false`, record the promotion receipt/evidence hash, rerun exact-head CI, and only then close issue #16 / mark A2 complete. If rejected, keep authority `NONE` and leave A2 unpromoted.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. issue #16
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `contracts/trading/autonomous-trader-v0.json`
7. A2 acceptance evidence and relevant tests/workflows
