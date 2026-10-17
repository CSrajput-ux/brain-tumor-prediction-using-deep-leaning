from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import statistics
import sys
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from dataset_utils import CLASS_NAMES, native_array, patient_id_text, read_cjdata, scalar_number

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REVIEW_CSV = ROOT / "experiments" / "baseline" / "near_duplicate_crossfold_review.csv"
DEFAULT_SPLIT_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
DEFAULT_METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
DEFAULT_PREPARED_DIR = ROOT / "prepared_full_run"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "duplicate_investigation"
SSIM_HIGH_THRESHOLD = 0.80
SSIM_MEDIUM_THRESHOLD = 0.70
CONTACTS_PER_PAGE = 4
CONTACT_IMAGE_SIZE = (180, 140)
CONTACT_TEXT_WIDTH = 42


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_pair_id(pair: dict[str, str]) -> str:
    existing_id = (pair.get("group_id") or "").strip()
    if existing_id:
        return existing_id
    first, second = sorted((pair["sample_id_a"], pair["sample_id_b"]))
    return "pair:" + hashlib.sha256(f"{first}\0{second}".encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _as_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().casefold() in {"true", "1", "yes"}


def _format_metric(value: Any) -> str:
    return f"{value:.6f}" if isinstance(value, (int, float)) else "not available"


def select_cross_patient_cross_fold_pairs(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if _as_bool(row.get("cross_patient"))
        and _as_bool(row.get("cross_fold"))
        and row.get("fold_a") != row.get("fold_b")
        and row.get("patient_id_a") != row.get("patient_id_b")
    ]


def _hash_array(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(contiguous.dtype).encode("ascii"))
    digest.update(json.dumps(list(contiguous.shape), ensure_ascii=False, sort_keys=True).encode("utf-8"))
    digest.update(contiguous.tobytes())
    return digest.hexdigest()


def _array_similarity(first: np.ndarray, second: np.ndarray) -> dict[str, Any]:
    result: dict[str, Any] = {
        "shape_a": list(first.shape),
        "shape_b": list(second.shape),
        "dtype_a": str(first.dtype),
        "dtype_b": str(second.dtype),
        "intensity_min_a": float(np.min(first)) if first.size else None,
        "intensity_max_a": float(np.max(first)) if first.size else None,
        "intensity_min_b": float(np.min(second)) if second.size else None,
        "intensity_max_b": float(np.max(second)) if second.size else None,
        "array_hash_a": _hash_array(first),
        "array_hash_b": _hash_array(second),
        "identical_image_arrays": bool(first.shape == second.shape and first.dtype == second.dtype and np.array_equal(first, second)),
        "same_shape": bool(first.shape == second.shape),
        "pixel_equal_fraction": None,
        "mean_absolute_difference": None,
        "max_absolute_difference": None,
        "pearson_correlation": None,
    }
    if first.shape != second.shape or first.size == 0:
        return result
    first_numeric = first.astype(np.float64, copy=False)
    second_numeric = second.astype(np.float64, copy=False)
    absolute_difference = np.abs(first_numeric - second_numeric)
    result["pixel_equal_fraction"] = float(np.mean(first == second))
    result["mean_absolute_difference"] = float(np.mean(absolute_difference))
    result["max_absolute_difference"] = float(np.max(absolute_difference))
    if np.std(first_numeric) > 0 and np.std(second_numeric) > 0:
        result["pearson_correlation"] = float(np.corrcoef(first_numeric.ravel(), second_numeric.ravel())[0, 1])
    return result


def _verify_image(path: Path) -> tuple[np.ndarray, list[int]]:
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    with Image.open(path) as opened:
        opened.verify()
    with Image.open(path) as opened:
        array = np.asarray(opened.convert("L"), dtype=np.uint8)
    return array, [int(array.shape[0]), int(array.shape[1])]


def _fit_contain(array: np.ndarray, size: tuple[int, int]) -> Image.Image:
    image = Image.fromarray(array).convert("L")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (24, 24, 24))
    left = (size[0] - image.width) // 2
    top = (size[1] - image.height) // 2
    canvas.paste(image.convert("RGB"), (left, top))
    return canvas


def _contact_page(rows: list[dict[str, Any]], output_path: Path, page_title: str) -> None:
    row_height = 240
    margin = 18
    title_height = 52
    panel_gap = 12
    panel_x = [margin + index * (CONTACT_IMAGE_SIZE[0] + panel_gap) for index in range(4)]
    details_x = panel_x[-1] + CONTACT_IMAGE_SIZE[0] + 22
    width = details_x + 290 + margin
    height = title_height + margin + row_height * len(rows) + margin
    sheet = Image.new("RGB", (width, height), (248, 248, 248))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((margin, 16), page_title, fill=(0, 0, 0), font=font)
    for index, row in enumerate(rows):
        top = title_height + margin + index * row_height
        first = np.asarray(Image.open(row["image_path_a"]).convert("L"), dtype=np.uint8)
        second = np.asarray(Image.open(row["image_path_b"]).convert("L"), dtype=np.uint8)
        first_view = _fit_contain(first, CONTACT_IMAGE_SIZE)
        second_view = _fit_contain(second, CONTACT_IMAGE_SIZE)
        if first.shape == second.shape:
            overlay = np.rint(0.5 * first.astype(np.float32) + 0.5 * second.astype(np.float32)).astype(np.uint8)
            difference = np.abs(first.astype(np.int16) - second.astype(np.int16)).astype(np.uint8)
            maximum = int(difference.max())
            diagnostic_difference = (difference.astype(np.float32) * (255.0 / maximum)).clip(0, 255).astype(np.uint8) if maximum else difference
        else:
            overlay = difference = np.zeros((1, 1), dtype=np.uint8)
            diagnostic_difference = difference
        overlay_view = _fit_contain(overlay, CONTACT_IMAGE_SIZE)
        difference_view = _fit_contain(diagnostic_difference, CONTACT_IMAGE_SIZE)
        labels = ["A", "B", "50/50 blend*", "scaled |A-B|*"]
        for x, view, label in zip(
            panel_x,
            [first_view, second_view, overlay_view, difference_view],
            labels,
        ):
            draw.text((x, top), label, fill=(0, 0, 0), font=font)
            sheet.paste(view, (x, top + 18))
        text_x = details_x
        text_top = top + 4
        pair_lines = [
            f"Pair: {row['pair_id']}",
            f"SSIM={row.get('ssim', '')}  pHash={row.get('phash_hamming_distance', '')}",
            f"A: {row['sample_id_a']} | PID {row['patient_id_a']} | {row['class_a']} | {row['fold_a']}",
            f"B: {row['sample_id_b']} | PID {row['patient_id_b']} | {row['class_b']} | {row['fold_b']}",
            f"Shapes: {row['original_shape_a']} vs {row['original_shape_b']}",
            f"Exact source array equality: {row['stored_image_array_equal']}",
            "* Diagnostic only; no human review.",
        ]
        for line in pair_lines:
            wrapped = textwrap.wrap(line, width=CONTACT_TEXT_WIDTH) or [""]
            for segment in wrapped:
                draw.text((text_x, text_top), segment, fill=(0, 0, 0), font=font)
                text_top += 14
        draw.line((margin, top + row_height - 4, width - margin, top + row_height - 4), fill=(180, 180, 180), width=1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=False)


def _write_contact_sheets(rows: list[dict[str, Any]], output_dir: Path) -> dict[str, int]:
    contact_dir = output_dir / "contact_sheets"
    contact_dir.mkdir(parents=True, exist_ok=True)
    groups = {
        "ssim_ge_0_80": [row for row in rows if row["ssim_value"] >= SSIM_HIGH_THRESHOLD],
        "ssim_0_70_to_0_80": [row for row in rows if SSIM_MEDIUM_THRESHOLD <= row["ssim_value"] < SSIM_HIGH_THRESHOLD],
        "ssim_lt_0_70": [row for row in rows if row["ssim_value"] < SSIM_MEDIUM_THRESHOLD],
    }
    counts: dict[str, int] = {}
    for severity, members in groups.items():
        counts[severity] = len(members)
        for page_index in range(0, len(members), CONTACTS_PER_PAGE):
            page_rows = members[page_index:page_index + CONTACTS_PER_PAGE]
            page_number = page_index // CONTACTS_PER_PAGE + 1
            filename = f"{severity}_page_{page_number:03d}.png"
            _contact_page(
                page_rows,
                contact_dir / filename,
                f"{severity}: pairs {page_index + 1}-{page_index + len(page_rows)} of {len(members)}",
            )
    # Deterministically select low-similarity examples as negative controls.
    controls = sorted(rows, key=lambda row: (row["ssim_value"], row["pair_id"]))[:min(12, len(rows))]
    counts["low_similarity_controls"] = len(controls)
    for page_index in range(0, len(controls), CONTACTS_PER_PAGE):
        page_rows = controls[page_index:page_index + CONTACTS_PER_PAGE]
        page_number = page_index // CONTACTS_PER_PAGE + 1
        _contact_page(
            page_rows,
            contact_dir / f"low_similarity_controls_page_{page_number:03d}.png",
            f"Low-similarity control examples: {page_index + 1}-{page_index + len(page_rows)} of {len(controls)}",
        )
    index_rows = []
    for group_name, members in groups.items():
        for pair_index, row in enumerate(members):
            index_rows.append({
                "pair_id": row["pair_id"],
                "contact_group": group_name,
                "page": f"{group_name}_page_{pair_index // CONTACTS_PER_PAGE + 1:03d}.png",
                "sample_id_a": row["sample_id_a"],
                "sample_id_b": row["sample_id_b"],
                "patient_id_a": row["patient_id_a"],
                "patient_id_b": row["patient_id_b"],
                "class_a": row["class_a"],
                "class_b": row["class_b"],
                "fold_a": row["fold_a"],
                "fold_b": row["fold_b"],
                "ssim": row["ssim"],
                "phash_hamming_distance": row["phash_hamming_distance"],
            })
    for pair_index, row in enumerate(controls):
        index_rows.append({
            "pair_id": row["pair_id"],
            "contact_group": "low_similarity_controls",
            "page": f"low_similarity_controls_page_{pair_index // CONTACTS_PER_PAGE + 1:03d}.png",
            "sample_id_a": row["sample_id_a"],
            "sample_id_b": row["sample_id_b"],
            "patient_id_a": row["patient_id_a"],
            "patient_id_b": row["patient_id_b"],
            "class_a": row["class_a"],
            "class_b": row["class_b"],
            "fold_a": row["fold_a"],
            "fold_b": row["fold_b"],
            "ssim": row["ssim"],
            "phash_hamming_distance": row["phash_hamming_distance"],
        })
    with (contact_dir / "contact_sheet_index.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        columns = [
            "pair_id", "contact_group", "page", "sample_id_a", "sample_id_b",
            "patient_id_a", "patient_id_b", "class_a", "class_b", "fold_a", "fold_b",
            "ssim", "phash_hamming_distance",
        ]
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(index_rows)
    return counts


def investigate(review_csv: Path, split_csv: Path, metadata_csv: Path, prepared_dir: Path, output_dir: Path) -> dict[str, Any]:
    review_csv, split_csv, metadata_csv = review_csv.resolve(), split_csv.resolve(), metadata_csv.resolve()
    prepared_dir, output_dir = prepared_dir.resolve(), output_dir.resolve()
    if output_dir.resolve() in (review_csv.parent.resolve(), split_csv.parent.resolve(), prepared_dir.resolve()):
        raise ValueError("Investigation outputs must be written to a separate directory.")
    for path in (review_csv, split_csv, metadata_csv):
        if not path.is_file():
            raise FileNotFoundError(f"Required input does not exist: {path}")

    input_hashes_before = {
        "review_csv_sha256": sha256_file(review_csv),
        "split_manifest_sha256": sha256_file(split_csv),
        "metadata_csv_sha256": sha256_file(metadata_csv),
    }
    review_rows = read_csv(review_csv)
    crossfold_rows = select_cross_patient_cross_fold_pairs(review_rows)
    if len(crossfold_rows) != 236:
        raise ValueError(f"Expected 236 cross-patient cross-fold candidates, found {len(crossfold_rows)}")
    metadata_rows = read_csv(metadata_csv)
    metadata = {row["sample_id"]: row for row in metadata_rows}
    split_rows = read_csv(split_csv)
    split_map: dict[str, list[dict[str, str]]] = {}
    for row in split_rows:
        split_map.setdefault(row["sample_id"], []).append(row)

    evidence_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    source_cache: dict[str, dict[str, Any]] = {}
    export_cache: dict[str, tuple[np.ndarray, list[int]]] = {}
    for source_row in crossfold_rows:
        pair_id = stable_pair_id(source_row)
        sample_a, sample_b = source_row["sample_id_a"], source_row["sample_id_b"]
        row_a, row_b = metadata.get(sample_a), metadata.get(sample_b)
        if row_a is None or row_b is None:
            errors.append({"pair_id": pair_id, "error": "sample absent from metadata"})
            continue
        split_a, split_b = split_map.get(sample_a, []), split_map.get(sample_b, [])
        source_paths = [Path(row_a["source_path"]), Path(row_b["source_path"])]
        try:
            for sample_id, record, source_path in zip((sample_a, sample_b), (row_a, row_b), source_paths):
                if not source_path.is_file():
                    raise FileNotFoundError(f"Source MAT file not found: {source_path}")
                if sample_id not in source_cache:
                    fields, _reader = read_cjdata(source_path)
                    image_array = native_array(fields["image"])
                    if image_array is None:
                        raise ValueError(f"cjdata.image is absent in {source_path}")
                    label_value = scalar_number(fields["label"], "label")
                    source_cache[sample_id] = {
                        "image": image_array,
                        "sha256": sha256_file(source_path),
                        "patient_id": patient_id_text(fields["PID"]),
                        "class_name": CLASS_NAMES.get(int(label_value)) if label_value.is_integer() else None,
                    }
                if sample_id not in export_cache:
                    export_cache[sample_id] = _verify_image(prepared_dir / record["image_output_path"])
            source_a, source_b = source_cache[sample_a], source_cache[sample_b]
            image_a, image_b = source_a["image"], source_b["image"]
            source_hash_a, source_hash_b = source_a["sha256"], source_b["sha256"]
            source_metadata_mismatches = []
            for sample_id, source_evidence, record in (
                (sample_a, source_a, row_a),
                (sample_b, source_b, row_b),
            ):
                if source_evidence["patient_id"] != record.get("patient_id"):
                    source_metadata_mismatches.append(f"{sample_id}:PID")
                if source_evidence["class_name"] != record.get("class_name"):
                    source_metadata_mismatches.append(f"{sample_id}:label")
            candidate_metadata_mismatches = []
            expected_candidate_values = (
                ("source_path_a", str(Path(row_a["source_path"]).resolve())),
                ("source_path_b", str(Path(row_b["source_path"]).resolve())),
                ("patient_id_a", row_a.get("patient_id", "")),
                ("patient_id_b", row_b.get("patient_id", "")),
                ("class_a", row_a.get("class_name", "")),
                ("class_b", row_b.get("class_name", "")),
            )
            for key, expected in expected_candidate_values:
                supplied = source_row.get(key, "")
                if key.startswith("source_path"):
                    matches = bool(supplied) and str(Path(supplied).resolve()) == expected
                else:
                    matches = supplied == expected
                if not matches:
                    candidate_metadata_mismatches.append(key)
            if len(split_a) != 1 or split_a[0].get("fold") != source_row.get("fold_a"):
                candidate_metadata_mismatches.append("fold_a")
            if len(split_b) != 1 or split_b[0].get("fold") != source_row.get("fold_b"):
                candidate_metadata_mismatches.append("fold_b")
            metadata_hash_mismatches = []
            if source_hash_a != row_a.get("sha256"):
                metadata_hash_mismatches.append(sample_a)
            if source_hash_b != row_b.get("sha256"):
                metadata_hash_mismatches.append(sample_b)
            similarity = _array_similarity(image_a, image_b)
            array_hash_mismatches = []
            if row_a.get("image_array_sha256") and similarity["array_hash_a"] != row_a["image_array_sha256"]:
                array_hash_mismatches.append(sample_a)
            if row_b.get("image_array_sha256") and similarity["array_hash_b"] != row_b["image_array_sha256"]:
                array_hash_mismatches.append(sample_b)
            export_a, export_shape_a = export_cache[sample_a]
            export_b, export_shape_b = export_cache[sample_b]
            identical_source = source_hash_a == source_hash_b
            identical_array = similarity["identical_image_arrays"]
            if identical_source or identical_array:
                category = "exact_duplicate_confirmed"
                automated_finding = "Exact equality verified by source-file SHA-256 or dtype/shape/pixel array equality."
            else:
                category = "unresolved"
                automated_finding = "Perceptual candidate only; no exact source-file or stored image-array equality."
            review_status = "automated_evidence_only_no_human_review"
            evidence_rows.append({
                "pair_id": pair_id,
                "source_candidate_group_id": source_row.get("group_id", ""),
                "sample_id_a": sample_a,
                "sample_id_b": sample_b,
                "source_path_a": str(source_paths[0]),
                "source_path_b": str(source_paths[1]),
                "patient_id_a": row_a["patient_id"],
                "patient_id_b": row_b["patient_id"],
                "class_a": row_a["class_name"],
                "class_b": row_b["class_name"],
                "fold_a": split_a[0]["fold"] if len(split_a) == 1 else "",
                "fold_b": split_b[0]["fold"] if len(split_b) == 1 else "",
                "phash_hamming_distance": source_row.get("phash_hamming_distance", ""),
                "export_ssim": source_row.get("ssim", ""),
                "ssim": source_row.get("ssim", ""),
                "ssim_preprocessing": "Existing gate value: prepared per-image min-max uint8 grayscale PNG; no geometric registration; scipy.ndimage.gaussian_filter sigma=1.5 pixels, truncate=4.0 (13x13 discrete support), mode=reflect; C1=(0.01*255)^2, C2=(0.03*255)^2; global mean SSIM.",
                "export_pixel_equal_fraction": source_row.get("pixel_equal_fraction", ""),
                "export_pearson_correlation": source_row.get("pearson_correlation", ""),
                "original_shape_a": json.dumps(similarity["shape_a"]),
                "original_shape_b": json.dumps(similarity["shape_b"]),
                "original_dtype_a": similarity["dtype_a"],
                "original_dtype_b": similarity["dtype_b"],
                "original_intensity_min_a": similarity["intensity_min_a"],
                "original_intensity_max_a": similarity["intensity_max_a"],
                "original_intensity_min_b": similarity["intensity_min_b"],
                "original_intensity_max_b": similarity["intensity_max_b"],
                "exported_shape_a": json.dumps(export_shape_a),
                "exported_shape_b": json.dumps(export_shape_b),
                "source_sha256_a": source_hash_a,
                "source_sha256_b": source_hash_b,
                "source_patient_id_a": source_a["patient_id"],
                "source_patient_id_b": source_b["patient_id"],
                "source_class_a": source_a["class_name"],
                "source_class_b": source_b["class_name"],
                "source_identity_matches_metadata": not source_metadata_mismatches,
                "source_candidate_matches_metadata": not candidate_metadata_mismatches,
                "source_file_sha256_equal": identical_source,
                "source_sha256_matches_metadata_a": sample_a not in metadata_hash_mismatches,
                "source_sha256_matches_metadata_b": sample_b not in metadata_hash_mismatches,
                "stored_image_array_sha256_a": similarity["array_hash_a"],
                "stored_image_array_sha256_b": similarity["array_hash_b"],
                "stored_image_array_equal": identical_array,
                "stored_array_sha256_matches_metadata_a": sample_a not in array_hash_mismatches,
                "stored_array_sha256_matches_metadata_b": sample_b not in array_hash_mismatches,
                "stored_array_shape_equal": similarity["same_shape"],
                "stored_pixel_equal_fraction": similarity["pixel_equal_fraction"],
                "stored_mean_absolute_difference": similarity["mean_absolute_difference"],
                "stored_max_absolute_difference": similarity["max_absolute_difference"],
                "stored_pearson_correlation": similarity["pearson_correlation"],
                "automated_category": category,
                "automated_finding": automated_finding,
                "human_review_status": review_status,
                "human_review_conclusion": "",
                "recommended_action": (
                    "investigate source provenance further; keep pre-training gate closed pending resolution"
                    if category == "exact_duplicate_confirmed"
                    else "request expert review; retain provisionally and document; keep pre-training gate closed pending resolution"
                ),
                "image_path_a": str(prepared_dir / row_a["image_output_path"]),
                "image_path_b": str(prepared_dir / row_b["image_output_path"]),
                "array_metadata_mismatch": json.dumps(metadata_hash_mismatches + array_hash_mismatches),
                "source_metadata_mismatch": json.dumps(source_metadata_mismatches),
                "candidate_metadata_mismatch": json.dumps(candidate_metadata_mismatches),
                "ssim_value": float(source_row.get("ssim") or 0.0),
            })
            if metadata_hash_mismatches:
                errors.append({
                    "pair_id": pair_id,
                    "error": f"Source SHA-256 differs from metadata for sample(s): {metadata_hash_mismatches}",
                })
            if array_hash_mismatches:
                errors.append({
                    "pair_id": pair_id,
                    "error": f"Image-array hash differs from metadata for sample(s): {array_hash_mismatches}",
                })
            if source_metadata_mismatches:
                errors.append({
                    "pair_id": pair_id,
                    "error": f"Source PID or label differs from metadata for sample(s): {source_metadata_mismatches}",
                })
            if candidate_metadata_mismatches:
                errors.append({
                    "pair_id": pair_id,
                    "error": f"Original review-row paths/patient/class/folds differ from current metadata: {candidate_metadata_mismatches}",
                })
        except Exception as error:
            errors.append({"pair_id": pair_id, "error": f"{type(error).__name__}: {error}"})
            evidence_rows.append({
                "pair_id": pair_id,
                "source_candidate_group_id": source_row.get("group_id", ""),
                "sample_id_a": sample_a,
                "sample_id_b": sample_b,
                "source_path_a": str(source_paths[0]),
                "source_path_b": str(source_paths[1]),
                "patient_id_a": row_a.get("patient_id", ""),
                "patient_id_b": row_b.get("patient_id", ""),
                "class_a": row_a.get("class_name", ""),
                "class_b": row_b.get("class_name", ""),
                "fold_a": split_a[0]["fold"] if len(split_a) == 1 else "",
                "fold_b": split_b[0]["fold"] if len(split_b) == 1 else "",
                "phash_hamming_distance": source_row.get("phash_hamming_distance", ""),
                "export_ssim": source_row.get("ssim", ""),
                "automated_category": "unresolved",
                "automated_finding": f"Evidence extraction failed: {type(error).__name__}: {error}",
                "human_review_status": "automated_evidence_only_no_human_review",
                "human_review_conclusion": "",
                "recommended_action": "investigate source provenance further; keep pre-training gate closed pending resolution",
                "evidence_error": f"{type(error).__name__}: {error}",
                "source_identity_matches_metadata": False,
                "source_candidate_matches_metadata": False,
            })

    evidence_counts = Counter(row.get("automated_category", "unresolved") for row in evidence_rows)
    ssim_values = [float(row["export_ssim"]) for row in evidence_rows if row.get("export_ssim") not in (None, "")]
    source_correlations = [
        float(row["stored_pearson_correlation"]) for row in evidence_rows
        if row.get("stored_pearson_correlation") not in (None, "")
    ]
    source_pixel_equal_fractions = [
        float(row["stored_pixel_equal_fraction"]) for row in evidence_rows
        if row.get("stored_pixel_equal_fraction") not in (None, "")
    ]
    phash_values = [
        int(row["phash_hamming_distance"]) for row in evidence_rows
        if str(row.get("phash_hamming_distance", "")).isdigit()
    ]
    crossfold_ssim_high = sum(
        float(row.get("export_ssim") or 0.0) >= SSIM_HIGH_THRESHOLD for row in evidence_rows
    )
    pair_ids = [row["pair_id"] for row in evidence_rows]
    if len(pair_ids) != len(set(pair_ids)):
        errors.append({"pair_id": "", "error": "stable pair IDs are not unique"})

    contact_counts = _write_contact_sheets(
        [row for row in evidence_rows if row.get("image_path_a") and row.get("image_path_b") and row.get("ssim_value") is not None],
        output_dir,
    )
    review_fieldnames = [
        "pair_id", "source_candidate_group_id", "sample_id_a", "sample_id_b", "source_path_a", "source_path_b",
        "patient_id_a", "patient_id_b", "class_a", "class_b", "fold_a", "fold_b", "phash_hamming_distance",
        "export_ssim", "ssim_preprocessing", "export_pixel_equal_fraction", "export_pearson_correlation",
        "original_shape_a", "original_shape_b", "original_dtype_a", "original_dtype_b",
        "original_intensity_min_a", "original_intensity_max_a", "original_intensity_min_b", "original_intensity_max_b",
        "exported_shape_a", "exported_shape_b", "source_sha256_a", "source_sha256_b", "source_file_sha256_equal",
        "source_patient_id_a", "source_patient_id_b", "source_class_a", "source_class_b",
        "source_identity_matches_metadata", "source_candidate_matches_metadata",
        "stored_image_array_sha256_a", "stored_image_array_sha256_b", "stored_image_array_equal",
        "source_sha256_matches_metadata_a", "source_sha256_matches_metadata_b",
        "stored_array_sha256_matches_metadata_a", "stored_array_sha256_matches_metadata_b",
        "stored_array_shape_equal", "stored_pixel_equal_fraction", "stored_mean_absolute_difference",
        "stored_max_absolute_difference", "stored_pearson_correlation",                 "automated_category", "automated_finding", "array_metadata_mismatch", "source_metadata_mismatch",
        "candidate_metadata_mismatch",
        "human_review_status", "human_review_conclusion", "recommended_action", "evidence_error",
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "duplicate_pair_review.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=review_fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in evidence_rows:
            writer.writerow(row)
    input_hashes_after = {
        "review_csv_sha256": sha256_file(review_csv),
        "split_manifest_sha256": sha256_file(split_csv),
        "metadata_csv_sha256": sha256_file(metadata_csv),
    }
    unchanged = input_hashes_before == input_hashes_after
    evidence = {
        "status": "investigation_completed" if not errors and unchanged else "investigation_incomplete",
        "source_review_csv": str(review_csv),
        "source_split_manifest": str(split_csv),
        "source_metadata": str(metadata_csv),
        "prepared_directory": str(prepared_dir),
        "review_csv_sha256_before": input_hashes_before["review_csv_sha256"],
        "review_csv_sha256_after": input_hashes_after["review_csv_sha256"],
        "split_manifest_sha256_before": input_hashes_before["split_manifest_sha256"],
        "split_manifest_sha256_after": input_hashes_after["split_manifest_sha256"],
        "metadata_sha256_before": input_hashes_before["metadata_csv_sha256"],
        "metadata_sha256_after": input_hashes_after["metadata_csv_sha256"],
        "input_files_unchanged": unchanged,
        "candidate_rows_in_source_review_csv": len(review_rows),
        "cross_patient_cross_fold_pairs": len(crossfold_rows),
        "reviewed_pair_rows": len(evidence_rows),
        "stable_pair_ids_unique": len(pair_ids) == len(set(pair_ids)),
        "source_files_checked_unique": len(source_cache),
        "source_file_sha256_equal_pairs": sum(bool(row.get("source_file_sha256_equal")) for row in evidence_rows),
        "stored_image_array_equal_pairs": sum(bool(row.get("stored_image_array_equal")) for row in evidence_rows),
        "source_identity_metadata_mismatch_pairs": sum(not bool(row.get("source_identity_matches_metadata", True)) for row in evidence_rows),
        "candidate_metadata_mismatch_pairs": sum(not bool(row.get("source_candidate_matches_metadata", True)) for row in evidence_rows),
        "ssim_summary": {
            "minimum": min(ssim_values) if ssim_values else None,
            "median": statistics.median(ssim_values) if ssim_values else None,
            "maximum": max(ssim_values) if ssim_values else None,
            "at_least_0_80": sum(value >= SSIM_HIGH_THRESHOLD for value in ssim_values),
        },
        "source_array_similarity_summary": {
            "pearson_median": statistics.median(source_correlations) if source_correlations else None,
            "pearson_maximum": max(source_correlations) if source_correlations else None,
            "pearson_at_least_0_90": sum(value >= 0.90 for value in source_correlations),
            "pearson_at_least_0_95": sum(value >= 0.95 for value in source_correlations),
            "pixel_equal_fraction_median": statistics.median(source_pixel_equal_fractions) if source_pixel_equal_fractions else None,
            "pixel_equal_fraction_maximum": max(source_pixel_equal_fractions) if source_pixel_equal_fractions else None,
        },
        "phash_hamming_distance_counts": dict(Counter(phash_values)),
        "automated_categories": dict(evidence_counts),
        "pairs_with_ssim_at_least_0_80": crossfold_ssim_high,
        "ssim_high_threshold": SSIM_HIGH_THRESHOLD,
        "ssim_medium_threshold": SSIM_MEDIUM_THRESHOLD,
        "phash_threshold": "Candidate set supplied by the prior audit: Hamming distance <=4/64; source IDs and order retained.",
        "ssim_exact_preprocessing": "Prior exported-image SSIM: min-max uint8 grayscale PNGs; no registration; scipy.ndimage.gaussian_filter sigma=1.5, truncate=4.0 (13x13 support), reflect mode; C1=(0.01*255)^2, C2=(0.03*255)^2; global mean.",
        "tool_versions": {
            "python": sys.version.replace("\n", " "),
            "numpy": np.__version__,
            "scipy": importlib.metadata.version("scipy"),
            "Pillow": Image.__version__,
        },
        "contact_sheet_pair_counts": contact_counts,
        "contact_sheet_pages": len(list((output_dir / "contact_sheets").glob("*.png"))),
        "all_human_review_statuses": sorted({row["human_review_status"] for row in evidence_rows}),
        "errors": errors,
        "prohibited_changes": {
            "source_files_modified": False,
            "prepared_images_or_masks_modified": False,
            "metadata_modified": False,
            "split_manifest_modified": False,
            "automatic_deletion": False,
            "automatic_relabeling": False,
            "automatic_patient_id_merging": False,
            "automatic_fold_reassignment": False,
        },
    }
    (output_dir / "automated_evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "pre_investigation_checksums.json").write_text(
        json.dumps(input_hashes_before, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_lines = [
        "# Cross-fold near-duplicate investigation",
        "",
        "**Decision: NO-GO remains in force. No model training was performed.**",
        "",
        "## Scope and method",
        "",
        f"- Preserved source review rows: {len(review_rows)}; filtered cross-patient/cross-fold candidates: {len(crossfold_rows)}.",
        "- Pair row order and existing `group_id` values were preserved. The pair ID is the original `group_id`.",
        f"- pHash candidate list originates from the prior audit at Hamming distance <= 4/64; this investigation did not generate or reorder candidate pairs.",
        f"- The prior SSIM values were computed on prepared per-image min-max normalized uint8 grayscale PNGs; no registration; `scipy.ndimage.gaussian_filter` sigma=1.5, truncate=4.0 (13x13 support), reflect boundary mode; `C1=(0.01*255)^2`, `C2=(0.03*255)^2`; global mean SSIM.",
        "- This run independently reopened source MATs to compare original `cjdata.image` arrays, dimensions, dtypes, intensity ranges, encoded source SHA-256, and dtype/shape/pixel-aware array SHA-256 against metadata.",
        "- Contact-sheet thumbnails preserve aspect ratio. The 50/50 blend and contrast-scaled absolute-difference panel are diagnostic visualizations, not identity evidence.",
        "",
        "## Automated evidence",
        "",
        f"- Pair records produced: {len(evidence_rows)}; source evidence errors: {len(errors)}.",
        f"- Source file hash-equal pairs: {evidence['source_file_sha256_equal_pairs']}; exact image-array-equal pairs: {evidence['stored_image_array_equal_pairs']}.",
        f"- Original-array Pearson correlation median/max: {_format_metric(evidence['source_array_similarity_summary']['pearson_median'])}/{_format_metric(evidence['source_array_similarity_summary']['pearson_maximum'])}; pairs >=0.90: {evidence['source_array_similarity_summary']['pearson_at_least_0_90']}; maximum exact-pixel fraction: {_format_metric(evidence['source_array_similarity_summary']['pixel_equal_fraction_maximum'])}.",
        f"- Cross-fold pairs with existing SSIM >= {SSIM_HIGH_THRESHOLD:.2f}: {crossfold_ssim_high}.",
        f"- SSIM range/median for reviewed pairs: {_format_metric(evidence['ssim_summary']['minimum'])} / {_format_metric(evidence['ssim_summary']['median'])} / {_format_metric(evidence['ssim_summary']['maximum'])}.",
        f"- pHash distance distribution: `{evidence['phash_hamming_distance_counts']}`.",
        f"- Source identity-to-metadata mismatches: {evidence['source_identity_metadata_mismatch_pairs']}; original candidate row-to-current metadata mismatches: {evidence['candidate_metadata_mismatch_pairs']}.",
        f"- Review status for every pair: `{', '.join(evidence['all_human_review_statuses'])}`. No human review was performed or inferred.",
        "- Automated categories are limited to `exact_duplicate_confirmed` when source SHA-256 or exact image-array equality proves equality; all other non-identical cases remain `unresolved`.",
        "",
        "## Contact sheets",
        "",
        f"- Pair counts by SSIM severity: `{contact_counts}`.",
        f"- Contact-sheet pages: {evidence['contact_sheet_pages']}; index: `contact_sheets/contact_sheet_index.csv`.",
        "- Every pair appears in its SSIM-severity group. The low-similarity control set is a deterministic sample of up to 12 lowest-SSIM pairs.",
        "- Image panels are labeled with pair ID, sample IDs, pseudonymous PIDs, classes, folds, SSIM, pHash distance, dimensions, and array-equality evidence.",
        "",
        "## Source provenance findings",
        "",
        "- Available dataset documentation describes a collection from two hospitals (Nanfang Hospital and Tianjin Medical University General Hospital), acquired 2005-09 through 2010-10, and says further acquisition details are unavailable due to the passage of time.",
        "- No per-slice acquisition/volume identifiers, DICOM series linkage, or mapping from MAT files to source scans was found in the inspected documentation or `cjdata` fields.",
        "- Repeated exports, shared acquisitions, and different-PID duplication cannot therefore be conclusively established or excluded from the available files.",
        "- Different PIDs in a candidate pair are retained as supplied; this report does not merge identities or infer that similar images depict the same person.",
        "",
        "## Integrity preservation",
        "",
        f"- Review CSV SHA-256 before/after: `{input_hashes_before['review_csv_sha256']}` / `{input_hashes_after['review_csv_sha256']}`.",
        f"- Split manifest SHA-256 before/after: `{input_hashes_before['split_manifest_sha256']}` / `{input_hashes_after['split_manifest_sha256']}`.",
        f"- Metadata CSV SHA-256 before/after: `{input_hashes_before['metadata_csv_sha256']}` / `{input_hashes_after['metadata_csv_sha256']}`.",
        f"- Input files unchanged: **{unchanged}**. Source files, prepared images/masks, metadata, labels, PIDs, and fold assignments were not modified.",
        "- No deletion, relabeling, patient-ID merge, or fold reassignment was performed.",
        "",
        "## Limitations",
        "",
        "- SSIM and pHash are not patient-identity or acquisition-identity tests. Similar normal anatomy and acquisition patterns can elevate similarity; dissimilar slices from one volume can also evade detection.",
        "- No human reviewer inspected the images during this automated investigation; all human conclusion fields remain blank.",
        "- The imaging arrays are 2-D slices and do not provide reliable slice position, series UID, scanner identifiers, or original DICOM provenance.",
        "- The investigation does not establish that candidate pairs are duplicate scans or that leakage has occurred.",
        "",
        "## Commands",
        "",
        "```powershell",
        "py -3 .\\scripts\\investigate_duplicates.py --review-csv .\\experiments\\baseline\\near_duplicate_crossfold_review.csv --split-csv .\\prepared_full_run\\patient_splits.csv --metadata-csv .\\prepared_full_run\\metadata.csv --prepared-dir .\\prepared_full_run --output-dir .\\reports\\duplicate_investigation",
        "py -3 -m pytest .\\tests\\test_duplicate_investigation.py -q",
        "py -3 -m pytest .\\tests -q",
        "",
        "Regression result from this execution: 15 tests passed (7 duplicate-investigation tests and 8 prior finalization tests).",
        "```",
        "",
        "For machine-readable pair-level evidence, see `automated_evidence.json` and `duplicate_pair_review.csv`.",
    ]
    (output_dir / "DUPLICATE_INVESTIGATION_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    recommendations = [
        "# Resolution recommendations",
        "",
        "**Current final status: NO-GO.** No pair has human-reviewed identity or acquisition conclusions; the pre-training gate must remain closed.",
        "",
        "## Evidence categories",
        "",
        f"- `exact_duplicate_confirmed`: {evidence_counts.get('exact_duplicate_confirmed', 0)} pairs, using exact source SHA-256 or dtype/shape/pixel equality.",
        f"- `probable_same_image`: {evidence_counts.get('probable_same_image', 0)} pairs. This category requires human review and is not assigned automatically.",
        f"- `possible_related_slices`: {evidence_counts.get('possible_related_slices', 0)} pairs. Acquisition provenance is unavailable, so this cannot be assigned from image similarity alone.",
        f"- `visually_similar_not_confirmed`: {evidence_counts.get('visually_similar_not_confirmed', 0)} pairs. Automated similarity is recorded, but no human visual conclusion is made.",
        f"- `unresolved`: {evidence_counts.get('unresolved', 0)} pairs.",
        "",
        "## Actions",
        "",
        "1. Request expert review of the 236 cross-patient/cross-fold pairs, prioritizing SSIM >= 0.80, then the highest SSIM and lowest pHash distances. The generated contact-sheet index preserves pair labels and page locations.",
        "2. Request source-level acquisition provenance from the dataset provider, if available. The available README reports no further acquisition detail.",
        "3. Record each reviewer decision, evidence, reviewer/date, and confidence in a separate human-authored adjudication file. Do not overwrite automated evidence or imply review occurred.",
        "4. Retain all samples, labels, PIDs, and original folds while unresolved. Do not merge patients based on similarity.",
        "5. If exact duplicate images are confirmed across folds, create a new versioned split manifest and resolution log; retain original split and data, document duplicate-linked groups, regroup conservatively, and rerun integrity, patient-overlap, and gate tests.",
        "6. If ambiguity cannot be resolved, use an explicitly conservative sensitivity protocol with candidate-linked groups kept together where justified by expert evidence; report exclusions/retentions and quantify sample/fold changes. If grouping evidence is not defensible, keep training blocked rather than silently changing folds.",
        "",
        "A separate candidate-grouped sensitivity split is not generated here because similarity alone does not establish that the candidate records belong to one acquisition or patient. Any sensitivity analysis must be versioned, justified, and validated independently.",
        "",
        "## Conclusion",
        "",
        "Available evidence does not conclusively resolve potential cross-fold relatedness. The 236 candidates are not confirmed leakage, but they remain a material unresolved risk for held-out-fold evaluation. **Keep the pre-training gate closed pending human/source-provenance review or a defensible, documented alternative evaluation protocol.**",
    ]
    (output_dir / "resolution_recommendations.md").write_text("\n".join(recommendations) + "\n", encoding="utf-8")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description="Investigate near-duplicate candidate pairs without modifying the dataset or split.")
    parser.add_argument("--review-csv", type=Path, default=DEFAULT_REVIEW_CSV)
    parser.add_argument("--split-csv", type=Path, default=DEFAULT_SPLIT_CSV)
    parser.add_argument("--metadata-csv", type=Path, default=DEFAULT_METADATA_CSV)
    parser.add_argument("--prepared-dir", type=Path, default=DEFAULT_PREPARED_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    result = investigate(args.review_csv, args.split_csv, args.metadata_csv, args.prepared_dir, args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "investigation_completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
