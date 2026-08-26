# Handoff — A1 LEAN chaos/fault closure

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state sources were re-read before changes. Property impact remains **STRENGTHEN** only: candidate pins, execution semantics, PIT rules, permitted differences, runtime dispositions, trading authority, and sealed-holdout restrictions were not changed.

The public A1 audit closed two previously implicit metamorphic relations and then found missing explicit LEAN process-boundary coverage for several contract-named fault classes. The metamorphic suite now explicitly enforces non-negative fee monotonicity and equivalent liquidity-bounded split-execution economics in addition to canonical key order, duplicate idempotence, event permutations, time shifts, future-known decoys, liquidity monotonicity, and repeated determinism.

The LEAN chaos campaign was expanded through commits `2121870bed04907e3a524d672655a0164a0820e1` and `2ede511d00f5213fdc266003e3280b21d1252e0b`. It now injects `nonzero_exit`, `runtime_exception`, `timeout`, `dependency_missing`, `candidate_output_corruption`, `duplicate_delivery`, `malformed_payload`, `invalid_reorder`, `dropped_event`, `crash_before_commit`, `crash_after_commit`, `restart_replay`, `persisted_evidence_corruption`, and contract-named `persisted_state_corruption`.

All non-committed faults must fail closed with authority `NONE`. The only recovery cases are `crash_after_commit` and `restart_replay`, which require exact persisted authoritative public evidence to revalidate against recomputed evidence before returning `RECOVERED_COMMITTED`; they grant no trading authority.

`a1-assurance` run `32926137710` passed the expanded metamorphic/chaos job and both mutation jobs. Artifact `a1-lean-process-fault-receipt` is `9591573749`, digest `sha256:736d60345a54e626f2d39317e701600a9ac99c6ccd93d9f590bb4ecb105f6a42`. On code head `2ede511d00f5213fdc266003e3280b21d1252e0b`, ordinary tests, runtime-candidates, both Nautilus evaluators, `a1-assurance`, and LEAN clean-determinism are green; legacy Phase-B and bootstrap-assurance were still completing when this handoff was persisted, so that code head is not yet claimed fully green across all eight workflows.

The public metamorphic/chaos audit is now closed for the current reference/LEAN slice. A1 remains **IN_PROGRESS** because genuine `HIDDEN_ACCEPTANCE` still requires an authorized external clean runner and actual public A1 seal-bound aggregate `SafeAcceptanceReceipt`. Ordinary agents may not inspect exact sealed cases or labels. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled.

## Next exact action

1. Require the chaos code head and final durable documentation head to finish the full eight-workflow exact-head validation matrix; fix genuine failures without weakening tests or invariants.
2. Once that public matrix is green, obtain genuine `HIDDEN_ACCEPTANCE` only through the authorized external clean-runner/sealed interface and ingest only its aggregate receipt. Never inspect or fabricate hidden evidence.
3. Preserve Nautilus negative/ineligibility/path-exhaustion evidence plus LEAN production differential, mutation, metamorphic, process-fault, and clean-determinism receipts.
4. Only after every conjunctive A1 gate, including hidden acceptance, is green may issue #15 assign final candidate dispositions and select a primary runtime. Do not start issue #16 or change trading/holdout authority beforehand.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-chaos-fault-closure.md`.
