# Handoff — A1 LEAN clean determinism green

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were re-read before this slice. Property impact remains **STRENGTHEN** only: the execution oracle, candidate pins, PIT boundary, permitted differences, runtime dispositions, trading authority, and sealed-holdout policy were not changed.

The prior durable head `0e6f3543e60a73177254ac1d6869e00588b118d4` is fully green across its seven workflows, including `a1-assurance` process-fault run `32919496473`. That run passed 56 independent reference/metamorphic/fault/LEAN tests, executed all five LEAN process-boundary injected fault classes (`candidate_output_corruption`, `dependency_missing`, `nonzero_exit`, `persisted_evidence_corruption`, `timeout`), and uploaded the passing receipt artifact `9589383666`.

The opaque hidden-acceptance public ingress was subsequently validated green on `b9feb6911b3f29582463daff42e94ec4ae00c132`. No sealed corpus or labels were accessed; genuine hidden acceptance still requires an authorized external clean runner and public A1 seal commitment.

This slice closes the explicit candidate-level `DETERMINISM` and `CLEAN_ENV` obligation for the currently exercised LEAN production public slice. Workflow `a1-lean-clean-determinism` executes three separate fresh Ubuntu runners, each independently checks out exact LEAN commit `185c691b89f28bd68e48d53c02147415134975f0`, builds the production `EquityFillModel.MarketOnOpenFill` probe, executes the unchanged public fixture, canonicalizes the result, and uploads an independent receipt. A fourth job requires all three receipts to be identical and still semantically conforming.

Run `32923522432` passed all four jobs. The closure receipt records candidate hash `8b216968a95ad42fcc308d182d8420a63590a0841b26e04d5874b17fdca9d1cc`, reference hash `a99fe8251b79ccfad3df44a067f2964af6655d15f054eb32d200378f53532555`, canonical production-probe hash `2124613ab196e32cd064bb94a248283ae898aa068f30c18050df0a52e3b6dc90`, three independent clean runs, equivalent receipts, authority `NONE`, and runtime disposition `PENDING`. Artifact `9590680190` has archive digest `sha256:237e77f4787ec5ee04790ddf0a3663ff56f3a899003727ead737dc8ea785771a`.

Exact workflow head `faa5d6e6c79b4009dbf57fef4b9e3611404c5bdc` finished green across all eight workflows: tests `32923522512`, legacy phase-b `32923522390`, bootstrap-assurance `32923522400`, runtime-candidates `32923522431`, callback adapter evaluation `32923522373`, pre-open evaluation `32923522381`, `a1-assurance` `32923522402`, and `a1-lean-clean-determinism` `32923522432`.

A1 remains **IN_PROGRESS**. Hidden acceptance is not passed. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require the documentation head containing this handoff to complete its exact-head validation cycle; fix genuine failures without weakening any test, property, mutation threshold, or authority boundary.
2. Provision/identify the authorized external A1 clean runner plus public `SealRecord`, execute the sealed corpus outside ordinary-agent visibility, and pass only its aggregate `SafeAcceptanceReceipt` through the public ingress. Never browse the private holdout with the current coarse GitHub identity or fabricate hidden evidence.
3. Audit the still-eligible LEAN path against `FQ-PROP-015` through `FQ-PROP-022` for any genuinely remaining candidate-level metamorphic or chaos/fault obligations not already covered by the current receipts, and implement explicit closure only where missing.
4. Preserve all Nautilus nonconformance/ineligibility/path-exhaustion receipts and all green LEAN mutation, process-fault, and clean-determinism evidence.
5. Only after every conjunctive A1 gate is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not advance to issue #16 or change capital/holdout authority beforehand.
