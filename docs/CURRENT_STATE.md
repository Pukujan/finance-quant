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

Property impact for the latest slices is **STRENGTHEN** only. The A1 oracle, candidate pins, permitted-difference policy, PIT boundary, and authority contract were not changed.

`FQ-PROP-022` has an explicit checkpoint/restart convergence oracle. `restart_daily_reference_from_checkpoint` accepts a checkpoint only when its canonical hash, runtime/fixture/seed identity, committed boundary, and full deterministic prefix state agree with the immutable fixture; a re-hashed but state-corrupted checkpoint still fails closed. The final replay is linked to the validated checkpoint and must converge to the uninterrupted authoritative execution state.

A dedicated `a1-assurance` workflow runs the owned reference/conformance fault and metamorphic suite plus source mutation testing. Metamorphic relations cover all six input permutations of the three-event public fixture, uniform timestamp shifts, insertion of a future-known decoy, and monotonicity under increased eligible liquidity. Fault cases cover checkpoint hash corruption, re-hashed state corruption, invalid committed boundaries, seed mismatch, and crash/restart convergence.

The first mutation workflow run `32915294812` correctly failed the threshold with two apparent critical survivors. Investigation showed the source-mutant runner was reusing timestamp-valid `.pyc` bytecode between rapid same-size mutations of `conformance.py`; this was a mutation-harness defect, not an oracle relaxation. The runner now purges module bytecode before every mutant and after restoration. Repaired run `32915409420` passed with **11/11 critical mutants killed (100%, required 98%)** and **2/2 high mutants killed (100%, required 95%)**, with zero critical survivors.

The still-eligible LEAN production normalizer is fail-closed. `load_probe_result` permits only known LEAN `TRACE::` diagnostic shapes and exactly one JSON object matching engine `LEAN` and scope `EquityFillModel.MarketOnOpenFill`; zero, duplicate, unrelated, array/non-object, malformed, extra JSON objects, or arbitrary non-JSON stdout are rejected. A CI-discovered integration defect showed that production LEAN prefixes TRACE diagnostics with a runtime timestamp (`20260825 TRACE:: ...`). The classifier now accepts only direct TRACE or a constrained date/date-time leader followed by TRACE, while rejecting arbitrary text merely containing `TRACE::`.

Independent tests cover direct and timestamped TRACE forms, arbitrary/unrecognized stdout, missing/duplicate/unrelated/non-object results, the unchanged valid public production differential, semantic drift in engine/scope/status/source event/fill time/instrument/quantity/price, and candidate-pin authority drift. The candidate-specific LEAN mutation gate now includes a fifth critical mutant that bypasses the timestamp/TRACE leader guard. Run `32919112339` passed the generic gate at **11/11 critical and 2/2 high mutants killed**, and the LEAN-specific gate at **100% kill rate with zero survivors**.

A process-boundary LEAN chaos/fault campaign is implemented and wired into `a1-assurance`. It injects a nonzero candidate exit, timeout, missing dependency, corrupted candidate stdout, and corrupted persisted evidence. Every injected case must produce a `FAIL_CLOSED` disposition, authority `NONE`, and no sealed-holdout access; persisted evidence is accepted only when it exactly matches recomputed authoritative public evidence. This is an evaluator/control-boundary campaign and does not enable credentials, CLI trading authority, paper execution, or live capital.

The opaque A1 hidden-acceptance **public ingress** is now implemented without accessing the private holdout. `finance_quant.acceptance.a1_hidden` accepts only the public `SealRecord` commitment and aggregate-only `SafeAcceptanceReceipt`, rejects extra fields, invalid digest identities, commitment/candidate mismatches, exhausted use numbers, non-pass status, failure classes on a passing receipt, duplicate aggregate metric names, and non-finite aggregate values. `scripts/verify_a1_hidden_acceptance.py` exposes the same fail-closed verifier, and `.github/workflows/a1-hidden-acceptance.yml` is a manual receipt-ingress workflow that has no holdout checkout or hidden-case execution path. This does **not** satisfy `HIDDEN_ACCEPTANCE` by itself: the actual A1 seal commitment and passing aggregate receipt must still be produced by an authorized external clean runner that ordinary agents cannot inspect.

## Validation status

Exact path-exhaustion head `85f32858b3e4ee17cf7c1240349fe6f2e6530c05` is fully green: tests `32914556208`, legacy phase-b `32914556200`, bootstrap-assurance `32914556224`, runtime-candidates `32914556234`, callback adapter evaluation `32914556217`, and pre-open/latency evaluation `32914556199`.

The durable baseline entering the LEAN-normalizer slice, `3bb38567252c66372c9418fa738edaf98768e709`, was verified fully green across all seven current workflows: tests, legacy phase-b, bootstrap-assurance, runtime-candidates, callback adapter evaluation, pre-open evaluation, and `a1-assurance`.

Documentation head `1eb0cef3cd55b0123d7a7db853dd152ea2db7c25` exposed two ordinary-test failures in `tests/test_lean_a1_probe_output.py`: the normalizer rejected production-shaped `20260825 TRACE::` diagnostics because it required `TRACE::` at column zero. The same defect caused downstream tests, Phase-B, bootstrap-assurance, and runtime-candidates to fail; `a1-assurance` and both Nautilus evaluators remained green. This was repaired without changing the execution oracle or permitted-difference policy.

Repair head `b8cc43daeb7d6fc34b5b1d8e6df6948e8c8e8c25` passed `a1-assurance` run `32919112339`, including the strengthened five-mutant LEAN gate at 100%.

The first process-fault implementation run, `32919228495` on head `8a23f12dd7dbc34f918b70f3b53f31b3ca618fbf`, passed all **56** independent reference/metamorphic/fault/LEAN tests and the mutation job. Its standalone process campaign failed before injection with `ModuleNotFoundError: No module named 'scripts'` because the workflow invoked the package-importing script by file path. The workflow invocation was repaired to `python -m scripts.a1_lean_process_fault_gate`; no fault semantics, oracle, or tests changed.

Exact repair/documentation head `0e6f3543e60a73177254ac1d6869e00588b118d4` is now fully green across all seven workflows: tests `32919496520`, legacy phase-b `32919496528`, bootstrap-assurance `32919496431`, runtime-candidates `32919496478`, callback adapter evaluation `32919496575`, pre-open evaluation `32919496514`, and `a1-assurance` `32919496473`. The `a1-assurance` metamorphic-chaos job completed the LEAN process-boundary campaign and uploaded artifact `a1-lean-process-fault-receipt` (`9589383666`, digest `sha256:51d80e6f6d3d811e17f748a02addb95e481fee1b148c15416bb776035c737c6d`); mutation receipts were also uploaded.

The new opaque-ingress implementation reached code/workflow head `fca142ee86aa886f100b127a9e1bcc80b4657a98`; exact-head PR workflows had not yet appeared at the durable update, so no green claim is made for that implementation or the subsequent documentation head until its own validation cycle completes.

A1 remains **IN_PROGRESS**. Hidden acceptance remains outstanding until an authorized external clean runner produces a passing aggregate receipt bound to an actual A1 public seal and exact candidate artifact. Candidate-level repeated-determinism/clean-environment closure and any remaining metamorphic/chaos obligations must also be established before candidate dispositions. No primary runtime may be selected yet.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and `a1-assurance`; fix genuine failures in the new opaque verifier without weakening its exact-schema, commitment, candidate-hash, use-budget, or fail-closed rules.
2. Preserve the now-green LEAN process-fault receipt, timestamped TRACE classifier, mutation thresholds, and Nautilus negative/ineligibility/path-exhaustion evidence.
3. Provision/identify the authorized A1 external clean-runner path and public A1 `SealRecord` without allowing ordinary agents to inspect private cases/labels. Execute the sealed corpus externally, then feed only its aggregate `SafeAcceptanceReceipt` through `a1-hidden-acceptance`. Do not use this repository's coarse GitHub identity to read the holdout and do not fabricate a receipt.
4. Close any remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations for the still-eligible LEAN path.
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
