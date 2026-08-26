# Handoff — A1 opaque hidden-acceptance ingress green

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1
Property impact: **STRENGTHEN** only

The exact opaque-ingress head `b9feb6911b3f29582463daff42e94ec4ae00c132` completed its entire PR validation cycle green. Tests run `32922509511` passed the new hidden-receipt verifier tests; legacy phase-b `32922509458`, bootstrap-assurance `32922509456`, runtime-candidates `32922509640`, callback adapter evaluation `32922509459`, pre-open evaluation `32922509428`, and `a1-assurance` `32922509433` also passed. Bootstrap assurance's contracts, formal TLA, full-validation, and fresh-environment jobs all passed.

The public A1 hidden-acceptance ingress is therefore validated. `finance_quant.acceptance.a1_hidden` consumes only a public `SealRecord` and aggregate-only `SafeAcceptanceReceipt`, while `scripts/verify_a1_hidden_acceptance.py` and `.github/workflows/a1-hidden-acceptance.yml` expose a fail-closed public verification path. Exact schemas, sha256 identities, seal commitment, candidate artifact identity, seal-use budget, passing status, empty failure classes on pass, unique aggregate metric names, and finite metric values are enforced.

No hidden case, label, fixture, or private holdout file was opened, searched, copied, or emitted. The public workflow does not checkout `finance-quant-holdout` and cannot itself satisfy `HIDDEN_ACCEPTANCE`. A real pass still requires an authorized external clean runner, an actual public A1 seal commitment, execution against the exact candidate artifact, and only the safe aggregate receipt flowing back to the public verifier.

Prior assurance evidence remains intact: LEAN's production next-open probe conforms on the public slice; the process-boundary chaos campaign is green and has a durable artifact; mutation gates kill all currently defined critical/high mutants above required thresholds; Nautilus native, callback-deferral, and published-latency paths remain negative/ineligible and public production-native path analysis is exhausted.

A1 remains **IN_PROGRESS**. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Provision or identify the authorized A1 external clean-runner path and public A1 `SealRecord` without granting ordinary agents access to private cases/labels.
2. Execute the sealed corpus externally against the exact candidate artifact, then pass only its aggregate `SafeAcceptanceReceipt` through `a1-hidden-acceptance`.
3. Close remaining LEAN candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault obligations with explicit receipts.
4. Preserve all existing oracle, mutation, fault, and Nautilus path-exhaustion invariants.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not begin issue #16 or change trading/holdout authority beforehand.
