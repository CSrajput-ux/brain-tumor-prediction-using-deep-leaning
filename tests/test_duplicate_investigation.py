from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.io import savemat

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from investigate_duplicates import (
    _array_similarity,
    _hash_array,
    investigate,
    select_cross_patient_cross_fold_pairs,
    stable_pair_id,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fixture(
    root: Path,
    missing_source: bool = False,
    missing_image: bool = False,
    invalid_source: bool = False,
) -> tuple[Path, Path, Path, Path]:
    source_dir = root / "source"
    prepared_dir = root / "prepared"
    output_dir = root / "output"
    source_dir.mkdir(parents=True)
    (source_dir / "brainTumorDataPublic_1").mkdir()
    prepared_dir.mkdir()
    image_a = np.arange(64, dtype=np.int16).reshape(8, 8)
    image_b = image_a.copy()
    image_b[3, 4] += 1
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[2:5, 2:5] = 1
    mat_a = source_dir / "brainTumorDataPublic_1" / "sample_a.mat"
    mat_b = source_dir / "brainTumorDataPublic_1" / "sample_b.mat"
    savemat(str(mat_a), {"cjdata": {"label": 1, "PID": "P_A", "image": image_a, "tumorMask": mask}})
    savemat(str(mat_b), {"cjdata": {"label": 1, "PID": "P_B", "image": image_b, "tumorMask": mask}})
    if invalid_source:
        mat_b.write_bytes(b"not a MATLAB file")
    export_a, export_b = prepared_dir / "a.png", prepared_dir / "b.png"
    Image.fromarray(np.asarray(image_a, dtype=np.uint8)).save(export_a)
    Image.fromarray(np.asarray(image_b, dtype=np.uint8)).save(export_b)
    metadata_rows = []
    for sample_id, mat_path, image, export in (
        ("sample_a", mat_a, image_a, export_a),
        ("sample_b", mat_b, image_b, export_b),
    ):
        metadata_rows.append({
            "sample_id": sample_id,
            "source_path": str(mat_path if not (missing_source and sample_id == "sample_b") else mat_path.parent / "missing.mat"),
            "patient_id": "P_A" if sample_id == "sample_a" else "P_B",
            "class_name": "meningioma",
            "sha256": _sha(mat_path),
            "image_array_sha256": _hash_array(image),
            "image_output_path": f"missing_{export.name}" if missing_image and sample_id == "sample_b" else export.name,
        })
    metadata_path = prepared_dir / "metadata.csv"
    _write_csv(metadata_path, metadata_rows, list(metadata_rows[0]))
    split_path = prepared_dir / "patient_splits.csv"
    split_rows = [
        {"sample_id": "sample_a", "patient_id": "P_A", "class": "meningioma", "fold": "fold_1"},
        {"sample_id": "sample_b", "patient_id": "P_B", "class": "meningioma", "fold": "fold_2"},
    ]
    _write_csv(split_path, split_rows, list(split_rows[0]))
    review_path = root / "near_duplicate_crossfold_review.csv"
    review_rows = []
    for index in range(236):
        review_rows.append({
            "group_id": f"original-pair-id-{index:03d}",
            "sample_id_a": "sample_a",
            "sample_id_b": "sample_b",
            "source_path_a": str(mat_a),
            "source_path_b": str(mat_b),
            "patient_id_a": "P_A",
            "patient_id_b": "P_B",
            "class_a": "meningioma",
            "class_b": "meningioma",
            "fold_a": "fold_1",
            "fold_b": "fold_2",
            "phash_hamming_distance": "2",
            "pixel_equal_fraction": "0.98",
            "ssim": "0.82",
            "pearson_correlation": "0.99",
            "cross_patient": "True",
            "cross_fold": "True",
        })
    _write_csv(review_path, review_rows, list(review_rows[0]))
    return review_path, split_path, metadata_path, prepared_dir


def test_candidate_count_and_pair_ids_are_stable() -> None:
    rows = [
        {
            "group_id": f"source-{index}",
            "sample_id_a": f"a-{index}",
            "sample_id_b": f"b-{index}",
            "patient_id_a": f"p-{index}",
            "patient_id_b": f"q-{index}",
            "fold_a": "fold_1",
            "fold_b": "fold_2",
            "cross_patient": "True",
            "cross_fold": "True",
        }
        for index in range(236)
    ]
    selected = select_cross_patient_cross_fold_pairs(rows)
    assert len(selected) == 236
    assert [stable_pair_id(row) for row in selected] == [f"source-{index}" for index in range(236)]


def test_missing_source_path_is_reported_and_not_human_reviewed(tmp_path: Path) -> None:
    review, split, metadata, prepared = _fixture(tmp_path, missing_source=True)
    result = investigate(review, split, metadata, prepared, tmp_path / "investigation")
    assert result["reviewed_pair_rows"] == 236
    assert result["errors"]
    with (tmp_path / "investigation" / "duplicate_pair_review.csv").open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert all(row["automated_category"] == "unresolved" for row in rows)
    assert all(row["human_review_status"] == "automated_evidence_only_no_human_review" for row in rows)


def test_invalid_mat_source_is_reported(tmp_path: Path) -> None:
    review, split, metadata, prepared = _fixture(tmp_path, invalid_source=True)
    result = investigate(review, split, metadata, prepared, tmp_path / "investigation")
    assert result["errors"]
    assert result["reviewed_pair_rows"] == 236
    with (tmp_path / "investigation" / "duplicate_pair_review.csv").open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert all(row["automated_category"] == "unresolved" for row in rows)
    assert all("Evidence extraction failed" in row["automated_finding"] for row in rows)


def test_missing_prepared_image_is_reported(tmp_path: Path) -> None:
    review, split, metadata, prepared = _fixture(tmp_path, missing_image=True)
    result = investigate(review, split, metadata, prepared, tmp_path / "investigation")
    assert result["errors"]
    assert result["reviewed_pair_rows"] == 236
    assert result["source_file_sha256_equal_pairs"] == 0


def test_source_array_equality_and_hash_evidence() -> None:
    first = np.arange(25, dtype=np.int16).reshape(5, 5)
    equal = first.copy()
    different = first.copy()
    different[2, 2] += 1
    identical_result = _array_similarity(first, equal)
    different_result = _array_similarity(first, different)
    assert identical_result["identical_image_arrays"] is True
    assert identical_result["array_hash_a"] == identical_result["array_hash_b"]
    assert different_result["identical_image_arrays"] is False
    assert different_result["array_hash_a"] != different_result["array_hash_b"]


def test_exact_source_and_image_array_equality_is_confirmed_without_merging_ids(tmp_path: Path) -> None:
    review, split, metadata_path, prepared = _fixture(tmp_path)
    source_a = tmp_path / "source" / "brainTumorDataPublic_1" / "sample_a.mat"
    source_b = tmp_path / "source" / "brainTumorDataPublic_1" / "sample_b.mat"
    source_b.write_bytes(source_a.read_bytes())
    with metadata_path.open(newline="", encoding="utf-8-sig") as stream:
        metadata = list(csv.DictReader(stream))
    metadata[1]["sha256"] = _sha(source_a)
    metadata[1]["image_array_sha256"] = metadata[0]["image_array_sha256"]
    _write_csv(metadata_path, metadata, list(metadata[0]))
    Image.open(prepared / "a.png").save(prepared / "b.png")
    output = tmp_path / "investigation_exact"
    result = investigate(review, split, metadata_path, prepared, output)
    assert result["source_file_sha256_equal_pairs"] == 236
    assert result["stored_image_array_equal_pairs"] == 236
    assert result["source_identity_metadata_mismatch_pairs"] == 236
    with (output / "duplicate_pair_review.csv").open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert all(row["automated_category"] == "exact_duplicate_confirmed" for row in rows)
    assert all(row["patient_id_a"] != row["patient_id_b"] for row in rows)
    assert all(row["source_identity_matches_metadata"] == "False" for row in rows)
    assert all(row["human_review_status"] == "automated_evidence_only_no_human_review" for row in rows)


def test_contact_sheet_index_labels_and_originals_preserved_and_deterministic(tmp_path: Path) -> None:
    review, split, metadata, prepared = _fixture(tmp_path)
    original_hashes = {
        "review": _sha(review),
        "split": _sha(split),
        "metadata": _sha(metadata),
        "source_a": _sha(tmp_path / "source" / "brainTumorDataPublic_1" / "sample_a.mat"),
        "source_b": _sha(tmp_path / "source" / "brainTumorDataPublic_1" / "sample_b.mat"),
    }
    first_output = tmp_path / "investigation_a"
    second_output = tmp_path / "investigation_b"
    first = investigate(review, split, metadata, prepared, first_output)
    second = investigate(review, split, metadata, prepared, second_output)
    assert first["input_files_unchanged"] is True
    assert first["cross_patient_cross_fold_pairs"] == 236
    assert first["source_file_sha256_equal_pairs"] == 0
    assert first["stored_image_array_equal_pairs"] == 0
    for name in ("duplicate_pair_review.csv", "automated_evidence.json", "DUPLICATE_INVESTIGATION_REPORT.md", "resolution_recommendations.md"):
        assert (first_output / name).read_bytes() == (second_output / name).read_bytes()
    first_sheets = sorted((first_output / "contact_sheets").glob("*.png"))
    second_sheets = sorted((second_output / "contact_sheets").glob("*.png"))
    assert [path.name for path in first_sheets] == [path.name for path in second_sheets]
    assert [_sha(path) for path in first_sheets] == [_sha(path) for path in second_sheets]
    with (first_output / "contact_sheets" / "contact_sheet_index.csv").open(newline="", encoding="utf-8-sig") as stream:
        index_rows = list(csv.DictReader(stream))
    primary_rows = [row for row in index_rows if row["contact_group"] != "low_similarity_controls"]
    assert len(primary_rows) == 236
    assert all(row["patient_id_a"] == "P_A" and row["patient_id_b"] == "P_B" for row in primary_rows)
    assert all(row["class_a"] == row["class_b"] == "meningioma" for row in primary_rows)
    assert all(row["fold_a"] == "fold_1" and row["fold_b"] == "fold_2" for row in primary_rows)
    assert all(row["ssim"] == "0.82" and row["phash_hamming_distance"] == "2" for row in primary_rows)
    assert first["prohibited_changes"]["automatic_deletion"] is False
    assert first["prohibited_changes"]["automatic_relabeling"] is False
    assert first["prohibited_changes"]["automatic_patient_id_merging"] is False
    assert first["prohibited_changes"]["automatic_fold_reassignment"] is False
    assert original_hashes == {
        "review": _sha(review),
        "split": _sha(split),
        "metadata": _sha(metadata),
        "source_a": _sha(tmp_path / "source" / "brainTumorDataPublic_1" / "sample_a.mat"),
        "source_b": _sha(tmp_path / "source" / "brainTumorDataPublic_1" / "sample_b.mat"),
    }
    assert len(list((first_output / "contact_sheets").glob("*.png"))) > 0
