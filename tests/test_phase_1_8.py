"""Phase 1.8 Tests — Final Protocol Ratification, Frozen Pre-Registration, and Gate Verification.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP_DIR_17 = ROOT / "experiments" / "phase_1_7"
EXP_DIR_18 = ROOT / "experiments" / "phase_1_8"
MANIFEST_DIR = EXP_DIR_17 / "candidate_grouped_manifests"
SPLITS_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
P18_CHECKSUMS_JSON = EXP_DIR_18 / "phase_1_8_checksums.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# 1. Authoritative baseline manifest preservation
def test_authoritative_manifest_preservation():
    assert SPLITS_CSV.exists(), "patient_splits.csv missing"
    assert METADATA_CSV.exists(), "metadata.csv missing"
    with open(P18_CHECKSUMS_JSON, encoding="utf-8") as f:
        p18 = json.load(f)
    assert _sha256(SPLITS_CSV) == p18["artifacts"]["patient_splits_csv"]["sha256"]
    assert _sha256(METADATA_CSV) == p18["artifacts"]["metadata_csv"]["sha256"]


# 2. Phase 1.8 deliverable presence and checksums
def test_phase_1_8_deliverables_and_checksums():
    required_files = [
        EXP_DIR_18 / "A_SENSITIVITY_DESIGN_RATIFICATION.md",
        EXP_DIR_18 / "B_EFFECT_SIZE_DECISION.md",
        EXP_DIR_18 / "C_FROZEN_PREREGISTRATION.md",
        EXP_DIR_18 / "D_UNRESOLVED_RISK_RECORD.md",
        EXP_DIR_18 / "E_FINAL_GATE_DECISION.md",
        EXP_DIR_18 / "phase_1_8_checksums.json",
    ]
    for rf in required_files:
        assert rf.exists(), f"Required Phase 1.8 deliverable missing: {rf}"

    with open(P18_CHECKSUMS_JSON, encoding="utf-8") as f:
        p18 = json.load(f)
    for k, v in p18["artifacts"].items():
        p = ROOT / v["path"]
        assert p.exists(), f"Artifact missing: {p}"
        assert _sha256(p) == v["sha256"], f"Checksum mismatch for: {p}"


# 3. Ratification of sensitivity thresholds (0.75 and 0.80 primary, 0.60 stress test)
def test_sensitivity_design_ratification_content():
    content = (EXP_DIR_18 / "A_SENSITIVITY_DESIGN_RATIFICATION.md").read_text(encoding="utf-8")
    assert "0.80" in content
    assert "0.75" in content
    assert "0.60" in content
    assert "percolation" in content.lower()
    assert "stress test" in content.lower()
    assert "zero residual" in content.lower()


# 4. Effect size framework verification
def test_effect_size_framework():
    content = (EXP_DIR_18 / "B_EFFECT_SIZE_DECISION.md").read_text(encoding="utf-8")
    assert "0.05" in content
    assert "0.10" in content
    assert "Zone 1" in content or "Predominant Context" in content
    assert "Zone 2" in content or "Dual" in content
    assert "Zone 3" in content or "Intratumoral" in content
    assert "No Post-Hoc Selection" in content or "not be modified" in content


# 5. Frozen pre-registration content and causal caveats
def test_frozen_preregistration_completeness_and_causal_caveat():
    content = (EXP_DIR_18 / "C_FROZEN_PREREGISTRATION.md").read_text(encoding="utf-8")
    assert "Macro-Averaged F1 Score" in content or "Macro-F1" in content
    assert "Balanced Accuracy" in content
    assert "Confusion Matrix" in content
    assert "I_{\\text{orig}}" in content or "I_{\\text{tumor}}" in content or "I_{orig}" in content
    assert "I_{\\text{placebo}}" in content or "I_{placebo}" in content
    assert "Cluster Bootstrap" in content or "cluster bootstrap" in content
    assert "Benjamini-Hochberg" in content
    assert "Do not treat a confidence change after masking as definitive causal proof" in content or (
        "NOT constitute definitive causal proof" in content
    ), "Pre-registration must contain explicit caveat on masking confidence changes and causal attribution"


# 6. Unresolved risk record verification
def test_unresolved_risk_record_completeness():
    content = (EXP_DIR_18 / "D_UNRESOLVED_RISK_RECORD.md").read_text(encoding="utf-8")
    assert "236" in content
    assert "DICOM" in content
    assert "pHash" in content
    assert "unknowable" in content.lower()


# 7. Final gate decision verification
def test_final_gate_decision_status():
    content = (EXP_DIR_18 / "E_FINAL_GATE_DECISION.md").read_text(encoding="utf-8")
    assert "GO-FOR-BASELINE-ONLY" in content
    assert "separately gated" in content.lower()
    assert "NO model training occurred" in content or "No model has been trained" in content


# 8. Zero residual leakage at ratified thresholds
@pytest.mark.parametrize("thresh, t_str", [(0.80, "0_80"), (0.75, "0_75")])
def test_zero_residual_leakage_on_ratified_manifests(thresh: float, t_str: str):
    review_csv = ROOT / "reports" / "duplicate_investigation" / "duplicate_pair_review.csv"
    with open(review_csv, newline="", encoding="utf-8-sig") as f:
        pairs = list(csv.DictReader(f))

    manifest_p = MANIFEST_DIR / f"split_regrouped_ssim_{t_str}.csv"
    with open(manifest_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    fold_map = {r["sample_id"]: r["fold"] for r in rows}
    active_pairs = [p for p in pairs if float(p["export_ssim"]) >= thresh]
    cross_fold_pairs = [p for p in active_pairs if fold_map[p["sample_id_a"]] != fold_map[p["sample_id_b"]]]
    assert len(cross_fold_pairs) == 0, f"Expected 0 cross-fold pairs with SSIM >= {thresh}, got {len(cross_fold_pairs)}"
