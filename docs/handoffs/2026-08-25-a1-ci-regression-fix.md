# Handoff — A1 exact-head CI regression fixes

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_ORACLE_SLICE`

## Completed this session

Re-read the durable project state and active A1 assurance contract before mutation. Exact-head GitHub Actions for head `8a92fb077b6fc1f401dd19367935adb970a86820` exposed two failures in run `32865330332`:

1. `scripts/validate_bootstrap_contracts.py` required the durable `BOOTSTRAP_COMPLETE` marker in `docs/CURRENT_STATE.md`, but the A1 state document had stopped spelling that machine status literally.
2. `FQ-PROP-018` duplicate-event behavior was operationally idempotent, but `input_hash` and therefore `receipt_hash` were computed from the raw fixture before exact-duplicate normalization, so semantically identical duplicate inputs produced different receipt identities.

Fixed both without weakening tests or invariants:

- `finance_quant/execution/reference.py` now constructs the canonical input identity from ordered/deduplicated events and deterministically ordered intents before hashing; exact duplicate events therefore preserve both execution effects and receipt identity, while conflicting duplicate IDs still fail closed.
- `docs/CURRENT_STATE.md` now retains the explicit `BOOTSTRAP_COMPLETE` machine-status marker alongside the current A1 semantic status.

No candidate runtime adapter was added or selected. Trading authority remains NONE; autonomous paper trading and live capital remain DISABLED; sealed holdout cases/labels were not accessed.

## Validation status

The failing authoritative test run was `32865330332`: **2 failed, 908 passed, 25 skipped**. Both failures were diagnosed from the job log and addressed directly.

Current exact branch head after the fixes is `62950f99e370585215e3f5ca5115d2afdb9083ca`. GitHub Actions runs for that exact head were queued/in progress at handoff time, including tests run `32871063780` and bootstrap-assurance runs `32871057276` / `32871063805`.

No A1 completion is claimed until exact-head CI is observed green and the remaining A1 gates are completed.

## Next exact action

1. Inspect GitHub Actions for exact head `62950f99e370585215e3f5ca5115d2afdb9083ca`; if any job fails, fix the real regression without weakening tests or invariants.
2. Only after the oracle/property slice is green, add the first thin candidate adapter behind `contracts/execution/runtime-conformance-v1.json`, limited to the semantic subset already covered by the independent daily-bar reference oracle.
3. Add field-class differential comparison and explicit permitted-difference recording before widening adapter scope.
4. Continue hidden acceptance, mutation, metamorphic, repeated determinism, clean-environment, differential, and chaos/fault evidence for both candidates before any runtime disposition.

Do not start #16, select a primary runtime, enable autonomous paper trading, enable live capital, or access sealed holdout cases until the applicable gates explicitly permit it.
