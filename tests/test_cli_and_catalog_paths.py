from pathlib import Path
import json

from finance_quant import __main__ as cli


ROOT = Path(__file__).resolve().parents[1]


def test_cli_lists_known_commands():
    assert cli.main(["help"]) == 0
    assert cli.main(["nope"]) == 2
    assert "scripts/smoke.py" in cli.COMMANDS["smoke"]
    for path in cli.COMMANDS.values():
        assert (ROOT / path).exists()


def test_property_catalog_oracles_point_at_existing_paths():
    catalog = json.loads((ROOT / "contracts/properties/finance-quant-properties-v1.json").read_text())
    missing = []
    for prop in catalog["properties"]:
        for oracle in prop["oracle"]:
            if oracle.startswith("tests/") and "::" in oracle:
                path = ROOT / oracle.split("::", 1)[0]
                if not path.exists():
                    missing.append(oracle)
            elif oracle.startswith("formal/") or oracle.startswith("tests/"):
                path = ROOT / oracle.split("::", 1)[0]
                if not path.exists():
                    missing.append(oracle)
    assert missing == []
