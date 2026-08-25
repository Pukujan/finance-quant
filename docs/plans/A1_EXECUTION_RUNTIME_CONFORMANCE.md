# A1 Execution Runtime Conformance — SDD/PDD

Issue: #15  
Assurance phase: A1  
Property impact: PRESERVE existing authority/PIT invariants; STRENGTHEN execution conformance.

## Purpose

Define the runtime-neutral execution semantics that NautilusTrader, LEAN, and the independent finance-quant reference simulator must satisfy before either OSS runtime can be selected. This contract is specification-first: no candidate gets semantic authority merely because its native behavior differs.

## Authority boundary

The runtime may simulate execution and report normalized evidence only. It may not grant brokerage authority, live-capital authority, holdout access, promotion authority, or widen risk. The sealed holdout remains inaccessible to ordinary implementation agents.

## Common deterministic fixture

Each candidate consumes the same ordered fixture stream. Every fixture event has `event_id`, `instrument_id`, `event_time`, `known_at`, `sequence`, and a typed payload. Order intents have immutable `intent_id`, `created_at`, side, quantity, order type, limit/stop fields where applicable, time-in-force, and deterministic cost-model identifiers.

Events are ordered by `(event_time, sequence, event_id)`. A runtime must reject ambiguous duplicate identities carrying different payloads. Exact duplicate events are idempotent.

For the initial daily-bar contract, an intent derived from bar t may not fill on bar t. Earliest eligible fill is the next tradable event after the intent's decision boundary. Candidate-specific same-bar defaults must be disabled or normalized away.

## Normalized receipt contract

Every run emits one canonical JSON receipt with stable key ordering and no absolute paths or wall-clock-only identity. Required top-level fields are:

- `contract_version`, `fixture_id`, `runtime`, `runtime_version`, `seed`, `status`;
- ordered `orders`, `fills`, `cash_ledger`, `positions`, `corporate_actions`, `rejections`, `faults`;
- terminal `cash`, `equity`, `nav`, `realized_pnl`, `unrealized_pnl`;
- `input_hash`, `receipt_hash`, and restart/replay lineage.

Normalized order states are `SUBMITTED | ACCEPTED | PARTIALLY_FILLED | FILLED | CANCELLED | REJECTED`. A terminal state cannot return to a non-terminal state. Fill quantity is positive and cumulative fill quantity may never exceed accepted order quantity.

Each fill records `fill_id`, `intent_id`, `instrument_id`, `event_time`, `quantity`, `price`, `fee`, `slippage`, and source event identity. Cash/position deltas must reconcile exactly to fills, fees, dividends, and splits under the fixture's declared decimal precision.

## PIT and event-time semantics

No execution decision or normalized fill may depend on an event whose `known_at` is later than the decision instant. Corporate actions may affect state only when their contract-declared effective/knowledge boundaries permit. Delisted instruments remain representable in historical state; delisting does not erase prior position or ledger history.

## Cost and liquidity semantics

Fees and slippage are deterministic pure functions of declared fixture inputs and model parameters. Missing or zero liquidity cannot synthesize an unconstrained fill. Partial fills consume at most declared available liquidity. Spread/slippage stress transformations may only worsen or preserve buyer cost and may only improve or preserve seller proceeds according to the declared sign convention.

## Account invariants

For every receipt:

`equity = cash + marked_position_value`

and terminal NAV must reconcile to the same accounting state under the fixture's valuation rule. Position changes equal signed executed quantities adjusted only by explicit corporate actions. Duplicate events/retries may not double-apply fills, fees, dividends, splits, or cash movements.

## Restart/replay

A crash may occur after any durable receipt boundary. Restart from the last committed boundary must produce the same authoritative terminal receipt as an uninterrupted run. Replayed inputs are idempotent; superseded duplicate attempt evidence remains visible but non-authoritative.

## Differential rules

The reference simulator is the semantic oracle for the subset it implements. Candidate comparison is field-class aware:

- exact: event/order identity, lifecycle transitions, quantities, terminal state, cash ledger identities, deterministic hashes after normalization;
- tolerance-bounded: decimal price/PnL fields only where the contract explicitly declares a numeric tolerance;
- permitted difference: candidate-native metadata that is excluded from the normalized receipt and recorded in the candidate disposition.

Any unlisted semantic difference is a conformance failure, not an automatic waiver.

## Initial hidden case classes

Exact hidden cases remain private. Public classes are: impossible same-bar fills; gaps; partial fills; duplicate/out-of-order events; split/dividend; delisting; missing/zero liquidity; short/borrow constraints where supported; fee/slippage boundaries; retry/restart; account reconciliation; and future-knowledge poisoning.

## Fault campaign

Adapters must be tested against deterministic injected faults: crash before/after commit boundary, duplicate delivery, reordered delivery within invalid bounds, dropped event, malformed payload, runtime exception, restart replay, and persisted-state corruption detection. Corruption must fail closed rather than invent authoritative execution state.

## Metamorphic relations

- Stable event reserialization/key order does not change the receipt hash.
- Exact duplicate delivery does not change authoritative terminal state.
- Adding an unavailable future-known event does not change an earlier decision/receipt prefix.
- Splitting one liquidity-limited fill into equivalent partial fills preserves terminal quantity/cash modulo declared rounding.
- Increasing non-negative fees cannot improve terminal NAV, all else equal.
- Re-running the identical fixture/seed at least three times yields receipt equivalence.

## A1 PDD property map

| Property ID | Statement | Severity | Primary A1 oracles |
| --- | --- | --- | --- |
| FQ-PROP-015 | No intent fills before its eligible execution boundary; daily bar-t decisions cannot fill on bar t. | critical | static/IR validator, unit/property tests, hidden same-bar corpus, differential |
| FQ-PROP-016 | Order lifecycle is monotone and cumulative filled quantity never exceeds accepted quantity. | critical | state-machine property tests, mutation, hidden lifecycle cases |
| FQ-PROP-017 | Normalized accounting reconciles fills/fees/corporate actions to cash, positions, equity and NAV. | critical | reference differential, property tests, hidden reconciliation cases |
| FQ-PROP-018 | Duplicate/retry/replay cannot double-apply authoritative execution effects. | critical | chaos/restart tests, metamorphic duplicate relation, mutation |
| FQ-PROP-019 | Runtime execution is PIT-safe: future-known events cannot influence earlier decisions or receipt prefixes. | critical | static/IR checks, poisoned-future hidden cases, metamorphic tests |
| FQ-PROP-020 | Identical normalized fixture/runtime pin/seed yields equivalent receipts across at least three independent runs. | high | repeated determinism and clean-environment reruns |
| FQ-PROP-021 | Candidate-specific semantics outside the permitted-difference list fail conformance rather than silently widening the contract. | high | differential validator mutation tests and hidden semantic-drift cases |
| FQ-PROP-022 | Fault/corruption handling fails closed and restart from a committed boundary converges to uninterrupted authoritative state. | critical | chaos/fault injection, restart differential, hidden corruption cases |

The executable oracle names above are contractual targets; implementation commits must bind them to concrete test nodes before A1 can complete. Hidden acceptance cases must remain outside this repository or otherwise inaccessible to ordinary agents.

## Candidate disposition gate

Each runtime ends A1 with exactly one disposition: `ADOPT`, `ADOPT_WITH_CONSTRAINTS`, `REFERENCE_ONLY`, or `REJECT`. A primary runtime may be named only after every required A1 gate is green. This document grants no paper or live trading authority.
