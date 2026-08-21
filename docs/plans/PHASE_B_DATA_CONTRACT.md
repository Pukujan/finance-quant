# Phase B Data Contract

**Status:** Contract for the Phase B Polygon ingest and canonical fixture freeze.
**Authority:** `finance_quant/ingest/polygon.py`, `finance_quant/pit/store.py`,
`finance_quant/pit/model.py`, and `scripts/freeze_fixture.py`.

This document defines what a Phase B record means, how Polygon fields are
mapped, and how a fixture becomes reproducible. It is deliberately explicit
about the distinction between the adapter's timestamp precision and the
current PIT model's day-granularity validation.

## 1. Temporal Authority and Polygon Mapping

`vt` is valid time: when the fact applies in market reality. `kt` is knowledge
time: the first time the ingest pipeline knows the fact. Queries must use both
clocks through `PITStore.as_of(namespace, instruments, vt_start, vt_end,
kt_bound)`; a record with `kt > kt_bound` is not visible.

For ordinary market bars, Polygon is the source authority:

| PIT field | Polygon input / rule |
|---|---|
| `namespace` | Literal `bar` |
| `instrument_id` | Requested Polygon ticker, pending mapping to stable internal symbology |
| `vt` | `t`, the aggregate/bar timestamp, parsed as epoch milliseconds and serialized in UTC ISO-8601 form |
| `kt` | UTC timestamp at mapping time (`_utcnow()`), serialized in ISO-8601 form |
| `payload.open` | `o` |
| `payload.high` | `h` |
| `payload.low` | `l` |
| `payload.close` | `c` |
| `payload.volume` | `v` |
| `payload.vwap` | `vw`, when supplied |
| `payload.trades` | `n`, when supplied |
| `source` | Adapter `source` value, default `polygon` |
| `revision` | Adapter revision, default `1`; higher revisions append corrections |
| `superseded_by` | `null` for newly emitted records |
| `ingest_receipt.endpoint` | `/v2/aggs/ticker/range` |
| `ingest_receipt.params` | Request parameters excluding `apiKey` |
| `ingest_receipt.fetched_at` | UTC time the logical fetch receipt was created |

The adapter requests adjusted daily bars with `adjusted=true` and `limit=50000`.
It follows every Polygon `next_url` page and emits one record per result row.
The page URL is used as-is and original query parameters are not resent.

Corporate-action records use `namespace=corporate_action`, the requested
ticker as `instrument_id`, and the same source/revision/supersession rules:

| Action | `vt` | Payload |
|---|---|---|
| Dividend | `ex_dividend_date` | `kind=dividend`, `amount=cash_amount`, `currency=currency`, `declaration_date`, `record_date`, `pay_date`, `frequency` |
| Split | `execution_date` | `kind=split`, `split_from`, `split_to` |

Polygon date values may be epoch milliseconds, numeric strings, ISO dates, or
ISO timestamps. They are parsed to UTC. The relevant endpoint is recorded in
the receipt: `/v3/reference/dividends` or `/v3/reference/splits`.

### Precision constraint

The adapter currently emits full UTC timestamps. `BitemporalRecord` currently
accepts only ten-character `YYYY-MM-DD` values, and the SQLite schema stores
the supplied strings without conversion. A Phase B path must therefore choose
and pin one of these compatible representations before loading adapter output
into `BitemporalRecord`: retain timestamp precision by widening the model
validation, or explicitly normalize both clocks to UTC dates. That decision
must be reflected in the fixture and will change its manifest hash. It must
not be handled by dropping `kt` or by reading “latest”.

## 2. PIT Record Schema

The logical record schema is:

```json
{
  "namespace": "bar",
  "instrument_id": "AAPL",
  "vt": "2024-01-02T05:00:00+00:00",
  "kt": "2024-01-02T05:00:01.123456+00:00",
  "payload": {
    "open": 100.0,
    "high": 105.0,
    "low": 99.0,
    "close": 103.0,
    "volume": 1000000,
    "vwap": 102.5,
    "trades": 5000
  },
  "source": "polygon",
  "revision": 1,
  "ingest_run_id": "<run-id>",
  "superseded_by": null
}
```

Required fields are `namespace`, `instrument_id`, `vt`, `kt`, `payload`,
`source`, and `revision`. `ingest_run_id` defaults to `fixture` in the model;
`superseded_by` defaults to `null`. Valid namespaces are `bar`, `fundamental`,
`corporate_action`, `universe`, and `macro`.

The fact key is `(namespace, instrument_id, vt)`. A correction is append-only:
it uses the same fact key, a higher `revision`, and preserves the older row.
For a knowledge bound `K`, visibility selects the highest revision among rows
with `kt <= K`. The store's snapshot includes all revisions, including buried
and superseded history. Deletes are not part of the PIT contract.

SQLite storage uses the columns `namespace`, `instrument_id`, `vt`, `kt`,
`revision`, JSON `payload`, `source`, `ingest_run_id`, and nullable
`superseded_by`; the primary key is `(namespace, instrument_id, vt, revision)`.

## 3. Manifest Hash Algorithm

The canonical fixture manifest hash is the lowercase hexadecimal SHA-256 digest
computed by `scripts.freeze_fixture.compute_manifest_hash`:

1. Convert each record to canonical JSON with sorted keys, compact separators
   (`(',', ':')`), UTF-8 encoding, and `default=str` for otherwise unsupported
   values.
2. Sort records by their canonical JSON strings. The fixture hash is therefore
   independent of input iteration order.
3. For each sorted JSON blob, update the SHA-256 state with its byte length as
   an unsigned eight-byte big-endian integer, then with the UTF-8 blob bytes.
4. Return the 64-character lowercase digest.

Conceptually:

```text
h = SHA256()
for blob in sort(canonical_json(record).encode("utf-8") for record in records):
    h.update(len(blob_as_text).to_bytes(8, "big"))
    h.update(blob)
return h.hexdigest()
```

The implementation prefixes `len(blob)` before UTF-8 encoding. For the
contract's ASCII fixture data this equals the byte length; implementations
should preserve the helper's exact behavior. This fixture manifest hash is
distinct from `PITStore.snapshot_pin()`, which uses sorted full-history
`BitemporalRecord.canonical()` bytes and BLAKE2b-256.

## 4. Corporate-Action `kt` Semantics

Corporate actions have separate event dates and knowledge time:

- Dividend `vt` is the ex-dividend date. Its declaration, record, and pay dates
  remain payload attributes.
- Split `vt` is the execution date. Its ratio remains payload data as
  `split_from` and `split_to`.
- `kt` is when the adapter obtains the Polygon record, currently the UTC
  `_utcnow()` at mapping time. It is not the ex-date, execution/effective date,
  declaration date, record date, or pay date.

Thus an action may legitimately have `kt < vt`: it can be known before it takes
effect. Before its knowledge time, an `as_of` query must not apply the action;
after its knowledge time, the action is visible even if its valid/effective date
is in the future. This preserves the PIT rule and prevents look-ahead bias.

The Phase B plan describes the intended authority as Polygon's announcement
timestamp. The current Polygon adapter does not receive or persist a separate
announcement timestamp; it uses fetch/mapping time instead. If Polygon's
announcement timestamp becomes available, it must replace mapping-time `kt`
explicitly and the fixture must be re-frozen under a new hash. No consumer may
infer `kt` from an event date.

## 5. Fixture Freeze and Verification

The canonical location is `data/fixtures/phase-b/`, containing:

- `records.jsonl`: one canonical JSON record per line;
- `manifest.json`: `manifest_id`, `snapshot_pin`, `record_count`, and
  `fixture_path`.

To freeze a store, from the repository root run:

```bash
python scripts/freeze_fixture.py --store-path path/to/pit.sqlite --fixture-dir data/fixtures/phase-b
```

The script loads the SQLite PIT store, obtains `dump_records()`, writes sorted-
key compact JSON records to `records.jsonl` in store dump order, computes the
manifest hash over the records, and writes `manifest.json`. If `--store-path`
is omitted or missing, it uses a deterministic two-record demo store; that is a
stub for tests, not the canonical real-data fixture.

To verify an existing manifest:

```bash
python scripts/freeze_fixture.py --store-path path/to/pit.sqlite --fixture-dir data/fixtures/phase-b --verify
```

Verification loads the same store, recomputes the exact manifest hash, and
fails with `snapshot_pin mismatch` if it differs from `manifest.json`. A clean
runner must use the same adapter/version, universe, date ranges, temporal
normalization, and source data; a changed `kt`, payload, revision, or record
set is expected to produce a different hash. CI should run `--verify` and
reject any mismatch. After verification, run the PIT property tests and the
full Phase B determinism drill; do not use a “latest” query as a substitute
for the pinned `as_of(vt, kt)` contract.
