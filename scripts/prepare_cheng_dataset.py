from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from dataset_utils import (
    CLASS_NAMES,
    EXPECTED_CLASS_COUNTS,
    file_sha256,
    json_value,
    native_array,
    patient_id_text,
    read_cjdata,
    scalar_number,
    stable_sample_id,
)

ROOT = Path(__file__).resolve().parent.parent
PHASH_COS = np.cos((2 * np.arange(32)[:, None] + 1) * np.arange(8)[None, :] * math.pi / 64)

PROCESSING_SUCCESS = "success"
PROCESSING_FAILED = "failed"
QUALITY_PASS = "pass"
QUALITY_WARNING = "warning"
QUALITY_FAIL = "fail"
MASK_VALID = "valid"
MASK_MISSING = "missing"
MASK_EMPTY = "empty"
MASK_INVALID = "invalid"
MASK_NOT_CHECKED = "not_checked"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _image_u8(image: np.ndarray) -> np.ndarray:
    if image.ndim != 2 or image.size == 0 or not np.issubdtype(image.dtype, np.number):
        raise ValueError("MRI image must be a non-empty numeric 2-D array")
    if not np.isfinite(image).all():
        raise ValueError("MRI image contains non-finite values")
    values = image.astype(np.float64, copy=False)
    low, high = float(values.min()), float(values.max())
    if high == low:
        return np.zeros(values.shape, dtype=np.uint8)
    scaled = (values - low) * (255.0 / (high - low))
    return np.clip(np.rint(scaled), 0, 255).astype(np.uint8)


def _perceptual_hash(image_u8: np.ndarray) -> int:
    resized = np.asarray(Image.fromarray(image_u8).resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float64)
    dct = (PHASH_COS.T @ resized @ PHASH_COS)[1:9, 1:9]
    median = float(np.median(dct))
    result = 0
    for bit in (dct > median).ravel():
        result = (result << 1) | int(bit)
    return result


def _discover(input_root: Path, input_dirs: list[Path] | None) -> tuple[list[tuple[Path, Path]], list[dict[str, Any]]]:
    archives = input_dirs or sorted(
        p for p in input_root.iterdir() if p.is_dir() and p.name.startswith("brainTumorDataPublic_")
    )
    if not archives:
        raise FileNotFoundError(f"No extracted brainTumorDataPublic_* folders found under {input_root}")
    discovered: list[tuple[Path, Path]] = []
    archive_rows: list[dict[str, Any]] = []
    for archive in archives:
        archive = archive.resolve()
        if not archive.is_dir():
            raise FileNotFoundError(f"Input folder does not exist: {archive}")
        files = sorted(archive.rglob("*.mat"), key=lambda p: str(p.relative_to(archive)).casefold())
        discovered.extend((archive, file) for file in files)
        archive_rows.append({"archive": archive, "files": files})
    return discovered, archive_rows


def _write_atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp.{uuid.uuid4().hex}")
    try:
        tmp_path.write_bytes(payload)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _write_atomic_image(path: Path, array: np.ndarray, mode: str = "L") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp.{uuid.uuid4().hex}")
    try:
        Image.fromarray(array, mode=mode).save(tmp_path, format="PNG")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _write_atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = f"{path.name}.tmp.{uuid.uuid4().hex}.npz"
    tmp_path = path.with_name(tmp_name)
    try:
        np.savez_compressed(tmp_path, **arrays)
        if not tmp_path.exists():
            raise FileNotFoundError(f"Compressed NPZ was not created at {tmp_path}")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _write_atomic_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp.{uuid.uuid4().hex}")
    try:
        with tmp_path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames or (list(rows[0].keys()) if rows else []), extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _mask_status_for(mask: np.ndarray | None, image: np.ndarray | None) -> str:
    if mask is None:
        return MASK_MISSING
    if mask.size == 0:
        return MASK_EMPTY
    if mask.ndim != 2 or not np.issubdtype(mask.dtype, np.number):
        return MASK_INVALID
    if not np.isfinite(mask).all():
        return MASK_INVALID
    if np.count_nonzero(mask) == 0:
        return MASK_EMPTY
    if image is not None and image.ndim == 2 and image.shape != mask.shape:
        return MASK_INVALID
    unique_values = np.unique(mask)
    if not np.isin(unique_values, [0, 1]).all():
        return MASK_INVALID
    return MASK_VALID


def _append_issue(issue_list: list[dict[str, Any]], *, sample_id: str, source_path: str, issue_type: str, message: str, severity: str) -> None:
    issue_list.append({
        "sample_id": sample_id,
        "source_path": source_path,
        "severity": severity,
        "issue_type": issue_type,
        "message": message,
    })


def _validate_staging(staging_dir: Path) -> dict[str, Any]:
    required = [
        "inventory.csv",
        "metadata.csv",
        "class_summary.csv",
        "patient_summary.csv",
        "duplicate_audit.csv",
        "validation_errors.csv",
        "validation_issues.csv",
        "manifest.json",
    ]
    missing = [name for name in required if not (staging_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Staging directory {staging_dir} is incomplete. Missing: {', '.join(missing)}")
    manifest = json.loads((staging_dir / "manifest.json").read_text(encoding="utf-8"))
    metadata_rows = list(csv.DictReader((staging_dir / "metadata.csv").open(newline="", encoding="utf-8-sig")))
    if manifest.get("discovered_mat_files") is not None and len(metadata_rows) != manifest["discovered_mat_files"]:
        raise ValueError("metadata rows do not match the discovered MAT-file count")
    return manifest


def _finalize_staged_run(staging_dir: Path, final_dir: Path, replace_existing: bool = False, keep_backup: bool = True) -> dict[str, Any]:
    if not staging_dir.exists():
        raise FileNotFoundError(f"Staging directory not found: {staging_dir}")
    manifest = _validate_staging(staging_dir)
    if final_dir.exists() and not replace_existing:
        raise FileExistsError(
            f"Final output already exists at {final_dir}. Re-run with --replace-existing to explicitly replace it. "
            "The old directory is kept as a backup until the new run is verified."
        )

    backup_dir = None
    if final_dir.exists() and replace_existing:
        backup_dir = final_dir.parent / f"{final_dir.name}.backup.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
        if backup_dir.exists():
            raise FileExistsError(f"Backup path already exists: {backup_dir}. Remove it or choose a different output directory.")
        os.replace(final_dir, backup_dir)

    try:
        try:
            os.replace(staging_dir, final_dir)
        except OSError:
            if final_dir.exists():
                raise
            shutil.copytree(staging_dir, final_dir)
            shutil.rmtree(staging_dir)
        _validate_staging(final_dir)
        manifest["status"] = "finalized"
        manifest["final_output_dir"] = str(final_dir)
        manifest["finalized_at"] = _utc_now()
        (final_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"status": "finalized", "final_dir": str(final_dir), "backup_dir": str(backup_dir) if backup_dir and keep_backup else None, "manifest": manifest}
    except Exception:
        if final_dir.exists() and final_dir.is_dir():
            shutil.rmtree(final_dir, ignore_errors=True)
        if backup_dir is not None and keep_backup and not final_dir.exists():
            os.replace(backup_dir, final_dir)
        raise


def prepare(input_root: Path, output_dir: Path, input_dirs: list[Path] | None = None,
            limit: int | None = None, run_label: str = "full", replace_existing: bool = False,
            stage_only: bool = False) -> dict[str, Any]:
    input_root = input_root.resolve()
    output_dir = output_dir.resolve()

    if output_dir.exists() and not replace_existing and not stage_only:
        raise FileExistsError(
            f"Final output '{output_dir}' already exists. Use --replace-existing only when you are deliberately replacing a previous finalized dataset."
        )

    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    run_scope = "pilot" if limit is not None else "full"
    if run_label:
        run_scope = run_label

    discovery, archive_rows = _discover(input_root, input_dirs)
    work = discovery[:limit] if limit is not None else discovery

    staging_dir = output_dir.parent / f".{output_dir.name}.staging.{run_id}"
    if staging_dir.exists():
        raise FileExistsError(f"Staging directory already exists: {staging_dir}. Remove it or choose a different run label.")
    staging_dir.mkdir(parents=True, exist_ok=False)

    state = {
        "status": "in_progress",
        "run_id": run_id,
        "run_scope": run_scope,
        "label": run_label,
        "created_at": _utc_now(),
        "output_dir": str(output_dir),
        "input_root": str(input_root),
    }
    _write_atomic_bytes(staging_dir / "RUN_STATE.json", (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    rows: list[dict[str, Any]] = []
    validation_issues: list[dict[str, Any]] = []
    validation_errors: list[dict[str, Any]] = []

    for archive, path in work:
        relative = path.relative_to(input_root).as_posix() if path.is_relative_to(input_root) else (
            f"{archive.name}/{path.relative_to(archive).as_posix()}"
        )
        sample_id = stable_sample_id(relative)
        source_sha = file_sha256(path)
        record = {
            "sample_id": sample_id,
            "original_filename": path.name,
            "source_path": str(path.resolve()),
            "source_relative_path": relative,
            "source_archive": archive.name,
            "class_label": None,
            "class_name": None,
            "patient_id": None,
            "class_label_raw": None,
            "image_shape": "",
            "image_dtype": "",
            "image_array_sha256": "",
            "mask_available": False,
            "mask_shape": "",
            "mask_dtype": "",
            "mask_binary_valid": False,
            "mask_empty": False,
            "mask_status": MASK_NOT_CHECKED,
            "tumor_pixels": None,
            "tumor_area_fraction": None,
            "tumor_border_available": False,
            "tumor_border_shape": "",
            "image_output_path": "",
            "mask_output_path": "",
            "overlay_output_path": "",
            "raw_array_output_path": "",
            "sha256": source_sha,
            "mat_reader": "",
            "processing_status": PROCESSING_FAILED,
            "quality_status": QUALITY_FAIL,
            "duplicate_status": "not_flagged",
            "validation_warnings": "[]",
            "validation_errors": "[]",
            "error_reason": "",
        }

        try:
            fields, reader = read_cjdata(path)
            record["mat_reader"] = reader
            label_value = scalar_number(fields["label"], "label")
            record["class_label_raw"] = label_value
            record["class_label"] = int(label_value) if float(label_value).is_integer() else float(label_value)
            record["class_name"] = CLASS_NAMES.get(int(float(label_value))) if float(label_value).is_integer() else None

            patient_id = patient_id_text(fields["PID"])
            record["patient_id"] = patient_id
            image = native_array(fields["image"])
            if image is None:
                raise ValueError("Missing required cjdata.image")
            if image.ndim != 2 or image.size == 0 or not np.issubdtype(image.dtype, np.number):
                raise ValueError("MRI image was not a valid 2-D numeric array")
            if not np.isfinite(image).all():
                raise ValueError("MRI image contains non-finite values")

            record["image_shape"] = json_value(list(image.shape))
            record["image_dtype"] = str(image.dtype)
            image_digest = hashlib.sha256()
            image_digest.update(str(image.dtype).encode("utf-8"))
            image_digest.update(json_value(list(image.shape)).encode("utf-8"))
            image_digest.update(np.ascontiguousarray(image).tobytes())
            record["image_array_sha256"] = image_digest.hexdigest()

            sample_issues: list[dict[str, Any]] = []
            if record["class_name"] is None:
                _append_issue(sample_issues, sample_id=sample_id, source_path=record["source_path"], issue_type="invalid_label", message=f"Unsupported cjdata.label value: {label_value!r}", severity="error")
            if record["patient_id"] in (None, ""):
                _append_issue(sample_issues, sample_id=sample_id, source_path=record["source_path"], issue_type="missing_patient_id", message="Patient ID missing or empty; splitting and provenance remain conservative.", severity="warning")

            display = _image_u8(image)
            image_path = staging_dir / "images" / (record["class_name"] or "unknown") / f"{sample_id}.png"
            _write_atomic_image(image_path, display, mode="L")
            record["image_output_path"] = image_path.relative_to(staging_dir).as_posix()

            mask = native_array(fields["tumorMask"])
            border = native_array(fields["tumorBorder"])
            record["mask_available"] = mask is not None
            record["tumor_border_available"] = border is not None
            if border is not None:
                record["tumor_border_shape"] = json_value(list(border.shape))

            arrays: dict[str, np.ndarray] = {"image": image}
            if border is not None:
                arrays["tumorBorder"] = border

            mask_status = _mask_status_for(mask, image)
            record["mask_status"] = mask_status
            if mask is not None:
                arrays["tumorMask"] = mask
                record["mask_shape"] = json_value(list(mask.shape))
                record["mask_dtype"] = str(mask.dtype)
                record["mask_binary_valid"] = np.isin(np.unique(mask), [0, 1]).all() if mask.size else True
                record["mask_empty"] = bool(np.count_nonzero(mask) == 0)
                record["tumor_pixels"] = int(np.count_nonzero(mask))
                if mask.ndim == 2 and image.ndim == 2 and mask.shape == image.shape:
                    record["tumor_area_fraction"] = float(record["tumor_pixels"] / image.size)
                if mask_status in {MASK_MISSING, MASK_EMPTY, MASK_INVALID}:
                    _append_issue(sample_issues, sample_id=sample_id, source_path=record["source_path"], issue_type="mask_quality", message=f"mask_status={mask_status}", severity="warning")
                if mask_status == MASK_VALID and mask.ndim == 2 and mask.size and np.issubdtype(mask.dtype, np.number):
                    mask_path = staging_dir / "masks" / (record["class_name"] or "unknown") / f"{sample_id}.png"
                    _write_atomic_image(mask_path, mask.astype(np.uint8), mode="L")
                    record["mask_output_path"] = mask_path.relative_to(staging_dir).as_posix()
            else:
                record["mask_binary_valid"] = False
                record["mask_empty"] = True
                _append_issue(sample_issues, sample_id=sample_id, source_path=record["source_path"], issue_type="missing_mask", message="Tumour mask absent for this sample.", severity="warning")

            raw_path = staging_dir / "raw_arrays" / f"{sample_id}.npz"
            _write_atomic_npz(raw_path, arrays)
            record["raw_array_output_path"] = raw_path.relative_to(staging_dir).as_posix()

            if mask is not None and mask_status == MASK_VALID and mask.ndim == 2 and mask.shape == image.shape:
                rgb = Image.fromarray(display, mode="L").convert("RGB")
                overlay = np.asarray(rgb, dtype=np.uint8).copy()
                selected = mask.astype(bool)
                overlay[selected] = (
                    (overlay[selected].astype(np.uint16) * 45 // 100)
                    + np.array([255, 0, 0], dtype=np.uint16) * 55 // 100
                ).astype(np.uint8)
                overlay_path = staging_dir / "overlays" / (record["class_name"] or "unknown") / f"{sample_id}_overlay.png"
                _write_atomic_image(overlay_path, overlay, mode="RGB")
                record["overlay_output_path"] = overlay_path.relative_to(staging_dir).as_posix()

            record["processing_status"] = PROCESSING_SUCCESS
            record["error_reason"] = ""
            record["validation_errors"] = json_value([issue for issue in sample_issues if issue["severity"] == "error"])
            record["validation_warnings"] = json_value([issue for issue in sample_issues if issue["severity"] == "warning"])

            if any(issue["severity"] == "error" for issue in sample_issues):
                record["quality_status"] = QUALITY_FAIL
            elif any(issue["severity"] == "warning" for issue in sample_issues):
                record["quality_status"] = QUALITY_WARNING
            else:
                record["quality_status"] = QUALITY_PASS

            validation_errors.extend([issue for issue in sample_issues if issue["severity"] == "error"])
            validation_issues.extend(sample_issues)
            rows.append(record)

        except Exception as exc:
            record["processing_status"] = PROCESSING_FAILED
            record["quality_status"] = QUALITY_FAIL
            record["error_reason"] = f"{type(exc).__name__}: {exc}"
            record["validation_errors"] = json_value([{
                "sample_id": sample_id,
                "source_path": record["source_path"],
                "severity": "error",
                "issue_type": "processing_failure",
                "message": record["error_reason"],
            }])
            record["validation_warnings"] = json_value([])
            processing_issue = {
                "sample_id": sample_id,
                "source_path": record["source_path"],
                "severity": "error",
                "issue_type": "processing_failure",
                "message": record["error_reason"],
            }
            validation_errors.append(processing_issue)
            validation_issues.append(processing_issue)
            rows.append(record)

    inventory_rows: list[dict[str, Any]] = []
    for archive_row in archive_rows:
        archive = archive_row["archive"]
        files = archive_row["files"]
        inventory_rows.append({
            "folder": str(archive),
            "folder_name": archive.name,
            "mat_file_count": len(files),
            "duplicate_filenames_within_folder": sum(count - 1 for count in Counter(p.name.casefold() for p in files).values() if count > 1),
            "unreadable_or_failed_in_run": sum(1 for row in rows if row["source_archive"] == archive.name and row["processing_status"] == PROCESSING_FAILED),
            "processed_in_run": sum(1 for row in rows if row["source_archive"] == archive.name and row["processing_status"] == PROCESSING_SUCCESS),
            "run_was_limited": limit is not None,
            "run_label": run_label,
            "run_scope": run_scope,
        })

    _write_atomic_csv(staging_dir / "inventory.csv", inventory_rows)
    _write_atomic_csv(staging_dir / "validation_errors.csv", validation_errors, ["sample_id", "source_path", "severity", "issue_type", "message"])
    _write_atomic_csv(staging_dir / "validation_issues.csv", validation_issues, ["sample_id", "source_path", "severity", "issue_type", "message"])

    class_rows: list[dict[str, Any]] = []
    for label, class_name in CLASS_NAMES.items():
        class_rows.append({
            "class_label": label,
            "class_name": class_name,
            "expected_reference_count": EXPECTED_CLASS_COUNTS[label],
            "processed_count": sum(row["processing_status"] == PROCESSING_SUCCESS and row["class_name"] == class_name for row in rows),
            "mask_available_count": sum(row["processing_status"] == PROCESSING_SUCCESS and row["class_name"] == class_name and row["mask_available"] for row in rows),
            "mask_valid_count": sum(row["processing_status"] == PROCESSING_SUCCESS and row["class_name"] == class_name and row["mask_status"] == MASK_VALID for row in rows),
            "quality_pass_count": sum(row["processing_status"] == PROCESSING_SUCCESS and row["class_name"] == class_name and row["quality_status"] == QUALITY_PASS for row in rows),
            "quality_warning_count": sum(row["processing_status"] == PROCESSING_SUCCESS and row["class_name"] == class_name and row["quality_status"] == QUALITY_WARNING for row in rows),
        })
    _write_atomic_csv(staging_dir / "class_summary.csv", class_rows)

    patient_rows: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["processing_status"] == PROCESSING_SUCCESS:
            grouped[row["patient_id"] if row["patient_id"] is not None else ""].append(row)
    for patient_id, samples in sorted(grouped.items()):
        patient_rows.append({
            "patient_id": patient_id,
            "slices": len(samples),
            **{name: sum(sample["class_name"] == name for sample in samples) for name in CLASS_NAMES.values()},
            "patient_id_missing": not bool(patient_id),
        })
    _write_atomic_csv(staging_dir / "patient_summary.csv", patient_rows, ["patient_id", "slices", *CLASS_NAMES.values(), "patient_id_missing"])

    duplicate_rows: list[dict[str, Any]] = []
    file_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["sha256"]:
            file_groups[row["sha256"]].append(row)
    for digest, group in file_groups.items():
        if len(group) > 1:
            for row in group:
                row["duplicate_status"] = "exact_duplicate"
            duplicate_rows.append({
                "classification": "exact_duplicate",
                "hash": digest,
                "sample_ids": json_value([r["sample_id"] for r in group]),
                "source_paths": json_value([r["source_path"] for r in group]),
                "count": len(group),
                "details": "Cryptographic verification confirmed identical source-file content; retained for traceability.",
            })

    valid_images = [row for row in rows if row["processing_status"] == PROCESSING_SUCCESS and row["image_output_path"]]
    if valid_images:
        image_hashes = []
        for row in valid_images:
            image_path = staging_dir / row["image_output_path"]
            with Image.open(image_path) as image:
                image_hashes.append((row, _perceptual_hash(np.asarray(image.convert("L")))))
        hashes = np.asarray([value for _, value in image_hashes], dtype=np.uint64)
        for index in range(len(image_hashes)):
            if index + 1 >= len(image_hashes):
                continue
            distances = np.bitwise_xor(hashes[index], hashes[index + 1:]).astype(np.uint64)
            hamming = np.array([bin(int(value)).count("1") for value in distances], dtype=np.int32)
            for offset, score in enumerate(hamming):
                if score <= 4:
                    left_row = image_hashes[index][0]
                    right_row = image_hashes[index + 1 + offset][0]
                    if left_row["sample_id"] != right_row["sample_id"]:
                        left_row["duplicate_status"] = "near_duplicate_candidate"
                        right_row["duplicate_status"] = "near_duplicate_candidate"
                        duplicate_rows.append({
                            "classification": "near_duplicate_candidate",
                            "group_id": f"phash:{left_row['sample_id']}:{right_row['sample_id']}",
                            "similarity_method": "pHash",
                            "similarity_score": int(score),
                            "sample_ids": json_value([left_row["sample_id"], right_row["sample_id"]]),
                            "patient_ids": json_value([left_row["patient_id"], right_row["patient_id"]]),
                            "class_names": json_value([left_row["class_name"], right_row["class_name"]]),
                            "image_sizes": json_value([left_row["image_shape"], right_row["image_shape"]]),
                            "source_paths": json_value([left_row["source_path"], right_row["source_path"]]),
                            "count": 2,
                            "details": "Candidate near duplicate based on exported-image pHash distance; retained for review and not deleted.",
                        })

    _write_atomic_csv(staging_dir / "metadata.csv", rows, [
        "sample_id", "original_filename", "source_path", "source_relative_path", "source_archive",
        "class_label", "class_name", "patient_id", "class_label_raw", "image_shape", "image_dtype",
        "image_array_sha256", "mask_available", "mask_shape", "mask_dtype", "mask_binary_valid",
        "mask_empty", "mask_status", "tumor_pixels", "tumor_area_fraction", "tumor_border_available",
        "tumor_border_shape", "image_output_path", "mask_output_path", "overlay_output_path",
        "raw_array_output_path", "sha256", "mat_reader", "processing_status", "quality_status",
        "duplicate_status", "validation_warnings", "validation_errors", "error_reason"
    ])
    _write_atomic_csv(staging_dir / "duplicate_audit.csv", duplicate_rows, [
        "classification", "group_id", "hash", "similarity_method", "similarity_score",
        "sample_ids", "patient_ids", "class_names", "image_sizes", "source_paths", "count", "details"
    ])

    try:
        import importlib.metadata as metadata
        package_versions = {name: metadata.version(name) for name in ["numpy", "scipy", "h5py", "Pillow", "scikit-learn", "pandas"] if metadata.version(name)}
    except Exception:
        package_versions = {}

    try:
        import subprocess
        git_commit = subprocess.check_output(["git", "-C", str(input_root), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        git_commit = "unknown"

    manifest = {
        "run_id": run_id,
        "run_scope": run_scope,
        "run_label": run_label,
        "created_at": _utc_now(),
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "staging_dir": str(staging_dir),
        "replace_existing": replace_existing,
        "archive_folders": [str(row["archive"]) for row in archive_rows],
        "discovered_mat_files": len(work),
        "source_file_sha256": {str(path): file_sha256(path) for _, path in work},
        "script_version": git_commit,
        "python_version": sys.version.replace("\n", " "),
        "dependency_versions": package_versions,
        "counts": {
            "processed": sum(row["processing_status"] == PROCESSING_SUCCESS for row in rows),
            "failed": sum(row["processing_status"] == PROCESSING_FAILED for row in rows),
            "quality_pass": sum(row["quality_status"] == QUALITY_PASS for row in rows),
            "quality_warning": sum(row["quality_status"] == QUALITY_WARNING for row in rows),
            "quality_fail": sum(row["quality_status"] == QUALITY_FAIL for row in rows),
            "missing_patient_id": sum(row["processing_status"] == PROCESSING_SUCCESS and row["patient_id"] in (None, "") for row in rows),
            "missing_mask": sum(row["processing_status"] == PROCESSING_SUCCESS and row["mask_status"] == MASK_MISSING for row in rows),
            "invalid_mask": sum(row["processing_status"] == PROCESSING_SUCCESS and row["mask_status"] in {MASK_EMPTY, MASK_INVALID} for row in rows),
            "exact_duplicate": sum(1 for row in rows if row["duplicate_status"] == "exact_duplicate"),
            "near_duplicate_candidate": sum(1 for row in rows if row["duplicate_status"] == "near_duplicate_candidate"),
        },
        "samples": [{
            "sample_id": row["sample_id"],
            "source_path": row["source_path"],
            "source_sha256": row["sha256"],
            "class_name": row["class_name"],
            "patient_id": row["patient_id"],
            "image_output": row["image_output_path"],
            "mask_output": row["mask_output_path"],
            "overlay_output": row["overlay_output_path"],
            "raw_array_output": row["raw_array_output_path"],
            "processing_status": row["processing_status"],
            "quality_status": row["quality_status"],
            "mask_status": row["mask_status"],
            "validation_errors": json.loads(row["validation_errors"]) if row["validation_errors"] else [],
            "validation_warnings": json.loads(row["validation_warnings"]) if row["validation_warnings"] else [],
        } for row in rows],
    }
    _write_atomic_bytes(staging_dir / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    state["status"] = "staged"
    _write_atomic_bytes(staging_dir / "RUN_STATE.json", (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    if not stage_only:
        _finalize_staged_run(staging_dir, output_dir, replace_existing=replace_existing)
        manifest["status"] = "finalized"
        _write_atomic_bytes(output_dir / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return {
            "run_id": run_id,
            "run_scope": run_scope,
            "output_dir": str(output_dir),
            "staging_dir": str(staging_dir),
            "status": "finalized",
            "counts": manifest["counts"],
            "manifest": manifest,
        }

    return {
        "run_id": run_id,
        "run_scope": run_scope,
        "output_dir": str(output_dir),
        "staging_dir": str(staging_dir),
        "status": "staged",
        "counts": manifest["counts"],
        "manifest": manifest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the Cheng Brain Tumor Dataset in a staged, recoverable workflow.")
    parser.add_argument("--input-root", type=Path, default=ROOT)
    parser.add_argument("--input-dir", type=Path, action="append", help="Archive folder to scan; may repeat.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "prepared")
    parser.add_argument("--limit", type=int, help="Process only the first N discovered files (pilot mode).")
    parser.add_argument("--run-label", type=str, default="full", help="Run label for dataset scope; e.g. pilot/full")
    parser.add_argument("--replace-existing", action="store_true", help="Explicitly replace an existing finalized output directory. This is not the default.")
    parser.add_argument("--stage-only", action="store_true", help="Stop after staging and validation without final promotion.")
    args = parser.parse_args()

    result = prepare(
        args.input_root.resolve(),
        args.output_dir.resolve(),
        [p.resolve() for p in args.input_dir] if args.input_dir else None,
        limit=args.limit,
        run_label=args.run_label,
        replace_existing=args.replace_existing,
        stage_only=args.stage_only,
    )
    print(json.dumps({"status": result["status"], "run_id": result["run_id"], "output_dir": result["output_dir"], "staging_dir": result["staging_dir"], "counts": result["counts"]}, indent=2))


if __name__ == "__main__":
    main()
