"""Edge-case tests targeting surviving mutants in phase_b_seal."""
import pytest
import re

from finance_quant.acceptance.phase_b_seal import (
    _is_valid_hex64,
    _check_merkle_root,
    _check_epoch_counts,
    validate,
    SealRecord,
    SealType,
    SealError,
    SealValidationError,
    SealEpochError,
)


def make_root(n: int = 0) -> str:
    return f"{n:064x}"


# ── __is_valid_hex64: non-hex chars ──────────────────────────────────────────

class TestIsValidHex64NonHexChars:
    def test_contains_g(self):
        assert _is_valid_hex64("g" * 64) is False

    def test_contains_z(self):
        assert _is_valid_hex64("z" + "a" * 63) is False

    def test_all_valid_hex(self):
        assert _is_valid_hex64("a" * 64) is True


# ── __is_valid_hex64: mixed case ─────────────────────────────────────────────

class TestIsValidHex64MixedCase:
    def test_mixed_case_is_still_valid(self):
        assert _is_valid_hex64("Aa" * 32) is True

    def test_all_uppercase_valid(self):
        assert _is_valid_hex64("AF" * 32) is True

    def test_all_lowercase_valid(self):
        assert _is_valid_hex64("af" * 32) is True


# ── __is_valid_hex64: wrong length ───────────────────────────────────────────

class TestIsValidHex64WrongLength:
    def test_length_63(self):
        assert _is_valid_hex64("a" * 63) is False

    def test_length_65(self):
        assert _is_valid_hex64("a" * 65) is False

    def test_empty_string(self):
        assert _is_valid_hex64("") is False

    def test_not_a_string(self):
        assert _is_valid_hex64(123) is False  # type: ignore


# ── __check_merkle_root: valid root passes ────────────────────────────────────

class TestCheckMerkleRootValidPasses:
    def test_matching_root_no_raise(self):
        root = make_root(42)
        record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
        _check_merkle_root(root, record)  # should not raise


# ── __check_merkle_root: mismatch raises ──────────────────────────────────────

class TestCheckMerkleRootMismatchRaises:
    def test_mismatch_raises(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="mismatch"):
            _check_merkle_root(make_root(2), record)


# ── __check_merkle_root: invalid root raises before comparison ────────────────

class TestCheckMerkleRootInvalidBeforeComparison:
    def test_non_hex_raises_validation_error(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="not a valid"):
            _check_merkle_root("zz" * 32, record)

    def test_wrong_length_raises(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="not a valid"):
            _check_merkle_root("ab", record)


# ── __check_epoch_counts: SEAL-A exactly 2 is OK ─────────────────────────────

class TestEpochCountsSealAExactly2:
    def test_seal_a_exactly_2_ok(self):
        registry = {1: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, registry)  # 1 + 1 = 2, OK


# ── __check_epoch_counts: SEAL-A 3 fails ──────────────────────────────────────

class TestEpochCountsSealAFails:
    def test_seal_a_three_raises(self):
        registry = {1: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError, match="at most 2"):
            _check_epoch_counts(record, registry)


# ── __check_epoch_counts: SEAL-B count 0 fails ────────────────────────────────

class TestEpochCountsSealBZeroFails:
    def test_seal_b_count_1_with_zero_prefix_is_ok(self):
        registry = {}
        record = SealRecord(merkle_root=make_root(1), epoch=5, seal_type=SealType.SEAL_B)
        _check_epoch_counts(record, registry)  # 0 + 1 = 1, SEAL-B exactly 1 OK


# ── __check_epoch_counts: SEAL-B count 2 fails ────────────────────────────────

class TestEpochCountsSealBCount2Fails:
    def test_seal_b_count_2_raises(self):
        registry = {}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B, count_in_epoch=2)
        with pytest.raises(SealEpochError, match="exactly 1"):
            _check_epoch_counts(record, registry)


# ── __check_epoch_counts: registry accumulation ───────────────────────────────

class TestEpochCountsRegistryAccumulation:
    def test_seal_a_accumulates_across_epochs(self):
        registry = {1: {SealType.SEAL_A: 2}, 2: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=2, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, registry)  # 1 + 1 = 2 in epoch 2, OK

    def test_seal_b_accumulates_with_prior_in_same_epoch(self):
        registry = {3: {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=3, seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError, match="exactly 1"):
            _check_epoch_counts(record, registry)
