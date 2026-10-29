"""Automated test suite for Phase 2: Duplicate detection, split integrity, and leakage audit."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_cheng_splits_exist_and_cover_all_samples() -> None:
    manifest_path = ROOT / "manifests" / "cheng_manifest.csv"
    splits_path = ROOT / "manifests" / "cheng_splits.csv"
    assert manifest_path.exists()
    assert splits_path.exists()

    manifest = read_csv(manifest_path)
    splits = read_csv(splits_path)

    assert len(manifest) == 3064
    assert len(splits) == 3064

    manifest_ids = {r["sample_id"] for r in manifest}
    splits_ids = {r["sample_id"] for r in splits}
    assert manifest_ids == splits_ids

    valid_folds = {f"fold_{i}" for i in range(1, 6)}
    for r in manifest:
        assert r["official_split"] in valid_folds


def test_cheng_patient_isolation_zero_leakage() -> None:
    manifest = read_csv(ROOT / "manifests" / "cheng_manifest.csv")
    patient_to_folds = defaultdict(set)
    for r in manifest:
        pid = r["patient_id"]
        assert pid, f"Sample {r['sample_id']} has empty patient_id"
        patient_to_folds[pid].add(r["official_split"])

    assert len(patient_to_folds) == 233
    violating_patients = {pid: folds for pid, folds in patient_to_folds.items() if len(folds) > 1}
    assert not violating_patients, f"Patient leakage detected: {violating_patients}"


def test_cheng_class_representation_per_fold() -> None:
    manifest = read_csv(ROOT / "manifests" / "cheng_manifest.csv")
    fold_classes = defaultdict(Counter)
    for r in manifest:
        fold_classes[r["official_split"]][r["class_label"]] += 1

    expected_classes = {"glioma", "meningioma", "pituitary"}
    for fold, counts in fold_classes.items():
        assert set(counts.keys()) == expected_classes
        for c in expected_classes:
            assert counts[c] >= 100, f"{fold} has only {counts[c]} samples for {c}"


def test_brisc_splits_preserve_official_partitions() -> None:
    manifest = read_csv(ROOT / "manifests" / "brisc_manifest.csv")
    splits = read_csv(ROOT / "manifests" / "brisc_splits.csv")
    assert len(manifest) == 6000
    assert len(splits) == 6000

    split_counts = Counter(r["official_split"] for r in manifest)
    assert split_counts["train"] == 4000
    assert split_counts["val"] == 1000
    assert split_counts["test"] == 1000
    assert split_counts["train"] + split_counts["val"] == 5000


def test_brisc_train_val_zero_duplicate_leakage() -> None:
    manifest = read_csv(ROOT / "manifests" / "brisc_manifest.csv")
    train_groups = {r["duplicate_group"] for r in manifest if r["official_split"] == "train" and r["duplicate_group"]}
    val_groups = {r["duplicate_group"] for r in manifest if r["official_split"] == "val" and r["duplicate_group"]}

    cross_leakage = train_groups.intersection(val_groups)
    assert not cross_leakage, f"Duplicate groups cross train and val: {cross_leakage}"


def test_brisc_test_leakage_properly_flagged() -> None:
    manifest = read_csv(ROOT / "manifests" / "brisc_manifest.csv")
    test_records = [r for r in manifest if r["official_split"] == "test"]
    assert len(test_records) == 1000

    leaked = [r for r in test_records if r["exclusion_reason"] == "train_test_duplicate_leakage"]
    assert len(leaked) == 101, f"Expected 101 leaked test samples, found {len(leaked)}"

    clean_test = [r for r in test_records if not r["exclusion_reason"]]
    assert len(clean_test) == 899


def test_duplicate_groups_consistency() -> None:
    groups = read_csv(ROOT / "manifests" / "duplicate_groups.csv")
    assert len(groups) == 278

    group_to_samples = defaultdict(list)
    for g in groups:
        assert g["dataset"] == "brisc"
        group_to_samples[g["group_id"]].append(g["sample_id"])

    # All duplicate groups must contain at least 2 samples
    for gid, sids in group_to_samples.items():
        assert len(sids) >= 2, f"Group {gid} has fewer than 2 samples: {sids}"


def test_cross_dataset_zero_exact_duplicates() -> None:
    pairs = read_csv(ROOT / "manifests" / "duplicate_pairs.csv")
    cross_exact = [p for p in pairs if p["dataset_a"] != p["dataset_b"] and p["decision"] == "confirmed_exact_pixel_duplicate"]
    assert len(cross_exact) == 0, f"Found unexpected exact cross-dataset duplicate pairs: {cross_exact}"

