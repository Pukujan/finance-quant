"""CSV snapshot export of an as_of extract. Derived artifact, not authority."""
from __future__ import annotations

import csv
from pathlib import Path

from finance_quant.pit.store import PITStore


def export_as_of_csv(store: PITStore, path: str | Path, namespace: str, instruments: list[str],
                     vt_start: str, vt_end: str, kt_bound: str) -> Path:
    path = Path(path)
    rows = store.as_of(namespace, instruments, vt_start, vt_end, kt_bound)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["namespace", "instrument_id", "vt", "kt", "revision", "close"])
        for r in rows:
            writer.writerow([r.namespace, r.instrument_id, r.vt, r.kt, r.revision,
                             r.payload.get("close", "")])
    return path
