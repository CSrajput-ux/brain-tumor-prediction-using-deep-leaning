"""
Automated validation and integrity tests for Phase 4 Independent Audit.
"""
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P4_DIR = ROOT / 'experiments' / 'phase_4_audit'
P3_DIR = ROOT / 'experiments' / 'phase_3_interventions'

def test_phase_4_required_artifacts_exist():
    """Verify all Phase 4 audit artifacts exist and are non-empty."""
    required = [
        'phase_4a_audit_results.json',
        'recomputed_metrics.csv',
        'recomputed_paired_contrasts.json',
        'multiple_testing_audit.csv',
        'robustness_audit_results.json',
        'sample_level_robustness_data.csv',
        'subgroup_audit_results.json',
        'INDEPENDENT_VALIDATION_REPORT.md',
        'phase_4_checksums.json'
    ]
    for r in required:
        fp = P4_DIR / r
        assert fp.exists(), f"Phase 4 file missing: {r}"
        assert fp.stat().st_size > 0, f"Phase 4 file empty: {r}"

def test_phase_4_checksums_verification():
    """Verify cryptographic integrity of Phase 4 audit files."""
    with open(P4_DIR / 'phase_4_checksums.json') as f:
        manifest = json.load(f)
        
    for fname, meta in manifest.items():
        fp = P4_DIR / fname
        assert fp.exists(), f"File in checksums does not exist: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        assert actual_sha == meta['sha256'], f"Checksum mismatch for {fname}"
        assert fp.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_4a_reproducibility_audit_results():
    """Verify Phase 4A audit findings."""
    with open(P4_DIR / 'phase_4a_audit_results.json') as f:
        res = json.load(f)
        
    assert res['checksums_verified_100_percent'] is True
    assert res['matched_predictions_rows'] == 55152
    assert res['global_max_prob_diff_vs_p2'] < 0.005
    assert res['prediction_label_agreement_vs_p2'] == 1.0
    
    # Partition isolation
    for sc, iso in res['partition_isolation'].items():
        assert iso['patient_crossings'] == 0
        assert iso['component_crossings'] == 0

def test_phase_4b_metric_reconciliation():
    """Verify that recomputed metrics match Phase 3 reported values."""
    p3_metrics = pd.read_csv(P3_DIR / 'metrics_by_condition.csv')
    p4_metrics = pd.read_csv(P4_DIR / 'recomputed_metrics.csv')
    
    p3_pooled = p3_metrics[p3_metrics['fold'] == 'pooled'].sort_values(['scenario', 'condition']).reset_index(drop=True)
    p4_sorted = p4_metrics.sort_values(['scenario', 'condition']).reset_index(drop=True)
    
    # Compare macro_f1
    diffs = np.abs(p3_pooled['macro_f1'].values - p4_sorted['macro_f1'].values)
    assert np.all(diffs < 1e-4), f"Macro-F1 discrepancy between reported and recomputed: {diffs.max()}"
    
    # Balanced accuracy
    bal_diffs = np.abs(p3_pooled['balanced_accuracy'].values - p4_sorted['balanced_accuracy'].values)
    assert np.all(bal_diffs < 1e-4), f"Balanced accuracy discrepancy: {bal_diffs.max()}"

def test_phase_4b_paired_contrasts_and_net_ci():
    """Verify paired contrasts and direct paired bootstrap net CI derivation."""
    with open(P4_DIR / 'recomputed_paired_contrasts.json') as f:
        contrasts = json.load(f)
        
    for sc in ['S0', 'S1', 'S2']:
        c = contrasts[sc]
        assert c['Net_contrast']['derived_from_paired_replicates'] is True
        assert c['Net_contrast']['point'] >= 0.05
        assert c['Net_contrast']['ci_95'][0] > 0.05
        
        # McNemar p-value bounded
        assert c['mcnemar_contingency_table']['reported_p_value_bounded'] > 0.0
        assert c['mcnemar_contingency_table']['reported_p_value_bounded'] <= 1e-15
        
        # Wilcoxon p-value bounded
        assert c['wilcoxon_patient_level']['reported_p_value_bounded'] > 0.0
        assert c['wilcoxon_patient_level']['reported_p_value_bounded'] <= 1e-13

def test_phase_4c_dose_response_and_placebo_integrity():
    """Verify lesion size correlation and placebo mask validity."""
    with open(P4_DIR / 'robustness_audit_results.json') as f:
        rob = json.load(f)
        
    assert rob['tumor_area_correlation_spearman'] > 0.30
    assert rob['zero_overlap_cases'] == 3064
    assert rob['exact_placebo_matches'] >= 3050

def test_phase_4d_pathology_dissociation():
    """Verify class-specific divergence between Meningioma and Pituitary."""
    with open(P4_DIR / 'subgroup_audit_results.json') as f:
        sub = json.load(f)
        
    c_summary = sub['class_summary']
    meningioma_drop = c_summary['prob_drop_removed_mean']['meningioma']
    pituitary_drop = c_summary['prob_drop_removed_mean']['pituitary']
    
    assert meningioma_drop > 0.15, f"Expected large meningioma drop, got {meningioma_drop}"
    assert pituitary_drop < 0.03, f"Expected tiny pituitary drop, got {pituitary_drop}"
