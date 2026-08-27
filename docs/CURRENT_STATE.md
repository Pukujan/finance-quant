# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A2_AWAITING_HITL assurance=A2 active_issue=16 -->

## Active direction

The active master plan is issue **#12 — OSS-first autonomous trader + visual research console**. A1 / issue **#15** is complete. A2 / issue **#16 — Autonomous Trader v0** has completed its public implementation/assurance work and genuine one-shot hidden acceptance. The formal remaining A2 gate is explicit `HITL_PROMOTION`.

**That promotion is intentionally on hold.** Before enabling unattended paper capability, the owner requested a product-level OSS architecture reassessment because the intended product is broader than the current validated A2 kernel: configurable starting paper capital, real historical/ongoing PIT data, temporal knowledge/RAG, local model training, paper execution, and a proper operator dashboard.

The immediate project action is therefore an OSS component bakeoff, not promotion.

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

## Reusable product/data assets already present

The repo also contains older but potentially reusable assets not yet promoted into the active autonomous-trader product path:

- bitemporal `vt/kt` PIT record semantics and durable SQLite PIT store;
- Polygon market-data/corporate-action ingestion;
- Qlib compiler boundary;
- temporal graph/KG boundary design;
- legacy research/evaluation fixtures.

These should be assessed alongside mature OSS rather than rewritten blindly.

## Active OSS reassessment

The detailed handoff is `docs/handoffs/2026-08-27-oss-product-architecture-reassessment.md`.

Initial verified candidates include FinRL-X (`AI4Finance-Foundation/FinRL-Trading`), Open Papertrade (`Open-Papertrade/Open-Papertrade`), Agentic Trading Lab (`Open-Finance-Lab/AgenticTrading`), Microsoft Qlib and RD-Agent, with OpenBB/FinGPT as follow-up candidates.

The objective is a layer-by-layer **KEEP / REPLACE / ADAPT / DELETE** decision for data/PIT, research/model training, temporal KG/RAG, execution/paper account, frontend/operator UX and local deployment. Finance-quant's unusual proven assets—PIT/authority semantics, exact account/replay evidence, sealed acceptance, mutation/chaos gates and promotion controls—should not be discarded unless a replacement explicitly passes conformance.

## Authority

- Trading authority: **NONE**
- Unattended paper: **DISABLED**
- Live capital: **DISABLED**
- Frontend authority: **OPERATOR_ONLY**

A passing hidden receipt does not itself grant capability authority. A2 remains `IN_PROGRESS` until a later explicit human `HITL_PROMOTION` is durably recorded.

## Next exact action

Perform the OSS product architecture bakeoff described in the latest handoff. Produce a decision matrix for each layer with current implementation, candidate OSS, KEEP/REPLACE/ADAPT/DELETE disposition, licensing/security/maintenance risks, required conformance tests, migration cost and custom code made unnecessary. Update the master roadmap/issues before implementing a material pivot.

Do **not** ask for A2 promotion first. Until the architecture decision is durable, keep authority `NONE`, paper disabled and live capital disabled, and do not consume another hidden seal use.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/LATEST.md`
4. `docs/handoffs/2026-08-27-oss-product-architecture-reassessment.md`
5. issue #12 and issue #16
6. issue #17 plus issues #19/#20/#21
7. relevant contracts/tests and external OSS repositories
