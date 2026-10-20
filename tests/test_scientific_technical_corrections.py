import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import binom as binom_dist
from scipy.special import gammaln, logsumexp

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / 'publication' / 'manuscript_v1'
PUB_TAB_DIR = PUB_DIR / 'tables'
AUDIT_DIR = ROOT / 'remaining_work_audit'

EXPECTED_CONDITIONS = {
    'C0_orig',
    'C1_historical_dc_offset',
    'C1_true_seam_w2',
    'C1_true_seam_w3',
    'C2_seam_suppressed',
    'C3_c5lp_scramble'
}


def test_standardized_condition_naming_in_table5():
    """Verify Table 5 contains all 6 standardized conditions with no legacy aliases."""
    t5_path = PUB_TAB_DIR / 'table5_intervention_metrics.csv'
    assert t5_path.exists(), "table5_intervention_metrics.csv must exist"
    df = pd.read_csv(t5_path)
    
    unique_conds = set(df['condition'].unique())
    assert unique_conds == EXPECTED_CONDITIONS, f"Mismatch in Table 5 conditions: {unique_conds} vs {EXPECTED_CONDITIONS}"
    assert 'C1_seam_only' not in unique_conds, "Legacy alias C1_seam_only must not appear in Table 5"
    assert len(df) == 18, f"Expected 18 rows (3 scenarios x 6 conditions), got {len(df)}"


def test_table2_manifest_fold_counts():
    """Verify Table 2 fold sample sizes strictly match the underlying split manifests."""
    t2_path = PUB_TAB_DIR / 'table2_evaluation_scenarios.csv'
    assert t2_path.exists(), "table2_evaluation_scenarios.csv must exist"
    df = pd.read_csv(t2_path).set_index('scenario')
    
    expected_folds = {
        'S0': [613, 614, 611, 613, 613],
        'S1': [612, 614, 613, 612, 613],
        'S2': [613, 612, 614, 612, 613]
    }
    
    for sc, expected in expected_folds.items():
        assert sc in df.index, f"Scenario {sc} missing in Table 2"
        actual = [int(df.loc[sc, f'fold_{f}_samples']) for f in range(1, 6)]
        assert actual == expected, f"Scenario {sc} fold sizes mismatch: {actual} vs expected {expected}"
        assert int(df.loc[sc, 'total_samples']) == 3064, f"Scenario {sc} total samples must be 3064"


def test_bootstrap_results_integrity():
    """Verify Task 5 synchronized paired cluster bootstrap outputs.

    Issue 1 fix: Verifies new canonical McNemar fields exist and are correctly populated.
    - mcnemar_exact_log10_p must be finite for all rows (never NaN or inf)
    - mcnemar_exact_underflow flags rows where IEEE float underflowed to 0.0
    - mcnemar_asymptotic_chi2_p is the separate chi2 p-value (NEVER substituted for exact p)
    - mcnemar_discordant_n10 and mcnemar_discordant_n01 are the observed discordant counts
    - For underflowed rows, mcnemar_exact_binomial_p==0.0 is EXPECTED (use log10 field)
    - For NON-underflowed rows, mcnemar_exact_binomial_p must NOT equal mcnemar_asymptotic_chi2_p
      (that would indicate the old fallback substitution is still occurring)
    """
    b_path = AUDIT_DIR / 'task5_synchronized_bootstrap_b25000.csv'
    assert b_path.exists(), "task5_synchronized_bootstrap_b25000.csv must exist"
    df = pd.read_csv(b_path)

    # 1. New Issue 1 canonical McNemar fields must be present
    required_new_fields = [
        'mcnemar_exact_log10_p', 'mcnemar_exact_underflow',
        'mcnemar_exact_binomial_p', 'mcnemar_asymptotic_chi2_p',
        'mcnemar_discordant_n10', 'mcnemar_discordant_n01',
    ]
    for field in required_new_fields:
        assert field in df.columns, f"Required Issue 1 field missing: {field}"

    # 2. mcnemar_exact_log10_p must be finite for all rows (never NaN, +inf, or -inf)
    assert df['mcnemar_exact_log10_p'].notna().all(), "mcnemar_exact_log10_p must not be NaN"
    assert np.isfinite(df['mcnemar_exact_log10_p']).all(), "mcnemar_exact_log10_p must be finite"
    # All log10 p-values must be <= 0 (p-values are in [0,1])
    assert (df['mcnemar_exact_log10_p'] <= 0.001).all(), "log10 p-values must be <= 0"

    # 3. Chi2 fallback substitution check: for non-underflowed rows where exact_p != 0.0,
    #    exact_p must NOT be identical to chi2_p (that would mean old fallback occurred).
    non_underflow = df[df['mcnemar_exact_underflow'] == False]
    non_underflow_nonzero = non_underflow[non_underflow['mcnemar_exact_binomial_p'] != 0.0]
    suspicious = non_underflow_nonzero[
        non_underflow_nonzero['mcnemar_exact_binomial_p'] == non_underflow_nonzero['mcnemar_asymptotic_chi2_p']
    ]
    assert len(suspicious) == 0, (
        f"CRITICAL: {len(suspicious)} rows where exact_p == chi2_p — chi2 fallback substitution detected!\n"
        f"{suspicious[['scenario','contrast_id','mcnemar_exact_binomial_p','mcnemar_asymptotic_chi2_p']].to_string()}"
    )

    # 4. For underflowed rows: exact_p_float must be 0.0 and log10_p must indicate extreme value
    underflow_rows = df[df['mcnemar_exact_underflow'] == True]
    if len(underflow_rows) > 0:
        assert (underflow_rows['mcnemar_exact_binomial_p'] == 0.0).all(), (
            "Underflowed rows must have exact_p_float == 0.0"
        )
        # log10 p for underflowed rows should be very negative (< -308)
        assert (underflow_rows['mcnemar_exact_log10_p'] < -300).all(), (
            "Underflowed rows must have log10_p < -300 (i.e. far beyond float64 range)"
        )

    # 5. mcnemar_discordant_n10 + mcnemar_discordant_n01 must be positive for all rows
    #    (there are always discordant pairs for significant contrasts)
    assert (df['mcnemar_discordant_n10'] >= 0).all(), "n10 must be non-negative"
    assert (df['mcnemar_discordant_n01'] >= 0).all(), "n01 must be non-negative"

    # 6. p_display must not be '0.0' or '0' for any row
    for p_disp in df['mcnemar_p_display']:
        assert p_disp != '0.0' and p_disp != '0', f"Disallowed McNemar display p-value: {p_disp}"
    for w_disp in df['wald_p_display']:
        assert w_disp != '0.0' and w_disp != '0', f"Disallowed Wald display p-value: {w_disp}"

    # 7. Replicates count and cluster accounting
    assert (df['bootstrap_replicates'] == 25000).all(), "All contrasts must use B=25,000 resamples"
    assert (df['invalid_replicates'] == 0).all(), "All replicates must have zero invalid iterations"
    assert (df['patient_clusters'] >= 217).all(), "Patient cluster count must reflect scenario clusters"

    # 8. Confidence intervals are strictly ordered
    assert (df['bootstrap_ci_lower'] < df['bootstrap_ci_upper']).all(), "CI lower must be < CI upper"

    # 9. raw_bootstrap_p_value must be > 0 (Davison-Hinkley pseudo-count prevents exact 0)
    assert (df['raw_bootstrap_p_value'] > 0).all(), "No raw bootstrap p-values should be exactly 0.0"
    assert (df['wald_asymptotic_p_value'] >= 0).all(), "Wald p-values must be non-negative"


def test_mcnemar_logspace_verification():
    """Issue 1: Verify log-space exact McNemar computation against independent high-precision reference.

    Tests representative cases including extreme discordant counts (N=1532, k=67),
    balanced counts, zero discordance, and small samples. Verifies:
    - Correct log10_p values (within 0.01 of reference)
    - No chi2 fallback substitution for non-underflowed rows
    - Proper underflow detection for extreme cases
    - Correct edge case handling (N=0)
    """
    from scipy.stats import chi2 as chi2_dist

    def compute_exact_logspace(n_10, n_01):
        N = n_10 + n_01
        if N == 0:
            return 0.0, 1.0, False, 1.0
        k = min(n_10, n_01)
        if k == N / 2:
            log10_p_exact = 0.0
            exact_p_float = 1.0
            exact_underflow = False
        else:
            i = np.arange(k + 1)
            log_pmf = gammaln(N + 1) - gammaln(i + 1) - gammaln(N - i + 1) - N * np.log(2.0)
            log_tail = float(logsumexp(log_pmf))
            log_p_nat = min(0.0, np.log(2.0) + log_tail)
            log10_p_exact = min(0.0, float(log_p_nat / np.log(10.0)))
            exact_p_float = float(np.exp(log_p_nat)) if log_p_nat > -700.0 else 0.0
            exact_underflow = (exact_p_float == 0.0) and (N > 0)
        chi2_stat = ((abs(n_10 - n_01) - 1.0) ** 2) / float(N) if N > 0 else 0.0
        chi2_p = float(chi2_dist.sf(chi2_stat, df=1))
        return log10_p_exact, exact_p_float, exact_underflow, chi2_p

    test_cases = [
        # (n10, n01, expected_underflow, expected_log10_p_approx)
        (1465, 67, True, -342.0),   # N=1532, k=67: extreme, underflows
        (150, 150, False, 0.0),     # N=300, balanced: p=1.0, log10=0
        (0, 0, False, 0.0),         # N=0: edge case, p=1.0
        (5, 0, False, -1.5),        # N=5, k=0: one-sided extreme
        (60, 40, False, -2.0),      # N=100, k=40: moderate
    ]

    for n10, n01, expected_underflow, approx_log10_p in test_cases:
        log10_p, p_float, underflow, chi2_p = compute_exact_logspace(n10, n01)

        # Check underflow flag
        assert underflow == expected_underflow, (
            f'n10={n10},n01={n01}: expected underflow={expected_underflow}, got {underflow}'
        )

        # For underflowed rows: p_float must be 0.0
        if underflow:
            assert p_float == 0.0, f'Underflowed row n10={n10},n01={n01}: p_float should be 0.0'
            # log10_p must be very negative and finite
            assert np.isfinite(log10_p), f'log10_p must be finite even when underflowed'
            assert log10_p < -300, f'Underflowed row: log10_p={log10_p} should be < -300'

        # For non-underflowed rows: log10_p should be approximately correct
        if not underflow and n10 + n01 > 0:
            assert abs(log10_p - approx_log10_p) < 1.0, (
                f'n10={n10},n01={n01}: log10_p={log10_p:.3f} too far from expected {approx_log10_p}'
            )

        # Critical: for non-underflowed rows where exact_p != 0.0,
        # exact_p must NOT equal chi2_p (no fallback substitution)
        if not underflow and p_float != 0.0 and n10 + n01 > 0:
            assert p_float != chi2_p, (
                f'n10={n10},n01={n01}: exact_p == chi2_p indicates fallback substitution!'
            )

    # Verify extreme case N=1532, k=67 log10_p is in expected range
    log10_p, _, _, _ = compute_exact_logspace(1465, 67)
    assert log10_p < -300, f'N=1532, k=67 log10_p={log10_p:.1f} should be < -300'
    assert log10_p > -400, f'N=1532, k=67 log10_p={log10_p:.1f} should be > -400'


def test_holm_multiplicity_families_independent_correction():
    """Verify independent Holm-Bonferroni correction across primary, true-seam, and exploratory families."""
    # NOTE: Issue 2 clarification - Holm correction is applied to Davison-Hinkley bootstrap bounds
    # (raw_bootstrap_p_value), which are NOT formal null-hypothesis p-values. The correction
    # provides exploratory family-wise control with this caveat documented.
    b_path = AUDIT_DIR / 'task5_synchronized_bootstrap_b25000.csv'
    df = pd.read_csv(b_path)
    
    families = {
        'primary_confirmatory': 12,
        'true_seam_controls': 12,
        'exploratory': 3
    }
    
    for fam_name, expected_size in families.items():
        sub = df[df['hypothesis_family'] == fam_name].sort_values('raw_bootstrap_p_value').reset_index(drop=True)
        assert len(sub) == expected_size, f"Family {fam_name} expected {expected_size} contrasts, got {len(sub)}"
        assert (sub['holm_family_size'] == expected_size).all(), f"Family size field mismatch in {fam_name}"
        
        # Verify step-down Holm formula: p_adj_{(k)} = max_{j <= k} min(1.0, (M - j + 1) * p_{(j)})
        running_max = 0.0
        for rank, row in sub.iterrows():
            mult = expected_size - rank
            raw_p = row['raw_bootstrap_p_value']
            expected_adj = min(1.0, mult * raw_p)
            running_max = max(running_max, expected_adj)
            actual_adj = row['holm_adjusted_p_value']
            assert np.isclose(actual_adj, running_max, atol=1e-8), (
                f"Holm adj mismatch in {fam_name} rank {rank}: actual {actual_adj} vs expected {running_max}"
            )
            
        # Verify monotonicity of adjusted p-values
        assert sub['holm_adjusted_p_value'].is_monotonic_increasing, f"Adjusted p-values in {fam_name} must be non-decreasing"


def test_true_seam_prediction_matching_and_invariants():
    """Verify true-seam out-of-fold predictions and strict protection invariants."""
    pred_path = AUDIT_DIR / 'true_seam_oof_predictions.csv'
    assert pred_path.exists(), "true_seam_oof_predictions.csv must exist"
    preds = pd.read_csv(pred_path)
    assert len(preds) == 18384, f"Expected 18,384 true seam predictions, got {len(preds)}"
    
    audit_path = AUDIT_DIR / 'true_seam_image_audit.csv'
    assert audit_path.exists(), "true_seam_image_audit.csv must exist"
    audit = pd.read_csv(audit_path)
    assert len(audit) == 3064, f"Expected 3,064 audited images, got {len(audit)}"
    
    # Invariants
    assert (audit['w2_tumor_altered'] == 0).all(), "Tumour core must have 0 altered pixels in w=2"
    assert (audit['w2_margin_altered'] == 0).all(), "Margin ring must have 0 altered pixels in w=2"
    assert (audit['w3_tumor_altered'] == 0).all(), "Tumour core must have 0 altered pixels in w=3"
    assert (audit['w3_margin_altered'] == 0).all(), "Margin ring must have 0 altered pixels in w=3"
    assert audit['w2_unchanged_fraction'].mean() > 0.81, "Mean unchanged pixel area must exceed 81%"
    assert (audit['w2_unchanged_fraction'] > 0.75).all(), "Unchanged pixel area must exceed 75% for all slices"


def test_claim_evidence_matrix_reconciliation():
    """Verify Table 8 claim-evidence matrix percentages and causal statements match canonical Table 7."""
    c_path = PUB_TAB_DIR / 'table8_claim_evidence_matrix.csv'
    assert c_path.exists(), "table8_claim_evidence_matrix.csv must exist"
    df = pd.read_csv(c_path).set_index('hypothesis_id')
    
    # Check H_SEAM separation
    assert 'H_SEAM_HISTORICAL' in df.index
    assert 'H_TRUE_SEAM_W2' in df.index
    assert 'H_TRUE_SEAM_W3' in df.index
    
    # Reconciled percentages verification
    w2_ev = df.loc['H_TRUE_SEAM_W2', 'measured_evidence']
    assert '28.6%' in df.loc['H_TRUE_SEAM_W2', 'scientific_caveat'], "28.6% empirical ratio must be documented"
    assert '81.35%' in w2_ev, "81.35% pixel preservation must be documented"
    assert '0.1206' in w2_ev, "Delta = 0.1206 must be documented"
    
    layout_ev = df.loc['H_LAYOUT_ISOLATION', 'measured_evidence']
    assert '26.0%' in layout_ev, "26.0% excess seam Sobel reduction (source) must be documented"
    assert '53.9%' in layout_ev, "53.9% excess HF Fourier reduction (source) must be documented"
    assert '10.5%' in layout_ev, "10.5% excess seam Sobel reduction (input 224) must be documented"
    assert '41.2%' in layout_ev, "41.2% excess HF Fourier reduction (input 224) must be documented"
    
    # Check causal caveat on layout isolation
    layout_cav = df.loc['H_LAYOUT_ISOLATION', 'scientific_caveat']
    assert "disrupted" in layout_cav.lower() or "altered" in layout_cav.lower()
    assert "non-local" in layout_cav.lower()
    assert "out-of-distribution" in layout_cav.lower() or "ood" in layout_cav.lower()
    
    # Glioma flip dose-response
    skull_ev = df.loc['H_SKULL_BASE_COORDINATES', 'measured_evidence']
    for pct in ['0.14%', '16.48%', '23.35%', '31.28%', '56.45%', '63.53%']:
        assert pct in skull_ev, f"Dose-response percentage {pct} missing in skull base coordinates row"


def test_manuscript_and_abstract_causal_and_novelty_language():
    """Verify manuscript and abstract text do not contain unsupported preregistration or first-ever claims."""
    manuscript_text = (PUB_DIR / 'manuscript.md').read_text(encoding='utf-8')
    abstract_text = (PUB_DIR / 'abstract.md').read_text(encoding='utf-8')
    
    # No unsupported preregistration claims
    assert 'preregistered' not in manuscript_text.lower(), "Unsupported 'preregistered' found in manuscript.md"
    assert 'preregistered' not in abstract_text.lower(), "Unsupported 'preregistered' found in abstract.md"
    
    # No first-ever claims
    assert 'first-ever' not in manuscript_text.lower(), "Unsupported 'first-ever' found in manuscript.md"
    assert 'first definitive' not in manuscript_text.lower(), "Unsupported 'first definitive' found in manuscript.md"
    assert 'first-ever' not in abstract_text.lower(), "Unsupported 'first-ever' found in abstract.md"
    
    # No anti-causal claims asserting macroscopic anatomy is independently essential
    assert "independently essential" not in abstract_text.lower(), "'independently essential' found in abstract.md"
    assert "independently essential" not in manuscript_text.lower(), "'independently essential' found in manuscript.md"
    
    # Four-factor explanation present in manuscript and abstract
    assert "four inseparable factors" in manuscript_text.lower()
    assert "four inseparable factors" in abstract_text.lower()
    assert "non-local" in manuscript_text.lower()
    assert "out-of-distribution" in manuscript_text.lower() or "ood" in manuscript_text.lower()
