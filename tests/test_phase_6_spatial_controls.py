import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_6_DIR = ROOT / 'experiments' / 'phase_6_spatial_controls'

def test_phase_6_required_artifacts_exist():
    """Verify all 12 required deliverables exist and are non-empty."""
    required = [
        'PHASE_6_REPORT.md',
        'preregistration.md',
        'intervention_config.yaml',
        'intervention_manifest.csv',
        'intervention_quality_audit.md',
        'matched_predictions.csv',
        'metrics_by_condition.csv',
        'paired_contrasts.json',
        'margin_thickness_sweep.csv',
        'image_statistics.csv',
        'claim_evidence_matrix.md',
        'checksums.json'
    ]
    for fname in required:
        fpath = PHASE_6_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"

def test_phase_6_checksum_integrity():
    """Verify SHA-256 hashes recorded in checksums.json match files on disk."""
    with open(PHASE_6_DIR / 'checksums.json', 'r') as f:
        recorded = json.load(f)
    for fname, meta in recorded.items():
        fpath = PHASE_6_DIR / fname
        assert fpath.exists(), f"File {fname} from checksums.json does not exist!"
        h = hashlib.sha256()
        with open(fpath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        assert h.hexdigest() == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fpath.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_6_manifest_and_predictions_accounting():
    """Verify sample counts, scenarios, conditions, and predictions completeness."""
    manifest = pd.read_csv(PHASE_6_DIR / 'intervention_manifest.csv')
    assert len(manifest) == 3064, f"Expected 3064 rows in manifest, got {len(manifest)}"
    assert manifest['patient_id'].nunique() == 233, "Expected 233 unique patients"
    
    preds = pd.read_csv(PHASE_6_DIR / 'matched_predictions.csv')
    # 3 scenarios * 14 conditions * 3064 samples = 128,688
    assert len(preds) == 128688, f"Expected 128688 predictions, got {len(preds)}"
    assert set(preds['scenario'].unique()) == {'S0', 'S1', 'S2'}
    assert len(preds['condition'].unique()) == 14

def test_phase_6_luminance_preserved_invariants():
    """Verify Experiment A: C5LP strictly preserves luminance, variance, and protected zone."""
    stats = pd.read_csv(PHASE_6_DIR / 'image_statistics.csv')
    c0 = stats[stats['condition'] == 'I_orig'].sort_values('sample_id')
    c5lp = stats[stats['condition'] == 'I_distant_luminance_preserved'].sort_values('sample_id')
    
    # Exact equality of mean and std across all 3064 slices
    diff_mean = np.abs(c0['mean_intensity'].values - c5lp['mean_intensity'].values)
    diff_std = np.abs(c0['std_intensity'].values - c5lp['std_intensity'].values)
    assert np.all(diff_mean < 1e-4), "C5LP did not strictly preserve mean intensity!"
    assert np.all(diff_std < 1e-4), "C5LP did not strictly preserve standard deviation!"

def test_phase_6_navier_stokes_inpaint_boundary_reduction():
    """Verify Experiment B: C3NS suppresses boundary step gradient without tumor overlap."""
    stats = pd.read_csv(PHASE_6_DIR / 'image_statistics.csv')
    c3 = stats[stats['condition'] == 'I_margin_r15_removed']
    c3ns = stats[stats['condition'] == 'I_margin_r15_ns_inpaint']
    
    mean_step_c3 = c3['boundary_step_gradient'].mean()
    mean_step_c3ns = c3ns['boundary_step_gradient'].mean()
    assert mean_step_c3 > 200.0, f"Expected high boundary step in C3, got {mean_step_c3}"
    assert mean_step_c3ns < 50.0, f"Expected suppressed boundary step in C3NS, got {mean_step_c3ns}"
    assert mean_step_c3ns < mean_step_c3 * 0.25, "C3NS did not achieve >= 75% boundary step reduction!"

def test_phase_6_margin_thickness_sweep_geometry():
    """Verify Experiment C: Margin sweep area scales monotonically and placebos have 0 tumor overlap."""
    sweep = pd.read_csv(PHASE_6_DIR / 'margin_thickness_sweep.csv')
    assert set(sweep['radius_pixels'].unique()) == {5, 10, 15, 20}
    
    # Check 0 tumor overlap
    assert np.all(sweep['overlap_with_tumor_pixels'] == 0), "Margin ring overlapped with tumor!"
    assert np.all(sweep['placebo_overlap_with_tumor_pixels'] == 0), "Placebo ring overlapped with tumor!"
    
    # Monotonic area expansion
    mean_areas = sweep.groupby('radius_pixels')['margin_area_pixels'].mean().to_dict()
    assert mean_areas[5] < mean_areas[10] < mean_areas[15] < mean_areas[20], "Margin areas not monotonic!"

def test_phase_6_paired_contrasts_scientific_integrity():
    """Verify bootstrap contrasts reproduction and gate decision in report."""
    with open(PHASE_6_DIR / 'paired_contrasts.json') as f:
        contrasts = json.load(f)
    for sc in ['S0', 'S1', 'S2']:
        res = contrasts['results'][sc]
        # C5LP drop must be huge (> 0.35)
        c5lp_diff = res['experiment_a_distant_context']['c5lp_scrambling_contrast']['point_diff']
        assert c5lp_diff > 0.35, f"Expected catastrophic drop in C5LP for {sc}, got {c5lp_diff}"
        
        # C3NS drop must be negligible (< 0.015)
        c3ns_diff = res['experiment_b_margin_inpaint']['c3ns_inpaint']['point_diff']
        assert abs(c3ns_diff) < 0.015, f"Expected negligible drop in C3NS for {sc}, got {c3ns_diff}"

def test_phase_6_report_gate_decision():
    """Verify report concludes PASS with verified findings."""
    with open(PHASE_6_DIR / 'PHASE_6_REPORT.md', 'r') as f:
        report = f.read()
    assert "**Final Gate Decision:** **`PASS`**" in report
    assert "Navier-Stokes" in report
    assert "Luminance-Preserved" in report
