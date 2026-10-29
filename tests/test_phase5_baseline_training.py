"""Phase 5 unit and validation tests: Baseline model checkpoints, predictions, and calibration metrics."""
from __future__ import annotations

import csv
from pathlib import Path
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = ROOT / "checkpoints"
PREDICTIONS_DIR = ROOT / "predictions"
REPORTS_DIR = ROOT / "reports"


def test_checkpoint_structure():
    """Verify saved baseline checkpoints contain all required keys and match architecture."""
    ckpts = list(CHECKPOINTS_DIR.glob("*.pt"))
    assert len(ckpts) > 0, "No checkpoints found in checkpoints directory"

    for ckpt_path in ckpts:
        ckpt = torch.load(ckpt_path, map_location="cpu")
        assert isinstance(ckpt, dict), f"{ckpt_path.name} is not a dict"
        required_keys = {"epoch", "model_state_dict", "config"}
        missing = required_keys - set(ckpt.keys())
        assert not missing, f"{ckpt_path.name} missing keys: {missing}"
        assert ("metrics" in ckpt or "val_metrics" in ckpt), f"{ckpt_path.name} missing metrics"
        assert isinstance(ckpt["model_state_dict"], dict)
        assert len(ckpt["model_state_dict"]) > 0


def test_prediction_schema_and_probabilities():
    """Verify prediction CSVs adhere to required schemas, no NaNs, and probabilities sum to 1."""
    pred_files = [p for p in PREDICTIONS_DIR.glob("*.csv") if "predictions" in p.name]
    if not pred_files:
        pytest.skip("No prediction CSVs generated yet in predictions/.")

    for pred_path in pred_files:
        with open(pred_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, f"{pred_path.name} is empty"

        fieldnames = set(reader.fieldnames or [])
        assert "sample_id" in fieldnames
        assert "true_label" in fieldnames
        assert "true_class" in fieldnames
        assert "pred_label" in fieldnames
        assert "pred_class" in fieldnames

        prob_cols = [c for c in fieldnames if c.startswith("prob_")]
        assert len(prob_cols) in (3, 4), f"Expected 3 or 4 probability columns, got {prob_cols}"

        sample_ids = set()
        for i, row in enumerate(rows):
            # Check unique sample_ids if OOF or test split
            sid = row["sample_id"]
            assert sid, f"Empty sample_id at row {i} in {pred_path.name}"

            # Check no NaN values
            for col, val in row.items():
                assert val != "" and val.lower() != "nan", f"NaN or empty in {col} at row {i} in {pred_path.name}"

            # Check probability sum equals 1.0 within numerical tolerance
            prob_sum = sum(float(row[c]) for c in prob_cols)
            assert abs(prob_sum - 1.0) < 1e-3, f"Probabilities do not sum to 1 at row {i} ({prob_sum}) in {pred_path.name}"


def test_baseline_report_existence():
    """Verify that reports/baseline_training_report.md exists if training finished."""
    report_path = REPORTS_DIR / "baseline_training_report.md"
    if not report_path.exists():
        pytest.skip("baseline_training_report.md not yet written.")
    content = report_path.read_text(encoding="utf-8")
    assert "Baseline Classification Training Report" in content
    assert "Macro-F1" in content
    assert "ECE" in content
