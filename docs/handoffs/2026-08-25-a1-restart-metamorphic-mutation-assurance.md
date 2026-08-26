# A1 restart, metamorphic, and mutation assurance

Date: 2026-08-25
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1
Property impact: **STRENGTHEN**

## Starting state

Required governance/state files were read before mutation. The starting path-exhaustion head `85f32858b3e4ee17cf7c1240349fe6f2e6530c05` was fully green at tests `32914556208`, legacy Phase-B `32914556200`, bootstrap assurance `32914556224`, runtime candidates `32914556234`, callback-adapter evaluation `32914556217`, and pre-open/latency evaluation `32914556199`.

Runtime selection was and remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed.

## FQ-PROP-022 restart convergence

The existing property statement requires both fail-closed corruption handling and convergence after restart from a committed boundary. Earlier public tests exercised corruption/idempotence but did not explicitly execute restart convergence.

`finance_quant.execution.reference.restart_daily_reference_from_checkpoint` now implements a deliberately simple independent replay oracle. Before accepting a checkpoint it validates:

- the normal receipt contract and canonical receipt hash;
- reference runtime/version, fixture identity, and seed;
- a nonnegative committed-event boundary within the immutable fixture; and
- exact equality of the checkpoint to the deterministic reference state implied by that fixture prefix.

The final fixture is then replayed and linked to the validated checkpoint through `parent_receipt_hash`. This is intentionally an oracle/replay mechanism, not a production runtime or trading capability.

New fault tests prove that a valid checkpoint converges to uninterrupted authoritative state, a directly corrupted checkpoint fails its hash, a corrupted checkpoint cannot become valid merely by recomputing its hash, an impossible committed boundary fails closed, and a seed mismatch fails closed.

## Metamorphic evidence

`tests/test_execution_metamorphic.py` adds independent relations over the public deterministic fixture:

- all six permutations of the three input events normalize to the identical receipt;
- shifting every event/knowledge/decision instant by the same offset preserves execution economics while covariantly shifting fill time;
- adding a future-known decoy cannot change execution economics; and
- increasing eligible liquidity cannot reduce filled quantity.

These relations preserve the existing next-event/PIT semantics and do not add a permitted runtime difference.

## Mutation evidence

`scripts/a1_execution_mutation_gate.py` applies explicit source mutants to finance-quant-owned execution conformance/reference code, verifies each mutation anchor is unique and syntactically valid, runs the independent targeted oracle in a fresh subprocess, restores source after each attempt, and enforces the assurance contract thresholds:

- critical minimum valid-mutant kill rate: 0.98;
- high minimum valid-mutant kill rate: 0.95; and
- no surviving critical invariant-bypass mutant.

The inventory mutates authority validation, missing receipt fields, forbidden identity inputs, normalized order states, self-hash exclusion, same-bar eligibility, future-known eligibility, zero-liquidity eligibility, partial-fill caps, open-vs-close fill price, fee accounting, ambiguous duplicate rejection, and canonical event ordering.

Initial run `32915294812` produced 9/11 critical kills and two apparent survivors. The failure was retained. Investigation found that rapid same-size rewrites of `conformance.py` could reuse timestamp-valid compiled `.pyc` bytecode across subprocesses, so the oracle was not always executing the current mutant. No threshold or test was changed. The mutation runner now purges module bytecode before each mutant oracle and after restoration.

Repaired run `32915409420` passed with 11/11 critical mutants killed (100%), 2/2 high mutants killed (100%), and zero critical survivors. The mutation receipt was uploaded as `a1-execution-mutation-receipt`.

## Validation and remaining scope

The new `a1-assurance` workflow run `32915409420` passed both its mutation and metamorphic-chaos jobs. On implementation head `54532d38470ddf70bbbadce7ebd0ba022ffe6bf0`, runtime-candidates `32915409410`, callback evaluator `32915409402`, and pre-open evaluator `32915409401` are also green; the ordinary pytest step in tests run `32915409427` passed. At this handoff update, the tests smoke step, legacy Phase-B, and bootstrap assurance were still completing, so this implementation head is not claimed as a fully green baseline yet.

This mutation receipt is scoped to the curated reference/conformance inventory. A1 still requires candidate-specific mutation/fault coverage of the still-eligible LEAN adapter/normalizer/evidence surfaces, opaque hidden acceptance, broader candidate-level metamorphic/chaos evidence, and the final complete repeated-determinism/clean-environment evidence set. No final candidate disposition or primary runtime selection is permitted yet.

## Next exact action

Require the durable documentation head to complete all ordinary and A1-specific workflows successfully. Then extend fail-closed mutation/fault coverage to the LEAN adapter/normalizer/evidence path, including malformed or duplicate probe objects, candidate crash/nonzero exit, timeout/dependency failure, and corrupted evidence. Establish the authorized opaque hidden-acceptance path without exposing sealed contents, and close the remaining candidate-level metamorphic, deterministic clean-environment, and chaos/fault obligations. Only after every conjunctive A1 gate passes may issue #15 assign final dispositions and select the primary runtime. Do not start issue #16 before durable state explicitly permits promotion.
