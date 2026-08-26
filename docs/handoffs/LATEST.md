# Handoff — A1 metamorphic relation closure

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state sources were re-read before this slice. The prior durable documentation head `36f55c97b1ea1bbe532e3088ad0d082fae7c312e` was verified fully green across all eight current PR workflows before changes.

Property impact remains **STRENGTHEN** only: the execution oracle, candidate pins, PIT boundary, permitted differences, runtime dispositions, trading authority, and sealed-holdout policy were not changed.

The public A1 metamorphic audit found two contract-declared relations that were not explicit in the dedicated suite: non-negative fee monotonicity and equivalent split-execution economics. Commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` adds independent reference-oracle tests requiring higher non-negative fees to never improve terminal NAV while preserving execution semantics, and requiring an equivalent liquidity-bounded `3 = 1 + 2` execution split to preserve aggregate executed quantity, terminal position, cash, and NAV.

Existing independent tests already cover canonical mapping-key order, exact duplicate idempotence, future-known decoys, all public event permutations, uniform time shifts, increased eligible-liquidity monotonicity, and repeated determinism. No runtime implementation or oracle semantics changed.

`a1-assurance` run `32925860727` passed its `metamorphic-chaos` job with the new relations and passed both generic and LEAN-specific mutation gates. Both Nautilus negative evaluators on the same code head also passed. At the time this handoff was written, ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and LEAN clean-determinism for the code head were still executing; therefore neither the code head nor the subsequent documentation head is yet claimed fully green.

A1 remains **IN_PROGRESS**. Genuine hidden acceptance still requires an authorized external clean runner and an actual public A1 seal-bound aggregate `SafeAcceptanceReceipt`; ordinary agents may not inspect exact sealed cases or labels. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled.

## Next exact action

1. Require the full eight-workflow exact-head validation matrix to finish green for the metamorphic code slice and final durable documentation head; fix genuine failures without weakening tests or invariants.
2. Finish the public A1 audit for any genuinely uncovered candidate-level chaos/fault relation beyond the existing LEAN process-boundary campaign plus generic restart/corruption oracles. Add only necessary contractual coverage.
3. Obtain `HIDDEN_ACCEPTANCE` only through the authorized external clean-runner/sealed interface and ingest only its aggregate receipt. Never inspect or fabricate hidden evidence.
4. Preserve Nautilus negative/ineligibility/path-exhaustion evidence plus LEAN mutation, process-fault, clean-determinism, and metamorphic receipts.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not start issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-metamorphic-relations-closure.md`.
