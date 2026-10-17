import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_9_DIR = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement'
PHASE_9_2_DIR = ROOT / 'experiments' / 'phase_9_2_manuscript_readiness'


def test_phase_9_2_required_artifacts_exist():
    """Verify all 9 required Phase 9.2 deliverables exist and are non-empty."""
    required = [
        'PHASE_9_2_READINESS_REPORT.md',
        'prediction_accounting.csv',
        'canonical_contrasts.csv',
        'statistical_audit.csv',
        'intervention_validity_matrix.csv',
        'claim_evidence_matrix.csv',
        'preregistration_deviation_log.md',
        'reproducibility_manifest.json',
        'manuscript_claims_allowed.md'
    ]
    for fname in required:
        fpath = PHASE_9_2_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"


def test_phase_9_2_prediction_accounting_integrity():
    """Verify prediction accounting: 15 checkpoints, 60 subsets, 3064 slices per scenario-condition."""
    acct = pd.read_csv(PHASE_9_2_DIR / 'prediction_accounting.csv')
    assert len(acct) == 60  # 3 scenarios * 5 folds * 4 conditions = 60
    assert acct['checkpoint_sha256'].nunique() == 15, "Expected 15 unique checkpoint hashes"
    
    # Check that out-of-fold sample counts sum to 3064 per scenario-condition
    for sc in ['S0', 'S1', 'S2']:
        for cond in ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']:
            sub = acct[(acct['scenario'] == sc) & (acct['condition'] == cond)]
            assert sub['test_fold_sample_count'].sum() == 3064, f"Sum mismatch for {sc} {cond}"
            assert sub['duplicate_records_count'].sum() == 0, f"Duplicates found for {sc} {cond}"


def test_phase_9_2_canonical_contrasts_fidelity():
    """Verify canonical contrasts calculation and fold standard deviations."""
    contrasts = pd.read_csv(PHASE_9_2_DIR / 'canonical_contrasts.csv')
    assert len(contrasts) == 15
    
    # Verify Holm FWER status
    c2_s0 = contrasts[(contrasts['scenario'] == 'S0') & (contrasts['contrast_id'] == 'C2_vs_C0')].iloc[0]
    assert c2_s0['signed_difference_A_minus_B'] > 0.40
    assert c2_s0['fold_std'] < 0.05, f"Fold std unexpectedly high: {c2_s0['fold_std']}"
    assert "REJECT_H0" in c2_s0['holm_fwer_status']


def test_phase_9_2_intervention_validity_matrix_invariants():
    """Verify 0 altered pixels in core and margin across all conditions."""
    matrix = pd.read_csv(PHASE_9_2_DIR / 'intervention_validity_matrix.csv')
    assert len(matrix) == 4
    for idx, row in matrix.iterrows():
        assert row['tumor_pixels_altered'] == 0, f"Tumor pixels altered in {row['condition_id']}"
        assert row['margin_pixels_altered'] == 0, f"Margin pixels altered in {row['condition_id']}"


def test_phase_9_2_gate_verdict_in_report():
    """Verify gate verdict is READY-WITH-LIMITATIONS."""
    report = (PHASE_9_2_DIR / 'PHASE_9_2_READINESS_REPORT.md').read_text(encoding='utf-8')
    assert "READY-WITH-LIMITATIONS" in report
    assert "Resolution of Prediction Accounting" in report
