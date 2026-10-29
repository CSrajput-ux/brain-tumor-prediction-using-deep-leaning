"""Phase 6 unit and validation tests: Counterfactual intervention engine, region geometry, inpainting, and QC audit."""
from __future__ import annotations

import numpy as np
import pytest

from src.interventions.inpainting import fill_region_matched_texture, inpaint_region_telea
from src.interventions.quality_metrics import compute_intervention_quality
from src.interventions.regions import extract_tissue_mask, generate_regions


@pytest.fixture
def synthetic_mri() -> tuple[np.ndarray, np.ndarray]:
    """Create synthetic cranial MRI slice with elliptical skull/brain and circular tumor."""
    h, w = 224, 224
    img = np.zeros((h, w), dtype=np.float32)

    # Intracranial parenchyma ellipse
    yy, xx = np.ogrid[:h, :w]
    brain_mask = ((xx - 112) ** 2 / 70 ** 2 + (yy - 112) ** 2 / 85 ** 2) <= 1.0
    img[brain_mask] = 0.55

    # Tumor core in left hemisphere
    tumor_mask = ((xx - 80) ** 2 + (yy - 100) ** 2) <= 14 ** 2
    tumor_mask_u8 = (tumor_mask & brain_mask).astype(np.uint8)
    img[tumor_mask_u8 > 0] = 0.90  # Contrast hyperintensity

    return img, tumor_mask_u8


def test_tissue_mask_extraction(synthetic_mri: tuple[np.ndarray, np.ndarray]) -> None:
    img, _ = synthetic_mri
    tissue = extract_tissue_mask(img, min_intensity=0.1)

    assert tissue.shape == img.shape
    assert set(np.unique(tissue)).issubset({0, 1})
    assert np.count_nonzero(tissue) > 5000
    # Background corners must be 0
    assert tissue[5, 5] == 0
    assert tissue[112, 112] == 1


def test_region_generation_exclusivity(synthetic_mri: tuple[np.ndarray, np.ndarray]) -> None:
    img, tumor_mask = synthetic_mri
    regions = generate_regions(tumor_mask, img, d1=4, d2=16)

    core = regions["core"]
    immediate = regions["immediate"]
    outer = regions["outer"]
    sham = regions["sham"]
    remote = regions["remote"]

    # Binary integrity
    for name, r in [("core", core), ("immediate", immediate), ("outer", outer), ("sham", sham), ("remote", remote)]:
        assert set(np.unique(r)).issubset({0, 1}), f"{name} is not binary"

    # All non-empty
    assert np.count_nonzero(core) > 0, "Core is empty"
    assert np.count_nonzero(immediate) > 0, "Immediate margin is empty"
    assert np.count_nonzero(outer) > 0, "Outer margin is empty"
    assert np.count_nonzero(sham) > 0, "Sham control is empty"
    assert np.count_nonzero(remote) > 0, "Remote patch is empty"

    # Strict pairwise non-overlap guarantees
    assert np.count_nonzero(core & immediate) == 0, "Core overlaps immediate"
    assert np.count_nonzero(core & outer) == 0, "Core overlaps outer"
    assert np.count_nonzero(immediate & outer) == 0, "Immediate overlaps outer"
    assert np.count_nonzero(core & sham) == 0, "Core overlaps sham"
    assert np.count_nonzero(immediate & sham) == 0, "Immediate overlaps sham"
    assert np.count_nonzero(outer & sham) == 0, "Outer overlaps sham"


def test_inpainting_telea_preservation(synthetic_mri: tuple[np.ndarray, np.ndarray]) -> None:
    img, tumor_mask = synthetic_mri
    regions = generate_regions(tumor_mask, img)
    core = regions["core"]

    edited = inpaint_region_telea(img, core, inpaint_radius=3, method="telea")

    assert edited.shape == img.shape
    assert edited.dtype == np.float32

    # Bitwise non-target pixel preservation
    non_target = (core == 0)
    np.testing.assert_allclose(edited[non_target], img[non_target], atol=1e-5)

    # Inpainted target must have changed
    target = (core > 0)
    assert not np.allclose(edited[target], img[target])

    # Quality control audit
    qc = compute_intervention_quality(img, edited, core)
    assert qc["passed_qc"] is True
    assert qc["is_valid_preservation"] is True
    assert qc["max_diff_outside"] <= 1e-5
    assert qc["mad_inside"] > 0.05


def test_texture_fill_preservation(synthetic_mri: tuple[np.ndarray, np.ndarray]) -> None:
    img, tumor_mask = synthetic_mri
    regions = generate_regions(tumor_mask, img)
    core = regions["core"]

    edited = fill_region_matched_texture(img, core, tissue_mask=regions["tissue_mask"], feather_radius=2, seed=42)

    assert edited.shape == img.shape
    non_target = (core == 0)
    np.testing.assert_allclose(edited[non_target], img[non_target], atol=1e-5)

    qc = compute_intervention_quality(img, edited, core)
    assert qc["passed_qc"] is True
    assert qc["max_diff_outside"] <= 1e-5


def test_qc_flags_external_corruption(synthetic_mri: tuple[np.ndarray, np.ndarray]) -> None:
    img, tumor_mask = synthetic_mri
    corrupted = img.copy()
    corrupted[10, 10] = 0.99  # Corrupt a non-mask background pixel

    qc = compute_intervention_quality(img, corrupted, tumor_mask)
    assert qc["is_valid_preservation"] is False
    assert qc["passed_qc"] is False
    assert qc["max_diff_outside"] > 0.1



def test_intervention_qc_manifest_and_montages() -> None:
    from pathlib import Path
    import pandas as pd

    root = Path(__file__).resolve().parents[1]
    qc_csv = root / "manifests" / "intervention_qc.csv"
    assert qc_csv.exists(), "intervention_qc.csv does not exist"

    df = pd.read_csv(qc_csv)
    assert len(df) == 1200, f"Expected 1200 records, got {len(df)}"

    required_cols = {
        "sample_id", "dataset", "class_label", "region", "method",
        "mask_pixels", "max_diff_outside", "mean_diff_outside",
        "mad_inside", "rmsd_inside", "intensity_shift",
        "boundary_discontinuity", "passed_qc", "plane",
    }
    missing = required_cols - set(df.columns)
    assert not missing, f"Missing columns in intervention_qc.csv: {missing}"

    # Strict outside preservation: all max_diff_outside <= 1e-5
    assert (df["max_diff_outside"] <= 1e-5).all(), "Found non-target pixel corruption"

    # All pass QC
    assert (df["passed_qc"] == True).all(), "Some interventions failed QC"

    # Montages exist
    montage_dir = root / "reports" / "intervention_montages"
    assert montage_dir.exists()
    montages = list(montage_dir.glob("*.png"))
    assert len(montages) == 24, f"Expected 24 montages, got {len(montages)}"

    # Report exists
    rep = root / "reports" / "intervention_qc_report.md"
    assert rep.exists()
    content = rep.read_text(encoding="utf-8")
    assert "Counterfactual Intervention Generation & Quality-Control Report" in content
    assert "100.00%" in content
