"""Phase 8 unit and validation tests: Secondary experiments, replication, and robustness audit."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
PREDICTIONS_DIR = ROOT / "predictions"


def test_secondary_robustness_report_content() -> None:
    rep_path = REPORTS_DIR / "secondary_robustness_report.md"
    if not rep_path.exists():
        pytest.skip("secondary_robustness_report.md not yet written.")

    content = rep_path.read_text(encoding="utf-8")
    assert "Secondary Experiments, Replication & Robustness Analysis" in content
    assert "Architectural Inductive Bias: ResNet-50 (CNN) vs DeiT-Small (ViT)" in content
    assert "Perturbation Engine Invariance: Method A (Inpainting) vs Method B (Texture Fill)" in content
    assert "Imaging-Plane Stratification (BRISC)" in content
    assert "Lesion Boundary Biology & Class Heterogeneity" in content
    assert "Duplicate Leakage Impact Summary" in content


def test_plane_stratification_completeness() -> None:
    csv_path = PREDICTIONS_DIR / "intervention_effects.csv"
    if not csv_path.exists():
        pytest.skip("intervention_effects.csv not yet written.")

    df = pd.read_csv(csv_path)
    brisc_df = df[df["dataset"] == "brisc"]

    planes = set(brisc_df["plane"].unique())
    assert {"axial", "coronal", "sagittal"}.issubset(planes), f"Missing planes in BRISC audit: {planes}"

    for plane in ["axial", "coronal", "sagittal"]:
        plane_count = len(brisc_df[brisc_df["plane"] == plane])
        assert plane_count > 0, f"No samples found for plane: {plane}"


def test_region_decay_hypothesis() -> None:
    csv_path = PREDICTIONS_DIR / "intervention_effects.csv"
    if not csv_path.exists():
        pytest.skip("intervention_effects.csv not yet written.")

    df = pd.read_csv(csv_path)
    # Overall core sensitivity must be greater than remote sensitivity
    mean_core_tau = df[df["region"] == "core"]["tau_sham_corrected"].mean()
    mean_remote_tau = df[df["region"] == "remote"]["tau_sham_corrected"].mean()

    assert mean_core_tau > mean_remote_tau, f"Expected Core tau ({mean_core_tau:.4f}) > Remote tau ({mean_remote_tau:.4f})"

