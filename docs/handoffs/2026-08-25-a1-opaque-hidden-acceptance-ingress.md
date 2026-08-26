# Handoff — A1 opaque hidden-acceptance ingress

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1
Property impact: **STRENGTHEN** only

Required governance/state files were re-read from the durable branch before changes. No candidate pin, execution oracle, PIT rule, permitted difference, runtime disposition, trading authority, or sealed-holdout authority changed.

The prior durable head `0e6f3543e60a73177254ac1d6869e00588b118d4` is fully green across all seven current PR workflows: tests `32919496520`, legacy phase-b `32919496528`, bootstrap-assurance `32919496431`, runtime-candidates `32919496478`, callback adapter evaluation `32919496575`, pre-open evaluation `32919496514`, and `a1-assurance` `32919496473`. The `a1-assurance` metamorphic-chaos job completed the repaired LEAN process-boundary fault campaign and uploaded `a1-lean-process-fault-receipt` artifact `9589383666` with digest `sha256:51d80e6f6d3d811e17f748a02addb95e481fee1b148c15416bb776035c737c6d`.

This slice establishes the public half of A1 hidden acceptance without reading or searching private cases/labels. `finance_quant.acceptance.a1_hidden` verifies only a public `SealRecord` plus aggregate-only `SafeAcceptanceReceipt`. It rejects schema extras, malformed sha256 identities, seal/receipt commitment mismatch, candidate-artifact mismatch, exhausted seal-use numbers, non-pass status, failure classes attached to a passing receipt, duplicate aggregate metric names, and non-finite aggregate values. Tests cover these fail-closed boundaries.

`scripts/verify_a1_hidden_acceptance.py` exposes the verifier as a CLI and emits only `PASS` or `FAIL_CLOSED` with authority `NONE`. `.github/workflows/a1-hidden-acceptance.yml` is a manual public receipt-ingress workflow. It accepts only public seal JSON, aggregate receipt JSON, and the expected candidate artifact hash; it does not checkout or execute the private holdout and therefore cannot by itself satisfy `HIDDEN_ACCEPTANCE`.

`docs/acceptance/SEALED_INTERFACE.md` now makes the A1 boundary explicit: the actual sealed corpus must execute in an authorized external clean runner, and only its safe aggregate receipt may flow back to the public verifier. Public fixtures, synthetic hidden cases, locally fabricated receipts, or the current repository's coarse GitHub identity are not substitutes.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed. The actual A1 public seal commitment and externally generated passing aggregate receipt remain outstanding, as do any remaining candidate-level determinism/clean-environment/metamorphic/chaos closure obligations.

## Next exact action

1. Require the final durable-state head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, `a1-nautilus-adapter-evaluation`, `a1-nautilus-preopen-evaluation`, and `a1-assurance`; fix verifier failures without weakening exact-schema, commitment, candidate-hash, use-budget, or fail-closed rules.
2. Provision or identify the authorized A1 external clean-runner path and public A1 `SealRecord` without allowing ordinary agents to inspect private cases/labels.
3. Execute the sealed A1 corpus externally against the exact public candidate artifact, then feed only the resulting aggregate `SafeAcceptanceReceipt` through `a1-hidden-acceptance`. Never fabricate or synthesize hidden evidence.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations while preserving Nautilus path-exhaustion evidence and LEAN mutation/fault evidence.
5. Only after every required A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not start issue #16 or change trading/holdout authority beforehand.
