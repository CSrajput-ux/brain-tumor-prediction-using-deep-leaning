"""Phase 7 unit and validation tests: Counterfactual sensitivity estimands, biostatistics, and audit output."""
from __future__ import annotations

import csv
from pathlib import Path
import numpy as np
import pytest
import torch

from src.interventions.audit import compute_paired_stats, evaluate_counterfactual_sensitivity
from src.models import build_model

ROOT = Path(__file__).resolve().parents[1]


def test_paired_biostatistical_stats() -> None:
    # Array with clear positive shift
    np.random.seed(42)
    x = np.array([0.5, 0.6, 0.55, 0.7, 0.65, 0.8, 0.75])
    y = np.array([0.1, 0.15, 0.12, 0.2, 0.18, 0.22, 0.19])

    stats_res = compute_paired_stats(x, y)
    assert stats_res["p_value"] < 0.05, f"Expected significant p-value, got {stats_res['p_value']}"
    assert stats_res["cohens_d"] > 2.0, f"Expected large effect size, got {stats_res['cohens_d']}"
    assert stats_res["mean_diff"] == pytest.approx(float(np.mean(x - y)))


def test_sensitivity_estimand_logic() -> None:
    # Dummy model returning deterministic probabilities
    model = build_model("resnet50", num_classes=3, pretrained=False)
    device = torch.device("cpu")

    img = np.full((224, 224), 0.5, dtype=np.float32)
    edited_imgs = {
        "core_method_a": np.full((224, 224), 0.1, dtype=np.float32),
        "sham_method_a": np.full((224, 224), 0.4, dtype=np.float32),
    }

    records = evaluate_counterfactual_sensitivity(
        model, device, img, edited_imgs, true_class_id=0, class_names=["cls0", "cls1", "cls2"]
    )

    assert len(records) == 2
    rec_by_reg = {r["region"]: r for r in records}

    assert "core" in rec_by_reg
    assert "sham" in rec_by_reg

    core_rec = rec_by_reg["core"]
    sham_rec = rec_by_reg["sham"]

    # tau_sham must be 0 by definition
    assert sham_rec["tau_sham_corrected"] == 0.0
    # tau_core must equal delta_core - delta_sham
    expected_tau = core_rec["delta_raw"] - sham_rec["delta_raw"]
    assert core_rec["tau_sham_corrected"] == pytest.approx(expected_tau, abs=1e-5)
    assert isinstance(core_rec["is_flipped"], bool)


def test_audit_artifacts_if_present() -> None:
    csv_path = ROOT / "predictions" / "intervention_effects.csv"
    if not csv_path.exists():
        pytest.skip("intervention_effects.csv not yet generated.")

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0, "intervention_effects.csv is empty"
    fieldnames = set(reader.fieldnames or [])

    required = {
        "sample_id", "dataset", "architecture", "plane", "true_class",
        "region", "method", "base_true_prob", "edit_true_prob",
        "delta_raw", "delta_sham", "tau_sham_corrected", "is_flipped",
    }
    missing = required - fieldnames
    assert not missing, f"Missing columns in intervention_effects.csv: {missing}"

    for r in rows:
        assert r["region"] in {"core", "immediate", "outer", "remote", "sham"}
        assert r["method"] in {"telea_inpaint", "matched_texture_fill"}
        assert -1.0 <= float(r["delta_raw"]) <= 1.0
        assert not np.isnan(float(r["tau_sham_corrected"]))
