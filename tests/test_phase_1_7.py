"""Phase 1.7 Tests — Sensitivity Analysis, Transitive Closure, Regrouped Manifests, and Pre-Registration Integrity.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import networkx as nx
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = ROOT / "experiments" / "phase_1_7"
MANIFEST_DIR = EXP_DIR / "candidate_grouped_manifests"
SPLITS_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
P16_CHECKSUMS_JSON = ROOT / "reports" / "independent_review" / "phase_1_6_checksums.json"
P17_CHECKSUMS_JSON = EXP_DIR / "phase_1_7_checksums.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# 1. Preservation of authoritative manifests
def test_authoritative_manifest_preservation():
    assert SPLITS_CSV.exists(), "patient_splits.csv missing"
    assert METADATA_CSV.exists(), "metadata.csv missing"
    with open(P16_CHECKSUMS_JSON, encoding="utf-8") as f:
        p16 = json.load(f)
    expected_splits = p16["artifacts"]["patient_splits_csv"]["sha256"]
    expected_meta = p16["artifacts"]["metadata_csv"]["sha256"]
    assert _sha256(SPLITS_CSV) == expected_splits, "Authoritative patient_splits.csv was modified!"
    assert _sha256(METADATA_CSV) == expected_meta, "Authoritative metadata.csv was modified!"


# 2. Synthetic connected components correctness
def test_synthetic_connected_components():
    G = nx.Graph()
    G.add_nodes_from(["s1", "s2", "s3", "s4", "s5", "s6"])
    G.add_edge("s1", "s2")
    G.add_edge("s2", "s3")  # transitive chain: s1-s2-s3
    G.add_edge("s4", "s5")  # component 2: s4-s5
    # s6 is singleton

    comps = sorted(list(nx.connected_components(G)), key=lambda c: (-len(c), sorted(list(c))[0]))
    assert len(comps) == 3
    assert comps[0] == {"s1", "s2", "s3"}
    assert comps[1] == {"s4", "s5"}
    assert comps[2] == {"s6"}


# 3. Threshold inclusion semantics (strictly >=)
def test_threshold_inclusion_semantics():
    pairs = [
        {"sample_a": "s1", "sample_b": "s2", "ssim": 0.80},
        {"sample_a": "s3", "sample_b": "s4", "ssim": 0.7999},
        {"sample_a": "s5", "sample_b": "s6", "ssim": 0.8001},
    ]
    threshold = 0.80
    edges = [(p["sample_a"], p["sample_b"]) for p in pairs if p["ssim"] >= threshold]
    assert ("s1", "s2") in edges, "Exact threshold value must be included (inclusive >=)"
    assert ("s5", "s6") in edges
    assert ("s3", "s4") not in edges, "Values below threshold must be excluded"


# 4. Deliverables presence and checksum integrity
def test_deliverable_presence_and_checksum_integrity():
    required_files = [
        EXP_DIR / "C1_TRANSITIVE_CLOSURE_REPORT.md",
        EXP_DIR / "C2_REGROUPED_FOLD_ASSESSMENT.md",
        EXP_DIR / "PREREGISTRATION_DRAFT.md",
        EXP_DIR / "PHASE_1_7_DECISION.md",
        EXP_DIR / "component_summary_by_threshold.csv",
        EXP_DIR / "component_membership.csv",
        EXP_DIR / "phase_1_7_checksums.json",
        MANIFEST_DIR / "split_regrouped_ssim_0_80.csv",
        MANIFEST_DIR / "split_regrouped_ssim_0_75.csv",
        MANIFEST_DIR / "split_regrouped_ssim_0_70.csv",
        MANIFEST_DIR / "split_regrouped_ssim_0_60.csv",
    ]
    for rf in required_files:
        assert rf.exists(), f"Required Phase 1.7 deliverable missing: {rf}"

    with open(P17_CHECKSUMS_JSON, encoding="utf-8") as f:
        p17 = json.load(f)
    for k, v in p17["artifacts"].items():
        p = ROOT / v["path"]
        assert p.exists(), f"Artifact in checksums missing: {p}"
        assert _sha256(p) == v["sha256"], f"Checksum mismatch for artifact: {p}"


# 5. Complete sample accounting in all manifests
@pytest.mark.parametrize("thresh_str", ["0_80", "0_75", "0_70", "0_60"])
def test_complete_sample_accounting(thresh_str: str):
    manifest_p = MANIFEST_DIR / f"split_regrouped_ssim_{thresh_str}.csv"
    with open(manifest_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3064, f"Expected 3064 rows in {manifest_p.name}, got {len(rows)}"

    with open(SPLITS_CSV, newline="", encoding="utf-8-sig") as f:
        orig_sample_ids = {r["sample_id"] for r in csv.DictReader(f)}
    manifest_sample_ids = {r["sample_id"] for r in rows}
    assert manifest_sample_ids == orig_sample_ids, f"Sample set mismatch in {manifest_p.name}"


# 6. Zero patient crossing across folds
@pytest.mark.parametrize("thresh_str", ["0_80", "0_75", "0_70", "0_60"])
def test_no_patient_overlap_across_folds(thresh_str: str):
    manifest_p = MANIFEST_DIR / f"split_regrouped_ssim_{thresh_str}.csv"
    with open(manifest_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    patient_folds = {}
    for r in rows:
        pid = r["patient_id"]
        fold = r["fold"]
        if pid in patient_folds:
            assert patient_folds[pid] == fold, f"Patient {pid} crosses folds in {manifest_p.name}!"
        else:
            patient_folds[pid] = fold


# 7. Zero component crossing across folds
@pytest.mark.parametrize("thresh_str", ["0_80", "0_75", "0_70", "0_60"])
def test_no_component_overlap_across_folds(thresh_str: str):
    manifest_p = MANIFEST_DIR / f"split_regrouped_ssim_{thresh_str}.csv"
    with open(manifest_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    comb_folds = {}
    sim_folds = {}
    for r in rows:
        c_id = r["combined_group_id"]
        s_id = r["sim_comp_id"]
        fold = r["fold"]
        if c_id in comb_folds:
            assert comb_folds[c_id] == fold, f"Combined group {c_id} crosses folds in {manifest_p.name}!"
        else:
            comb_folds[c_id] = fold
        if s_id in sim_folds:
            assert sim_folds[s_id] == fold, f"Similarity component {s_id} crosses folds in {manifest_p.name}!"
        else:
            sim_folds[s_id] = fold


# 8. Class count constraints and balance verification
@pytest.mark.parametrize("thresh_str", ["0_80", "0_75", "0_70", "0_60"])
def test_class_count_constraints_and_balance(thresh_str: str):
    manifest_p = MANIFEST_DIR / f"split_regrouped_ssim_{thresh_str}.csv"
    with open(manifest_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    fold_classes = {}
    for r in rows:
        fold = r["fold"]
        cls = r["class"]
        fold_classes.setdefault(fold, {}).setdefault(cls, 0)
        fold_classes[fold][cls] += 1

    for fold, counts in fold_classes.items():
        for cls in ["glioma", "meningioma", "pituitary"]:
            assert counts.get(cls, 0) >= 50, f"Class {cls} has <50 samples in {fold} of {manifest_p.name}"

    if thresh_str == "0_60":
        # At 0.60, fold 5 must have the percolation distortion documented
        fold_totals = {f: sum(counts.values()) for f, counts in fold_classes.items()}
        assert fold_totals["fold_5"] == 992, "Fold 5 expected to contain 992 samples due to giant component"
        assert max(fold_totals.values()) - min(fold_totals.values()) == 474


# 9. Deterministic component and membership IDs
def test_component_membership_integrity():
    mem_p = EXP_DIR / "component_membership.csv"
    with open(mem_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3064
    for r in rows:
        assert r["sim_comp_0_80"].startswith("sim_0_80_")
        assert r["comb_grp_0_80"].startswith("comb_0_80_")
        assert r["sim_comp_0_60"].startswith("sim_0_60_")
        assert r["comb_grp_0_60"].startswith("comb_0_60_")


# 10. Pre-registration draft completeness
def test_preregistration_completeness():
    prereg_p = EXP_DIR / "PREREGISTRATION_DRAFT.md"
    content = prereg_p.read_text(encoding="utf-8")
    assert "Macro-Averaged F1 Score" in content or "Macro-F1" in content
    assert "Balanced Accuracy" in content
    assert "Confusion Matrix" in content
    assert "I_{tumor}" in content or "I_{\\text{tumor}}" in content
    assert "I_{removed}" in content or "I_{\\text{removed}}" in content
    assert "I_{placebo}" in content or "I_{\\text{placebo}}" in content
    assert "I_{context_shift}" in content or "I_{\\text{context\\_shift}}" in content
    assert "DECISION REQUIRING EXPLICIT RESEARCHER APPROVAL" in content, (
        "Pre-registration must flag that numeric effect size bound requires explicit researcher approval"
    )
    assert "Bootstrap" in content
