# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_ORACLE_SLICE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**.

Bootstrap issue **#13** is complete. Current work is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, governed by assurance phase **A1** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) remains **PARKED**. Its PIT, IR, property catalog, sealed holdout, mutation-hardening, deterministic rerun, reference-interpreter, TLA+, LEAN/Qlib, and evidence assets remain preserved as legacy baselines/oracles. Do not treat #11 as active sequencing authority.

## Current capability

- Project status: **A1_ORACLE_SLICE**
- Bootstrap machine status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Frontend: roadmap/vertical-slice policy only; **OPERATOR_ONLY** authority
- Sealed holdout: remains isolated; ordinary agents may not inspect exact cases/labels

## A0 bootstrap evidence

A0 completed after the bootstrap branch passed the full validation stack on 2026-08-25. The validated implementation head was `b01e9be2c6dd9eb27a1189dc5454f0e7a61db2ef` before the semantic state-transition commit.

Authoritative successful workflow runs for that validated implementation head:

- tests: run `32850720334` — full pytest + smoke: **PASS**;
- Phase-B legacy oracle: run `32850720245` — benchmark + three-run determinism + `verify --phase-b`: **PASS**;
- bootstrap assurance: run `32850720179` — contracts/docs/property oracles + pinned non-skippable TLA/TLC + full Windows validation + fresh isolated environment: **PASS**.

A0 validation uncovered and fixed real defects rather than weakening gates: legacy TLA syntax/protocol holes, fresh-venv package installation, cross-platform README generated-block checking, temp-directory B1–B5 artifact references, and LEAN custom-data absolute-path nondeterminism.

## Active A1 objective

Issue #15 must select the execution/runtime substrate by evidence, not preference. NautilusTrader and LEAN must be exercised through the same finance-quant execution contracts and normalized receipts.

A1 requires, at minimum, SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential and metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection.

The A1 SDD/PDD is defined in `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md` and `contracts/execution/runtime-conformance-v1.json`. Stable properties `FQ-PROP-015` through `FQ-PROP-022` are now also bound into the global property catalog.

The first executable finance-quant-owned oracle slice now exists:

- `finance_quant/execution/conformance.py` fail-closes on A1 authority/contract drift and validates/canonicalizes normalized receipts;
- `finance_quant/execution/reference.py` is a deliberately tiny independent daily-bar semantic oracle, not a production runtime;
- `tests/test_execution_conformance.py` verifies contract binding, required receipt fields, deterministic canonical hashes, normalized order states, and forbidden identity inputs;
- `tests/test_execution_reference.py` exercises next-event fill timing, partial-liquidity bounds, accounting reconciliation, duplicate idempotency, ambiguous-duplicate rejection, future-known-event isolation, three-run determinism, and zero-liquidity rejection.

This slice does **not** select NautilusTrader or LEAN and grants no paper/live trading authority.

## Validation status for current A1 work

The implementation/property-binding head before durable-state documentation updates was `fabb737032a7cf423836bd921b0d06539d9af46a`.

Local clone/test execution remains unavailable because the automation execution environment cannot resolve `github.com`; this is an environment/network blocker, not a repository test result. GitHub Actions run `32865148522` was queued for that implementation head at the time of this handoff. Exact-head CI must be rechecked after the documentation commits; no A1 gate is claimed complete solely from queued CI.

A1 remains **IN_PROGRESS**. Hidden acceptance, candidate differential evidence, mutation threshold evidence, complete metamorphic coverage, candidate clean-environment evidence, and chaos/fault campaigns remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Verify the exact current branch head in GitHub Actions and fix any regression without weakening tests or invariants.
2. Once the property-binding/reference-oracle slice is green, add the first **thin** candidate adapter behind `contracts/execution/runtime-conformance-v1.json` and exercise only the semantic subset implemented by the independent reference oracle.
3. Add field-class differential comparison and candidate-specific permitted-difference recording before expanding adapter scope.
4. Continue hidden, mutation, metamorphic, repeated determinism, clean-environment, and chaos evidence for both candidates before any runtime disposition.

Do not select a primary runtime until all A1 required gates pass. Do **not** start Autonomous Trader v0 (#16) until #15 has explicit runtime dispositions and every required A1 gate passes.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. `contracts/properties/finance-quant-properties-v1.json`
9. `finance_quant/execution/conformance.py` and `finance_quant/execution/reference.py`
10. relevant execution/IR/property specs and tests
