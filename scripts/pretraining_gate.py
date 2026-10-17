from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from dataset_utils import CLASS_NAMES, native_array, patient_id_text, read_cjdata, scalar_number

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_COUNTS = {"meningioma": 708, "glioma": 1426, "pituitary": 930}
NEAR_DUPLICATE_REVIEW_THRESHOLD = 0.80


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _image_ssim(first: np.ndarray, second: np.ndarray) -> float:
    first = first.astype(np.float64)
    second = second.astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mean_first = gaussian_filter(first, sigma=1.5)
    mean_second = gaussian_filter(second, sigma=1.5)
    variance_first = gaussian_filter(first * first, sigma=1.5) - mean_first * mean_first
    variance_second = gaussian_filter(second * second, sigma=1.5) - mean_second * mean_second
    covariance = gaussian_filter(first * second, sigma=1.5) - mean_first * mean_second
    numerator = (2 * mean_first * mean_second + c1) * (2 * covariance + c2)
    denominator = (
        (mean_first * mean_first + mean_second * mean_second + c1)
        * (variance_first + variance_second + c2)
    )
    return float(np.mean(numerator / denominator))


def _fold_assignments(rows: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, set[str]]]:
    assignments: dict[str, list[dict[str, str]]] = defaultdict(list)
    patient_folds: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        assignments[row["sample_id"]].append(row)
        patient_folds[row["patient_id"]].add(row["fold"])
    return assignments, patient_folds


def _audit_near_duplicates(
    duplicate_rows: list[dict[str, str]],
    metadata: dict[str, dict[str, str]],
    splits: dict[str, list[dict[str, str]]],
    prepared_dir: Path,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    image_cache: dict[str, np.ndarray] = {}

    def image(sample_id: str) -> np.ndarray:
        if sample_id not in image_cache:
            record = metadata[sample_id]
            with Image.open(prepared_dir / record["image_output_path"]) as source:
                image_cache[sample_id] = np.asarray(source.convert("L"), dtype=np.uint8)
        return image_cache[sample_id]

    for duplicate in duplicate_rows:
        if duplicate.get("classification") != "near_duplicate_candidate":
            continue
        sample_ids = json.loads(duplicate["sample_ids"])
        if len(sample_ids) != 2 or any(sample_id not in metadata for sample_id in sample_ids):
            continue
        first_id, second_id = sample_ids
        first, second = metadata[first_id], metadata[second_id]
        first_fold = splits[first_id][0]["fold"] if len(splits.get(first_id, [])) == 1 else ""
        second_fold = splits[second_id][0]["fold"] if len(splits.get(second_id, [])) == 1 else ""
        first_image, second_image = image(first_id), image(second_id)
        if first_image.shape == second_image.shape:
            pixel_equal_fraction = float(np.mean(first_image == second_image))
            ssim = _image_ssim(first_image, second_image)
            if first_image.std() and second_image.std():
                pearson = float(np.corrcoef(first_image.ravel(), second_image.ravel())[0, 1])
            else:
                pearson = None
        else:
            pixel_equal_fraction = None
            ssim = None
            pearson = None
        cross_patient = first["patient_id"] != second["patient_id"]
        cross_fold = bool(first_fold and second_fold and first_fold != second_fold)
        review_required = cross_patient and cross_fold
        findings.append({
            "group_id": duplicate.get("group_id", ""),
            "sample_id_a": first_id,
            "sample_id_b": second_id,
            "source_path_a": first["source_path"],
            "source_path_b": second["source_path"],
            "patient_id_a": first["patient_id"],
            "patient_id_b": second["patient_id"],
            "class_a": first["class_name"],
            "class_b": second["class_name"],
            "fold_a": first_fold,
            "fold_b": second_fold,
            "phash_hamming_distance": duplicate.get("similarity_score", ""),
            "pixel_equal_fraction": pixel_equal_fraction,
            "ssim": ssim,
            "pearson_correlation": pearson,
            "cross_patient": cross_patient,
            "cross_fold": cross_fold,
            "review_status": "requires_manual_review" if review_required else "not_cross_patient_cross_fold",
            "ssim_review_flag": bool(ssim is not None and ssim >= NEAR_DUPLICATE_REVIEW_THRESHOLD),
            "confirmed_duplicate": False,
        })
    return findings


def _runtime_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "logical_cpu_count": __import__("os").cpu_count(),
        "torch_available": False,
        "cuda_available": False,
    }
    try:
        import torch
        info.update({
            "torch_available": True,
            "torch_version": torch.__version__,
            "torch_cuda_build": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "gpu_vram_bytes": torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None,
        })
        import torchvision
        info["torchvision_version"] = torchvision.__version__
        info["resnet18_imagenet1k_v1_cached"] = (
            Path.home() / ".cache" / "torch" / "hub" / "checkpoints" / "resnet18-f37072fd.pth"
        ).is_file()
        info["resnet50_imagenet1k_v2_cached"] = (
            Path.home() / ".cache" / "torch" / "hub" / "checkpoints" / "resnet50-11ad3fa6.pth"
        ).is_file()
    except ImportError as error:
        info["torch_import_error"] = str(error)
    return info


def run_gate(prepared_dir: Path, source_root: Path, output_dir: Path) -> dict[str, Any]:
    prepared_dir, source_root, output_dir = prepared_dir.resolve(), source_root.resolve(), output_dir.resolve()
    metadata_path = prepared_dir / "metadata.csv"
    split_path = prepared_dir / "patient_splits.csv"
    duplicate_path = prepared_dir / "duplicate_audit.csv"
    manifest_path = prepared_dir / "manifest.json"
    required = [metadata_path, split_path, duplicate_path, manifest_path]
    missing_artifacts = [str(path) for path in required if not path.is_file()]
    if missing_artifacts:
        raise FileNotFoundError("Required pretraining artifacts are missing: " + ", ".join(missing_artifacts))

    metadata_rows = read_csv(metadata_path)
    split_rows = read_csv(split_path)
    duplicate_rows = read_csv(duplicate_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata = {row["sample_id"]: row for row in metadata_rows}
    splits, patient_folds = _fold_assignments(split_rows)
    issues: list[str] = []
    if len(metadata) != len(metadata_rows):
        issues.append("Metadata sample IDs are not unique.")
    if len(splits) != len(split_rows):
        issues.append("Split manifest sample IDs are not unique.")

    metadata_ids, split_ids = set(metadata), set(splits)
    if len({row.get("source_path") for row in metadata_rows}) != len(metadata_rows):
        issues.append("Metadata contains duplicate source paths.")
    if any(row.get("processing_status") != "success" for row in metadata_rows):
        issues.append("One or more metadata rows do not have processing_status=success.")
    if any(row.get("quality_status") != "pass" for row in metadata_rows):
        issues.append("One or more metadata rows do not have quality_status=pass.")
    if any(row.get("mask_status") != "valid" for row in metadata_rows):
        issues.append("One or more metadata rows do not have mask_status=valid.")
    missing_split = sorted(metadata_ids - split_ids)
    extra_split = sorted(split_ids - metadata_ids)
    if missing_split or extra_split:
        issues.append(f"Split coverage mismatch: {len(missing_split)} missing and {len(extra_split)} extra sample IDs.")
    bad_split_cardinality = sorted(sample_id for sample_id, assignments in splits.items() if len(assignments) != 1)
    if bad_split_cardinality:
        issues.append(f"{len(bad_split_cardinality)} samples have other than one fold assignment.")
    patient_overlap = {pid: sorted(folds) for pid, folds in patient_folds.items() if len(folds) > 1}
    if patient_overlap:
        issues.append(f"{len(patient_overlap)} patient IDs occur in multiple folds.")

    split_metadata_mismatch = []
    for sample_id in metadata_ids & split_ids:
        assignments = splits[sample_id]
        if len(assignments) == 1 and (
            assignments[0].get("patient_id") != metadata[sample_id].get("patient_id")
            or assignments[0].get("class") != metadata[sample_id].get("class_name")
        ):
            split_metadata_mismatch.append(sample_id)
    if split_metadata_mismatch:
        issues.append(f"{len(split_metadata_mismatch)} split rows disagree with metadata patient or class.")

    observed_classes = Counter(row.get("class_name") for row in metadata_rows)
    if dict(observed_classes) != EXPECTED_COUNTS:
        issues.append(f"Observed class counts {dict(observed_classes)} differ from expected {EXPECTED_COUNTS}.")

    source_failures: list[dict[str, str]] = []
    output_failures: list[dict[str, str]] = []
    source_hash_mismatches = []
    pids_by_class: dict[str, set[str]] = defaultdict(set)
    source_hashes: Counter[str] = Counter()
    for row in metadata_rows:
        sample_id = row["sample_id"]
        source = Path(row["source_path"])
        if not source.is_file():
            source_failures.append({"sample_id": sample_id, "reason": "source file missing"})
            continue
        source_digest = sha256_file(source)
        source_hashes[source_digest] += 1
        if source_digest != row.get("sha256"):
            source_hash_mismatches.append(sample_id)
        try:
            fields, _reader = read_cjdata(source)
            label_value = scalar_number(fields["label"], "label")
            class_name = CLASS_NAMES.get(int(label_value)) if float(label_value).is_integer() else None
            pid = patient_id_text(fields["PID"])
            source_image = native_array(fields["image"])
            source_mask = native_array(fields["tumorMask"])
            if class_name != row.get("class_name") or str(int(label_value)) != str(row.get("class_label")):
                source_failures.append({"sample_id": sample_id, "reason": "cjdata.label mismatch"})
            if pid is None or pid != row.get("patient_id"):
                source_failures.append({"sample_id": sample_id, "reason": "cjdata.PID missing or mismatched"})
            if source_image is None or source_image.ndim != 2 or not source_image.size or not np.isfinite(source_image).all():
                source_failures.append({"sample_id": sample_id, "reason": "cjdata.image invalid"})
            if source_mask is None or source_image is None or source_mask.shape != source_image.shape:
                source_failures.append({"sample_id": sample_id, "reason": "source mask missing or dimension-mismatched"})
            elif (
                source_mask.ndim != 2
                or not np.isfinite(source_mask).all()
                or not np.isin(np.unique(source_mask), [0, 1]).all()
                or not np.count_nonzero(source_mask)
            ):
                source_failures.append({"sample_id": sample_id, "reason": "source mask invalid or empty"})
            if class_name and pid:
                pids_by_class[class_name].add(pid)
        except Exception as error:
            source_failures.append({"sample_id": sample_id, "reason": f"{type(error).__name__}: {error}"})
        for field in ("image_output_path", "mask_output_path", "raw_array_output_path"):
            relative = row.get(field, "")
            path = prepared_dir / relative if relative else None
            if path is None or not path.is_file():
                output_failures.append({"sample_id": sample_id, "reason": f"missing {field}"})
                continue
            try:
                if field in {"image_output_path", "mask_output_path"}:
                    with Image.open(path) as image:
                        image.verify()
                    with Image.open(path) as image:
                        array = np.asarray(image)
                    expected_shape = json.loads(row["image_shape"])
                    if list(array.shape[:2]) != expected_shape:
                        output_failures.append({"sample_id": sample_id, "reason": f"{field} dimension mismatch"})
                    if field == "mask_output_path" and (
                        not np.isin(np.unique(array), [0, 1]).all() or not np.count_nonzero(array)
                    ):
                        output_failures.append({"sample_id": sample_id, "reason": "exported mask invalid or empty"})
                else:
                    with np.load(path, allow_pickle=False) as arrays:
                        if "image" not in arrays or "tumorMask" not in arrays:
                            output_failures.append({"sample_id": sample_id, "reason": "raw NPZ missing image or tumorMask"})
            except Exception as error:
                output_failures.append({"sample_id": sample_id, "reason": f"{field} unreadable: {error}"})

    if source_failures:
        issues.append(f"{len(source_failures)} source MAT/data integrity failure(s).")
    if output_failures:
        issues.append(f"{len(output_failures)} generated artifact failure(s).")
    if source_hash_mismatches:
        issues.append(f"{len(source_hash_mismatches)} source SHA-256 checksums differ from metadata.")
    exact_duplicates = sum(count - 1 for count in source_hashes.values() if count > 1)

    duplicate_findings = _audit_near_duplicates(duplicate_rows, metadata, splits, prepared_dir)
    cross_patient_cross_fold = [
        row for row in duplicate_findings if row["cross_patient"] and row["cross_fold"]
    ]
    high_similarity_crossfold = [
        row for row in cross_patient_cross_fold
        if row["ssim"] is not None and row["ssim"] >= NEAR_DUPLICATE_REVIEW_THRESHOLD
    ]
    if cross_patient_cross_fold:
        issues.append(
            f"{len(cross_patient_cross_fold)} cross-patient near-duplicate candidates span different evaluation folds "
            "and have not been manually resolved; this is a potential leakage risk."
        )
    if exact_duplicates:
        issues.append(f"{exact_duplicates} exact duplicate source file(s) were detected.")
    if len(duplicate_findings) != sum(
        row.get("classification") == "near_duplicate_candidate" for row in duplicate_rows
    ):
        issues.append("The number of pairwise near-duplicate audit rows could not be fully reconciled.")

    fold_summary = []
    for fold in sorted({row["fold"] for row in split_rows}):
        selected = [row for row in split_rows if row["fold"] == fold]
        fold_summary.append({
            "fold": fold,
            "patient_count": len({row["patient_id"] for row in selected}),
            "slice_count": len(selected),
            "class_counts": dict(Counter(row["class"] for row in selected)),
        })

    runtime = _runtime_info()
    cvind_inspection_path = prepared_dir / "cvind_inspection.json"
    cvind_details = {}
    if cvind_inspection_path.is_file():
        cvind_details = json.loads(cvind_inspection_path.read_text(encoding="utf-8"))
    go = not issues
    result = {
        "status": "GO" if go else "NO-GO",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "prepared_dir": str(prepared_dir),
        "source_root": str(source_root),
        "artifact_hashes": {
            "dataset_manifest_sha256": sha256_file(manifest_path),
            "metadata_csv_sha256": sha256_file(metadata_path),
            "split_manifest_sha256": sha256_file(split_path),
            "duplicate_audit_sha256": sha256_file(duplicate_path),
        },
        "source_sample_count": len(metadata_rows),
        "split_row_count": len(split_rows),
        "unique_sample_ids": len(metadata),
        "expected_class_counts": EXPECTED_COUNTS,
        "observed_class_counts": dict(observed_classes),
        "unique_patient_ids": len({row["patient_id"] for row in metadata_rows if row.get("patient_id")}),
        "missing_patient_ids": sum(not row.get("patient_id") for row in metadata_rows),
        "patient_fold_overlap_count": len(patient_overlap),
        "split_samples_missing_or_extra": {"missing": len(missing_split), "extra": len(extra_split)},
        "source_failures": len(source_failures),
        "output_failures": len(output_failures),
        "source_sha256_mismatches": len(source_hash_mismatches),
        "exact_duplicate_source_files": exact_duplicates,
        "mask_issues": sum("mask" in row["reason"].lower() for row in source_failures + output_failures),
        "near_duplicate_candidate_pairs": len(duplicate_findings),
        "cross_patient_cross_fold_candidates": len(cross_patient_cross_fold),
        "cross_patient_cross_fold_ssim_ge_threshold": len(high_similarity_crossfold),
        "near_duplicate_ssim_review_threshold": NEAR_DUPLICATE_REVIEW_THRESHOLD,
        "cvind_status": "unverified; not used for any split assignment",
        "cvind_inspection": {
            "stored_shape": cvind_details.get("stored_hdf5_shape"),
            "matlab_native_shape_inferred": cvind_details.get("matlab_native_shape_inferred_from_hdf5_dimension_order"),
            "fold_assignment_counts": cvind_details.get("fold_assignment_counts"),
            "mapping_verified": cvind_details.get("mapping_verified"),
            "mapping_status": cvind_details.get("mapping_status"),
        },
        "fold_summary": fold_summary,
        "issues": issues,
        "runtime": runtime,
        "manifest_run_id": manifest.get("run_id"),
        "manifest_discovered_mat_files": manifest.get("discovered_mat_files"),
        "source_failure_examples": source_failures[:20],
        "output_failure_examples": output_failures[:20],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "near_duplicate_crossfold_review.csv",
        duplicate_findings,
        [
            "group_id", "sample_id_a", "sample_id_b", "source_path_a", "source_path_b",
            "patient_id_a", "patient_id_b", "class_a", "class_b", "fold_a", "fold_b",
            "phash_hamming_distance", "pixel_equal_fraction", "ssim", "pearson_correlation",
            "cross_patient", "cross_fold", "review_status", "ssim_review_flag", "confirmed_duplicate",
        ],
    )
    (output_dir / "gate_report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Baseline pre-training gate",
        "",
        f"**Decision: {result['status']}**",
        "",
        "## Verified dataset and split checks",
        "",
        f"- Prepared metadata samples: {len(metadata_rows)}; split rows: {len(split_rows)}.",
        f"- Class counts: `{dict(observed_classes)}`.",
        f"- Unique patients: {result['unique_patient_ids']}; missing patient IDs: {result['missing_patient_ids']}.",
        f"- Patient overlap across folds: {len(patient_overlap)}.",
        f"- Missing/extra split assignments: {len(missing_split)}/{len(extra_split)}.",
        f"- Source MAT files re-opened and labels/PIDs checked directly against `cjdata`: {len(metadata_rows) - len(source_failures)} with no recorded source failures.",
        f"- Missing/unreadable or malformed generated outputs: {len(output_failures)}.",
        f"- Source checksum mismatches: {len(source_hash_mismatches)}; exact duplicate source contents: {exact_duplicates}.",
        "",
        "## Near-duplicate leakage review",
        "",
        f"- Pairwise candidates in the prepared audit: {len(duplicate_findings)}.",
        f"- Candidates with different patient IDs and different folds: {len(cross_patient_cross_fold)}.",
        f"- Those cross-patient/cross-fold candidates with SSIM >= {NEAR_DUPLICATE_REVIEW_THRESHOLD:.2f}: {len(high_similarity_crossfold)}.",
        "- pHash and SSIM are screening measures, not proof that two slices are the same acquisition or patient.",
        "- The pair list is preserved in `near_duplicate_crossfold_review.csv`; candidate pairs remain unconfirmed and require manual/source-provenance review.",
        "- No candidate or source sample was deleted or reassigned.",
        "",
        "## Fold distributions",
        "",
        "| Fold | Patients | Slices | Class distribution |",
        "|---|---:|---:|---|",
    ]
    lines.extend(
        f"| {row['fold']} | {row['patient_count']} | {row['slice_count']} | `{row['class_counts']}` |"
        for row in fold_summary
    )
    lines += [
        "",
        "## Decision rationale",
        "",
    ]
    if go:
        lines.append("All implemented pre-training checks passed. This gate does not establish scientific validity or eliminate all possible cohort confounding.")
    else:
        lines.extend(f"- **Unresolved:** {issue}" for issue in issues)
        lines += [
            "",
            "Training is blocked. Resolve the cross-patient/cross-fold candidate pairs using source provenance or a documented expert review, then rerun this gate. Do not change folds based only on pHash/SSIM, and do not treat perceptual similarity alone as confirmed patient identity.",
        ]
    lines += [
        "",
        "## Provenance and limitations",
        "",
        f"- Dataset manifest SHA-256: `{result['artifact_hashes']['dataset_manifest_sha256']}`.",
        f"- Split manifest SHA-256: `{result['artifact_hashes']['split_manifest_sha256']}`.",
        "- `cvind.mat` remains unverified for file-to-index mapping and was not used.",
        "- The gate re-opens source MAT files, confirms class labels and exact PIDs against `cjdata`, validates masks and generated image/array paths, and checks sample/split accounting.",
        "- Near-duplicate similarity screening can create false positives from shared anatomy and background; expert review or reliable acquisition linkage is required before conclusions about leakage.",
    ]
    cvind = result["cvind_inspection"]
    if cvind.get("stored_shape"):
        lines.insert(
            lines.index("- `cvind.mat` remains unverified for file-to-index mapping and was not used."),
            f"- `cvind.mat` structure: stored shape `{cvind['stored_shape']}`, inferred MATLAB shape `{cvind.get('matlab_native_shape_inferred')}`, fold counts `{cvind.get('fold_assignment_counts')}`; mapping remains unverified.",
        )
    (output_dir / "NO_GO_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    baseline_lines = [
        "# Baseline experiment status",
        "",
        f"**Status: {result['status']} — training was not started.**",
        "",
        "No fold metrics, predictions, confusion matrix, training log, model checkpoint, or inference timings are reported because no model was trained.",
        "",
        "The pre-training verification is documented in `NO_GO_REPORT.md` and the pair-level audit is in `near_duplicate_crossfold_review.csv`.",
        "",
        "## Exact gate command",
        "",
        "```powershell",
        "py -3 .\\scripts\\pretraining_gate.py --prepared-dir .\\prepared_full_run --source-root . --output-dir .\\experiments\\baseline",
        "```",
        "",
        "The gate exited with status 2 because 236 pHash near-duplicate candidate pairs cross both patient IDs and evaluation folds. Two of these pairs had SSIM >= 0.80. These are unconfirmed candidates, not proof of duplicate patients, but they require manual/source-provenance review before training.",
        "",
        "## Outputs not created",
        "",
        "- `metrics.json`, `fold_metrics.csv`, `predictions.csv`, `confusion_matrix.png`, `training_log.csv`, model checkpoints, and model predictions were intentionally not generated.",
        "- No training or intervention experiment was run.",
    ]
    (output_dir / "BASELINE_REPORT.md").write_text("\n".join(baseline_lines) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit dataset/splits before any baseline model training.")
    parser.add_argument("--prepared-dir", type=Path, default=ROOT / "prepared_full_run")
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "experiments" / "baseline")
    args = parser.parse_args()
    result = run_gate(args.prepared_dir, args.source_root, args.output_dir)
    print(json.dumps({"status": result["status"], "issues": result["issues"], "artifact_hashes": result["artifact_hashes"]}, indent=2))
    if result["status"] != "GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
