# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_LEAN_DIFFERENTIAL_SLICE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**. Current work is GitHub issue **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, assurance phase **A1**. The legacy Phase-B plan remains parked and preserved only as an oracle.

## Current capability and authority

- Project status: **A1_LEAN_DIFFERENTIAL_SLICE**
- Bootstrap machine status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Runtime selection: **NONE / PENDING**
- Trading authority: **NONE**
- Autonomous paper and live execution: **DISABLED**
- Sealed holdout: isolated; ordinary agents may not inspect exact cases or labels

## A1 contract

The governing assurance contract is `contracts/assurance/capability-assurance-v1.json`; the A1 SDD/PDD is `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`; the executable runtime contract is `contracts/execution/runtime-conformance-v1.json`. A1 is conjunctive: SDD/PDD, static/IR, unit/regression, property/stateful, hidden acceptance, mutation, differential, metamorphic, repeated determinism, clean-environment, and chaos/fault evidence must all pass before final candidate dispositions or promotion. Properties `FQ-PROP-015` through `FQ-PROP-022` remain authoritative.

## Candidate evidence

LEAN remains pinned to commit `185c691b89f28bd68e48d53c02147415134975f0`. Its credential-free production `EquityFillModel.MarketOnOpenFill` probe conforms on the public two-bar slice: three runs fill quantity `5` at price `11` at `2026-06-02T13:30:00Z` from `bar-2`. Candidate-level clean determinism is also green: workflow run `32923522432` built the pinned production probe independently on three fresh Ubuntu runners and produced identical semantic evidence. This remains evidence only; `runtime_disposition` is `PENDING`.

NautilusTrader remains pinned to `v1.230.0`, commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. Public production-native path analysis is exhausted for the unchanged next-bar-open MARKET/GTC contract: native GTC matching produces a deterministic `FQ-PROP-015` same-bar failure; PIT-safe callback deferral produces a deterministic `FQ-PROP-021` failure by filling bar 2 at close `12` rather than open `11`; `AT_THE_OPEN` / `AT_THE_CLOSE` are rejected; and the native insert-latency/pre-open mechanism is unavailable through the exact published wheel's public API. Private bindings, future bar payload, custom fill logic, or oracle changes remain ineligible. Nautilus `runtime_disposition` stays `PENDING` until every A1 gate completes.

## Assurance evidence

Property impact is **STRENGTHEN** only. Candidate pins, execution semantics, PIT boundaries, permitted differences, holdout restrictions, and authority were not widened.

The finance-quant reference/conformance layer has executable public oracles for `FQ-PROP-015` through `FQ-PROP-022`, including same-bar prevention, lifecycle/quantity bounds, accounting reconciliation, duplicate idempotence, future-knowledge poisoning, repeated determinism, fail-closed semantic drift, and checkpoint/restart corruption/convergence.

The `a1-assurance` workflow runs reference/conformance/property, metamorphic, fault/restart, LEAN normalizer/process-boundary tests, and both generic and candidate-specific mutation gates. Generic mutation evidence has passed at **11/11 critical** and **2/2 high** mutants killed; LEAN-specific mutation evidence has passed at **100%** with zero survivors. The LEAN process-boundary fault campaign requires fail-closed behavior for nonzero exit, timeout, missing dependency, candidate-output corruption, and persisted-evidence corruption, always retaining authority `NONE`.

The public metamorphic relation set now has explicit executable coverage across the conformance/reference/metamorphic suites: canonical mapping-key order, exact duplicate idempotence, all public event permutations, uniform time shifts, unavailable future-known decoys, monotonicity under increased eligible liquidity, non-negative fee monotonicity, equivalent liquidity-bounded split-execution economics, and repeated deterministic execution. Commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` added the two previously implicit relations: higher non-negative fees cannot improve terminal NAV while preserving fill semantics, and an economically equivalent `3 = 1 + 2` execution split preserves aggregate quantity, position, cash, and NAV. `a1-assurance` run `32925860727` passed the strengthened metamorphic/chaos job and both mutation jobs.

The opaque A1 hidden-acceptance public ingress exists and is fail-closed, but this does **not** satisfy `HIDDEN_ACCEPTANCE`. Genuine completion requires an authorized external clean runner to execute the sealed corpus and provide only an aggregate `SafeAcceptanceReceipt` bound to the public A1 `SealRecord`. Ordinary agents must not inspect or fabricate sealed cases, labels, or receipts.

## Validation status

Exact LEAN clean-determinism documentation head `36f55c97b1ea1bbe532e3088ad0d082fae7c312e` was verified fully green across all eight current PR workflows before the metamorphic closure slice began.

Metamorphic code head `e4382711b732172d938bffd2c3e2a0a013ffa9d6` has a green `a1-assurance` run `32925860727`, including the strengthened metamorphic/chaos job and both mutation gates; both Nautilus evaluators on that head are also green. Ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and LEAN clean-determinism were still executing when durable state was written, so that code head is not yet claimed fully green.

A1 remains **IN_PROGRESS**. Genuine hidden acceptance is still outstanding. The remaining public work is to verify the full exact-head matrix and finish the candidate-level chaos/fault audit; no primary runtime may be selected yet.

## Next exact action

1. Require the metamorphic code slice and final durable documentation head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, `a1-assurance`, and `a1-lean-clean-determinism`; fix genuine failures without weakening any invariant.
2. Finish the still-eligible LEAN candidate-level chaos/fault audit against `FQ-PROP-015` through `FQ-PROP-022`; add a new gate only for a genuinely uncovered contractual fault relation.
3. Obtain genuine `HIDDEN_ACCEPTANCE` only through the authorized external clean-runner/sealed interface, and ingest only the aggregate `SafeAcceptanceReceipt`. Do not inspect the private holdout or fabricate evidence.
4. Preserve Nautilus negative/ineligibility/path-exhaustion evidence plus LEAN mutation, process-fault, clean-determinism, and metamorphic evidence.
5. Only after every required A1 gate is green may issue #15 assign final candidate dispositions (`ADOPT | ADOPT_WITH_CONSTRAINTS | REFERENCE_ONLY | REJECT`), select a primary runtime, and explicitly permit promotion.

Do not start issue #16 or change any authority/holdout restriction while A1 remains incomplete.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. `docs/acceptance/SEALED_INTERFACE.md`
9. relevant A1 adapter/probe/workflow files and tests
