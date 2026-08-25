# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_LEAN_DIFFERENTIAL_SLICE assurance=A1 active_issue=15 -->

## Active direction

Current work is GitHub issue **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, assurance phase **A1**. The legacy Phase-B plan remains parked and preserved only as an oracle.

## Current capability and authority

- Project status: **A1_LEAN_DIFFERENTIAL_SLICE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Runtime selection: **NONE / PENDING**
- Trading authority: **NONE**
- Autonomous paper and live execution: **DISABLED**
- Sealed holdout: isolated; ordinary agents may not inspect exact cases or labels

## A1 contract

The governing assurance contract is `contracts/assurance/capability-assurance-v1.json`; the A1 SDD/PDD is `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`; the executable runtime contract is `contracts/execution/runtime-conformance-v1.json`. A1 is conjunctive: SDD/PDD, static/IR, unit/regression, property/stateful, hidden acceptance, mutation, differential, metamorphic, repeated determinism, clean-environment, and chaos/fault evidence must all pass before final candidate dispositions or promotion. Properties `FQ-PROP-015` through `FQ-PROP-022` remain authoritative.

## Candidate evidence

LEAN remains pinned to commit `185c691b89f28bd68e48d53c02147415134975f0`. Its credential-free production `EquityFillModel.MarketOnOpenFill` probe conforms on the public two-bar slice: three runs fill quantity `5` at price `11` at `2026-06-02T13:30:00Z` from `bar-2`. This is evidence only; `runtime_disposition` remains `PENDING`.

NautilusTrader remains pinned to `v1.230.0`, commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. Native GTC production matching fills the bar-1 decision immediately on bar 1, a deterministic `FQ-PROP-015` failure. The pinned engine also rejects `AT_THE_OPEN` / `AT_THE_CLOSE` time-in-force.

A PIT-safe thin callback-deferral adapter has now also been executed. It buffers the already-created bar-1 MARKET intent and submits it only from the bar-2 strategy callback, while retaining production `BacktestEngine` / `SimulatedExchange` matching, native GTC, no custom fill model, and no future bar payload before submission. Run `32907656115` produced three identical fills: quantity `5`, price `12.00`, time `2026-06-02T13:30:00Z`, source `bar-2`. The unchanged oracle requires price `11`; evidence records `semantic_conformance: FAIL` and `failed_property: FQ-PROP-021`. This eliminates simple callback deferral as a conforming workaround.

## Validation status

Durable pre-adapter head `8deb8d7e6106dbaef2e12f28fa8687fc6ca280f9` is fully green: tests `32906305762`, runtime-candidates `32906305711`, phase-b `32906305810`, and bootstrap-assurance `32906305786`, including full-validation and fresh-environment.

Adapter implementation head `faafc0ce616d07d7d99fc623ba0ceddb20912406` has a green outcome-neutral adapter evaluation (`32907656115`). Its ordinary tests, legacy phase-b, bootstrap-assurance, and unchanged runtime-candidates checks were still running when this state was persisted. The durable-state commit itself must also be validated.

A1 remains **IN_PROGRESS**. Hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete determinism/clean-environment evidence, chaos/fault campaigns, and final candidate dispositions remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Require the exact durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, and `a1-nautilus-adapter-evaluation`; fix genuine failures without weakening any invariant.
2. Evaluate a Nautilus production-native command-queue/latency mechanism only if its release boundary can be derived PIT-safely from contract-known/session information without future event payloads while preserving the MARKET intent and production matching. Otherwise record the mechanism as ineligible.
3. Preserve the native `FQ-PROP-015` and deferred-callback `FQ-PROP-021` negative evidence and continue all remaining conjunctive A1 gates for still-eligible runtime paths.
4. Only after every required A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime.

Do not start issue #16 or change any authority/holdout restriction while A1 remains incomplete.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. active GitHub issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. relevant A1 adapter/probe/workflow files and tests
