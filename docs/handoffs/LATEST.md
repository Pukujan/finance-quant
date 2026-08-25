# Handoff — A1 exact-head CI regression fixes

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_ORACLE_SLICE`

## Completed this session

Exact-head GitHub Actions exposed two real regressions in the new A1 oracle slice, and both were fixed without weakening tests or invariants:

- restored the explicit `BOOTSTRAP_COMPLETE` machine-status marker in `docs/CURRENT_STATE.md`, keeping the completed A0 state coherent with the bootstrap contract validator while A1 remains active;
- changed the independent reference oracle to hash its normalized semantic input (ordered/deduplicated events plus deterministic intent ordering), so exact duplicate events preserve execution effects **and** receipt identity under `FQ-PROP-018`; conflicting duplicate IDs still fail closed.

The failing authoritative test run was `32865330332`: **2 failed, 908 passed, 25 skipped**. The failures were the bootstrap marker check and duplicate-event receipt hashes; both were diagnosed directly from the Actions job log.

No candidate adapter was added or selected. Trading authority remains NONE; autonomous paper trading and live capital remain DISABLED; sealed holdout exact cases/labels were not accessed.

## Validation status

The implementation/doc fixes were committed through `62950f99e370585215e3f5ca5115d2afdb9083ca`; subsequent durable handoff commits move branch HEAD but do not change implementation semantics. GitHub Actions for the repaired branch are running/queued and must be checked on the final exact handoff head before any adapter work begins.

No A1 phase completion is claimed. Hidden acceptance, candidate differential evidence, mutation threshold evidence, complete metamorphic coverage, candidate clean-environment evidence, and chaos/fault campaigns remain outstanding.

## Next exact action

1. Verify GitHub Actions on the exact current branch head and fix any remaining failure without weakening tests or invariants.
2. If the oracle/property slice is green, add the first **thin** candidate adapter behind `contracts/execution/runtime-conformance-v1.json`, limited to the semantic subset already implemented by `finance_quant/execution/reference.py`.
3. Add field-class differential comparison and explicit permitted-difference recording before widening candidate coverage.
4. Continue hidden/mutation/metamorphic/determinism/clean-env/chaos evidence for both candidates before any runtime disposition.

Do not select a primary runtime until every required A1 gate passes. Do not start #16 and do not enable paper/live capital authority.

Append-only record: `docs/handoffs/2026-08-25-a1-ci-regression-fix.md`.
