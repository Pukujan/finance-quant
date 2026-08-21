"""Test-local path setup.

Ensures the repository root is on ``sys.path`` so scripts and finance_quant are
importable regardless of the current working directory (including mutmut's
mutant copy).
"""
import os
import sys
from pathlib import Path

import pytest

_here = Path(__file__).resolve()
ROOT = _here.parents[1]
if ROOT.name == "mutants":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_addoption(parser):
    parser.addoption(
        "--run-optional-stores",
        action="store_true",
        default=False,
        help="Run optional store adapter tests (Timescale, XTDB, Arctic)",
    )


def _optional_stores_enabled(config) -> bool:
    return config.getoption("--run-optional-stores", default=False) or os.environ.get("FQ_TEST_OPTIONAL_STORES") == "1"


def pytest_collection_modifyitems(config, items):
    if _optional_stores_enabled(config):
        return
    skip = pytest.mark.skip(reason="pass --run-optional-stores or set FQ_TEST_OPTIONAL_STORES=1")
    for item in items:
        if "optional_store" in item.keywords:
            item.add_marker(skip)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "optional_store: tests for optional store adapters (Timescale, XTDB, Arctic)"
    )
