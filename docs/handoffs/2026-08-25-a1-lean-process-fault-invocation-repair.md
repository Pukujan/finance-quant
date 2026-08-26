# Handoff — A1 LEAN process fault invocation repair

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

This is an append-only continuation of `2026-08-25-a1-lean-trace-process-fault.md`.

The first `a1-assurance` execution of the new LEAN process-boundary campaign, run `32919228495` on implementation head `8a23f12dd7dbc34f918b70f3b53f31b3ca618fbf`, failed only at the standalone campaign invocation. The independent fault tests had already passed **56/56**. The failure was `ModuleNotFoundError: No module named 'scripts'` because the workflow invoked `python scripts/a1_lean_process_fault_gate.py`; that execution mode places the `scripts/` directory, rather than the repository root, on `sys.path` while the campaign intentionally imports the existing `scripts.run_lean_a1_fill_probe` module.

No execution property, fault expectation, mutation threshold, or oracle was changed. The workflow now invokes the exact same campaign as `python -m scripts.a1_lean_process_fault_gate`, matching the package-import mode already exercised by pytest. Repair head `df2a0a2ed0395275178951663107873b4756d767` launched all seven PR workflows; they were queued/in progress at this handoff update.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, and `a1-assurance`; specifically confirm the process campaign completes and uploads its machine-readable receipt.
2. Preserve the timestamped TRACE classifier repair and the five-critical-mutant LEAN mutation gate; do not relax unknown-stdout handling.
3. Establish the authorized opaque hidden-acceptance execution path without inspecting, copying, or exposing sealed cases/labels.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not begin issue #16 beforehand.
