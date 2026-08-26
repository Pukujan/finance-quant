# Handoff — A1 opaque hidden-acceptance ingress

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read from the durable branch before changes. This slice is **STRENGTHEN** only: candidate pins, execution oracle, PIT boundary, permitted differences, runtime dispositions, trading authority, and sealed-holdout policy are unchanged.

The prior durable head `0e6f3543e60a73177254ac1d6869e00588b118d4` is fully green across all seven PR workflows. In particular, `a1-assurance` run `32919496473` completed the repaired LEAN process-boundary campaign and uploaded `a1-lean-process-fault-receipt` artifact `9589383666` with digest `sha256:51d80e6f6d3d811e17f748a02addb95e481fee1b148c15416bb776035c737c6d`.

This slice establishes the public half of A1 hidden acceptance without reading or searching private cases/labels. `finance_quant.acceptance.a1_hidden` verifies only a public `SealRecord` and aggregate-only `SafeAcceptanceReceipt`; it fails closed on schema extras, digest/commitment/candidate mismatch, exhausted use numbers, non-pass status, passing receipts with failure classes, duplicate aggregate metrics, and non-finite aggregates. `scripts/verify_a1_hidden_acceptance.py` exposes the same verifier, and `.github/workflows/a1-hidden-acceptance.yml` is a manual aggregate-receipt ingress workflow with no private-holdout checkout or execution path.

`docs/acceptance/SEALED_INTERFACE.md` now explicitly states that this public ingress does **not** satisfy `HIDDEN_ACCEPTANCE`. An authorized external clean runner must execute the actual sealed A1 corpus and emit only a safe aggregate receipt tied to the exact public candidate artifact and public seal commitment. Public fixtures, fabricated receipts, or the repository's coarse GitHub identity are not substitutes.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and `a1-assurance`; fix genuine verifier failures without weakening its fail-closed rules.
2. Provision/identify the authorized A1 external clean-runner path and public A1 `SealRecord` without exposing private cases/labels.
3. Execute the sealed A1 corpus externally against the exact candidate artifact, then feed only the aggregate `SafeAcceptanceReceipt` through `a1-hidden-acceptance`.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations.
5. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime. Do not start issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-opaque-hidden-acceptance-ingress.md`.
