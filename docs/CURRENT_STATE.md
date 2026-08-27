# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=A2_AUTONOMOUS_TRADER_V0 assurance=A2 active_issue=16 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**. A1 / issue **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff** is complete. Active work is now **#16 — Autonomous Trader v0 — unattended local paper vertical slice**, assurance phase **A2**.

The legacy Phase-B plan remains parked and preserved only as an oracle.

## A1 final decision

A1 completed on 2026-08-27 after every required conjunctive gate, including genuine sealed `HIDDEN_ACCEPTANCE`, was satisfied for the selected LEAN candidate artifact.

- Primary runtime: **LEAN** pinned to commit `185c691b89f28bd68e48d53c02147415134975f0`
- LEAN disposition: **ADOPT_WITH_CONSTRAINTS**
- NautilusTrader pinned to `v1.230.0` / `8160730c7c550480b0a439fb11086a4c4de15f0b`
- NautilusTrader disposition: **REJECT** for the A1 primary-runtime role because the pinned production path violates mandatory execution semantics (`FQ-PROP-015`, with the explored deferral path also failing `FQ-PROP-021`)
- Independent validation oracle: the finance-quant reference simulator remains authoritative for the contract subset it implements
- Local extension/fork policy: thin adapters only; no upstream fork is authorized by A1

LEAN's disposition is constrained to the validated deterministic daily-bar next-eligible-open execution slice. A1 does not claim unrestricted full-LEAN/backtest conformance and grants no paper/live authority.

## A1 hidden acceptance evidence

The authorized isolated runner reported a completed real sealed run against frozen public evaluation SHA `4739392b15319bb209d657294834fed4cfb02d29` and candidate artifact SHA-256 `ed2b7b335f4be0f256fc7b28b8df12ae0a337c7b2bdec0c9925ddcd9bef630ff`.

Operational private-package identities reported aggregate-safely:

- scorer package SHA-256: `385a95ee8d35eb6264b1c67026d4355ba25fe80026eaad11fed68055a977924f`
- evaluator revision: `a1-private-evaluator-v2`
- evaluator SHA-256: `754a93e6d1ec5a3c045b786b4b7af7edd1c8d984decee052e5ded77e0ff66f11`
- sealed bundle SHA-256: `8ea6827e6a8fbb00792c392896efcaefdde1dad68e10f772cc5874d4b0821033`
- seal use consumed: `1 / 1`

The canonical public `SealRecord` is `docs/acceptance/A1_ISSUE_15_SEAL_RECORD.json`; the aggregate-only passing receipt is `docs/acceptance/A1_ISSUE_15_SAFE_ACCEPTANCE_RECEIPT.json`. The canonical record's derived commitment hash is `c87d13ac10602d613f9730438dc527ffa4f870e676c5f532fe7e60d0da42a038`, exactly matching the receipt. The receipt reports `status=pass`, `use_number=1`, and no failure classes.

The runner report included the derived `commitment_hash` alongside the SealRecord for convenience. The frozen public loader requires the serialized SealRecord itself to contain exactly the seven dataclass fields, so the durable public record omits that derived field. Recomputing the commitment with the frozen public hashing rule yields exactly the receipt commitment. Applying the frozen fail-closed verifier logic to the canonical record and receipt succeeds. No GitHub `workflow_dispatch` run exists for `a1-hidden-acceptance`; the reported public-verifier pass was therefore not a GitHub Actions ingress run, and this state does not claim otherwise.

No hidden case, label, expected output, case ID, trace, oracle internal, or hidden count is recorded publicly.

## Public validation status

The pre-transition public head `658f87a929071c5f1ead136b4a323cf946b43d86` completed all eight PR-triggered workflows successfully: tests `33018591994`, legacy Phase-B `33018592049`, bootstrap-assurance `33018592059`, runtime-candidates `33018592017`, Nautilus callback evaluator `33018591969`, Nautilus pre-open evaluator `33018592003`, `a1-assurance` `33018592021`, and LEAN clean-determinism `33018591968`.

The A1 public SDD/PDD, static/IR, unit/regression, property/stateful, mutation, differential, metamorphic, repeated determinism, clean-environment, and chaos/fault gates were green before the sealed run. The passing sealed receipt closes the remaining `HIDDEN_ACCEPTANCE` gate. A1 is therefore **COMPLETE**.

## Current capability and authority

- Assurance phase: **A2 — Autonomous Trader v0**
- Active issue: **#16**
- Selected execution runtime: **LEAN / ADOPT_WITH_CONSTRAINTS**
- Trading authority: **NONE**
- Autonomous paper capability: **DISABLED**
- Live capital: **DISABLED**
- Frontend authority: **OPERATOR_ONLY**
- Sealed holdout: isolated; ordinary agents may not inspect exact cases or labels

A2 explicitly requires `HITL_PROMOTION` before unattended paper capability may be enabled. Closing A1 does not satisfy that A2 promotion gate.

## Next exact action

Implement issue #16 as a minimal, deterministic vertical slice:

`PIT/replay input -> deterministic baseline strategy -> portfolio intent -> risk gate -> constrained LEAN execution -> local virtual account -> immutable SessionReceipt -> API/events -> operator evidence UI`.

Preserve the A1 semantics and pins. Add persistent account/order/fill state, exact accounting reconciliation, restart/resume/idempotency, duplicate/out-of-order handling, deterministic replay, session-receipt lineage, clean repeated runs, mutation/chaos/hidden A2 evidence, and explicit HITL promotion before enabling unattended paper operation. There remains no brokerage/live credential path and no capital authority.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and active issue #16
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. `contracts/execution/lean-a1-candidate-pin-v1.json`
7. issue #16 requirements and relevant A2 contracts/tests as they are created
