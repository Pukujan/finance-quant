# Handoff — A1 execution conformance specified

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_SPECIFIED`

## Completed this session

The first A1 specification/property-design step required by durable state is complete. Added:

- `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
- `contracts/execution/runtime-conformance-v1.json`

These artifacts define the shared execution semantics for the NautilusTrader-vs-LEAN bakeoff before either candidate is adapted or selected: deterministic event ordering, no same-bar daily fills, normalized order/fill/account receipts, PIT boundaries, liquidity/cost rules, accounting reconciliation, restart/replay idempotency, differential comparison classes, hidden-case classes, fault injection, metamorphic relations, and three-run determinism.

Stable A1 properties `FQ-PROP-015`–`FQ-PROP-022` are specified. Property impact is PRESERVE existing authority/PIT restrictions and STRENGTHEN execution conformance.

Specification commit: `66a27de58d1192a4bfb658df6f2cbc8dc26ca362`.

No runtime has been selected. Trading authority remains NONE; autonomous paper trading and live capital remain DISABLED; sealed holdout exact cases/labels remain inaccessible to ordinary agents.

## Validation status

No GitHub Actions workflow run was visible for the specification commit when checked.

A local validation attempt was made using clone + JSON parse + full pytest, but the execution environment failed before clone with `Could not resolve host: github.com`. This is an environment/network blocker and is not counted as a test failure or pass.

Accordingly, no A1 gate is claimed complete beyond SDD/PDD authoring. STATIC_IR, UNIT_REGRESSION, PROPERTY_STATEFUL, HIDDEN_ACCEPTANCE, MUTATION, DIFFERENTIAL, METAMORPHIC, DETERMINISM, CLEAN_ENV, and CHAOS_FAULT remain outstanding.

## Durable state update

`docs/CURRENT_STATE.md` now records project status `A1_SPECIFIED` and points fresh sessions to the new A1 contract artifacts.

Append-only record: `docs/handoffs/2026-08-25-a1-specification.md`.

## Next exact action

1. Bind `FQ-PROP-015`–`FQ-PROP-022` into `contracts/properties/finance-quant-properties-v1.json` with concrete executable oracle targets.
2. Add contract/schema/semantic validators and unit/property tests for canonical execution receipts.
3. Implement the smallest independent reference-simulator slice needed to exercise the shared deterministic fixture.
4. Only after that add thin NautilusTrader and LEAN adapters and begin differential/hidden/mutation/determinism/clean-env/chaos evidence.

Do not start Autonomous Trader v0 (#16) until #15 has explicit runtime dispositions and every required A1 gate passes. Do not enable paper/live capital authority.
