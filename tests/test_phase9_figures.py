"""Phase 9 unit and validation tests: Publication figures verification."""
from __future__ import annotations

from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "figures"


def test_all_10_figures_exist_and_valid() -> None:
    expected_figures = [
        "fig1_study_design.png",
        "fig2_preprocessing_alignment.png",
        "fig3_calibration_reliability.png",
        "fig4_regional_evidence_effects.png",
        "fig5_architecture_comparison.png",
        "fig6_method_robustness.png",
        "fig7_plane_stratification.png",
        "fig8_class_heterogeneity.png",
        "fig9_brisc_leakage_artifact.png",
        "fig10_intervention_gallery.png",
    ]

    for fname in expected_figures:
        fpath = FIGURES_DIR / fname
        assert fpath.exists(), f"Figure {fname} is missing"
        size = fpath.stat().st_size
        assert size > 10_000, f"Figure {fname} is abnormally small ({size} bytes)"

        # Check PNG header
        with open(fpath, "rb") as f:
            header = f.read(8)
            assert header == b"\x89PNG\r\n\x1a\n", f"Invalid PNG magic bytes in {fname}"

