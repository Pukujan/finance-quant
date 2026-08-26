# Handoff — A1 LEAN chaos/fault closure

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state sources were re-read before this slice. Property impact remains **STRENGTHEN** only: candidate pins, execution semantics, PIT rules, permitted differences, runtime dispositions, trading authority, and sealed-holdout restrictions were not changed.

The public chaos/fault audit found that the existing LEAN process-boundary campaign covered process exit, timeout, missing dependency, candidate-output corruption, and persisted-evidence corruption, but several fault classes explicitly named by the A1 runtime contract were not represented on the stateless public probe boundary.

Commits `2121870bed04907e3a524d672655a0164a0820e1` and `2ede511d00f5213fdc266003e3280b21d1252e0b` expand the campaign and its independent tests. The campaign now injects and records: `nonzero_exit`, `runtime_exception`, `timeout`, `dependency_missing`, `candidate_output_corruption`, `duplicate_delivery`, `malformed_payload`, `invalid_reorder`, `dropped_event`, `crash_before_commit`, `crash_after_commit`, `restart_replay`, `persisted_evidence_corruption`, and contract-named `persisted_state_corruption`.

All non-committed faults must fail closed with authority `NONE`. `crash_after_commit` and `restart_replay` are the only recovery cases: they are accepted solely when exact persisted authoritative public evidence is revalidated byte-for-semantic equality against recomputed evidence, and their disposition is `RECOVERED_COMMITTED`; they still grant no trading authority. No broker credentials, paper/live execution, custom fill logic, or sealed-holdout access was introduced.

`a1-assurance` run `32926137710` passed the expanded metamorphic/chaos job and both mutation jobs. It uploaded `a1-lean-process-fault-receipt` artifact `9591573749` with digest `sha256:736d60345a54e626f2d39317e701600a9ac99c6ccd93d9f590bb4ecb105f6a42`. On the same code head, ordinary tests, runtime-candidates, both Nautilus evaluators, and LEAN clean-determinism are green; legacy Phase-B and bootstrap-assurance were still completing at the time this handoff was written, so the code head is not yet claimed fully green across all eight workflows.

Together with the prior metamorphic closure, the public A1 engineering audit now has explicit executable coverage for the contract-declared metamorphic and fault classes applicable to the current reference/LEAN slice. Genuine `HIDDEN_ACCEPTANCE` remains outstanding and cannot be performed by an ordinary agent.

A1 remains **IN_PROGRESS**. Runtime selection is `NONE / PENDING`; trading authority is `NONE`; autonomous paper/live execution is disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require `2ede511d00f5213fdc266003e3280b21d1252e0b` and the subsequent durable documentation head to finish the full eight-workflow exact-head validation matrix; fix genuine failures without weakening any invariant.
2. Treat genuine `HIDDEN_ACCEPTANCE` as the remaining external A1 gate only after the full public matrix is green: an authorized external clean runner must execute the sealed corpus and provide only the public seal-bound aggregate `SafeAcceptanceReceipt`. Ordinary agents must not inspect or fabricate hidden evidence.
3. Preserve Nautilus path-exhaustion evidence plus LEAN production differential, mutation, metamorphic, process-fault, and clean-determinism receipts.
4. Only after every conjunctive A1 gate, including hidden acceptance, is green may issue #15 assign final candidate dispositions and select the primary runtime. Do not begin issue #16 or change trading/holdout authority beforehand.
