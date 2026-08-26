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

The production-native latency candidate—native insert latency plus a session-derived pre-open strategy-clock settlement point—was evaluated fail-closed. Pinned source commit `8160730c7c550480b0a439fb11086a4c4de15f0b` contains the native inflight-command queue, `StaticLatencyModel` binding source, generated public stub, and a unit test importing `StaticLatencyModel` from `nautilus_trader.execution`. However, the exact published `nautilus_trader==1.230.0` CPython 3.12 Linux wheel does not export that public symbol. Evaluator run `32910563339` therefore records `mechanism_status: INELIGIBLE_PUBLISHED_API_UNAVAILABLE`, `semantic_conformance: NOT_EXECUTED`, `source_release_skew: true`, `runtime_disposition: PENDING`, and authority `NONE`. No private `_libnautilus` binding was used to bypass the published API, and the next-open oracle was not changed.

Public production-native path analysis for pinned Nautilus is exhausted for the unchanged next-bar-open MARKET/GTC contract. The remaining session-clock variant cannot close the gap: in the pinned `BacktestEngine` event loop, timer callbacks are advanced before the next data item is routed, then pending commands/events are drained and exchanges are settled before that next market-data event. A pre-open timer submission without native latency therefore settles against prior market state before bar 2 is routed; submitting from the bar-2 callback is already executable negative evidence that fills at bar-2 close `12`, not open `11`; and native insert latency is unavailable through the pinned published wheel's public API. Reaching into private bindings, consuming future bar payload, adding custom fill logic, or changing the MARKET/GTC intent would violate the A1 comparison boundary and is not an eligible workaround. This is candidate-path exhaustion evidence only; Nautilus `runtime_disposition` remains `PENDING` until every conjunctive A1 assurance gate completes.

## Assurance evidence added

Property impact for the latest slice is **STRENGTHEN** only. The A1 oracle, candidate pins, permitted-difference policy, PIT boundary, and authority contract were not changed.

`FQ-PROP-022` now has an explicit checkpoint/restart convergence oracle. `restart_daily_reference_from_checkpoint` accepts a checkpoint only when its canonical hash, runtime/fixture/seed identity, committed boundary, and full deterministic prefix state agree with the immutable fixture; a re-hashed but state-corrupted checkpoint still fails closed. The final replay is linked to the validated checkpoint and must converge to the uninterrupted authoritative execution state.

A dedicated `a1-assurance` workflow now runs the owned reference/conformance fault and metamorphic suite plus source mutation testing. Metamorphic relations cover all six input permutations of the three-event public fixture, uniform timestamp shifts, insertion of a future-known decoy, and monotonicity under increased eligible liquidity. Fault cases cover checkpoint hash corruption, re-hashed state corruption, invalid committed boundaries, seed mismatch, and crash/restart convergence.

The first mutation workflow run `32915294812` correctly failed the threshold with two apparent critical survivors. Investigation showed the source-mutant runner was reusing timestamp-valid `.pyc` bytecode between rapid same-size mutations of `conformance.py`; this was a mutation-harness defect, not an oracle relaxation. The runner now purges module bytecode before every mutant and after restoration. Repaired run `32915409420` passed with **11/11 critical mutants killed (100%, required 98%)** and **2/2 high mutants killed (100%, required 95%)**, with zero critical survivors. This is valid threshold evidence for the curated finance-quant reference/conformance mutation inventory; mutation coverage of remaining candidate-specific adapter/normalizer surfaces is still outstanding before final A1 disposition.

## Validation status

Exact path-exhaustion head `85f32858b3e4ee17cf7c1240349fe6f2e6530c05` is fully green: tests `32914556208`, legacy phase-b `32914556200`, bootstrap-assurance `32914556224`, runtime-candidates `32914556234`, callback adapter evaluation `32914556217`, and pre-open/latency evaluation `32914556199`.

Assurance implementation head `54532d38470ddf70bbbadce7ebd0ba022ffe6bf0` has green `a1-assurance` run `32915409420`, runtime-candidates `32915409410`, callback evaluator `32915409402`, and pre-open evaluator `32915409401`. Its full ordinary pytest step also passed in tests run `32915409427`; at the last durable-state update, that workflow's smoke step plus legacy phase-b and bootstrap-assurance were still completing, so this head is not yet recorded as a fully green baseline.

A1 remains **IN_PROGRESS**. Hidden acceptance is still outstanding. Candidate-specific mutation/normalizer fault coverage, broader candidate-level metamorphic/chaos evidence, and the final complete determinism/clean-environment evidence set must still be closed before candidate dispositions. No primary runtime may be selected yet.

## Next exact action

1. Require this durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and the new `a1-assurance` workflow; fix genuine failures without weakening any invariant or mutation threshold.
2. Preserve the native Nautilus `FQ-PROP-015`, deferred-callback `FQ-PROP-021`, published-latency-API ineligibility, and public-path-exhaustion evidence. Do not manufacture conformity through private bindings, future event payload, custom fill logic, or changed order semantics.
3. Extend A1 mutation/fault evidence to the still-eligible LEAN adapter/normalizer/evidence surfaces, including malformed/duplicate runtime output, candidate crash/nonzero exit, timeout/dependency failure, and receipt corruption, all fail-closed. Keep the 0.98 critical / 0.95 high thresholds and zero critical-bypass survivor rule.
4. Establish the opaque hidden-acceptance execution path without reading or exposing sealed cases/labels, then run the authorized hidden corpus externally/through its permitted gate. Do not synthesize public cases and call them hidden.
5. Close any remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations. Only after every required A1 gate is green may issue #15 assign final candidate dispositions (`ADOPT | ADOPT_WITH_CONSTRAINTS | REFERENCE_ONLY | REJECT`), select a primary runtime, and explicitly permit promotion.

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
