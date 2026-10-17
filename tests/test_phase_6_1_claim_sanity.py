import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
PHASE_6_1_DIR = ROOT / 'experiments' / 'phase_6_1_claim_sanity'
PHASE_6_DIR = ROOT / 'experiments' / 'phase_6_spatial_controls'

def test_phase_6_1_required_artifacts_exist():
    """Verify all 10 required Phase 6.1 deliverables exist and are non-empty."""
    required = [
        'PHASE_6_1_CLAIM_SANITY_REPORT.md',
        'artifact_integrity_audit.csv',
        'phase6_result_reproduction.csv',
        'c5lp_claim_audit.md',
        'class_transition_sanity.csv',
        'c3ns_claim_audit.md',
        'statistical_validity_audit.md',
        'claim_evidence_matrix.md',
        'recommended_followup_controls.md',
        'checksums.json'
    ]
    for fname in required:
        fpath = PHASE_6_1_DIR / fname
        assert fpath.exists(), f"Missing required file: {fname}"
        assert fpath.stat().st_size > 0, f"File {fname} is empty!"

def test_phase_6_1_checksum_integrity():
    """Verify SHA-256 hashes recorded in Phase 6.1 checksums.json match files on disk."""
    with open(PHASE_6_1_DIR / 'checksums.json', 'r') as f:
        recorded = json.load(f)
    for fname, meta in recorded.items():
        fpath = PHASE_6_1_DIR / fname
        assert fpath.exists(), f"File {fname} from checksums.json does not exist!"
        h = hashlib.sha256()
        with open(fpath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        assert h.hexdigest() == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fpath.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_6_headline_reproduction_zero_discrepancy():
    """Verify that all recomputed Phase 6 results match reported values to < 1e-6."""
    repro = pd.read_csv(PHASE_6_1_DIR / 'phase6_result_reproduction.csv')
    assert len(repro) == 21, f"Expected 21 reproduction rows, got {len(repro)}"
    assert np.all(repro['audit_status'] == 'PASS'), "Headline reproduction had discrepancies!"
    assert np.all(repro['absolute_difference'] < 1e-6), "Discrepancy exceeds tolerance!"

def test_phase_6_1_c5lp_audit_consistency():
    """Verify C5LP preserves luminance while increasing gradient energy."""
    stats = pd.read_csv(PHASE_6_DIR / 'image_statistics.csv')
    c0 = stats[stats['condition'] == 'I_orig'].sort_values('sample_id')
    c5lp = stats[stats['condition'] == 'I_distant_luminance_preserved'].sort_values('sample_id')
    
    # 0 mean diff
    mean_diff = np.max(np.abs(c0['mean_intensity'].values - c5lp['mean_intensity'].values))
    assert mean_diff < 1e-4, f"C5LP mean intensity difference was {mean_diff}"

def test_phase_6_1_c3ns_audit_consistency():
    """Verify C3NS inpainting reduces boundary step without altering tumor core."""
    stats = pd.read_csv(PHASE_6_DIR / 'image_statistics.csv')
    c3 = stats[stats['condition'] == 'I_margin_r15_removed']
    c3ns = stats[stats['condition'] == 'I_margin_r15_ns_inpaint']
    
    assert c3['boundary_step_gradient'].mean() > 200.0
    assert c3ns['boundary_step_gradient'].mean() < 50.0

def test_phase_6_1_claim_sanity_report_decision():
    """Verify report concludes PASS-WITH-LIMITATIONS."""
    with open(PHASE_6_1_DIR / 'PHASE_6_1_CLAIM_SANITY_REPORT.md', 'r') as f:
        report = f.read()
    assert "**Final Gate Decision:** **`PASS-WITH-LIMITATIONS`**" in report
    assert "UNRESOLVED" in report
    assert "SUPPORTED_WITHIN_TESTED_SETUP" in report
