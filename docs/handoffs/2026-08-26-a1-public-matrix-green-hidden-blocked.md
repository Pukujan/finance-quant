# A1 public matrix green; hidden acceptance blocked on authorized runner

Date: 2026-08-26
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

## Starting state

Required sources were re-read in repository order: `AGENTS.md`, `docs/CURRENT_STATE.md`, active issue #15, `docs/handoffs/LATEST.md`, and `contracts/assurance/capability-assurance-v1.json`, followed by `docs/acceptance/SEALED_INTERFACE.md`.

Starting durable head was `4739392b15319bb209d657294834fed4cfb02d29`.

## Validation

The starting durable head is fully green across all eight required public PR workflows:

- tests `32926469922` — success
- legacy Phase-B `32926469919` — success
- bootstrap-assurance `32926469897` — success
- runtime-candidates `32926469900` — success
- a1-nautilus-adapter-evaluation `32926469912` — success
- a1-nautilus-preopen-evaluation `32926469910` — success
- a1-assurance `32926469899` — success
- a1-lean-clean-determinism `32926469909` — success

No test, invariant, execution oracle, PIT rule, candidate pin, or authority boundary was changed.

## Blocker determination

A1 remains conjunctive and `HIDDEN_ACCEPTANCE` remains mandatory. The sealed interface requires an authorized external clean runner to execute the private corpus and emit only an aggregate `SafeAcceptanceReceipt` bound to the public `SealRecord`. Public CI and the ordinary repository GitHub identity are explicitly not valid clean-runner identities. The public `a1-hidden-acceptance` workflow only verifies aggregate ingress and cannot execute or inspect the holdout itself.

Therefore this run cannot legitimately complete hidden acceptance. No private holdout repository access, case/label inspection, fabricated receipt, synthetic substitute, or authority bypass was attempted.

## Durable state

A1 remains `IN_PROGRESS`.

- Runtime selection: `NONE / PENDING`
- Trading authority: `NONE`
- Autonomous paper/live execution: `DISABLED`
- Sealed holdout: untouched by ordinary agent
- Issue #16: not started

## Next exact action

1. Authorized external clean runner executes the exact candidate artifact against the sealed A1 corpus under `docs/acceptance/SEALED_INTERFACE.md`.
2. Runner emits only the public `SealRecord` and aggregate `SafeAcceptanceReceipt`.
3. Aggregate evidence is verified through `.github/workflows/a1-hidden-acceptance.yml` / `finance_quant.acceptance.a1_hidden`.
4. If hidden acceptance fails, preserve only the aggregate failure receipt and fix public implementation defects without inspecting hidden cases or weakening invariants.
5. Only after hidden acceptance passes and every other A1 gate remains green may issue #15 assign final candidate dispositions, select a primary runtime, and explicitly permit promotion.
