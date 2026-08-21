"""Hypothesis property-based tests for finance_quant.acceptance.phase_b_seal.

Covers:
- epoch-counter invariants (SEAL-A ≤ 2/epoch, SEAL-B = 1/epoch)
- hex-validation edge cases (valid/hex/length/case for _is_valid_hex64)
- root-mismatch propagation for every validate() path
"""
from __future__ import annotations

import re

import pytest
from hypothesis import Verbosity, assume, given, settings, strategies as st

from finance_quant.acceptance.phase_b_seal import (
    SealEpochError,
    SealError,
    SealRecord,
    SealType,
    SealValidationError,
    _check_epoch_counts,
    _check_merkle_root,
    _is_valid_hex64,
    validate,
)

# ── strategies ───────────────────────────────────────────────────────────────

# Exactly-64-char hex strings via binary→hex conversion (guaranteed valid)
_valid_root: st.SearchStrategy[str] = st.binary(min_size=32, max_size=32).map(bytes.hex)

_arbitrary_str = st.text(min_size=0, max_size=128)

_valid_epoch = st.integers(min_value=1, max_value=2**31)
_negative_epoch = st.integers(min_value=-2**31, max_value=-1)
_bad_count = st.integers(min_value=-5, max_value=0)


# ===========================================================================
# 1. Epoch-counter invariants
# ===========================================================================

class TestEpochInvariantSealA:
    """SEAL-A may never exceed 2 per epoch."""

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=30, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_two_total_is_ok(self, root, epoch):
        """Registry showing 1 + this record (count=1) = 2 must pass."""
        registry = {int(epoch): {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_A)
        assert validate(root, record, registry) is record

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=30, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_three_total_raises(self, root, epoch):
        """Existing count 2 + 1 raises."""
        registry = {int(epoch): {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError, match=r"at most 2|would have 3"):
            validate(root, record, registry)

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=20, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_no_registry_any_count_leq_2_ok(self, root, epoch):
        """When registry is empty, a single SEAL-A record passes."""
        registry: dict[int, dict[SealType, int]] = {}
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_A)
        result = validate(root, record, registry)
        assert result is record


class TestEpochInvariantSealB:
    """SEAL-B must always have exactly 1 per epoch."""

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=30, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_zero_plus_one(self, root, epoch):
        """No prior seals + one new → exactly 1 OK."""
        registry: dict[int, dict[SealType, int]] = {}
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_B)
        result = validate(root, record, registry)
        assert result is record

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=30, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_prior_exists_raises(self, root, epoch):
        """One prior + this = 2 → violates "exactly 1"."""
        registry = {int(epoch): {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError, match="exactly 1|would have 2"):
            validate(root, record, registry)

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=20, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_count_in_epoch_gt_1_raises(self, root, epoch):
        """A SealB with count_in_epoch > 1 fails even without a prior entry."""
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_B, count_in_epoch=3)
        with pytest.raises(SealEpochError, match="exactly 1|would have 3"):
            validate(root, record, {})

    @given(_valid_root, _valid_epoch)
    @settings(max_examples=20, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_count_in_epoch_varies_but_always_exactly_one_required(self, root, epoch):
        """Any count_in_epoch != 1 produces SEALEpochError regardless."""
        record = SealRecord(merkle_root=root[:64], epoch=int(epoch), seal_type=SealType.SEAL_B, count_in_epoch=5)
        with pytest.raises(SealEpochError):
            validate(root, record, {})


class TestEpochCrossEpochIsolation:
    """Different epochs are independent – a full epoch doesn't leak."""

    @given(_valid_root, st.integers(min_value=1, max_value=1000))
    @settings(max_examples=20, suppress_health_check=[], verbosity=Verbosity.quiet)
    def test_seal_a_full_epoch_does_not_affect_next(self, root, full_epoch):
        """If epoch X already has 2 SEAL-A records, epoch X+1 can still take 2 more."""
        registry = {int(full_epoch): {SealType.SEAL_A: 2}}
        next_ep = int(full_epoch) + 1
        record = SealRecord(merkle_root=root[:64], epoch=next_ep, seal_type=SealType.SEAL_A)
        result = validate(root, record, registry)
        assert result is record


# ===========================================================================
# 2. Hex validation properties
# ===========================================================================

class TestIsValidHex64Properties:

    @given(st.integers())
    def test_non_integer_input_returns_false(self, n):
        """_is_valid_hex64 must reject non-string inputs gracefully."""
        assert _is_valid_hex64(n) is False

    @given(st.none())
    def test_none_input_returns_false(self, val):
        assert _is_valid_hex64(val) is False  # type: ignore[arg-type]

    # Specifically-chosen known-good strings (all ≤ 0x7A, so fully within
    # the [0-9a-fA-F] pattern and well-behaved).
    @pytest.mark.parametrize(
        "s",
        [
            "0" * 64,
            "f" * 64,
            "FF" * 32,
            "Af" * 32,
            "aabbccdd11223344aabbccdd11223344aabbccdd11223344aabbccdd11223344",
            "DeAdBeEfCaFe1234DEADBEEFCAFEBABE00001111222233334444555566667777",
        ],
    )
    def test_known_good_hex64_passes(self, s):
        assert _is_valid_hex64(s) is True

    # Known-bad strings
    @pytest.mark.parametrize("s", ["", "a" * 63, "a" * 65, "g" * 64, "hello", "@#$%^&*"])
    def test_known_bad_hex64_fails(self, s):
        assert _is_valid_hex64(s) is False

    # Determinism over arbitrary input
    @given(_arbitrary_str)
    @settings(max_examples=20)
    def test_deterministic_result(self, s):
        v1 = _is_valid_hex64(s)
        v2 = _is_valid_hex64(s)
        assert v1 == v2

    # Idempotent over same value
    @given(_arbitrary_str)
    @settings(max_examples=20)
    def test_idempotent_evaluation(self, s):
        results = {_is_valid_hex64(s) for _ in range(10)}
        assert len(results) == 1

    # Every valid hex64 string returns True (completeness)
    @given(_valid_root)
    @settings(max_examples=30)
    def test_valid_hex64_completeness(self, s):
        assert _is_valid_hex64(s) is True

    # Wrong-length strings return False (no false positives on exact length)
    @given(st.binary(min_size=1, max_size=31).map(bytes.hex))
    def test_short_hex_rejected(self, s):
        assert _is_valid_hex64(s) is False

    @given(st.binary(min_size=34, max_size=34).map(bytes.hex))
    def test_long_hex_rejected(self, s):
        assert _is_valid_hex64(s) is False

    # Non-hex chars rejected
    @given(st.text(min_size=1, max_size=64, alphabet="ghijklmnopqrstuvwxyz"))
    def test_non_hex_chars_rejected(self, s):
        assert _is_valid_hex64(s) is False


class TestCheckMerkleRootRoundTrip:
    """_check_merkle_root matches its public API."""

    @given(_valid_root)
    @settings(max_examples=20)
    def test_matching_root_no_raise(self, root):
        record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
        _check_merkle_root(root, record)

    @given(_valid_root)
    @settings(max_examples=20)
    def test_same_root_reflexive(self, root):
        """:_check_merkle_root(root, SealRecord(root=...)) never raises."""
        record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
        # Should not raise
        _check_merkle_root(root, record)

    # Generate two distinct hex64 strings via flatmap
    @given(_valid_root.flatmap(lambda first: _valid_root.map(lambda second: (first, second))))
    @settings(max_examples=30)
    def test_distinct_roots_mismatch(self, pair):
        r1, r2 = pair
        assume(r1 != r2)
        record = SealRecord(merkle_root=r1, epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="mismatch"):
            _check_merkle_root(r2, record)


class TestValidateRootMismatch:
    """validate() must surface root mismatches through SealValidationError."""

    @given(st.one_of(
        st.tuples(_valid_root.filter(lambda a: True), _valid_root.filter(lambda b: True)).filter(lambda p: p[0] != p[1]),
    ))
    @settings(max_examples=30)
    def test_different_roots_raise_validation_error(self, pair):
        r1, r2 = pair
        assume(r1 != r2)
        with pytest.raises(SealValidationError, match="mismatch"):
            validate(r1, SealRecord(merkle_root=r2, epoch=1, seal_type=SealType.SEAL_A))

    @given(_valid_root)
    @settings(max_examples=20)
    def test_same_root_passes_and_returns_identity(self, root):
        record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
        result = validate(root, record)
        assert result is record

    # Determinism on same inputs
    @given(_valid_root)
    @settings(max_examples=10)
    def test_validate_result_deterministic(self, root):
        record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
        r1 = validate(root, record)
        r2 = validate(root, record)
        assert r1 is r2


class TestSealRecordConstruction:
    """Structural invariant on SealRecord construction."""

    @given(_negative_epoch)
    def test_sub_one_epoch_raises(self, ep):
        with pytest.raises(SealError):
            SealRecord(merkle_root="0" * 64, epoch=int(ep), seal_type=SealType.SEAL_A)

    @given(_valid_epoch)
    def test_epoch_1_is_min_ok(self, ep):
        rec = SealRecord(merkle_root="0" * 64, epoch=int(ep), seal_type=SealType.SEAL_A)
        assert rec.epoch >= 1

    @given(_bad_count)
    def test_zero_or_neg_count_raises(self, c):
        with pytest.raises(SealError):
            SealRecord(merkle_root="0" * 64, epoch=1, seal_type=SealType.SEAL_A, count_in_epoch=int(c))

    def test_count_one_ok(self):
        rec = SealRecord(merkle_root="0" * 64, epoch=1, seal_type=SealType.SEAL_A, count_in_epoch=1)
        assert rec.count_in_epoch == 1

    @given(st.text(min_size=1, max_size=63, alphabet="0123456789abcdef"))
    def test_merkle_root_too_short_raises(self, bad):
        with pytest.raises(SealError):
            SealRecord(merkle_root=bad, epoch=1, seal_type=SealType.SEAL_A)

    @given(st.text(min_size=65, max_size=66, alphabet="0123456789abcdef"))
    def test_merkle_root_too_long_raises(self, bad):
        with pytest.raises(SealError):
            SealRecord(merkle_root=bad, epoch=1, seal_type=SealType.SEAL_A)

    def test_empty_merkle_root_raises(self):
        with pytest.raises(SealError):
            SealRecord(merkle_root="", epoch=1, seal_type=SealType.SEAL_A)

    # Immutability
    @given(_valid_root)
    @settings(max_examples=10)
    def test_seal_record_is_frozen(self, root):
        rec = SealRecord(merkle_root=root, epoch=42, seal_type=SealType.SEAL_B)
        with pytest.raises(Exception):
            rec.epoch = 99  # type: ignore[attr-defined]
