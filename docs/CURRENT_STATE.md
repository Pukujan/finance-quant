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

LEAN remains pinned to commit `185c691b89f28bd68e48d53c02147415134975f0`. Its credential-free production `EquityFillModel.MarketOnOpenFill` probe conforms on the public two-bar slice: three runs fill quantity `5` at price `11` at `2026-06-02T13:30:00Z` from `bar-2`. Candidate-level clean determinism is green across three independent fresh runners. This remains evidence only; `runtime_disposition` is `PENDING`.

NautilusTrader remains pinned to `v1.230.0`, commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. Public production-native path analysis is exhausted for the unchanged next-bar-open MARKET/GTC contract: native GTC matching produces a deterministic `FQ-PROP-015` same-bar failure; PIT-safe callback deferral produces a deterministic `FQ-PROP-021` failure by filling bar 2 at close `12` rather than open `11`; `AT_THE_OPEN` / `AT_THE_CLOSE` are rejected; and native insert-latency/pre-open timing is unavailable through the exact published wheel's public API. Private bindings, future bar payload, custom fill logic, or oracle changes remain ineligible. Nautilus `runtime_disposition` stays `PENDING` until every A1 gate completes.

## Assurance evidence

Property impact is **STRENGTHEN** only. Candidate pins, execution semantics, PIT boundaries, permitted differences, holdout restrictions, and authority were not widened.

The finance-quant reference/conformance layer has executable public oracles for `FQ-PROP-015` through `FQ-PROP-022`, including same-bar prevention, lifecycle/quantity bounds, accounting reconciliation, duplicate idempotence, future-knowledge poisoning, repeated determinism, fail-closed semantic drift, and checkpoint/restart corruption/convergence.

The public metamorphic relation set has explicit executable coverage across the conformance/reference/metamorphic suites: canonical mapping-key order, exact duplicate idempotence, all public event permutations, uniform time shifts, unavailable future-known decoys, monotonicity under increased eligible liquidity, non-negative fee monotonicity, equivalent liquidity-bounded split-execution economics, and repeated deterministic execution. Commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` added the two previously implicit relations; `a1-assurance` run `32925860727` passed them with both mutation gates green.

The LEAN process-boundary chaos/fault campaign explicitly exercises all contract-named fault classes applicable to the stateless public probe boundary plus existing process failures: `nonzero_exit`, `runtime_exception`, `timeout`, `dependency_missing`, `candidate_output_corruption`, `duplicate_delivery`, `malformed_payload`, `invalid_reorder`, `dropped_event`, `crash_before_commit`, `crash_after_commit`, `restart_replay`, `persisted_evidence_corruption`, and `persisted_state_corruption`. All non-committed cases fail closed with authority `NONE`. `crash_after_commit` and `restart_replay` recover only after exact persisted authoritative public evidence revalidates against recomputed evidence, and remain authority `NONE`. `a1-assurance` run `32926137710` passed the expanded campaign and both mutation jobs; artifact `9591573749` has digest `sha256:736d60345a54e626f2d39317e701600a9ac99c6ccd93d9f590bb4ecb105f6a42`.

The opaque A1 hidden-acceptance public ingress exists and is fail-closed, but this does **not** satisfy `HIDDEN_ACCEPTANCE`. Genuine completion requires an authorized external clean runner to execute the sealed corpus and provide only an aggregate `SafeAcceptanceReceipt` bound to the public A1 `SealRecord`. Ordinary agents must not inspect or fabricate sealed cases, labels, or receipts. The repository's ordinary/public CI identity is explicitly ineligible to act as that runner.

## Validation status

Exact durable head `4739392b15319bb209d657294834fed4cfb02d29` is fully green across all eight required public PR workflows: tests `32926469922`, legacy Phase-B `32926469919`, bootstrap-assurance `32926469897`, runtime-candidates `32926469900`, Nautilus callback evaluator `32926469912`, Nautilus pre-open evaluator `32926469910`, `a1-assurance` `32926469899`, and LEAN clean-determinism `32926469909`.

The public SDD/PDD, static/IR, unit/regression, property/stateful, mutation, differential, metamorphic, determinism, clean-environment, and chaos/fault work is green for the current A1 public slice. The remaining conjunctive blocker is genuine **HIDDEN_ACCEPTANCE** through the authorized external clean-runner/sealed interface. No primary runtime may be selected and A1 may not be promoted until that aggregate receipt verifies successfully.

A1 remains **IN_PROGRESS**.

## Next exact action

1. Obtain genuine `HIDDEN_ACCEPTANCE` only through the authorized external clean runner described by `docs/acceptance/SEALED_INTERFACE.md`; the runner must execute the sealed corpus without exposing cases or labels and emit only the public `SealRecord` plus aggregate `SafeAcceptanceReceipt` for the exact candidate artifact under evaluation.
2. Ingest that aggregate-only evidence through `.github/workflows/a1-hidden-acceptance.yml` / `finance_quant.acceptance.a1_hidden`. Do not inspect the private holdout, use the repository's coarse GitHub identity as the clean runner, or fabricate a receipt.
3. If hidden acceptance fails, preserve the aggregate failure receipt and fix only public implementation/oracle defects consistent with the unchanged contract; never optimize against hidden cases or weaken invariants.
4. Only after hidden acceptance passes and every conjunctive A1 gate remains green may issue #15 assign final candidate dispositions (`ADOPT | ADOPT_WITH_CONSTRAINTS | REFERENCE_ONLY | REJECT`), select a primary runtime, update machine-readable state, and explicitly permit promotion.

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
