# Handoff — A1 LEAN timestamped TRACE repair + process fault gate

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read at the then-current branch head before changes: `AGENTS.md`, `docs/CURRENT_STATE.md`, GitHub issue #15, `docs/handoffs/LATEST.md`, and `contracts/assurance/capability-assurance-v1.json`. The branch had advanced beyond the prior handoff, so work resumed from current head rather than stale chat state.

This slice is **STRENGTHEN** only. The A1 execution oracle, LEAN/Nautilus pins, PIT boundary, permitted-difference policy, runtime dispositions, trading authority, and sealed-holdout policy were not changed.

Exact head `1eb0cef3cd55b0123d7a7db853dd152ea2db7c25` exposed two ordinary-test failures in `tests/test_lean_a1_probe_output.py`. Production-shaped LEAN diagnostics are emitted as `20260825 TRACE:: ...`; the newly tightened normalizer only accepted `TRACE::` at column zero. This also caused downstream Phase-B/bootstrap/runtime-candidate failures. `a1-assurance` and both Nautilus evaluators were green, establishing that the failure was the production stdout classifier rather than the execution oracle.

`load_probe_result` now accepts only direct TRACE or TRACE preceded by a constrained LEAN date/date-time leader. Arbitrary runtime text and arbitrary text merely containing `TRACE::` still fail closed. Independent tests cover direct TRACE, date-prefixed TRACE, date-time-prefixed TRACE, timestamped non-TRACE text, and invalid arbitrary TRACE-containing text.

The LEAN mutation gate gained a fifth critical mutant, `A1-LEAN-TRACE-LEADER-BYPASS`, which replaces the constrained classifier with a permissive substring test. Repair head `b8cc43daeb7d6fc34b5b1d8e6df6948e8c8e8c25` passed `a1-assurance` run `32919112339`: generic mutation remained 11/11 critical and 2/2 high killed; the LEAN-specific mutation gate passed at 100% with zero survivors.

The documented process-level LEAN chaos/fault slice is also implemented. `scripts/a1_lean_process_fault_gate.py` injects nonzero exit, timeout, missing dependency, corrupted candidate stdout, and corrupted persisted evidence. Every injected condition must classify `FAIL_CLOSED`; persisted evidence is accepted only when it exactly equals recomputed authoritative evidence from the unchanged public fixture. `tests/test_a1_lean_process_fault_gate.py` independently checks the healthy process path, exact persisted-evidence validation, and all injected fault dispositions. `a1-assurance` now runs the campaign and uploads `a1-lean-process-fault-receipt`.

Process-fault implementation head `8a23f12dd7dbc34f918b70f3b53f31b3ca618fbf` launched all seven PR workflows. They were queued/in progress at the durable documentation update; the final documentation head must therefore complete its own exact-head cycle before being called fully green.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final documentation head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, and `a1-assurance`; fix genuine failures without weakening invariants or mutation thresholds.
2. Confirm and retain the uploaded LEAN process-fault receipt proving fail-closed behavior for all five injected process/evidence faults.
3. Establish the authorized opaque hidden-acceptance execution path without reading, copying, or exposing sealed cases/labels; do not substitute public fixtures for hidden acceptance.
4. Close any remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations. Preserve Nautilus negative/ineligibility/path-exhaustion evidence unchanged.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions, select a primary runtime, and explicitly permit promotion. Do not begin issue #16 beforehand.
