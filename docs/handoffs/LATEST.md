# Handoff — A1 LEAN normalizer fail-closed assurance

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. Starting durable head `3bb38567252c66372c9418fa738edaf98768e709` was fully green across tests, legacy Phase-B, bootstrap assurance, runtime candidates, both Nautilus evaluators, and `a1-assurance` before this slice began.

This slice is **STRENGTHEN** only. The A1 execution oracle, candidate pins, permitted semantic differences, PIT boundary, runtime disposition, authority, and sealed-holdout policy are unchanged.

The LEAN production-probe stdout normalizer now fails closed on unexpected non-JSON output. Only explicit `TRACE::` diagnostics may accompany exactly one JSON object for engine `LEAN` and scope `EquityFillModel.MarketOnOpenFill`. Zero, duplicate, unrelated, array, malformed, or extra JSON objects fail validation. Raw stdout/stderr remain preserved by the production candidate workflow.

Independent public tests cover TRACE tolerance; unexpected stdout; missing/duplicate/unrelated/non-object results; the unchanged valid public production differential; semantic drift in engine, scope, status, source event, fill time, instrument, quantity, and price; and candidate-pin authority drift including credentials/CLI enablement.

A candidate-specific LEAN mutation gate now mutates the TRACE, extra-JSON, engine, and credential/CLI guards. All are critical; the gate requires at least 98% kill rate and zero critical survivors, and its receipt records authority `NONE` plus sealed-holdout denial. `a1-assurance` runs these tests and the mutation gate alongside the existing generic assurance layer.

Implementation head `fad748fd9775c95f33740cd13bc5867dd6e1e79a` launched its exact-head CI cycle. At this durable update, final-head workflows were still queued/in progress because several sequential commits each triggered the PR workflows, so a full-green final-head claim is intentionally withheld.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, and `a1-assurance`; fix genuine failures without weakening any invariant or mutation threshold.
2. Extend LEAN candidate fault evidence to process-level failures: nonzero candidate exit/crash, timeout/dependency failure, and candidate/evidence receipt corruption, all fail closed.
3. Establish and execute the authorized opaque hidden-acceptance path without reading, copying, or exposing sealed cases/labels. Never label public fixtures as hidden acceptance.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime.
5. Do not advance to issue #16 or change trading/holdout authority until durable state explicitly permits promotion.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-normalizer-fail-closed-assurance.md`.
