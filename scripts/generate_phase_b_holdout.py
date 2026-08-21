"""Generate the local synthetic Phase B holdout and its private labels."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.acceptance.seal import merkle_root


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    out = Path("data/fixtures/phase-b-holdout")
    out.mkdir(parents=True, exist_ok=True)
    symbols = ["AAA", "BBB", "CCC", "DDD", "EEE"]
    lines: list[bytes] = []
    labels: list[str] = []
    start = date(2025, 1, 1)
    for day in range(20):
        trading_day = start + timedelta(days=day)
        for index, symbol in enumerate(symbols):
            close = 100.0 + index * 10 + day * 0.25
            record = {
                "instrument_id": symbol,
                "namespace": "bar",
                "vt": f"{trading_day.isoformat()}T16:00:00Z",
                "kt": f"{trading_day.isoformat()}T16:00:01Z",
                "payload": {"open": close - 0.5, "high": close + 0.5,
                            "low": close - 1.0, "close": close, "volume": 1000 + index * 100 + day},
                "source": {"vendor": "synthetic", "feed": "stocks/eod", "collection_method": "generated"},
                "revision": 1,
                "superseded_by": None,
            }
            encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
            lines.append(encoded)
            labels.append(json.dumps({"instrument_id": symbol, "as_of": record["vt"],
                                      "future_return": round((index - 2) * 0.01 + day * 0.0001, 6)},
                                     sort_keys=True, separators=(",", ":")))
    feature_bytes = b"".join(lines)
    label_bytes = ("\n".join(labels) + "\n").encode()
    (out / "feature_records.jsonl").write_bytes(feature_bytes)
    (out / "labels.jsonl").write_bytes(label_bytes)
    record_hashes = [sha256(line.rstrip(b"\n")) for line in lines]
    manifest = {
        "case_set_id": "PHASE-B-HOLDOUT-20D",
        "feature_records": "feature_records.jsonl",
        "labels": "labels.jsonl",
        "record_count": len(record_hashes),
        "record_sha256": record_hashes,
        "feature_records_sha256": sha256(feature_bytes),
        "labels_sha256": sha256(label_bytes),
        "merkle_root": merkle_root(record_hashes),
        "eval_harness_sha": "h" * 40,
        "max_uses": 2,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(manifest["merkle_root"])


if __name__ == "__main__":
    main()
