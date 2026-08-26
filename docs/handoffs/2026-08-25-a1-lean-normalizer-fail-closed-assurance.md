# Handoff — A1 LEAN normalizer fail-closed assurance

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. Starting durable head `3bb38567252c66372c9418fa738edaf98768e709` was fully green across tests, legacy Phase-B, bootstrap assurance, runtime candidates, both Nautilus evaluators, and `a1-assurance` before this slice began.

This slice is **STRENGTHEN** only. It does not change the A1 execution oracle, candidate pins, permitted-difference list, PIT rules, candidate disposition, authority, or sealed-holdout policy.

The LEAN production-probe stdout normalizer now fails closed on unexpected non-JSON output. Only explicit `TRACE::` diagnostic lines may accompany the production result, and the output must contain exactly one JSON object matching engine `LEAN` and scope `EquityFillModel.MarketOnOpenFill`; zero, duplicate, unrelated, array, malformed, or extra JSON objects are rejected. Raw stdout/stderr remain preserved by the production workflow.

Independent public tests now cover explicit TRACE tolerance; unprefixed runtime text rejection; missing, duplicate, unrelated, and non-object result rejection; preservation of the valid public production differential; semantic drift in engine, probe scope, fill status, source event, fill time, instrument, quantity, and price; and candidate-pin authority drift including credentials/CLI enablement.

A candidate-specific mutation gate was added for the LEAN normalizer. It mutates the TRACE prefix guard, extra-JSON guard, engine guard, and credential/CLI guard; all are critical and the gate requires at least 98% kill rate with zero critical survivors. The receipt explicitly records authority `NONE` and sealed-holdout access denied. `a1-assurance` now runs the LEAN public fault tests and candidate-specific mutation gate in addition to the existing generic A1 assurance suite.

Implementation head before this documentation commit was `fad748fd9775c95f33740cd13bc5867dd6e1e79a`. Its exact-head CI cycle was launched. At this handoff update, workflows were still queued/in progress due to the sequence of commits, so no fully-green claim is made for the final documentation head. Earlier intermediate head `17c46edd9f7b448ecde42e49664acbc8b783873b` already had green `a1-assurance` and both Nautilus evaluators while its broader workflows were still completing.

A1 remains **IN_PROGRESS**. Runtime selection is `NONE / PENDING`; trading authority is `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, and `a1-assurance`; inspect and fix genuine failures without weakening any invariant or mutation threshold.
2. Extend LEAN candidate fault evidence to process-level failures not covered by pure normalizer tests: nonzero candidate exit/crash, timeout/dependency failure, and candidate/evidence receipt corruption, all fail closed.
3. Establish and execute the authorized opaque hidden-acceptance path without reading, copying, or exposing sealed cases/labels. Never synthesize public fixtures and call them hidden.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime.
5. Do not advance to issue #16 or change trading/holdout authority until durable state explicitly permits promotion.
