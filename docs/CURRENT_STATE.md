# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A1_LEAN_DIFFERENTIAL_SLICE assurance=A1 active_issue=15 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**. Current work is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff**, governed by assurance phase **A1** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) remains **PARKED** and preserved as a legacy oracle. Do not treat it as active sequencing authority.

## Current capability and authority

- Project status: **A1_LEAN_DIFFERENTIAL_SLICE**
- Bootstrap machine status: **BOOTSTRAP_COMPLETE**
- Assurance phase: **A1 — OSS execution/runtime bakeoff**
- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Sealed holdout: isolated; ordinary agents may not inspect exact cases/labels

## A1 objective and mandatory gates

Issue #15 must select the execution/runtime substrate by evidence, not preference. LEAN and NautilusTrader must be exercised through the same finance-quant contracts and normalized receipts. A1 is conjunctive: SDD/PDD, static/IR validation, unit/regression, property/state-machine testing, hidden acceptance, mutation testing, differential/metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection must all pass before disposition or promotion.

The A1 SDD/PDD is `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`; the executable runtime contract is `contracts/execution/runtime-conformance-v1.json`. Stable properties `FQ-PROP-015` through `FQ-PROP-022` remain bound in the property catalog.

## LEAN production candidate status

The finance-quant LEAN slice directly exercises pinned LEAN commit `185c691b89f28bd68e48d53c02147415134975f0` through production `EquityFillModel.MarketOnOpenFill`, without brokerage credentials or the LEAN CLI, against `fixtures/execution/a1-lean-fill-probe-v1.json`. Candidate evidence remains `runtime_disposition: PENDING` and `authority: NONE`.

During 2026-08-25 continuation, harness defects were corrected without changing the oracle, fixture, fill expectation, PIT timing rule, acceptance threshold, or authority boundary. The final determinism workflow preserves raw LEAN stdout/stderr but compares canonical extracted probe JSON plus normalized evidence across three independent runs.

Exact-head runtime-candidates run `32884104244` completed **SUCCESSFULLY** on implementation head `aeb5cd4ab6f53a966bbc344e45afde1b2a552573`. Its `lean-production-fill-probe` job verified the candidate pin/license, built the production LEAN fill-model probe, ran three deterministic candidate probes, and uploaded A1 receipts. The prior semantic evidence remained the contracted fill (`quantity=5`, `price=11`, `fill_time=2026-06-02T13:30:00Z`, source `bar-2`) with identical canonical candidate/reference receipt hashes across repeated runs.

This is a genuine LEAN production-slice pass, but it is **not** an A1 runtime disposition. NautilusTrader evidence and all remaining conjunctive A1 gates are still required.

## Validation status

- Runtime-candidates run `32884104244`: **PASS** for the credential-free LEAN production fill probe and three-run canonical determinism.
- Durable-state head `30b957c1f1b51d771177f5b686aaacd57bed74a9` ordinary tests run `32884427022`: `927 passed, 25 skipped, 2 failed`; both failures were caused by `docs/handoffs/LATEST.md` using `Next:` instead of the validator-required literal `Next exact action` heading.
- Bootstrap-assurance run `32884427008`: failed in fresh-environment/full-validation/contracts for the same handoff-format contract; the formal TLA job passed.
- Commit `99ee4a1574d00ba4eff67b5e24aeb806cbe11a57` repaired the durable handoff heading and recorded the LEAN green receipt without modifying runtime semantics, tests, properties, or authority.

A1 remains **IN_PROGRESS**. NautilusTrader production candidate evidence, hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete candidate chaos/fault campaigns, and final conjunctive gate receipts remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Recheck the exact-head CI triggered by the durable handoff/state repair and require ordinary tests/bootstrap-assurance to return green; fix any real failure without weakening tests or invariants.
2. If that baseline is green, implement the corresponding thin credential-free **NautilusTrader** production candidate evidence for exactly the same public daily-bar subset and normalized comparison classes.
3. Continue the remaining A1 hidden, mutation, metamorphic, deterministic/clean-environment, and chaos/fault evidence for both candidates.
4. Only after every conjunctive A1 gate passes may #15 record candidate dispositions and select a primary runtime.

Do not start #16, enable autonomous paper authority, enable live capital, or inspect sealed-holdout exact cases/labels while A1 remains incomplete.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #15
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
7. `contracts/execution/runtime-conformance-v1.json`
8. relevant execution adapter/probe/workflow files and tests
