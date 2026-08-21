"""Targeted tests to kill surviving mutmut mutants in _check_merkle_root and _check_epoch_counts."""
import pytest

from finance_quant.acceptance.phase_b_seal import (
    SealEpochError,
    SealError,
    SealRecord,
    SealType,
    SealValidationError,
    validate,
    _check_merkle_root,
    _check_epoch_counts,
    _is_valid_hex64,
)


def make_root(n: int = 0) -> str:
    return f"{n:064x}"


# ---- _is_valid_hex64 ----

class TestIsValidHex64:
    def test_valid_hex64(self):
        assert _is_valid_hex64("a" * 64)
        assert _is_valid_hex64("0" * 64)
        assert _is_valid_hex64("ABCDEF0123456789" * 4)

    def test_upper_and_lower(self):
        assert _is_valid_hex64("aAbBcCdD" * 8)

    def test_too_short(self):
        assert not _is_valid_hex64("f" * 63)

    def test_too_long(self):
        assert not _is_valid_hex64("f" * 65)

    def test_non_hex_char(self):
        assert not _is_valid_hex64("g" + "0" * 63)

    def test_not_string(self):
        assert not _is_valid_hex64(123)
        assert not _is_valid_hex64(None)

    def test_empty_string(self):
        assert not _is_valid_hex64("")


# ---- _check_merkle_root ----

class TestCheckMerkleRoot:
    def test_valid_root_matches(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_merkle_root(make_root(1), record)

    def test_mismatch_raises(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="mismatch"):
            _check_merkle_root(make_root(2), record)

    def test_mismatch_message_content(self):
        """Kill mutant that changes the error message."""
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="merkle_root mismatch"):
            _check_merkle_root(make_root(99), record)

    def test_invalid_hex64_raises_validation_error(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="not a valid 64-char hex"):
            _check_merkle_root("zzz", record)

    def test_invalid_hex64_too_short(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="not a valid 64-char hex"):
            _check_merkle_root("deadbeef", record)

    def test_empty_string_merkle_root(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError, match="not a valid 64-char hex"):
            _check_merkle_root("", record)

    def test_non_string_merkle_root(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError):
            _check_merkle_root(12345, record)

    def test_hex64_but_wrong_value(self):
        """Ensure the specific mismatch message is asserted, not just any error."""
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError) as exc_info:
            _check_merkle_root("0" * 64, record)
        assert "mismatch" in str(exc_info.value)
        assert "merkle_root" in str(exc_info.value)


# ---- _check_epoch_counts ----

class TestCheckEpochCounts:
    def test_seal_a_first_seal_ok(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, {})

    def test_seal_a_second_seal_ok(self):
        registry = {1: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, registry)

    def test_seal_a_third_seal_raises(self):
        registry = {1: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError, match="at most 2"):
            _check_epoch_counts(record, registry)

    def test_seal_a_third_seal_message_content(self):
        """Kill mutant that alters the epoch count or boundary."""
        registry = {1: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError) as exc_info:
            _check_epoch_counts(record, registry)
        msg = str(exc_info.value)
        assert "would have 3" in msg
        assert "epoch 1" in msg

    def test_seal_b_first_seal_ok(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
        _check_epoch_counts(record, {})

    def test_seal_b_second_seal_raises(self):
        registry = {1: {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError, match="exactly 1"):
            _check_epoch_counts(record, registry)

    def test_seal_b_second_seal_message_content(self):
        registry = {1: {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError) as exc_info:
            _check_epoch_counts(record, registry)
        msg = str(exc_info.value)
        assert "would have 2" in msg
        assert "epoch 1" in msg

    def test_seal_b_zero_count_in_epoch_is_one(self):
        """count_in_epoch contributes to observed count."""
        registry = {}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B, count_in_epoch=1)
        _check_epoch_counts(record, registry)

    def test_seal_b_count_in_epoch_two_raises(self):
        """count_in_epoch=2 when registry has 0 means observed=2, which != 1 for SEAL-B."""
        registry = {}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B, count_in_epoch=2)
        with pytest.raises(SealEpochError, match="exactly 1"):
            _check_epoch_counts(record, registry)

    def test_seal_b_count_in_epoch_two_message(self):
        registry = {}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B, count_in_epoch=2)
        with pytest.raises(SealEpochError) as exc_info:
            _check_epoch_counts(record, registry)
        assert "would have 2" in str(exc_info.value)

    def test_seal_b_existing_one_plus_count_one_raises(self):
        registry = {5: {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=5, seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError, match="exactly 1"):
            _check_epoch_counts(record, registry)

    def test_seal_a_existing_two_plus_count_one_raises(self):
        registry = {3: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=3, seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError, match="at most 2"):
            _check_epoch_counts(record, registry)

    def test_seal_a_existing_two_message_content(self):
        registry = {3: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=3, seal_type=SealType.SEAL_A)
        with pytest.raises(SealEpochError) as exc_info:
            _check_epoch_counts(record, registry)
        msg = str(exc_info.value)
        assert "would have 3" in msg
        assert "epoch 3" in msg

    def test_different_epoch_no_interference(self):
        registry = {1: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=2, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, registry)

    def test_none_registry_treated_as_empty(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, None)

    def test_unknown_seal_type_raises_seal_error(self):
        class FakeSealType:
            pass
        record = SealRecord.__new__(SealRecord)
        object.__setattr__(record, 'merkle_root', make_root(1))
        object.__setattr__(record, 'epoch', 1)
        object.__setattr__(record, 'seal_type', FakeSealType())
        object.__setattr__(record, 'count_in_epoch', 1)
        with pytest.raises(SealError, match="unknown seal_type"):
            _check_epoch_counts(record, {})

    def test_seal_a_boundary_exactly_two_allowed(self):
        """Observed = 2 should NOT raise for SEAL-A (limit is >2)."""
        registry = {1: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        _check_epoch_counts(record, registry)

    def test_seal_b_count_in_epoch_three_raises_with_correct_message(self):
        registry = {2: {SealType.SEAL_B: 0}}
        record = SealRecord(merkle_root=make_root(1), epoch=2, seal_type=SealType.SEAL_B, count_in_epoch=3)
        with pytest.raises(SealEpochError) as exc_info:
            _check_epoch_counts(record, registry)
        assert "would have 3" in str(exc_info.value)


# ---- validate integration: ordering and error specificity ----

class TestValidateOrderingAndErrors:
    def test_merkle_error_before_epoch_error(self):
        """Merkle validation runs first; even with epoch violation, merkle fails first."""
        registry = {1: {SealType.SEAL_A: 2}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError):
            validate(make_root(2), record, registry)

    def test_valid_seal_a_with_registry(self):
        registry = {1: {SealType.SEAL_A: 0}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        result = validate(make_root(1), record, registry)
        assert result is record

    def test_validate_returns_record_on_success(self):
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
        assert validate(make_root(1), record) is record

    def test_validate_raises_seal_epoch_error_not_validation_for_epoch(self):
        registry = {1: {SealType.SEAL_B: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
        with pytest.raises(SealEpochError) as exc_info:
            validate(make_root(1), record, registry)
        assert isinstance(exc_info.value, SealError)

    def test_seal_a_count_in_epoch_boundary_one(self):
        """count_in_epoch=1 is the default; ensure it's tested explicitly."""
        registry = {1: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A, count_in_epoch=1)
        validate(make_root(1), record, registry)

    def test_seal_a_count_in_epoch_two_would_exceed(self):
        """count_in_epoch=2 when registry already has 1 => observed=3, exceeds limit."""
        registry = {1: {SealType.SEAL_A: 1}}
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A, count_in_epoch=2)
        with pytest.raises(SealEpochError, match="would have 3"):
            validate(make_root(1), record, registry)

    def test_error_type_is_not_mixed(self):
        """Bad merkle_root must raise SealValidationError, never SealEpochError."""
        record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
        with pytest.raises(SealValidationError):
            validate("deadbeef", record)
