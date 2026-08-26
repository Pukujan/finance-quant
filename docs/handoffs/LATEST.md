# Handoff — A1 restart, metamorphic, and mutation assurance

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

Required governance/state files were read before changes. The prior path-exhaustion head `85f32858b3e4ee17cf7c1240349fe6f2e6530c05` completed green across tests `32914556208`, legacy Phase-B `32914556200`, bootstrap assurance `32914556224`, runtime candidates `32914556234`, callback-adapter evaluation `32914556217`, and pre-open/latency evaluation `32914556199` before this assurance slice proceeded.

This slice is a **STRENGTHEN** of existing A1 properties only. No execution oracle, runtime pin, permitted semantic difference, PIT rule, authority boundary, or candidate disposition changed.

`FQ-PROP-022` now has explicit executable restart-convergence evidence. The new reference checkpoint restart path validates the checkpoint canonical hash, reference runtime/fixture/seed identity, committed event boundary, and full deterministic prefix state implied by the immutable fixture. A checkpoint whose state was corrupted and then re-hashed is still rejected. A valid checkpoint replays to the same authoritative final orders, fills, ledgers, positions, cash, equity, and NAV as uninterrupted execution, with explicit parent receipt lineage.

The new `a1-assurance` workflow also exercises metamorphic relations covering all event-input permutations, uniform timestamp shifts, future-known decoys, and increased-liquidity monotonicity, plus fault cases for hash corruption, re-hashed state corruption, invalid committed boundaries, seed mismatch, and restart convergence.

A source-level mutation gate was added for finance-quant-owned execution conformance/reference surfaces. Initial run `32915294812` failed at 9/11 critical mutants because two rapid same-size source mutations reused timestamp-valid Python bytecode. The tests themselves were not weakened. The runner was repaired to purge the mutated module's `.pyc` before each oracle execution and after restoration. Repaired run `32915409420` is green at 11/11 critical mutants killed (100% vs 98% required), 2/2 high mutants killed (100% vs 95% required), and zero critical survivors. The uploaded mutation receipt is retained in CI lineage.

On implementation head `54532d38470ddf70bbbadce7ebd0ba022ffe6bf0`, `a1-assurance` `32915409420`, runtime-candidates `32915409410`, callback evaluator `32915409402`, and pre-open evaluator `32915409401` are green. The ordinary pytest step in tests run `32915409427` also passed; its smoke step, legacy Phase-B, and bootstrap assurance were still completing at the time of this durable update, so full exact-head green status has not been claimed yet.

This evidence does **not** finish A1. Hidden acceptance remains outstanding, as do candidate-specific mutation/fault coverage for the LEAN normalizer/evidence path, broader candidate-level chaos/metamorphic evidence, and the final complete determinism/clean-environment evidence set. Nautilus public production-native next-open paths remain exhausted but its final disposition is still `PENDING`; LEAN remains positive evidence only; primary runtime selection remains `NONE / PENDING`.

Trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## Next exact action

1. Require this durable documentation head to pass tests, legacy phase-b, bootstrap-assurance, runtime-candidates, both Nautilus evaluators, and `a1-assurance`.
2. Extend mutation/fault coverage to the still-eligible LEAN adapter/normalizer/evidence surfaces. Malformed/duplicate runtime output, nonzero candidate exit/crash, timeout/dependency failure, and receipt corruption must all fail closed; keep the existing mutation thresholds unchanged.
3. Establish and execute the authorized opaque hidden-acceptance path without reading, copying, or exposing sealed cases/labels. Public fixtures must never be mislabeled as hidden acceptance.
4. Close remaining candidate-level metamorphic, repeated-determinism, clean-environment, and chaos/fault evidence. Only then may issue #15 assign final candidate dispositions and select a primary runtime.
5. Do not advance to issue #16 or change trading/holdout authority before durable state explicitly permits promotion.

Append-only record: `docs/handoffs/2026-08-25-a1-restart-metamorphic-mutation-assurance.md`.
