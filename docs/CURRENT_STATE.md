# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=BOOTSTRAP_COMPLETE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**.

Bootstrap issue **#13** is complete. Current work is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, governed by assurance phase **A1** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) remains **PARKED**. Its PIT, IR, property catalog, sealed holdout, mutation-hardening, deterministic rerun, reference-interpreter, TLA+, LEAN/Qlib, and evidence assets remain preserved as legacy baselines/oracles. Do not treat #11 as active sequencing authority.

## Current capability

- Project status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Frontend: roadmap/vertical-slice policy only; **OPERATOR_ONLY** authority
- Sealed holdout: remains isolated; ordinary agents may not inspect exact cases/labels

## A0 bootstrap evidence

A0 completed after the bootstrap branch passed the full validation stack on 2026-08-25. The validated implementation head was `b01e9be2c6dd9eb27a1189dc5454f0e7a61db2ef` before this semantic state-transition commit.

Authoritative successful workflow runs for that validated implementation head:

- tests: run `32850720334` — full pytest + smoke: **PASS**;
- Phase-B legacy oracle: run `32850720245` — benchmark + three-run determinism + `verify --phase-b`: **PASS**;
- bootstrap assurance: run `32850720179` — contracts/docs/property oracles + pinned non-skippable TLA/TLC + full Windows validation + fresh isolated environment: **PASS**.

A0 validation uncovered and fixed real defects rather than weakening gates: legacy TLA syntax/protocol holes, fresh-venv package installation, cross-platform README generated-block checking, temp-directory B1–B5 artifact references, and LEAN custom-data absolute-path nondeterminism.

## Active A1 objective

Issue #15 must select the execution/runtime substrate by evidence, not preference. NautilusTrader and LEAN must be exercised through the same finance-quant execution contracts and normalized receipts.

A1 requires, at minimum, SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential and metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection.

Do **not** start Autonomous Trader v0 (#16) until #15 has an explicit A1 disposition and every required A1 gate passes.

## Next exact action

Start **#15** by writing the execution-runtime conformance specification and property map **before adding/selecting runtime implementation code**. Define common deterministic fixtures, normalized order/fill/account receipts, hidden execution cases, differential comparison rules, mutation targets, and failure-injection scenarios for NautilusTrader and LEAN.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. relevant execution/IR/property specs and tests
