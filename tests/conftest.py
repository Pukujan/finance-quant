"""Test-local path setup.

Ensures the repository root is on ``sys.path`` so scripts and finance_quant are
importable regardless of the current working directory (including mutmut's
mutant copy).
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve()
ROOT = _here.parents[1]
if ROOT.name == "mutants":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
