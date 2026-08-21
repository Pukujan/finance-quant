This directory contains architecture and project-boundary documentation. The live work graph is tracked in GitHub Issues.

## Optional store tests

Tests for optional store adapters (Timescale, XTDB, Arctic) are gated behind `--run-optional-stores`.

```bash
python -m pytest tests/test_optional_store_contract.py -q --run-optional-stores
# or
FQ_TEST_OPTIONAL_STORES=1 python -m pytest tests/test_optional_store_contract.py -q
```

Install optional dependencies first if available: `pip install "psycopg[binary]" xtdb-client arcticdb`.
Without the flag or env var, these tests are skipped automatically.
