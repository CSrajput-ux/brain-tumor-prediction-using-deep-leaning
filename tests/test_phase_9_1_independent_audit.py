import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_9_DIR = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement'
AUDIT_DIR = ROOT / 'experiments' / 'phase_9_1_independent_audit'


def test_phase_9_1_required_artifacts_exist():
    """Verify all 9 required Phase 9.1 deliverables exist and are non-empty."""
    required = [
        'PHASE_9_1_AUDIT_REPORT.md',
        'canonical_metrics_recalculated.csv',
        'canonical_contrasts_recalculated.csv',
        'bootstrap_reproduction.csv',
        'mcnemar_reproduction.csv',
        'contrast_sign_audit.csv',
        'intervention_validity_reassessment.md',
        'claim_evidence_matrix.csv',
        'checksums.json'
    ]
    for fname in required:
        fpath = AUDIT_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"


def test_phase_9_1_checksum_integrity():
    """Verify recorded SHA-256 hashes in checksums.json match files on disk."""
    with open(AUDIT_DIR / 'checksums.json', 'r') as f:
        recorded = json.load(f)
    for fname, meta in recorded.items():
        if fname in ['test_results.txt', 'checksums.json']:
            continue
        fpath = AUDIT_DIR / fname
        assert fpath.exists(), f"File {fname} does not exist!"
        h = hashlib.sha256()
        with open(fpath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        assert h.hexdigest() == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fpath.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"


def test_phase_9_1_metrics_recalculation_fidelity():
    """Verify independent recalculation matches reported Phase 9 primary metrics exactly."""
    recalc = pd.read_csv(AUDIT_DIR / 'canonical_metrics_recalculated.csv')
    orig = pd.read_csv(PHASE_9_DIR / 'primary_metrics.csv')
    
    assert len(recalc) == len(orig) == 12
    max_diff = np.abs(recalc['macro_f1'].values - orig['macro_f1'].values).max()
    assert max_diff < 1e-10, f"Macro-F1 discrepancy {max_diff} exceeds tolerance!"


def test_phase_9_1_bootstrap_reproduction_fidelity():
    """Verify bootstrap reproduction matches Phase 9 confidence intervals within tolerance."""
    boot = pd.read_csv(AUDIT_DIR / 'bootstrap_reproduction.csv')
    assert len(boot) == 15
    assert (boot['ci_match_within_tolerance'] == True).all(), "Some bootstrap CIs did not reproduce!"


def test_phase_9_1_contrast_sign_audit_integrity():
    """Verify contrast sign directions and audit reconciliation notes."""
    sign_df = pd.read_csv(AUDIT_DIR / 'contrast_sign_audit.csv')
    assert len(sign_df) == 15
    
    # Check C3 vs C2 specifically
    c3_c2_s0 = sign_df[(sign_df['scenario'] == 'S0') & (sign_df['contrast_id'] == 'C3_vs_C2')].iloc[0]
    assert c3_c2_s0['canonical_signed_diff'] < 0, "Expected negative signed diff for C3 vs C2 in S0"
    assert "C2 (seam-suppressed scramble) experienced a GREATER performance drop" in c3_c2_s0['audit_reconciliation_notes']


def test_phase_9_1_gate_decision_in_report():
    """Verify final audit gate decision is PASS-WITH-LIMITATIONS."""
    report_text = (AUDIT_DIR / 'PHASE_9_1_AUDIT_REPORT.md').read_text(encoding='utf-8')
    assert "PASS-WITH-LIMITATIONS" in report_text
    assert "72% Explained by Seams" in report_text
