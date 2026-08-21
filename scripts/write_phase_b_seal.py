"""Create the Phase B sealed-holdout commitment from feature records only.

The labels file is deliberately not read: the public seal commits to its hash,
but contains no label values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.acceptance.mini_set import make_mini_set_commitment, write_mini_set_receipt


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the Phase B holdout seal")
    parser.add_argument("--fixture", default="data/fixtures/phase-b-holdout")
    parser.add_argument("--out", default="docs/acceptance/PHASE_B_HOLDOUT_SEAL.json")
    args = parser.parse_args(argv)

    fixture = Path(args.fixture)
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    records_path = fixture / manifest["feature_records"]
    labels_path = fixture / manifest["labels"]
    if manifest["labels_sha256"] != _sha256(labels_path):
        raise ValueError("labels do not match the sealed manifest")

    seal = make_mini_set_commitment(
        [line_hash for line_hash in manifest["record_sha256"]],
        manifest["labels_sha256"],
        manifest["eval_harness_sha"],
        max_uses=manifest["max_uses"],
        case_set_id=manifest["case_set_id"],
    )
    # Ensure the manifest points at the exact bytes that were committed.
    if _sha256(records_path) != manifest["feature_records_sha256"]:
        raise ValueError("feature records do not match the sealed manifest")
    out = write_mini_set_receipt(seal, "phase-b-holdout-features", {}, [], args.out)
    print(json.dumps({"path": str(out), "merkle_root": seal.case_merkle_root}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
