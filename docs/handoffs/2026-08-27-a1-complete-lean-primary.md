# A1 complete — LEAN selected as constrained primary runtime

Date: 2026-08-27
Branch: `bootstrap/oss-autonomous-trader-replatform`
Completed issue: #15
Next active issue: #16
Completed assurance phase: A1
Next assurance phase: A2
Starting public head: `658f87a929071c5f1ead136b4a323cf946b43d86`
Frozen public evaluation baseline: `4739392b15319bb209d657294834fed4cfb02d29`
Candidate artifact SHA-256: `ed2b7b335f4be0f256fc7b28b8df12ae0a337c7b2bdec0c9925ddcd9bef630ff`
Pinned LEAN runtime: `185c691b89f28bd68e48d53c02147415134975f0`

## Conjunctive A1 closure

Before hidden acceptance, all public A1 obligations were green: SDD/PDD, static/IR, unit/regression, property/stateful, mutation, differential, metamorphic, repeated determinism, clean-environment, and chaos/fault evidence. Starting head `658f87a929071c5f1ead136b4a323cf946b43d86` is green across all eight PR-triggered workflows: tests `33018591994`, legacy Phase-B `33018592049`, bootstrap-assurance `33018592059`, runtime-candidates `33018592017`, Nautilus callback evaluator `33018591969`, Nautilus pre-open evaluator `33018592003`, `a1-assurance` `33018592021`, and LEAN clean-determinism `33018591968`.

An authorized isolated scorer then executed the real A1 sealed corpus once. Aggregate-safe identities reported:

- scorer package SHA-256 `385a95ee8d35eb6264b1c67026d4355ba25fe80026eaad11fed68055a977924f`
- evaluator revision `a1-private-evaluator-v2`
- evaluator SHA-256 `754a93e6d1ec5a3c045b786b4b7af7edd1c8d984decee052e5ded77e0ff66f11`
- sealed bundle SHA-256 `8ea6827e6a8fbb00792c392896efcaefdde1dad68e10f772cc5874d4b0821033`
- seal use `1 / 1`

Canonical public evidence is committed as `docs/acceptance/A1_ISSUE_15_SEAL_RECORD.json` and `docs/acceptance/A1_ISSUE_15_SAFE_ACCEPTANCE_RECEIPT.json`. The canonical SealRecord derives commitment `c87d13ac10602d613f9730438dc527ffa4f870e676c5f532fe7e60d0da42a038`; the receipt binds the same commitment and exact candidate hash, reports `status=pass`, `use_number=1`, and has an empty failure-class list.

The runner's presentation embedded the derived commitment hash next to the SealRecord fields, while the frozen public loader accepts exactly the seven serialized dataclass fields. The durable record therefore stores the canonical seven-field form. Its commitment independently recomputes to the reported value and the frozen fail-closed verifier logic accepts the canonical record/receipt/candidate tuple. There is no GitHub Actions `workflow_dispatch` run for `a1-hidden-acceptance`, so none is claimed.

No hidden cases, labels, expected outputs, traces, case IDs, counts, or oracle internals were requested or published.

## Final runtime dispositions

### LEAN — `ADOPT_WITH_CONSTRAINTS`

LEAN at commit `185c691b89f28bd68e48d53c02147415134975f0` is the primary runtime for Autonomous Trader v0. The selection is constrained to the A1-validated deterministic daily-bar next-eligible-open execution slice. A2 must add persistent virtual-account, accounting, restart/replay, session lineage, authority, and multi-session evidence before unattended paper promotion. No unrestricted full-runtime conformance claim is made.

### NautilusTrader — `REJECT`

NautilusTrader `v1.230.0` / `8160730c7c550480b0a439fb11086a4c4de15f0b` is rejected for the A1 primary-runtime role. Pinned production evidence violates the mandatory next-eligible execution boundary (`FQ-PROP-015`); the explored PIT-safe callback deferral path fills at the later bar close rather than open (`FQ-PROP-021`); native pre-open timing sufficient for the unchanged contract is unavailable through the pinned public API. The contract/oracles are not weakened to accommodate those semantics.

The independent finance-quant reference simulator remains the validation oracle for the subset it implements. Thin adapters remain the local extension policy; no upstream runtime fork is authorized by this decision.

## Authority

A1 completion selects an execution body only. Trading authority remains `NONE`; autonomous paper and live-capital capability remain disabled. A2/issue #16 requires explicit `HITL_PROMOTION` before unattended paper capability can be enabled.

## Next exact action

Begin A2 / issue #16 using constrained LEAN as selected execution runtime. Build the deterministic local-paper vertical slice with persistent virtual account truth, immutable SessionReceipt lineage, exact reconciliation, restart/resume/idempotency, deterministic replay, risk non-widening, API/UI non-authority, A2 hidden/mutation/chaos evidence, and explicit HITL promotion before unattended paper activation.
