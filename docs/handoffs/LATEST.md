# Handoff — A1 LEAN process fault invocation repair

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read from the current durable branch before changes. This slice remains **STRENGTHEN** only: the A1 oracle, candidate pins, PIT boundary, permitted differences, runtime dispositions, authority, and sealed-holdout policy are unchanged.

The timestamped LEAN TRACE repair remains intact. The normalizer accepts only direct TRACE or TRACE preceded by a constrained LEAN date/date-time leader, while arbitrary stdout and arbitrary lines merely containing `TRACE::` fail closed. Repair head `b8cc43daeb7d6fc34b5b1d8e6df6948e8c8e8c25` passed `a1-assurance` run `32919112339`, including 11/11 critical plus 2/2 high generic mutants and the LEAN-specific gate at 100% with zero survivors.

The process-boundary LEAN chaos/fault campaign injects nonzero exit, timeout, missing dependency, corrupted candidate stdout, and corrupted persisted evidence. On its first `a1-assurance` run (`32919228495`, head `8a23f12dd7dbc34f918b70f3b53f31b3ca618fbf`), all independent fault tests passed **56/56**, but the standalone campaign step failed before execution with `ModuleNotFoundError: No module named 'scripts'`. The workflow had invoked the package-importing campaign by file path, which placed `scripts/` rather than the repository root on `sys.path`.

No fault semantics or test expectations were changed. The workflow now invokes the same campaign as `python -m scripts.a1_lean_process_fault_gate`, matching the import mode already exercised by pytest. Repair head `df2a0a2ed0395275178951663107873b4756d767` launched all seven PR workflows; they were queued/in progress when this handoff was written.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and `a1-assurance`; specifically confirm the LEAN process-fault campaign completes and uploads its receipt.
2. Preserve the timestamped TRACE classifier and five-critical-mutant LEAN gate; fix failures without weakening unknown-stdout or authority guards.
3. Establish and execute the authorized opaque hidden-acceptance path without reading, copying, or exposing sealed cases/labels. Never substitute public fixtures for hidden acceptance.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations while preserving Nautilus negative/ineligibility/path-exhaustion evidence.
5. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime. Do not advance to issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-process-fault-invocation-repair.md`.
