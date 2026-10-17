"""
Automated unit and statistical validation tests for Phase 4.1 Reconciliation Gate.
"""
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REC_DIR = ROOT / 'experiments' / 'phase_4_1_reconciliation'

def test_phase_4_1_required_artifacts_exist():
    """Verify all Phase 4.1 deliverables exist and are non-empty."""
    required = [
        'RECONCILIATION_REPORT.md',
        'bootstrap_method_comparison.md',
        'reconciled_paired_contrasts.json',
        'condition_metric_reconciliation.csv',
        'statistical_tests.csv',
        'bootstrap_comparison_data.json',
        'checksums.json'
    ]
    for r in required:
        fp = REC_DIR / r
        assert fp.exists(), f"Phase 4.1 deliverable missing: {r}"
        assert fp.stat().st_size > 0, f"Phase 4.1 deliverable is empty: {r}"

def test_phase_4_1_checksum_verification():
    """Verify cryptographic hash integrity of all Phase 4.1 files."""
    with open(REC_DIR / 'checksums.json') as f:
        manifest = json.load(f)
        
    for fname, meta in manifest.items():
        fp = REC_DIR / fname
        assert fp.exists(), f"File in checksums does not exist: {fname}"
        with open(fp, 'rb') as in_f:
            actual_sha = hashlib.sha256(in_f.read()).hexdigest()
        assert actual_sha == meta['sha256'], f"Checksum mismatch for {fname}"
        assert fp.stat().st_size == meta['size_bytes'], f"Size mismatch for {fname}"

def test_sample_and_cluster_accounting():
    """Verify exact sample, patient, cluster, and replicate accounting."""
    with open(REC_DIR / 'reconciled_paired_contrasts.json') as f:
        contrasts = json.load(f)
        
    for sc, expected_clusters in [('S0', 233), ('S1', 231), ('S2', 217)]:
        acct = contrasts[sc]['sample_accounting']
        assert acct['unique_patients'] == 233
        assert acct['unique_clusters'] == expected_clusters
        assert acct['unique_samples'] == 3064
        assert acct['bootstrap_replicates'] == 2000
        assert acct['valid_replicates'] == 2000

def test_placebo_and_net_contrast_reconciliation():
    """Verify paired placebo CI strictly excludes zero and Net contrast exceeds 0.05."""
    with open(REC_DIR / 'reconciled_paired_contrasts.json') as f:
        contrasts = json.load(f)
        
    for sc in ['S0', 'S1', 'S2']:
        c = contrasts[sc]
        # Placebo CI strictly excludes zero
        plac_ci = c['Delta_placebo']['ci_95']
        assert plac_ci[0] > 0.0, f"Reconciled placebo CI should exclude zero in {sc}: {plac_ci}"
        assert plac_ci[1] < 0.03, f"Placebo CI upper bound unexpectedly high in {sc}: {plac_ci}"
        
        # Net contrast strictly exceeds 0.05
        net_pt = c['Net_contrast']['point']
        net_ci = c['Net_contrast']['ci_95']
        assert net_pt > 0.05
        assert net_ci[0] > 0.05, f"Net contrast CI lower bound below 0.05 in {sc}: {net_ci}"
        assert c['Net_contrast']['derived_from_paired_replicates'] is True

def test_mcnemar_transitions_reconciliation():
    """Verify paired correctness transitions for tumor removal and placebo."""
    tests_df = pd.read_csv(REC_DIR / 'statistical_tests.csv')
    s0_mcnemar_rem = tests_df[(tests_df['scenario'] == 'S0') & (tests_df['test_name'] == 'McNemar_Tumor_Removal')].iloc[0]
    
    assert s0_mcnemar_rem['discordant_b_correct_to_incorrect'] == 330
    assert s0_mcnemar_rem['discordant_c_incorrect_to_correct'] == 26
    assert s0_mcnemar_rem['p_value_bounded'] <= 1e-15

def test_final_gate_decision():
    """Verify final gate decision in report is RECONCILED."""
    with open(REC_DIR / 'RECONCILIATION_REPORT.md', encoding='utf-8') as f:
        report = f.read()
    assert "**`RECONCILED`**" in report
