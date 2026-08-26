# Handoff — A1 LEAN timestamped TRACE repair + process fault gate

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read at the current branch head before changes. The branch had advanced beyond the prior handoff, so this run resumed from durable repository state rather than stale conversation state.

This slice is **STRENGTHEN** only. The A1 execution oracle, candidate pins, permitted semantic differences, PIT boundary, runtime dispositions, authority, and sealed-holdout policy are unchanged.

Head `1eb0cef3cd55b0123d7a7db853dd152ea2db7c25` exposed a genuine integration defect: production LEAN emits timestamp-prefixed diagnostics such as `20260825 TRACE:: ...`, while the tightened stdout normalizer accepted `TRACE::` only at column zero. Two ordinary tests failed and the same defect propagated to Phase-B, bootstrap assurance, and runtime-candidates; `a1-assurance` and both Nautilus evaluators remained green.

The classifier now accepts only direct TRACE or TRACE preceded by a constrained LEAN date/date-time leader. Arbitrary stdout and arbitrary lines merely containing `TRACE::` still fail closed. Independent tests cover direct/date/date-time TRACE forms and reject timestamped non-TRACE or arbitrary TRACE-containing text.

The LEAN mutation gate now includes a fifth critical TRACE-leader bypass mutant. Repair head `b8cc43daeb7d6fc34b5b1d8e6df6948e8c8e8c25` passed `a1-assurance` run `32919112339`: the generic mutation gate remained 11/11 critical and 2/2 high killed, and the LEAN gate passed at 100% with zero survivors.

The documented process-level LEAN fault campaign is now implemented and wired into `a1-assurance`. It injects nonzero exit, timeout, missing dependency, corrupted candidate stdout, and corrupted persisted evidence. All five conditions must be classified `FAIL_CLOSED`; persisted evidence must exactly match recomputed authoritative public evidence. The workflow uploads a machine-readable `a1-lean-process-fault-receipt`. Process-fault implementation head `8a23f12dd7dbc34f918b70f3b53f31b3ca618fbf` launched the seven PR workflows, which were still queued/in progress at the durable update.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and `a1-assurance`; fix genuine failures without weakening any invariant or mutation threshold.
2. Confirm and preserve the LEAN process-fault receipt proving fail-closed handling for nonzero exit, timeout, dependency loss, candidate-output corruption, and persisted-evidence corruption.
3. Establish and execute the authorized opaque hidden-acceptance path without reading, copying, or exposing sealed cases/labels. Never substitute public fixtures for hidden acceptance.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations while preserving all Nautilus negative/ineligibility/path-exhaustion evidence.
5. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime. Do not advance to issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-trace-process-fault.md`.
