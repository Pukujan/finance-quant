# Handoff — A1 opaque hidden-acceptance ingress green

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read before this slice. Property impact remains **STRENGTHEN** only: candidate pins, execution oracle, PIT boundary, permitted differences, runtime dispositions, trading authority, and sealed-holdout policy are unchanged.

The opaque public hidden-acceptance ingress is now validated on exact head `b9feb6911b3f29582463daff42e94ec4ae00c132`. All seven PR workflows passed: tests `32922509511`, legacy phase-b `32922509458`, bootstrap-assurance `32922509456`, runtime-candidates `32922509640`, callback adapter evaluation `32922509459`, pre-open evaluation `32922509428`, and `a1-assurance` `32922509433`. Bootstrap assurance also passed its fresh-environment job.

`finance_quant.acceptance.a1_hidden`, `scripts/verify_a1_hidden_acceptance.py`, and `.github/workflows/a1-hidden-acceptance.yml` therefore provide a green, fail-closed **aggregate receipt ingress**. The verifier rejects schema extras, malformed digests, commitment/candidate mismatch, exhausted seal uses, non-pass status, passing receipts with failure classes, duplicate aggregate metric names, and non-finite metrics. It does not read or execute private cases or labels.

This is not a hidden-acceptance pass. The actual A1 sealed corpus still requires an authorized external clean runner plus a public A1 `SealRecord`; only the resulting aggregate `SafeAcceptanceReceipt` may be supplied to the public workflow. Public fixtures, fabricated receipts, private-repository browsing with the current coarse identity, or synthetic hidden cases remain prohibited substitutes.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Provision/identify the authorized A1 external clean-runner path and public A1 `SealRecord` without exposing private cases/labels; execute the sealed corpus externally and feed only its aggregate receipt through `a1-hidden-acceptance`.
2. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations for LEAN with explicit receipts.
3. Preserve the green LEAN process-fault and mutation evidence and all Nautilus negative/ineligibility/path-exhaustion evidence.
4. Only after every required A1 gate passes may issue #15 assign final candidate dispositions and select a primary runtime. Do not start issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-opaque-hidden-ingress-green.md`.
