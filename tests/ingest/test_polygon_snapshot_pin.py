"""Tests for snapshot_pin – mutants of polygon_ref.py.

Mutants targeted
----------------
1. Same records, different order  →  hash differs (order-sensitive implementation)
2. Changing any single field      →  hash differs
3. Empty record list              →  deterministic empty-hash
4. Unicode / emoji in payload     →  hash stable and differs from ASCII-only
5. Length-prefix sensitivity       → inserting a record that is a prefix of another
                                   changes the combined hash vs concatenating them
"""
from __future__ import annotations

import hashlib
import json

from finance_quant.ingest.polygon import snapshot_pin


# ------------------------------------------------------------------ helpers

def _canonical(recs):
    """Return the raw concatenated input that snapshot_pin hashes, for
    manual comparison when needed."""
    parts = []
    for rec in recs:
        blob = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
        parts.append(len(blob).to_bytes(8, "big") + blob.encode("utf-8"))
    return b"".join(parts)


# ================================================================ tests

def test_same_records_different_order_produce_different_hash():
    """Mutant 1: the iterator processes records in sequence; swapping two
    top-level records must change the resulting SHA-256.

    Reference behavior: orders A,B and B,A yield different hashes because
    each iteration updates the running digest in order.
    """
    a = {"id": 1}
    b = {"id": 2}
    hash_ab = snapshot_pin([a, b])
    hash_ba = snapshot_pin([b, a])
    assert hash_ab != hash_ba, (
        "snapshot_pin must be order-sensitive; "
        f"found identical hash {hash_ab!r}"
    )


def test_changing_any_single_field_changes_hash():
    """Mutant 2: if any field in any record changes, the hash must change.
    Tests several kinds of mutations: nested value, missing extra field,
    and a top-level key added."""
    base = [{"symbol": "AAPL", "payload": {"open": 100}}]
    h_original = snapshot_pin(base)

    mutations = [
        [{"symbol": "AAPL", "payload": {"open": 101}}],           # nested int change
        [{"symbol": "GOOG"}],                                      # removed field
        [{"symbol": "AAPL", "extra": 9}],                          # added field
        [{"symbol": "aapl"}],                                       # case change
        [{"payload": {"open": 100}}],                               # top-level key changed
        [{"symbol": "AAPL", "payload": {"open": "100"}}],          # type change (int→str)
    ]
    for mut in mutations:
        h_mut = snapshot_pin(mut)
        assert h_mut != h_original, (
            f"Hash should differ after mutation {mut}; "
            f"got same hash {h_mut!r}"
        )


def test_empty_records_yields_stable_hash():
    """Mutant 3: zero records produces a fixed, deterministic hash
    (just the SHA-256 of nothing)."""
    h_empty_1 = snapshot_pin([])
    h_empty_2 = snapshot_pin([])
    expected = hashlib.sha256().hexdigest()
    assert h_empty_1 == h_empty_2 == expected, (
        f"Empty records hash mismatch: {h_empty_1!r} != {expected!r}"
    )


def test_empty_vs_nonempty_hash_differs():
    """Ensure empty is distinct from one record."""
    h_empty = snapshot_pin([])
    h_one = snapshot_pin([{"x": 1}])
    assert h_empty != h_one


def test_unicode_payload():
    """Mutant 4: unicode characters (incl. emoji) in fields are handled."""
    ascii_recs = [{"symbol": "AAPL", "note": "hello"}]
    unicode_recs = [{"symbol": "AAPL", "note": "hëllö wörld ☃ snowman 🐙"}]
    emoji_recs = [{"emoji": "🚀💰📈"}, {"symbol": ""}]

    h_ascii = snapshot_pin(ascii_recs)
    h_unicode = snapshot_pin(unicode_recs)
    h_emoji = snapshot_pin(emoji_recs)

    assert h_ascii != h_unicode, "ASCII and unicode payloads differ"
    assert h_unicode != h_emoji, "Unicode and emoji payloads differ"

    # Re-run to confirm determinism within unicode
    h_unicode_2 = snapshot_pin(unicode_recs)
    assert h_unicode == h_unicode_2, "unicode pin must be deterministic"

    # Verify no encoding error
    raw = _canonical(unicode_recs)
    assert isinstance(raw, bytes)


def test_length_prefix_sensitivity_prefix_record():
    """Mutant 5 (length-prefix sensitivity): the hash must differ from a naive
    SHA-256 over the raw concatenated JSON blobs. The 8-byte length prefix
    before each record guarantees this.
    """
    recs = [{"r": 1}, {"r": 2}]
    actual = snapshot_pin(recs)

    # Naive concatenation without length prefixes.
    raw = b"".join(
        json.dumps(r, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        for r in recs
    )
    naive = hashlib.sha256(raw).hexdigest()

    assert actual != naive, (
        "snapshot_pin must include length prefixes; raw concatenation hash matches"
    )
