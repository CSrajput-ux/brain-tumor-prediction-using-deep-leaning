from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from dataset_utils import CLASS_NAMES, EXPECTED_CLASS_COUNTS, json_value

ROOT = Path(__file__).resolve().parent.parent
PHASH_COS = np.cos((2 * np.arange(32)[:, None] + 1) * np.arange(8)[None, :] * math.pi / 64)
POPCOUNT = np.array([int(i).bit_count() for i in range(256)], dtype=np.uint8)


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _is_success(row: dict) -> bool:
    return str(row.get("processing_status", "")).lower() in {"success", "processed"}


def _phash(image: np.ndarray) -> int:
    if image.ndim != 2:
        image = np.asarray(Image.fromarray(image).convert("L"))
    resized = np.asarray(Image.fromarray(image.astype(np.uint8)).resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float64)
    coefficients = (PHASH_COS.T @ resized @ PHASH_COS)[1:9, 1:9]
    median = float(np.median(coefficients))
    result = 0
    for bit in (coefficients > median).ravel():
        result = (result << 1) | int(bit)
    return int(result)


def _near_duplicate_pairs(rows: list[dict], output_dir: Path, max_distance: int = 4) -> list[dict]:
    valid = []
    for row in rows:
        if not _is_success(row) or not row.get("image_output_path"):
            continue
        image_path = output_dir / row["image_output_path"]
        try:
            with Image.open(image_path) as image:
                valid.append((row, _phash(np.asarray(image.convert("L")))))
        except (OSError, ValueError, TypeError):
            continue
    if len(valid) < 2:
        return []
    hashes = np.asarray([value for _, value in valid], dtype=np.uint64)
    pairs = []
    for index in range(len(valid)):
        distances = POPCOUNT[
            np.bitwise_xor(hashes[index], hashes[index + 1:]).view(np.uint8).reshape(-1, 8)
        ].sum(axis=1)
        for offset in np.flatnonzero(distances <= max_distance):
            right = index + 1 + int(offset)
            left_row, right_row = valid[index][0], valid[right][0]
            pairs.append({
                "duplicate_type": "near_duplicate_phash",
                "value": f"hamming={int(distances[offset])}",
                "sample_ids": json_value([left_row["sample_id"], right_row["sample_id"]]),
                "source_paths": json_value([left_row["source_path"], right_row["source_path"]]),
                "count": 2,
                "details": (
                    "Per-image normalized PNG pHash distance <=4/64; candidate only, retained; "
                    f"{'same PID' if left_row.get('patient_id') and left_row['patient_id'] == right_row.get('patient_id') else 'different PIDs' if left_row.get('patient_id') and right_row.get('patient_id') else 'PID unavailable'}; "
                    f"{'same class' if left_row.get('class_name') == right_row.get('class_name') else 'different classes'}."
                ),
            })
    return pairs


def validate(output_dir: Path, report_dir: Path, require_complete: bool = True) -> dict:
    metadata_path = output_dir / "metadata.csv"
    inventory_path = output_dir / "inventory.csv"
    if not metadata_path.is_file() or not inventory_path.is_file():
        raise FileNotFoundError("metadata.csv or inventory.csv missing; run prepare_cheng_dataset.py first")

    rows = _read_csv(metadata_path)
    inventory = _read_csv(inventory_path)
    errors: list[str] = []
    warnings: list[str] = []
    discovered = sum(int(row["mat_file_count"]) for row in inventory)
    processed_rows = [row for row in rows if _is_success(row)]
    failed_rows = [row for row in rows if not _is_success(row)]

    classes = Counter(row.get("class_name") for row in processed_rows if row.get("class_name"))
    patient_ids = [row.get("patient_id") for row in processed_rows if row.get("patient_id")]
    patient_counts = Counter(patient_ids)
    missing_pid = [row for row in processed_rows if not row.get("patient_id")]
    missing_masks = [row for row in processed_rows if str(row.get("mask_available", "")).lower() != "true"]
    invalid_masks = [row for row in processed_rows if str(row.get("mask_status", "")).lower() not in {"valid", "missing"}]
    image_mask_mismatches = [
        row for row in processed_rows
        if str(row.get("mask_available", "")).lower() == "true" and row.get("mask_shape") and row.get("image_shape") != row.get("mask_shape")
    ]

    ids = [row["sample_id"] for row in rows]
    if len(set(ids)) != len(ids):
        errors.append(f"Duplicate stable sample IDs: {len(ids) - len(set(ids))}")
    if len(rows) != discovered and require_complete:
        errors.append(f"Metadata rows {len(rows)} do not equal discovered .mat files {discovered}")
    if len(ids) != len(set(row["source_path"] for row in rows)):
        errors.append("One or more source files appear more than once in metadata")

    output_path_issues: list[str] = []
    for directory in ("images", "masks", "raw_arrays", "overlays"):
        if not (output_dir / directory).is_dir():
            output_path_issues.append(f"Missing output directory: {directory}")
    for row in processed_rows:
        for key in ("image_output_path", "raw_array_output_path"):
            relative = row.get(key)
            if not relative:
                output_path_issues.append(f"{row['sample_id']}: missing {key}")
                continue
            if not (output_dir / relative).is_file():
                output_path_issues.append(f"{row['sample_id']}: missing {key} ({relative})")
        if row.get("mask_output_path") and not (output_dir / row["mask_output_path"]).is_file():
            output_path_issues.append(f"{row['sample_id']}: missing mask output ({row['mask_output_path']})")
        if row.get("overlay_output_path") and not (output_dir / row["overlay_output_path"]).is_file():
            output_path_issues.append(f"{row['sample_id']}: missing overlay output ({row['overlay_output_path']})")
        try:
            if row.get("image_output_path"):
                with Image.open(output_dir / row["image_output_path"]) as image:
                    exported_shape = [image.height, image.width]
                    if row.get("image_shape") and json.loads(row["image_shape"]) != exported_shape:
                        output_path_issues.append(f"{row['sample_id']}: exported image dimensions differ from source")
            if row.get("mask_output_path"):
                with Image.open(output_dir / row["mask_output_path"]) as mask:
                    if row.get("mask_shape") and json.loads(row["mask_shape"]) != [mask.height, mask.width]:
                        output_path_issues.append(f"{row['sample_id']}: exported mask dimensions differ from source")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            output_path_issues.append(f"{row['sample_id']}: output image/mask cannot be read: {exc}")
    if output_path_issues:
        errors.extend(output_path_issues)

    # Duplicate audit built from metadata and exported images.
    duplicate_rows = []
    filename_groups: dict[str, list[dict]] = defaultdict(list)
    checksum_groups: dict[str, list[dict]] = defaultdict(list)
    image_checksum_groups: dict[str, list[dict]] = defaultdict(list)
    patient_class_groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        filename_groups[row.get("original_filename", "").casefold()].append(row)
        if row.get("sha256"):
            checksum_groups[row["sha256"]].append(row)
        if row.get("image_array_sha256"):
            image_checksum_groups[row["image_array_sha256"]].append(row)
        if _is_success(row) and row.get("patient_id"):
            patient_class_groups[row["patient_id"]].append(row)
    for name, group in filename_groups.items():
        if len(group) > 1:
            duplicate_rows.append({
                "duplicate_type": "filename",
                "value": name,
                "sample_ids": json_value([r["sample_id"] for r in group]),
                "source_paths": json_value([r["source_path"] for r in group]),
                "count": len(group),
                "details": "Duplicate filename across scanned folders; retained for audit.",
            })
    for digest, group in checksum_groups.items():
        if len(group) > 1:
            duplicate_rows.append({
                "duplicate_type": "sha256",
                "value": digest,
                "sample_ids": json_value([r["sample_id"] for r in group]),
                "source_paths": json_value([r["source_path"] for r in group]),
                "count": len(group),
                "details": "Exact duplicate source content confirmed by SHA-256.",
            })
    duplicate_rows.extend(_near_duplicate_pairs(rows, output_dir))

    summary = {
        "run_root": str(output_dir),
        "discovered_mat_files": discovered,
        "successful_samples": len(processed_rows),
        "failed_samples": len(failed_rows),
        "class_counts": dict(classes),
        "unique_patient_ids": len(set(patient_ids)),
        "missing_patient_ids": len(missing_pid),
        "missing_masks": len(missing_masks),
        "invalid_masks": len(invalid_masks),
        "image_mask_mismatches": len(image_mask_mismatches),
        "duplicate_rows": len(duplicate_rows),
        "errors": errors,
        "warnings": warnings,
        "quality_status_counts": dict(Counter(row.get("quality_status", "") for row in processed_rows)),
        "mask_status_counts": dict(Counter(row.get("mask_status", "") for row in processed_rows)),
        "expected_class_counts": EXPECTED_CLASS_COUNTS,
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "validation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Cheng dataset validation",
        "",
        f"- Discovered MAT files: {discovered}",
        f"- Successfully processed files: {len(processed_rows)}",
        f"- Failed or unreadable files: {len(failed_rows)}",
        f"- Class counts: {dict(classes)}",
        f"- Unique patient IDs: {len(set(patient_ids))}",
        f"- Missing patient IDs: {len(missing_pid)}",
        f"- Missing masks: {len(missing_masks)}",
        f"- Invalid masks: {len(invalid_masks)}",
        f"- Image-mask mismatches: {len(image_mask_mismatches)}",
        f"- Duplicate findings: {len(duplicate_rows)}",
        "",
    ]
    if errors:
        lines.append("## Errors")
        for error in errors:
            lines.append(f"- {error}")
    if warnings:
        lines.append("## Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")
    (report_dir / "DATASET_AUDIT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate prepared Cheng dataset outputs and report quality issues.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "prepared")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--allow-partial", action="store_true", help="Allow validation of a partial run without requiring every source file to be accounted for.")
    args = parser.parse_args()
    summary = validate(args.output_dir, args.report_dir, require_complete=not args.allow_partial)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
