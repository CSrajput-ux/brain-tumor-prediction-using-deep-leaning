"""
Automated validation and integrity tests for Phase 3 Intervention Study.
"""
import os
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P3_DIR = ROOT / 'experiments' / 'phase_3_interventions'
P2_DIR = ROOT / 'experiments' / 'phase_2_baseline'

def test_phase_3_required_artifacts_exist():
    """Verify all mandatory Phase 3 files exist and are non-empty."""
    required_files = [
        'mask_audit_stats.csv',
        'mask_audit_contact_sheet.png',
        'mask_audit_report.md',
        'intervention_config.yaml',
        'intervention_manifest.csv',
        'matched_predictions.csv',
        'metrics_by_condition.csv',
        'paired_differences.json',
        'BASELINE_VS_INTERVENTION_REPORT.md',
        'intervention_contrasts_plot.png',
        'confusion_matrices_plot.png',
        'per_class_reliance_plot.png',
        'checksums.json'
    ]
    for rf in required_files:
        fp = P3_DIR / rf
        assert fp.exists(), f"Required Phase 3 file missing: {rf}"
        assert fp.stat().st_size > 0, f"File is empty: {rf}"

def test_phase_3_checksum_verification():
    """Verify cryptographic integrity of all Phase 3 artifacts."""
    with open(P3_DIR / 'checksums.json') as f:
        manifest = json.load(f)
        
    for fname, meta in manifest.items():
        fp = P3_DIR / fname
        assert fp.exists(), f"File in checksums does not exist: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        assert actual_sha == meta['sha256'], f"SHA-256 mismatch for {fname}"
        assert fp.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_tumor_mask_audit_integrity():
    """Verify spatial and numerical properties of all 3,064 masks."""
    df_masks = pd.read_csv(P3_DIR / 'mask_audit_stats.csv')
    assert len(df_masks) == 3064, f"Expected 3064 masks, got {len(df_masks)}"
    
    # Zero empty masks
    assert (df_masks['fg_pixels'] == 0).sum() == 0, "Empty masks found!"
    assert df_masks['fg_pixels'].min() >= 100, f"Implausibly tiny mask found: {df_masks['fg_pixels'].min()}"
    
    # Area fraction bounded
    assert df_masks['fg_fraction'].max() < 0.50, f"Implausibly large mask found: {df_masks['fg_fraction'].max()}"
    
    # Connected components well bounded
    assert df_masks['num_cc'].max() <= 3, f"Unexpected high CC count: {df_masks['num_cc'].max()}"

def test_intervention_manifest_matching():
    """Verify matched contralateral placebo geometry in intervention manifest."""
    manifest_df = pd.read_csv(P3_DIR / 'intervention_manifest.csv')
    assert len(manifest_df) == 3064, f"Manifest length mismatch: {len(manifest_df)}"
    
    # Placebo area matches tumor area exactly for >= 99.5% of cases (12 midline cases slightly clipped at boundary)
    exact_matches = (manifest_df['tumor_area_pixels'] == manifest_df['placebo_area_pixels']).sum()
    assert exact_matches >= 3050, f"Expected >= 3050 exact area matches, got {exact_matches}"
    
    # Overlap must be strictly zero across all 3,064 samples
    assert np.all(manifest_df['placebo_overlap_pixels'] == 0), "Placebo overlaps with tumor!"

def test_matched_predictions_matrix():
    """Verify dimensions and consistency of matched predictions."""
    preds_df = pd.read_csv(P3_DIR / 'matched_predictions.csv')
    expected_rows = 3064 * 3 * 6  # 3064 samples * 3 scenarios * 6 conditions
    assert len(preds_df) == expected_rows, f"Expected {expected_rows} prediction rows, got {len(preds_df)}"
    
    # Probability sums
    prob_sums = preds_df['prob_meningioma'] + preds_df['prob_glioma'] + preds_df['prob_pituitary']
    assert np.allclose(prob_sums, 1.0, atol=1e-4), "Softmax probabilities do not sum to 1.0!"
    
    # Argmax prediction check
    pred_labels = preds_df[['prob_meningioma', 'prob_glioma', 'prob_pituitary']].values.argmax(axis=1)
    assert np.all(pred_labels == preds_df['pred_label'].values), "Argmax does not match pred_label!"

def test_pre_registered_contrasts_and_safeguards():
    """Verify paired differences, net reliance margins, and pre-registered zone properties."""
    with open(P3_DIR / 'paired_differences.json') as f:
        diffs = json.load(f)
        
    for sc in ['S0', 'S1', 'S2']:
        sc_data = diffs[sc]
        
        # 1. Delta_removal must be statistically significant and drop >= 0.10 point estimate
        d_rem = sc_data['Delta_removal']['point_estimate']
        assert d_rem >= 0.10, f"Expected Delta_removal >= 0.10 in {sc}, got {d_rem}"
        
        # 2. Delta_placebo must be minimal and CI must span 0
        d_plac = sc_data['Delta_placebo']['point_estimate']
        ci_plac = sc_data['Delta_placebo']['ci_95']
        assert d_plac < 0.03, f"Placebo drop too large in {sc}: {d_plac}"
        assert ci_plac[0] <= 0 <= ci_plac[1], f"Placebo CI does not cross zero in {sc}: {ci_plac}"
        
        # 3. Net tumor reliance must exceed 0.05 pre-registered margin
        net_rel = sc_data['Net_tumor_reliance']['point_estimate']
        assert net_rel >= 0.05, f"Net tumor reliance below 0.05 margin in {sc}: {net_rel}"
        
        # 4. Context shift must have negligible impact
        d_ctx = sc_data['Delta_context_shift']['point_estimate']
        ci_ctx = sc_data['Delta_context_shift']['ci_95']
        assert abs(d_ctx) < 0.02, f"Context shift unexpectedly large in {sc}: {d_ctx}"
        assert ci_ctx[0] <= 0 <= ci_ctx[1], f"Context shift CI does not cross zero in {sc}"
        
        # 5. Zone assignment and boundary spanning documented
        assert sc_data['zone_assignment']['zone_code'] == 'ZONE_3'
        assert sc_data['zone_assignment']['spans_zone_boundary'] is True

def test_frozen_baseline_invariance():
    """Confirm zero baseline checkpoints or files were modified during Phase 3."""
    with open(P2_DIR / 'checksums.json') as f:
        p2_checksums = json.load(f)
        
    artifacts = p2_checksums['artifacts'] if 'artifacts' in p2_checksums else p2_checksums
    for fname, meta in artifacts.items():
        fp = ROOT / fname
        assert fp.exists(), f"Phase 2 baseline file missing: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        expected_sha = meta['sha256'] if isinstance(meta, dict) else meta
        assert actual_sha == expected_sha, f"Phase 2 baseline file modified during Phase 3: {fname}"
