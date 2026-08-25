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

During 2026-08-25 continuation, two additional harness defects were found and corrected without changing the oracle, fixture, fill expectation, PIT timing rule, acceptance threshold, or authority boundary:

1. Run `32876861792` showed the standalone probe reached LEAN `Symbol.Create` without an `IMapFileProvider`. The harness now constructs an equity SID explicitly with `SecurityIdentifier.GenerateEquity(..., mapSymbol: false)` and `new Symbol(sid, value)`, preserving the equity type/market while excluding unrelated map-file lookup. Commit: `30936a2d6381ea4fa7a5f7a20c5d4ed07959dfcd`.
2. Run `32883152940` then proved the production fill itself succeeded, but LEAN emitted a TRACE line before the JSON result. `scripts/run_lean_a1_fill_probe.py` now tolerates non-JSON runtime log lines while requiring exactly one JSON object with the expected LEAN engine/scope; zero or multiple matches fail closed. Targeted tests cover TRACE-prefix, missing-result, and duplicate-result cases. Commits: `0c3a30523388334fc2161635531de38efafad259`, `625059cf04e400531b535cd8495d5a2329b2b070`.

On exact head `625059cf04e400531b535cd8495d5a2329b2b070`, runtime-candidates run `32883830248` produced three successful semantic evidence files. Each had `semantic_conformance: PASS`, identical candidate receipt hash `8b216968a95ad42fcc308d182d8420a63590a0841b26e04d5874b17fdca9d1cc`, identical reference receipt hash `a99fe8251b79ccfad3df44a067f2964af6655d15f054eb32d200378f53532555`, and the expected LEAN fill (`quantity=5`, `price=11`, `fill_time=2026-06-02T13:30:00Z`, source `bar-2`). The workflow nevertheless failed because it byte-compared raw stdout files whose LEAN TRACE prefixes contain different wall-clock timestamps.

Commit `aeb5cd4ab6f53a966bbc344e45afde1b2a552573` preserves every raw stdout/stderr artifact but moves the three-run determinism assertion to canonical extracted probe JSON plus normalized evidence. This does not weaken the determinism gate: all semantic candidate fields and normalized receipt evidence must still be byte-identical across all three independent runs, while nondeterministic diagnostic timestamps are retained rather than treated as runtime semantics.

Exact-head runtime-candidates run `32884104244` was still **IN_PROGRESS** when this state was written. Do not claim the LEAN candidate workflow is green until that exact run completes successfully.

## Validation status

- Prior exact-head ordinary tests before the final determinism-workflow correction passed on `30936a2d6381ea4fa7a5f7a20c5d4ed07959dfcd` via tests run `32883152941`.
- Head `625059cf04e400531b535cd8495d5a2329b2b070` launched tests `32883830252`, Phase-B `32883830258`, and bootstrap-assurance runs while the candidate evidence above was collected.
- Final implementation head before this durable-state commit is `aeb5cd4ab6f53a966bbc344e45afde1b2a552573`; exact-head runtime-candidates `32884104244` and the ordinary assurance workflows are still running/rechecking.

A1 remains **IN_PROGRESS**. NautilusTrader production candidate evidence, hidden acceptance, mutation-threshold evidence, broader metamorphic coverage, complete candidate chaos/fault campaigns, and final conjunctive gate receipts remain outstanding. No primary runtime may be selected yet.

## Next exact action

1. Re-read the authority chain and recheck exact-head runtime-candidates run `32884104244` plus exact-head tests, Phase-B, and bootstrap-assurance workflows. If the LEAN run fails, inspect the preserved `a1-lean-production-fill-probe` artifact and fix only the harness/runtime integration; do not weaken the oracle, three-run semantic determinism, PIT, or authority invariants.
2. If the exact LEAN candidate run passes, record that receipt and implement the corresponding thin credential-free **NautilusTrader** production candidate evidence for exactly the same public daily-bar subset and comparison classes.
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
