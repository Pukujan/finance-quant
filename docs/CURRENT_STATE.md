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

The public metamorphic relation set now has explicit executable coverage across the conformance/reference/metamorphic suites: canonical mapping-key order, exact duplicate idempotence, all public event permutations, uniform time shifts, unavailable future-known decoys, monotonicity under increased eligible liquidity, non-negative fee monotonicity, equivalent liquidity-bounded split-execution economics, and repeated deterministic execution. Commit `e4382711b732172d938bffd2c3e2a0a013ffa9d6` added the two previously implicit relations; `a1-assurance` run `32925860727` passed them with both mutation gates green.

The LEAN process-boundary chaos/fault campaign now explicitly exercises all contract-named fault classes applicable to the stateless public probe boundary plus existing process failures: `nonzero_exit`, `runtime_exception`, `timeout`, `dependency_missing`, `candidate_output_corruption`, `duplicate_delivery`, `malformed_payload`, `invalid_reorder`, `dropped_event`, `crash_before_commit`, `crash_after_commit`, `restart_replay`, `persisted_evidence_corruption`, and `persisted_state_corruption`. All non-committed cases fail closed with authority `NONE`. `crash_after_commit` and `restart_replay` recover only after exact persisted authoritative public evidence revalidates against recomputed evidence, and remain authority `NONE`. `a1-assurance` run `32926137710` passed the expanded campaign and both mutation jobs; artifact `9591573749` has digest `sha256:736d60345a54e626f2d39317e701600a9ac99c6ccd93d9f590bb4ecb105f6a42`.

The opaque A1 hidden-acceptance public ingress exists and is fail-closed, but this does **not** satisfy `HIDDEN_ACCEPTANCE`. Genuine completion requires an authorized external clean runner to execute the sealed corpus and provide only an aggregate `SafeAcceptanceReceipt` bound to the public A1 `SealRecord`. Ordinary agents must not inspect or fabricate sealed cases, labels, or receipts.

## Validation status

Exact LEAN clean-determinism documentation head `36f55c97b1ea1bbe532e3088ad0d082fae7c312e` was verified fully green across all eight PR workflows before the latest public assurance slices.

On chaos code head `2ede511d00f5213fdc266003e3280b21d1252e0b`, ordinary tests `32926137657`, runtime-candidates `32926137666`, both Nautilus evaluators `32926137697` / `32926137703`, `a1-assurance` `32926137710`, and LEAN clean-determinism `32926137725` are green. Legacy Phase-B `32926137668` and bootstrap-assurance `32926137698` were still completing when durable state was written, so the code head is not yet claimed fully green across all eight workflows.

The public metamorphic and chaos/fault audit is now closed for the current reference/LEAN slice. A1 remains **IN_PROGRESS** because genuine hidden acceptance remains outstanding; no primary runtime may be selected yet.

## Next exact action

1. Require the chaos code head and final durable documentation head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, `a1-assurance`, and `a1-lean-clean-determinism`; fix genuine failures without weakening any invariant.
2. Once the full public matrix is green, obtain genuine `HIDDEN_ACCEPTANCE` only through the authorized external clean-runner/sealed interface and ingest only the aggregate `SafeAcceptanceReceipt`. Do not inspect the private holdout or fabricate evidence.
3. Preserve Nautilus negative/ineligibility/path-exhaustion evidence plus LEAN production differential, mutation, metamorphic, process-fault, and clean-determinism evidence.
4. Only after every required A1 gate, including hidden acceptance, is green may issue #15 assign final candidate dispositions (`ADOPT | ADOPT_WITH_CONSTRAINTS | REFERENCE_ONLY | REJECT`), select a primary runtime, and explicitly permit promotion.

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
