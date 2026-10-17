"""
Automated validation and statistical test suite for Phase 5 — Context Reliance and Spatial Interventions.
"""
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P5_DIR = ROOT / 'experiments' / 'phase_5_context_reliance'

def test_phase_5_required_artifacts_exist():
    """Verify that all Phase 5 required deliverables exist and are non-empty."""
    required = [
        'preregistration.md',
        'intervention_config.yaml',
        'intervention_manifest.csv',
        'intervention_quality_audit.md',
        'matched_predictions.csv',
        'metrics_by_condition.csv',
        'paired_contrasts.json',
        'context_reliance_report.md',
        'limitations_and_claims.md',
        'checksums.json',
        'spatial_intervention_contact_sheet.png'
    ]
    for r in required:
        fp = P5_DIR / r
        assert fp.exists(), f"Phase 5 deliverable missing: {r}"
        assert fp.stat().st_size > 0, f"Phase 5 deliverable is empty: {r}"

def test_phase_5_checksum_integrity():
    """Verify cryptographic hash integrity of all Phase 5 files."""
    with open(P5_DIR / 'checksums.json') as f:
        manifest = json.load(f)
        
    for fname, meta in manifest.items():
        fp = P5_DIR / fname
        assert fp.exists(), f"File in checksums does not exist: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        assert actual_sha == meta['sha256'], f"Checksum mismatch for {fname}"
        assert fp.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_phase_5_sample_and_cluster_accounting():
    """Verify exact sample, patient, cluster, and replicate accounting."""
    with open(P5_DIR / 'paired_contrasts.json') as f:
        contrasts = json.load(f)
        
    expected_clusters = {'S0': 233, 'S1': 231, 'S2': 217}
    for sc, k_expected in expected_clusters.items():
        acct = contrasts[sc]['sample_accounting']
        assert acct['unique_patients'] == 233
        assert acct['unique_clusters'] == k_expected
        assert acct['unique_samples'] == 3064
        assert acct['bootstrap_replicates'] == 2000

def test_phase_5_matched_predictions_accounting():
    """Verify exact row counts, condition distribution, and baseline agreement."""
    df = pd.read_csv(P5_DIR / 'matched_predictions.csv')
    assert len(df) == 64344
    assert df['condition'].nunique() == 7
    for cond in ['I_orig', 'I_tumor_removed', 'I_placebo_focal', 'I_margin_removed', 'I_margin_placebo', 'I_distant_perturbed', 'I_margin_feathered']:
        assert (df['condition'] == cond).sum() == 9192
        
    # Baseline comparison with Phase 3 I_orig
    p3_df = pd.read_csv(ROOT / 'experiments' / 'phase_3_interventions' / 'matched_predictions.csv')
    p3_orig = p3_df[p3_df['condition'] == 'I_orig'].sort_values(['scenario', 'sample_id']).reset_index(drop=True)
    p5_orig = df[df['condition'] == 'I_orig'].sort_values(['scenario', 'sample_id']).reset_index(drop=True)
    
    agreements = (p3_orig['pred_label'] == p5_orig['pred_label']).sum()
    agreement_rate = agreements / 9192
    assert agreement_rate >= 0.9998, f"Baseline agreement rate too low: {agreement_rate}"

def test_phase_5_statistical_contrasts():
    """Verify key statistical findings across all scenarios."""
    with open(P5_DIR / 'paired_contrasts.json') as f:
        contrasts = json.load(f)
        
    for sc in ['S0', 'S1', 'S2']:
        c = contrasts[sc]['contrasts']
        
        # 1. Net Tumor Reliance exceeds 0.05
        net_tumor = c['Net_tumor_reliance']
        assert net_tumor['point'] > 0.05
        assert net_tumor['ci_95'][0] > 0.05
        
        # 2. Net Margin Reliance falls below 0.03 threshold but is positive
        net_margin = c['Net_margin_reliance']
        assert net_margin['point'] < 0.03
        assert net_margin['ci_95'][0] > 0.00
        
        # 3. Distant Context Perturbation produces large drop
        delta_dist = c['Delta_distant_perturbed']
        assert delta_dist['point'] > 0.08
        assert delta_dist['ci_95'][0] > 0.05
        assert delta_dist['mcnemar_p_value'] < 1e-40
        
        # 4. Margin Feathered sensitivity check encompasses zero
        delta_feather = c['Delta_margin_feathered']
        assert delta_feather['ci_95'][0] <= 0.00 <= delta_feather['ci_95'][1]
        assert delta_feather['mcnemar_p_value'] > 0.01

def test_phase_5_gate_decision_and_epistemic_integrity():
    """Verify that gate decision is PASS-WITH-LIMITATIONS and epistemic claims are maintained."""
    with open(P5_DIR / 'context_reliance_report.md', encoding='utf-8') as f:
        report = f.read()
    assert "PASS-WITH-LIMITATIONS" in report
    
    with open(P5_DIR / 'limitations_and_claims.md', encoding='utf-8') as f:
        claims = f.read()
    assert "NO Claim of Discovering Clinical \"Shortcuts\"" in claims
    assert "NO Claim of Anatomical or Biological Segmentation Ground Truth" in claims
