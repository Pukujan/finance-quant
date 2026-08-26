# Handoff — A1 metamorphic relation closure

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state sources were re-read before this slice: `AGENTS.md`, `docs/CURRENT_STATE.md`, issue #15, `docs/handoffs/LATEST.md`, and `contracts/assurance/capability-assurance-v1.json`. The prior documentation head `36f55c97b1ea1bbe532e3088ad0d082fae7c312e` was verified fully green across all eight current PR workflows before changes.

Property impact is **STRENGTHEN** only. No execution oracle, candidate pin, PIT boundary, permitted difference, runtime disposition, trading authority, or sealed-holdout rule changed.

The public A1 metamorphic audit found that the contract-declared fee monotonicity and equivalent split-execution economic relations were not explicitly represented in `tests/test_execution_metamorphic.py`. Existing independent coverage already binds canonical mapping-key order, exact duplicate idempotence, future-known decoys, event permutation, uniform time shifts, eligible-liquidity monotonicity, and three-run determinism/clean-environment evidence.

Commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` adds two independent reference-oracle tests:

- increasing a non-negative per-unit fee from `0.10` to `0.35` must preserve execution quantity/price/source and positions while terminal NAV cannot improve;
- splitting an economically equivalent liquidity-bounded quantity of `3` into two independently identified quantities `1 + 2` at the same eligible event must preserve aggregate executed quantity, terminal position, cash, and NAV.

No runtime implementation was changed. The tests exercise only the finance-quant-owned reference oracle and use the existing public fixture semantics.

`a1-assurance` run `32925860727` passed its `metamorphic-chaos` job with the new relations and passed both generic and LEAN-specific mutation gates. Both Nautilus negative evaluators on the same code head also passed. At handoff time, ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and LEAN clean-determinism were still executing, so `e4382711...` is not yet claimed as a fully green exact-head baseline.

A1 remains **IN_PROGRESS**. Genuine `HIDDEN_ACCEPTANCE` remains outstanding and may only be satisfied by an authorized external clean runner producing the public seal-bound aggregate receipt; ordinary agents must not inspect sealed cases or labels. Runtime selection remains `NONE / PENDING`, trading authority remains `NONE`, and autonomous paper/live execution remains disabled.

## Next exact action

1. Require commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` and the subsequent durable documentation head to complete the full eight-workflow exact-head matrix; fix any genuine failure without weakening tests or invariants.
2. Preserve the explicit public metamorphic relations, mutation thresholds, LEAN process-fault and clean-determinism receipts, and Nautilus path-exhaustion evidence.
3. Complete the remaining public A1 audit for any candidate-level chaos/fault obligation not already covered by the process-boundary campaign and generic restart/corruption oracles. Add a gate only for a genuinely uncovered contractual fault relation.
4. Obtain genuine hidden acceptance only through the authorized external clean-runner/sealed interface and ingest only the aggregate `SafeAcceptanceReceipt`; never inspect or fabricate hidden evidence.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not begin issue #16 or change trading/holdout authority before that point.
