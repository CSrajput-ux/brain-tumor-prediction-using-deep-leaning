"""
Automated unit and validation test suite for Phase 5.1 — Spatial Intervention Validity Audit.
"""
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / 'experiments' / 'phase_5_1_spatial_validity'
P5_DIR = ROOT / 'experiments' / 'phase_5_context_reliance'

def test_phase_5_1_required_artifacts_exist():
    """Verify that all Phase 5.1 audit deliverables exist and are non-empty."""
    required = [
        'SPATIAL_VALIDITY_AUDIT.md',
        'artifact_provenance_audit.csv',
        'distant_intervention_geometry.csv',
        'margin_intervention_geometry.csv',
        'intervention_image_statistics.csv',
        'recomputed_paired_contrasts.json',
        'pituitary_class_reanalysis.csv',
        'claim_evidence_matrix.md',
        'additional_control_recommendations.md',
        'checksums.json'
    ]
    for r in required:
        fp = AUDIT_DIR / r
        assert fp.exists(), f"Phase 5.1 deliverable missing: {r}"
        assert fp.stat().st_size > 0, f"Phase 5.1 deliverable is empty: {r}"

def test_phase_5_1_checksum_integrity():
    """Verify cryptographic hash integrity of all Phase 5.1 files."""
    with open(AUDIT_DIR / 'checksums.json') as f:
        manifest = json.load(f)
        
    for fname, meta in manifest.items():
        fp = AUDIT_DIR / fname
        assert fp.exists(), f"File in checksums does not exist: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        assert actual_sha == meta['sha256'], f"Checksum mismatch for {fname}"
        assert fp.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_5_1_provenance_audit_all_pass():
    """Verify all 26 provenance and artifact integrity checks in Audit A passed."""
    df = pd.read_csv(AUDIT_DIR / 'artifact_provenance_audit.csv')
    assert len(df) >= 26
    assert (df['status'] == 'PASS').all(), f"Failed checks: {df[df['status'] != 'PASS'].to_dict('records')}"

def test_phase_5_1_spatial_geometry_invariants():
    """Verify spatial geometry invariants from Audit B."""
    dist_df = pd.read_csv(AUDIT_DIR / 'distant_intervention_geometry.csv')
    assert len(dist_df) == 3064
    assert dist_df['tumor_preserved_exact'].all(), "Tumor pixels were unexpectedly modified in C5"
    assert dist_df['margin_preserved_exact'].all(), "Margin pixels were unexpectedly modified in C5"
    
    marg_df = pd.read_csv(AUDIT_DIR / 'margin_intervention_geometry.csv')
    assert len(marg_df) == 3064
    assert (marg_df['margin_c3_tumor_overlap'] == 0).all(), "C3 margin overlaps with tumor"
    assert (marg_df['placebo_c4_tumor_overlap'] == 0).all(), "C4 placebo margin overlaps with tumor"
    assert marg_df['margin_area_ratio_c4_vs_c3'].mean() > 0.90, "Placebo margin area mismatch"

def test_phase_5_1_image_statistics_integrity():
    """Verify intensity statistics and boundary gradient steps from Audit C."""
    stat_df = pd.read_csv(AUDIT_DIR / 'intervention_image_statistics.csv')
    assert len(stat_df) == 3064 * 7
    
    means = stat_df.groupby('condition')['mean_intensity'].mean()
    assert means['C5_I_distant_perturbed'] < 25.0, "C5 did not exhibit expected global intensity drop"
    assert means['C0_I_orig'] > 35.0
    
    grads = stat_df.groupby('condition')['boundary_gradient_step'].mean()
    assert grads['C3_I_margin_removed'] > 200.0, "C3 expected sharp boundary step discontinuity"
    assert grads['C6_I_margin_feathered'] < 50.0, "C6 expected smooth boundary infill"

def test_phase_5_1_statistical_reproduction_exact_match():
    """Verify that recomputed paired contrasts match Phase 5 exactly within float precision."""
    with open(AUDIT_DIR / 'recomputed_paired_contrasts.json') as f:
        recomputed = json.load(f)
    with open(P5_DIR / 'paired_contrasts.json') as f:
        original = json.load(f)
        
    for sc in ['S0', 'S1', 'S2']:
        for cname in ['Delta_tumor_removed', 'Delta_placebo_focal', 'Delta_margin_removed', 'Delta_margin_placebo', 'Delta_distant_perturbed', 'Delta_margin_feathered']:
            pt_rec = recomputed[sc]['contrasts'][cname]['point']
            pt_orig = original[sc]['contrasts'][cname]['point']
            assert abs(pt_rec - pt_orig) < 1e-6, f"Point estimate mismatch in {sc} {cname}: {pt_rec} vs {pt_orig}"
            
            ci_rec = recomputed[sc]['contrasts'][cname]['ci_95']
            ci_orig = original[sc]['contrasts'][cname]['ci_95']
            assert abs(ci_rec[0] - ci_orig[0]) < 1e-6, f"CI lower bound mismatch in {sc} {cname}"
            assert abs(ci_rec[1] - ci_orig[1]) < 1e-6, f"CI upper bound mismatch in {sc} {cname}"

def test_phase_5_1_pituitary_reanalysis_accounting():
    """Verify pituitary sample counts and transition accounting from Audit E."""
    pit_df = pd.read_csv(AUDIT_DIR / 'pituitary_class_reanalysis.csv')
    pooled = pit_df[pit_df['fold'] == 'POOLED_ALL_FOLDS']
    assert len(pooled) == 3
    for _, row in pooled.iterrows():
        assert row['pituitary_samples_count'] == 930
        assert row['pit_transitions_correct_to_incorrect'] >= 170
        assert row['pit_transitions_incorrect_to_correct'] <= 2
        assert row['mean_prob_pituitary_shift'] < -0.15

def test_phase_5_1_audit_report_and_gate_decision():
    """Verify that audit report exists, is comprehensive, and concludes PASS-WITH-LIMITATIONS."""
    with open(AUDIT_DIR / 'SPATIAL_VALIDITY_AUDIT.md', encoding='utf-8') as f:
        report = f.read()
    assert "PASS-WITH-LIMITATIONS" in report
    
    with open(AUDIT_DIR / 'claim_evidence_matrix.md', encoding='utf-8') as f:
        matrix = f.read()
    assert "SUPPORTED_WITHIN_TESTED_SETUP" in matrix
    assert "PARTIALLY_SUPPORTED" in matrix
    assert "UNRESOLVED" in matrix
    assert "NOT_SUPPORTED_BY_CURRENT_EVIDENCE" in matrix
