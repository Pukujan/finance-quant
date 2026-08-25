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

LEAN remains pinned to commit `185c691b89f28bd68e48d53c02147415134975f0`. Its credential-free production `EquityFillModel.MarketOnOpenFill` probe conforms on the public two-bar slice: three runs fill quantity `5` at price `11` at `2026-06-02T13:30:00Z` from `bar-2`. This is evidence only; `runtime_disposition` remains `PENDING`.

NautilusTrader remains pinned to `v1.230.0`, commit `8160730c7c550480b0a439fb11086a4c4de15f0b`. Native GTC production matching fills the bar-1 decision immediately on bar 1, a deterministic `FQ-PROP-015` failure. The pinned engine also rejects `AT_THE_OPEN` / `AT_THE_CLOSE` time-in-force.

A PIT-safe thin callback-deferral adapter has also been executed. It buffers the already-created bar-1 MARKET intent and submits it only from the bar-2 strategy callback, while retaining production `BacktestEngine` / `SimulatedExchange` matching, native GTC, no custom fill model, and no future bar payload before submission. Run `32907656115` produced three identical fills: quantity `5`, price `12.00`, time `2026-06-02T13:30:00Z`, source `bar-2`. The unchanged oracle requires price `11`; evidence records `semantic_conformance: FAIL` and `failed_property: FQ-PROP-021`. This eliminates simple callback deferral as a conforming workaround.

The next production-native timing candidate—native insert latency plus a session-derived pre-open strategy-clock settlement point—has been evaluated fail-closed. Pinned source commit `8160730c7c550480b0a439fb11086a4c4de15f0b` contains the native inflight-command queue, `StaticLatencyModel` binding source, generated public stub, and a unit test importing `StaticLatencyModel` from `nautilus_trader.execution`. However, the exact published `nautilus_trader==1.230.0` CPython 3.12 Linux wheel does not export that public symbol. Evaluator run `32910563339` therefore records `mechanism_status: INELIGIBLE_PUBLISHED_API_UNAVAILABLE`, `semantic_conformance: NOT_EXECUTED`, `source_release_skew: true`, `runtime_disposition: PENDING`, and authority `NONE`. No private `_libnautilus` binding was used to bypass the published API, and the next-open oracle was not changed.

## Validation status

Durable pre-adapter head `8deb8d7e6106dbaef2e12f28fa8687fc6ca280f9` is fully green: tests `32906305762`, runtime-candidates `32906305711`, phase-b `32906305810`, and bootstrap-assurance `32906305786`, including full-validation and fresh-environment.

The callback-deferral evaluator is green at run `32907656115`. The prior durable head `0caffcf8bcc164a282960c6bbf2cf6aeddce8378` was subsequently verified green across ordinary tests, legacy Phase-B, bootstrap assurance, runtime candidates, and the outcome-neutral callback evaluator before the latency/clock slice began.

The latency/clock evaluator had two integration-only failures that did not exercise or weaken the semantic oracle: the first preflight asserted a non-existent source marker instead of the pinned `has_pending_commands` / `generate_inflight_command` / `process(...)` surface; the second exposed the published-wheel `StaticLatencyModel` import failure. Both were corrected fail-closed. Exact published-wheel evaluator run `32910563339` is green and uploaded artifact `a1-nautilus-native-latency-preopen-evaluation` with the ineligibility receipt. The final documentation head still must complete its exact-head validation cycle before it may be treated as a green resumable baseline.

A1 remains **IN_PROGRESS**. Hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete determinism/clean-environment evidence, chaos/fault campaigns, and final candidate dispositions remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Require the exact durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, and `a1-nautilus-preopen-evaluation`; fix genuine failures without weakening any invariant.
2. Preserve the native `FQ-PROP-015`, deferred-callback `FQ-PROP-021`, and published-latency-API ineligibility receipts. Do not use private Nautilus bindings to manufacture eligibility.
3. Determine whether any remaining **public production-native** NautilusTrader mechanism can realize the unchanged next-bar-open MARKET semantics using only contract/session-known timing and no future event payload or custom fill model. If none exists, record that candidate-path exhaustion explicitly rather than weakening the differential.
4. Continue all remaining conjunctive A1 hidden-acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault gates for still-eligible runtime paths. Only after every required A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime.

Do not start issue #16 or change any authority/holdout restriction while A1 remains incomplete.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. relevant A1 adapter/probe/workflow files and tests
