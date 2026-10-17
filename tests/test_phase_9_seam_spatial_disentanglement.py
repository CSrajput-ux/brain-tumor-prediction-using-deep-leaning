import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_9_DIR = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement'


def test_phase_9_required_artifacts_exist():
    """Verify all 19 required Phase 9 deliverables exist and are non-empty."""
    required = [
        'PHASE_9_FINAL_REPORT.md',
        'preregistration_verification.md',
        'experiment_config.yaml',
        'condition_definitions.md',
        'intervention_validity_audit.csv',
        'image_statistics.csv',
        'condition_visual_audit.pdf',
        'condition_visual_audit_contact_sheet.png',
        'matched_predictions.csv',
        'primary_metrics.csv',
        'paired_contrasts.csv',
        'class_transition_analysis.csv',
        'patient_level_effects.csv',
        'bootstrap_results.csv',
        'statistical_validity_report.md',
        'claim_evidence_matrix.md',
        'limitations_and_failure_modes.md',
        'checksums.json',
        'execution_log.txt'
    ]
    for fname in required:
        fpath = PHASE_9_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"


def test_phase_9_checksum_integrity():
    """Verify recorded SHA-256 hashes in checksums.json match files on disk."""
    with open(PHASE_9_DIR / 'checksums.json', 'r') as f:
        recorded = json.load(f)
    for fname, meta in recorded.items():
        if fname in ['test_results.txt', 'checksums.json']:
            continue
        fpath = PHASE_9_DIR / fname
        assert fpath.exists(), f"File {fname} does not exist!"
        h = hashlib.sha256()
        with open(fpath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        assert h.hexdigest() == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fpath.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"


def test_phase_9_sample_and_prediction_accounting():
    """Verify sample counts, scenario coverage, conditions, and predictions completeness."""
    # Matched predictions: 3 scenarios * 4 conditions * 3064 slices = 36,768 rows
    preds = pd.read_csv(PHASE_9_DIR / 'matched_predictions.csv')
    assert len(preds) == 36768, f"Expected 36,768 predictions, got {len(preds)}"
    assert set(preds['scenario'].unique()) == {'S0', 'S1', 'S2'}
    assert set(preds['condition'].unique()) == {'C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble'}
    assert preds['patient_id'].nunique() == 233, "Expected 233 unique patients"

    # Image statistics: 4 conditions * 3064 slices = 12,256 rows
    stats = pd.read_csv(PHASE_9_DIR / 'image_statistics.csv')
    assert len(stats) == 12256, f"Expected 12,256 statistics rows, got {len(stats)}"
    assert set(stats['condition'].unique()) == {'C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble'}


def test_phase_9_intervention_invariants():
    """Verify 0 altered pixels in core and margin, and seam suppression efficacy."""
    audit = pd.read_csv(PHASE_9_DIR / 'intervention_validity_audit.csv')
    assert len(audit) == 3064, f"Expected 3064 audit rows, got {len(audit)}"
    
    # 0 pixels altered in tumour core and 15px margin across all conditions
    assert np.all(audit['c1_tumor_altered'] == 0), "C1 altered core pixels!"
    assert np.all(audit['c1_margin_altered'] == 0), "C1 altered margin pixels!"
    assert np.all(audit['c2_tumor_altered'] == 0), "C2 altered core pixels!"
    assert np.all(audit['c2_margin_altered'] == 0), "C2 altered margin pixels!"
    assert np.all(audit['c3_tumor_altered'] == 0), "C3 altered core pixels!"
    assert np.all(audit['c3_margin_altered'] == 0), "C3 altered margin pixels!"
    assert np.all(audit['validity_status'] == 'PASS'), "Non-pass status found!"

    # Seam Sobel energy suppression in C2 relative to C3
    stats = pd.read_csv(PHASE_9_DIR / 'image_statistics.csv')
    c0_seam = stats[stats['condition'] == 'C0_orig']['sobel_energy_seam'].mean()
    c1_seam = stats[stats['condition'] == 'C1_seam_only']['sobel_energy_seam'].mean()
    c2_seam = stats[stats['condition'] == 'C2_seam_suppressed']['sobel_energy_seam'].mean()
    c3_seam = stats[stats['condition'] == 'C3_c5lp_scramble']['sobel_energy_seam'].mean()

    assert c1_seam > 100.0, f"Expected elevated seam Sobel in C1, got {c1_seam}"
    assert c1_seam > c0_seam * 3.0, "C1 did not substantially increase seam Sobel over baseline!"
    assert c3_seam > 115.0, f"Expected high seam Sobel in C3, got {c3_seam}"
    assert c2_seam < 85.0, f"Expected suppressed seam Sobel in C2, got {c2_seam}"
    assert c2_seam < c3_seam * 0.65, "C2 did not suppress seam Sobel by >= 35%!"


def test_phase_9_preregistered_hypothesis_outcomes():
    """Verify primary paired contrasts and preregistered hypothesis criteria."""
    contrasts = pd.read_csv(PHASE_9_DIR / 'paired_contrasts.csv')
    assert len(contrasts) == 15  # 5 contrasts * 3 scenarios

    for sc in ['S0', 'S1', 'S2']:
        sc_c = contrasts[contrasts['scenario'] == sc].set_index('contrast_id')
        
        # 1. Reproduction of C3 vs C0
        c3_drop = sc_c.loc['C3_vs_C0', 'delta_macro_f1']
        assert 0.38 <= c3_drop <= 0.46, f"{sc} C3 drop out of expected range: {c3_drop}"
        assert sc_c.loc['C3_vs_C0', 'ci_2_5'] > 0.30

        # 2. H1: Seam-only effect C1 vs C0 is statistically significant
        c1_drop = sc_c.loc['C1_vs_C0', 'delta_macro_f1']
        assert 0.25 <= c1_drop <= 0.35, f"{sc} C1 drop out of expected range: {c1_drop}"
        assert sc_c.loc['C1_vs_C0', 'ci_2_5'] > 0.20
        assert sc_c.loc['C1_vs_C0', 'mcnemar_p_value'] < 1e-10

        # 3. H2: Seam-suppressed rearrangement effect C2 vs C0 >= 0.150
        c2_drop = sc_c.loc['C2_vs_C0', 'delta_macro_f1']
        assert c2_drop >= 0.150, f"{sc} C2 drop did not meet threshold 0.150: {c2_drop}"
        assert sc_c.loc['C2_vs_C0', 'ci_2_5'] > 0.30

        # 4. H3: Scrambling is significantly worse than seams alone (C3 vs C1 > 0)
        c3_vs_c1 = sc_c.loc['C3_vs_C1', 'delta_macro_f1']
        assert c3_vs_c1 > 0.08, f"{sc} C3 vs C1 difference too small: {c3_vs_c1}"
        assert sc_c.loc['C3_vs_C1', 'ci_2_5'] > 0.05
