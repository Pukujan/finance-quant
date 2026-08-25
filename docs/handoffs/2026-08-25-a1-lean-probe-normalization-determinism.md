# Handoff — A1 LEAN production probe normalization/determinism

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_LEAN_DIFFERENTIAL_SLICE`

## Completed this continuation

Required authority/state was read before mutation: `AGENTS.md`, `docs/CURRENT_STATE.md`, GitHub issue #15, `docs/handoffs/LATEST.md`, `contracts/assurance/capability-assurance-v1.json`, and the A1 conformance plan.

The previously pending LEAN run `32876861792` was confirmed failed only in candidate execution. Preserved diagnostics showed a standalone-harness `Symbol.Create` map-file-provider dependency, not a fill-semantic mismatch. The probe now constructs the equity security identifier explicitly with `mapSymbol: false`; commit `30936a2d6381ea4fa7a5f7a20c5d4ed07959dfcd`.

The next exact candidate run `32883152940` compiled and reached the actual production fill successfully. Its raw stdout contained a LEAN TRACE line followed by a valid result JSON. The normalizer had assumed the whole file was JSON, so parsing—not LEAN semantics—failed. `scripts/run_lean_a1_fill_probe.py` now requires exactly one expected LEAN production-result object while tolerating non-JSON runtime log lines, with targeted zero/one/multiple-result tests. Commits `0c3a30523388334fc2161635531de38efafad259` and `625059cf04e400531b535cd8495d5a2329b2b070`.

Runtime-candidates run `32883830248` on `625059cf04e400531b535cd8495d5a2329b2b070` then produced three successful, identical semantic evidence receipts. All three report `semantic_conformance: PASS`, candidate hash `8b216968a95ad42fcc308d182d8420a63590a0841b26e04d5874b17fdca9d1cc`, reference hash `a99fe8251b79ccfad3df44a067f2964af6655d15f054eb32d200378f53532555`, and the contracted LEAN fill (`5 @ 11`, `2026-06-02T13:30:00Z`, source `bar-2`). The workflow still failed only because raw LEAN TRACE prefixes include per-run wall-clock timestamps and the workflow byte-compared raw stdout.

Commit `aeb5cd4ab6f53a966bbc344e45afde1b2a552573` keeps raw stdout/stderr for diagnostics but makes the three-run determinism gate compare canonical extracted probe JSON and normalized evidence. No semantic comparison, fixture, PIT constraint, acceptance threshold, or authority invariant was weakened.

## Validation state

- tests run `32883152941` on the preceding exact implementation head: **PASS**.
- runtime-candidates `32883830248`: semantic probe/evidence **PASS x3**; workflow overall **FAIL** only at invalid raw-log byte comparison.
- final code/workflow head before durable documentation: `aeb5cd4ab6f53a966bbc344e45afde1b2a552573`.
- exact-head runtime-candidates `32884104244`: **IN_PROGRESS** at handoff time.
- exact-head tests/Phase-B/bootstrap-assurance workflows are also re-running; do not record final gate success until they complete.

A1 remains **IN_PROGRESS**. No runtime disposition was made. Trading authority remains **NONE**; autonomous paper and live capital remain **DISABLED**. No sealed-holdout exact cases/labels were accessed.

## Next exact action

1. Recheck runtime-candidates `32884104244` and the exact-head ordinary workflows. If LEAN fails, inspect the preserved candidate artifact and fix only the integration defect without weakening semantic determinism, differential/PIT, or authority gates.
2. After a genuine exact-head LEAN pass, record the receipt and proceed within issue #15 to equivalent credential-free **NautilusTrader** production candidate evidence for the same public daily-bar subset.
3. Complete the remaining conjunctive A1 hidden acceptance, mutation, metamorphic, determinism/clean-environment, and chaos/fault evidence for both candidates.
4. Do not select a primary runtime, start #16, or enable any trading authority until every required A1 gate passes.
