"""Phase 2 Tests — Controlled Baseline Training Verification and Integrity Audit.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = ROOT / "experiments" / "phase_2_baseline"
CHECKSUMS_JSON = EXP_DIR / "checksums.json"
SPLITS_CSV = ROOT / "prepared_full_run" / "patient_splits.csv"
METADATA_CSV = ROOT / "prepared_full_run" / "metadata.csv"
P18_CHECKSUMS = ROOT / "experiments" / "phase_1_8" / "phase_1_8_checksums.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# 1. Authoritative baseline manifest preservation
def test_authoritative_manifest_preservation():
    assert SPLITS_CSV.exists()
    assert METADATA_CSV.exists()
    with open(P18_CHECKSUMS, encoding="utf-8") as f:
        p18 = json.load(f)
    assert _sha256(SPLITS_CSV) == p18["artifacts"]["patient_splits_csv"]["sha256"], "Authoritative splits modified!"
    assert _sha256(METADATA_CSV) == p18["artifacts"]["metadata_csv"]["sha256"], "Authoritative metadata modified!"


# 2. Phase 2 deliverables presence and cryptographic checksums
def test_phase_2_deliverables_and_checksums():
    assert CHECKSUMS_JSON.exists(), "checksums.json missing"
    with open(CHECKSUMS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_artifacts"] == 51
    for k, v in data["artifacts"].items():
        p = ROOT / v["path"]
        assert p.exists(), f"Artifact missing: {p}"
        assert _sha256(p) == v["sha256"], f"Checksum mismatch: {p}"


# 3. All 15 checkpoints exist and load valid state dicts
@pytest.mark.parametrize("scenario", ["S0", "S1", "S2"])
@pytest.mark.parametrize("fold", ["fold_1", "fold_2", "fold_3", "fold_4", "fold_5"])
def test_checkpoint_validity(scenario: str, fold: str):
    ckpt_p = EXP_DIR / scenario / f"{fold}_best_checkpoint.pt"
    assert ckpt_p.exists(), f"Checkpoint missing: {ckpt_p}"
    assert ckpt_p.stat().st_size > 90 * 1024 * 1024, "Checkpoint too small"

    ckpt = torch.load(ckpt_p, map_location="cpu", weights_only=True)
    assert "model_state_dict" in ckpt
    assert "epoch" in ckpt
    assert "val_macro_f1" in ckpt
    assert "fc.weight" in ckpt["model_state_dict"]
    assert ckpt["model_state_dict"]["fc.weight"].shape == (3, 2048)


# 4. Pooled out-of-fold predictions completeness and probability validity
def test_pooled_oof_predictions_integrity():
    pred_p = EXP_DIR / "pooled_oof_predictions.csv"
    assert pred_p.exists()
    with open(pred_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 3064 * 3, f"Expected 9192 rows, got {len(rows)}"

    for sc in ["S0", "S1", "S2"]:
        sc_rows = [r for r in rows if r["scenario"] == sc]
        assert len(sc_rows) == 3064
        unique_samples = {r["sample_id"] for r in sc_rows}
        assert len(unique_samples) == 3064

        for r in sc_rows:
            p_m = float(r["prob_meningioma"])
            p_g = float(r["prob_glioma"])
            p_p = float(r["prob_pituitary"])
            assert 0.0 <= p_m <= 1.0
            assert 0.0 <= p_g <= 1.0
            assert 0.0 <= p_p <= 1.0
            assert abs(p_m + p_g + p_p - 1.0) < 1e-3, "Probabilities must sum to ~1.0"
            assert r["true_class"] in ["meningioma", "glioma", "pituitary"]
            assert r["pred_class"] in ["meningioma", "glioma", "pituitary"]


# 5. Fold metrics integrity
def test_fold_metrics_integrity():
    metrics_p = EXP_DIR / "fold_metrics.csv"
    assert metrics_p.exists()
    with open(metrics_p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 15, f"Expected 15 fold metric rows, got {len(rows)}"
    for r in rows:
        f1 = float(r["test_macro_f1"])
        assert f1 >= 0.85, f"Fold Macro-F1 unexpectedly low ({f1}) in {r['scenario']} {r['fold']}"
        assert int(r["num_test_samples"]) in [611, 612, 613, 614]


# 6. Metrics JSON structure and bootstrap CIs
def test_metrics_json_integrity():
    metrics_json_p = EXP_DIR / "metrics.json"
    assert metrics_json_p.exists()
    with open(metrics_json_p, encoding="utf-8") as f:
        data = json.load(f)

    for sc in ["S0", "S1", "S2"]:
        assert sc in data["scenarios"]
        sc_data = data["scenarios"][sc]
        f1 = sc_data["pooled_macro_f1"]
        assert f1 >= 0.90, f"Scenario {sc} pooled Macro-F1 below 0.90 ({f1})"
        ci = sc_data["pooled_macro_f1_95ci"]
        assert len(ci) == 2
        assert ci[0] <= f1 <= ci[1]
        assert sc_data["clusters_count"] in [217, 231, 233]

    assert "paired_comparisons" in data
    assert "S0_vs_S1" in data["paired_comparisons"]
    assert "S0_vs_S2" in data["paired_comparisons"]
    assert "S1_vs_S2" in data["paired_comparisons"]


# 7. Baseline report content and completion decision
def test_baseline_report_contents():
    report_p = EXP_DIR / "BASELINE_REPORT.md"
    assert report_p.exists()
    content = report_p.read_text(encoding="utf-8")
    assert "BASELINE-COMPLETE-PENDING-INDEPENDENT-AUDIT" in content
    assert "RTX 4050" in content
    assert "ResNet-50" in content
    assert "S0" in content and "S1" in content and "S2" in content
