import json
import subprocess
import sys
from pathlib import Path


def test_scorecard_bh_discoveries_are_zero_on_canonical_fixture():
    proc = subprocess.run(
        [sys.executable, str(Path("scripts/run_search_scorecard.py"))],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(proc.stdout)
    assert data["bh_discoveries_across_all_lanes"] == 0
    assert data["lanes"][0]["authority"] == "propose_only"
    assert data["lanes"][1]["authority"] == "propose_only"
    assert round(data["lanes"][0]["median_rank_ic"], 6) == 0.314286
    assert round(data["lanes"][1]["median_rank_ic"], 6) == -0.4
