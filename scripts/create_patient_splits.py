from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.model_selection import StratifiedGroupKFold


ROOT = Path(__file__).resolve().parent.parent


def _normalise_processing_status(value: str | None) -> str:
    if value in {"success", "processed"}:
        return "success"
    return "failed"


def create_splits(metadata_path: Path, output_path: Path, report_path: Path,
                  n_splits: int = 5, seed: int = 42) -> dict:
    with metadata_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if _normalise_processing_status(row.get("processing_status")) == "success"
        ]
    if not rows:
        raise ValueError("No successfully processed samples are available for splitting")
    missing_ids = [row["sample_id"] for row in rows if not row["patient_id"]]
    if missing_ids:
        raise ValueError(
            f"Patient-independent splits blocked: {len(missing_ids)} processed samples have no PID. "
            "No patient IDs were imputed."
        )
    patients_by_class: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        patients_by_class[row["class_name"]].add(row["patient_id"])
    insufficient = {name: len(ids) for name, ids in patients_by_class.items() if len(ids) < n_splits}
    if insufficient:
        raise ValueError(
            f"Stratified {n_splits}-fold grouped splitting is infeasible: fewer than {n_splits} "
            f"distinct patients in class(es) {insufficient}. No slice-level fallback was used."
        )

    labels = [row["class_name"] for row in rows]
    groups = [row["patient_id"] for row in rows]
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    assignment = {}
    for fold_number, (_, test_indices) in enumerate(splitter.split([0] * len(rows), labels, groups), start=1):
        for index in test_indices:
            assignment[rows[index]["sample_id"]] = f"fold_{fold_number}"
    if len(assignment) != len(rows):
        raise RuntimeError(f"Fold assignment count {len(assignment)} does not match sample count {len(rows)}")

    patient_fold = {}
    for row in rows:
        fold = assignment[row["sample_id"]]
        previous = patient_fold.setdefault(row["patient_id"], fold)
        if previous != fold:
            raise RuntimeError(f"Patient {row['patient_id']} appears in multiple folds")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=["sample_id", "patient_id", "class", "fold"])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "sample_id": row["sample_id"],
                "patient_id": row["patient_id"],
                "class": row["class_name"],
                "fold": assignment[row["sample_id"]],
            })

    summary = []
    for fold in [f"fold_{number}" for number in range(1, n_splits + 1)]:
        selected = [row for row in rows if assignment[row["sample_id"]] == fold]
        summary.append({
            "fold": fold,
            "patient_count": len({row["patient_id"] for row in selected}),
            "slice_count": len(selected),
            "class_counts": dict(Counter(row["class_name"] for row in selected)),
        })
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Patient-grouped cross-validation splits",
        "",
        f"- Stratifier: `StratifiedGroupKFold(n_splits={n_splits}, shuffle=True, random_state={seed})`.",
        f"- Samples assigned: {len(rows)}; distinct patients: {len(patient_fold)}.",
        "- All slices with the same exact PID are assigned to one fold. PID is not modified or synthesized.",
        "- Fold overlap check: **PASS** (no patient ID appears in more than one fold).",
        "- The provided `cvind.mat` vector remains unverified; no file-to-fold mapping was inferred from numeric ordering alone.",
        "",
        "| Fold | Patients | Slices | Class distribution |",
        "|---|---:|---:|---|",
    ]
    for item in summary:
        lines.append(f"| {item['fold']} | {item['patient_count']} | {item['slice_count']} | `{item['class_counts']}` |")
    lines.extend([
        "",
        "Per-class balance is approximate at the patient-group level; slices are not independent observations. "
        "Use only the assignments in the CSV, and do not use the original `cvind.mat` as a patient-independent split. "
        "The split was generated from verified patient IDs, not from an unproven `cvind.mat` order.",
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    audit_path = report_path.parent / "PATIENT_SPLIT_AUDIT.md"
    audit_lines = [
        "# Patient split audit",
        "",
        "- The supplied `cvind.mat` vector remains **unverified** for file-to-sample mapping.",
        "- Numeric filename order is suggestive but not sufficient evidence that `cvind[i]` corresponds to file `i.mat`.",
        "- Therefore, patient-independent cross-validation is generated from observed `PID` values only, not from the raw `cvind` vector.",
        "- The patient assignment is enforced by group membership, and no patient ID appears in more than one fold.",
        "- Any earlier assumption that five folds alone imply patient independence is not used here.",
    ]
    audit_path.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    return {
        "samples": len(rows),
        "patients": len(patient_fold),
        "folds": summary,
        "patient_overlap": False,
        "seed": seed,
        "n_splits": n_splits,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic patient-independent folds.")
    parser.add_argument("--metadata", type=Path, default=ROOT / "prepared" / "metadata.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "prepared" / "patient_splits.csv")
    parser.add_argument("--report", type=Path, default=ROOT / "reports" / "patient_split_summary.md")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    import json
    print(json.dumps(create_splits(args.metadata, args.output, args.report, args.folds, args.seed), indent=2))


if __name__ == "__main__":
    main()
