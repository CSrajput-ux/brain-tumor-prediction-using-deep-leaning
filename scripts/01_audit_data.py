"""Summarize generated manifests into a human- and machine-readable data audit."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summary(rows: list[dict]) -> dict:
    usable = [r for r in rows if not r["exclusion_reason"] and "unreadable" not in r["quality_flags"]]
    return {
        "indexed_samples": len(rows),
        "readable_samples": len(usable),
        "class_counts": dict(sorted(Counter(r["class_label"] for r in rows).items())),
        "official_split_counts": dict(sorted(Counter(r["official_split"] or "not_supplied" for r in rows).items())),
        "plane_counts": dict(sorted(Counter(r["plane"] or "not_supplied" for r in rows).items())),
        "patient_count_if_supplied": len({r["patient_id"] for r in rows if r["patient_id"]}),
        "mask_available_count": sum(r["mask_available"] == "True" for r in rows),
        "missing_mask_count": sum("missing_mask" in r["quality_flags"] for r in rows),
        "empty_mask_count": sum("empty_tumor_mask" in r["quality_flags"] for r in rows),
        "dimension_mismatch_count": sum("dimension_mismatch" in r["quality_flags"] for r in rows),
        "unreadable_or_malformed_count": sum("unreadable" in r["quality_flags"] for r in rows),
        "quality_flag_counts": dict(sorted(Counter(
            flag for r in rows for flag in r["quality_flags"].split(";") if flag
        ).items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-dir", type=Path, default=ROOT / "manifests")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    out = {name: summary(read_rows(args.manifest_dir / f"{name}_manifest.csv")) for name in ("cheng", "brisc")}
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / "data_audit_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lines = ["# Data audit", "", "Generated from local manifests; counts below are observed, not expected release counts.", ""]
    for name, value in out.items():
        lines.extend([f"## {name}", "", "```json", json.dumps(value, indent=2), "```", ""])
    (args.report_dir / "data_audit.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
