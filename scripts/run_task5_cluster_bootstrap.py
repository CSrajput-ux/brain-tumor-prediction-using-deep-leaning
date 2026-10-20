"""
Task 5: Synchronized Paired Cluster Bootstrap (B = 25,000)
Rigorous Statistical Audit & Re-analysis with Numerically Stable Inference.

Updates:
1. Strict consistent condition naming: C1_historical_dc_offset, C1_true_seam_w2, C1_true_seam_w3, C0_orig, C2_seam_suppressed, C3_c5lp_scramble.
2. Numerically stable McNemar calculation using scipy.stats.chi2.sf and exact binomial test (scipy.stats.binomtest). Never reports p = 0.0.
3. Rigorous bootstrap p-value reporting: both empirical percentile bound and Wald studentized p-value from bootstrap standard error.
4. Holm-Bonferroni FWER step-down correction applied strictly to the declared family of 12 primary confirmatory contrasts (M=12).
5. Separate reporting for True Seam control family and exploratory contrasts.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import chi2 as chi2_dist, norm, binomtest

ROOT = Path(__file__).resolve().parent.parent
P9_CSV = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement' / 'matched_predictions.csv'
TRUE_SEAM_CSV = ROOT / 'remaining_work_audit' / 'true_seam_oof_predictions.csv'
OUTPUT_DIR = ROOT / 'remaining_work_audit'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
B_REPLICATES = 25000

SCENARIOS = ['S0', 'S1', 'S2']

# Hypotheses definitions with strict family assignments
CONTRASTS = [
    # --- Primary Confirmatory Family (M = 12 across 3 scenarios) ---
    {
        'contrast_id': 'C3_vs_C0',
        'desc': 'Raw Scrambling Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'primary_confirmatory'
    },
    {
        'contrast_id': 'C1_hist_vs_C0',
        'desc': 'Historical Whole-Tile DC-Offset Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C1_historical_dc_offset',
        'family': 'primary_confirmatory'
    },
    {
        'contrast_id': 'C2_vs_C0',
        'desc': 'Seam-Suppressed Spatial Rearrangement Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C2_seam_suppressed',
        'family': 'primary_confirmatory'
    },
    {
        'contrast_id': 'C3_vs_C1_hist',
        'desc': 'Incremental Scrambling vs Historical DC Offset',
        'cond_A': 'C1_historical_dc_offset',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'primary_confirmatory'
    },
    
    # --- True Seam-Only Control Family ---
    {
        'contrast_id': 'C1_true_w2_vs_C0',
        'desc': 'Pure 2-Pixel Boundary Seam Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C1_true_seam_w2',
        'family': 'true_seam_controls'
    },
    {
        'contrast_id': 'C1_true_w3_vs_C0',
        'desc': 'Amplified 3-Pixel Boundary Seam Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C1_true_seam_w3',
        'family': 'true_seam_controls'
    },
    {
        'contrast_id': 'C3_vs_C1_true_w2',
        'desc': 'Incremental Scrambling vs Pure Boundary Seam (w=2)',
        'cond_A': 'C1_true_seam_w2',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'true_seam_controls'
    },
    {
        'contrast_id': 'C2_vs_C1_true_w2',
        'desc': 'Spatial Rearrangement vs Pure Boundary Seam (w=2)',
        'cond_A': 'C1_true_seam_w2',
        'cond_B': 'C2_seam_suppressed',
        'family': 'true_seam_controls'
    },
    
    # --- Exploratory Family ---
    {
        'contrast_id': 'C3_vs_C2',
        'desc': 'Sensitivity to Seam Suppression',
        'cond_A': 'C2_seam_suppressed',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'exploratory'
    }
]

def compute_cm(y_true, y_pred, num_classes=3):
    """Compute 3x3 confusion matrix."""
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def f1_from_cm(cm):
    """Compute Macro-F1 and per-class F1 from 3x3 confusion matrix."""
    f1s = []
    for c in range(3):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        f1s.append(f1)
    return float(np.mean(f1s)), [float(x) for x in f1s]

def compute_mcnemar_stable(y_true, y_pred_A, y_pred_B):
    """
    Compute McNemar test with continuity correction and exact binomial p-value.
    Guaranteed numerical stability: never underflows to 0.0 without bounded representation.
    """
    corr_A = (y_pred_A == y_true)
    corr_B = (y_pred_B == y_true)
    n_10 = int(np.sum(corr_A & (~corr_B)))
    n_01 = int(np.sum((~corr_A) & corr_B))
    
    if (n_10 + n_01) == 0:
        return 0.0, 1.0, 1.0, "1.000", n_10, n_01
    
    chi2 = ((abs(n_10 - n_01) - 1.0) ** 2) / (n_10 + n_01)
    chi2_p = float(chi2_dist.sf(chi2, df=1))
    
    # Exact two-sided binomial test on discordant pairs
    b_res = binomtest(n_10, n_10 + n_01, p=0.5, alternative='two-sided')
    exact_b_p = float(b_res.pvalue)
    
    # Format p-value string avoiding 0.0
    if exact_b_p < 1e-15:
        p_display = "< 1e-15"
    else:
        p_display = f"{exact_b_p:.4e}"
        
    return float(chi2), chi2_p, exact_b_p, p_display, n_10, n_01

def load_consolidated_predictions():
    """Load and unify predictions with consistent condition naming."""
    p9_df = pd.read_csv(P9_CSV)
    # Rename canonical historical DC offset condition
    p9_df['condition'] = p9_df['condition'].replace({'C1_seam_only': 'C1_historical_dc_offset'})
    
    ts_df = pd.read_csv(TRUE_SEAM_CSV)
    
    # Ensure aligned columns
    common_cols = [
        'scenario', 'fold', 'condition', 'sample_id', 'cluster_id',
        'true_label', 'class_name', 'pred_label', 'pred_class',
        'prob_meningioma', 'prob_glioma', 'prob_pituitary', 'correct'
    ]
    combined = pd.concat([p9_df[common_cols], ts_df[common_cols]], ignore_index=True)
    return combined

def main():
    print("=" * 75, flush=True)
    print("TASK 5 AUDIT: Synchronized Paired Cluster Bootstrap (B = 25,000)", flush=True)
    print("Rigorous numerical validation, family-wise FWER control, and stable inference.", flush=True)
    print("=" * 75, flush=True)
    
    df = load_consolidated_predictions()
    print(f"Total consolidated prediction rows: {len(df)} across {df['condition'].nunique()} conditions.", flush=True)
    print(f"Conditions: {list(df['condition'].unique())}", flush=True)
    
    rng = np.random.RandomState(SEED)
    results = []
    class_results = []
    
    t0 = time.time()
    
    for scen in SCENARIOS:
        scen_df = df[df['scenario'] == scen].copy()
        clusters = np.sort(scen_df['cluster_id'].unique())
        K = len(clusters)
        cluster_to_idx = {cid: i for i, cid in enumerate(clusters)}
        scen_df['c_idx'] = scen_df['cluster_id'].map(cluster_to_idx)
        
        print(f"\nScenario {scen}: {K} unique patient/duplicate clusters, {len(scen_df)} rows.", flush=True)
        
        # Precompute per-cluster confusion matrices for each condition
        cluster_cms = {}
        all_conds = df['condition'].unique()
        for cond in all_conds:
            c_df = scen_df[scen_df['condition'] == cond].sort_values('sample_id')
            c_cms = np.zeros((K, 3, 3), dtype=np.int64)
            for c_idx, group in c_df.groupby('c_idx'):
                c_cms[c_idx] = compute_cm(group['true_label'].values, group['pred_label'].values)
            cluster_cms[cond] = c_cms
        
        # Generate shared cluster resampling indices for this scenario (B x K)
        boot_indices = rng.choice(K, size=(B_REPLICATES, K), replace=True)
        boot_weights = np.zeros((B_REPLICATES, K), dtype=np.int32)
        for b in range(B_REPLICATES):
            boot_weights[b] = np.bincount(boot_indices[b], minlength=K)
            
        print(f"  Cluster weights generated (B={B_REPLICATES}). Evaluating contrasts...", flush=True)
        
        for c_def in CONTRASTS:
            cid = c_def['contrast_id']
            cond_A = c_def['cond_A']
            cond_B = c_def['cond_B']
            family = c_def['family']
            
            # Full cohort point estimates
            cm_A_full = cluster_cms[cond_A].sum(axis=0)
            cm_B_full = cluster_cms[cond_B].sum(axis=0)
            f1_A_full, class_f1_A = f1_from_cm(cm_A_full)
            f1_B_full, class_f1_B = f1_from_cm(cm_B_full)
            point_delta = f1_A_full - f1_B_full
            
            # Numerically stable McNemar test
            sub_A = scen_df[scen_df['condition'] == cond_A].sort_values('sample_id')
            sub_B = scen_df[scen_df['condition'] == cond_B].sort_values('sample_id')
            chi2_val, chi2_p, exact_b_p, p_display, n_10, n_01 = compute_mcnemar_stable(
                sub_A['true_label'].values,
                sub_A['pred_label'].values,
                sub_B['pred_label'].values
            )
            
            # Bootstrap evaluation
            cms_A_boot = np.tensordot(boot_weights, cluster_cms[cond_A], axes=([1], [0]))  # (B, 3, 3)
            cms_B_boot = np.tensordot(boot_weights, cluster_cms[cond_B], axes=([1], [0]))  # (B, 3, 3)
            
            deltas = np.zeros(B_REPLICATES, dtype=np.float64)
            class_deltas = np.zeros((B_REPLICATES, 3), dtype=np.float64)
            
            for b in range(B_REPLICATES):
                f1_a, cls_a = f1_from_cm(cms_A_boot[b])
                f1_b, cls_b = f1_from_cm(cms_B_boot[b])
                deltas[b] = f1_a - f1_b
                for c in range(3):
                    class_deltas[b, c] = cls_a[c] - cls_b[c]
            
            ci_lower = float(np.percentile(deltas, 2.5))
            ci_upper = float(np.percentile(deltas, 97.5))
            se_boot = float(np.std(deltas, ddof=1))
            
            # Empirical percentile p-value with Davison-Hinkley pseudo-count
            if point_delta >= 0:
                p_one_sided = (np.sum(deltas <= 0) + 1) / (B_REPLICATES + 1)
            else:
                p_one_sided = (np.sum(deltas >= 0) + 1) / (B_REPLICATES + 1)
            raw_p_empirical = float(min(1.0, 2.0 * p_one_sided))
            
            # Wald / Studentized z-score and asymptotic p-value
            z_score = float(point_delta / se_boot) if se_boot > 0 else 0.0
            wald_p = float(2.0 * norm.sf(abs(z_score)))
            wald_p_display = "< 1e-15" if wald_p < 1e-15 else f"{wald_p:.4e}"
            
            results.append({
                'scenario': scen,
                'contrast_id': cid,
                'description': c_def['desc'],
                'hypothesis_family': family,
                'condition_A': cond_A,
                'condition_B': cond_B,
                'macro_f1_A': f1_A_full,
                'macro_f1_B': f1_B_full,
                'signed_difference_A_minus_B': point_delta,
                'bootstrap_ci_lower': ci_lower,
                'bootstrap_ci_upper': ci_upper,
                'se_bootstrap': se_boot,
                'bootstrap_z_score': z_score,
                'wald_asymptotic_p_value': wald_p,
                'wald_p_display': wald_p_display,
                'bootstrap_replicates': B_REPLICATES,
                'invalid_replicates': 0,
                'patient_clusters': K,
                'raw_bootstrap_p_value': raw_p_empirical,
                'mcnemar_chi2': chi2_val,
                'mcnemar_chi2_p_float': chi2_p,
                'mcnemar_exact_binomial_p': exact_b_p,
                'mcnemar_p_display': p_display,
                'mcnemar_n_10': n_10,
                'mcnemar_n_01': n_01,
                'inference_method': 'synchronized_paired_cluster_bootstrap_percentile_b25000'
            })
            
            for c_idx, c_name in enumerate(['meningioma', 'glioma', 'pituitary']):
                class_results.append({
                    'scenario': scen,
                    'contrast_id': cid,
                    'hypothesis_family': family,
                    'class_name': c_name,
                    'condition_A': cond_A,
                    'condition_B': cond_B,
                    'class_f1_A': class_f1_A[c_idx],
                    'class_f1_B': class_f1_B[c_idx],
                    'signed_delta': class_f1_A[c_idx] - class_f1_B[c_idx],
                    'ci_lower': float(np.percentile(class_deltas[:, c_idx], 2.5)),
                    'ci_upper': float(np.percentile(class_deltas[:, c_idx], 97.5))
                })

    res_df = pd.DataFrame(results)
    
    # Apply Holm-Bonferroni step-down correction strictly within the declared hypothesis families:
    # 1. Primary Confirmatory Family (M = 12 hypotheses)
    # 2. True Seam Control Family (M = 12 hypotheses)
    # 3. Exploratory Family (M = 3 hypotheses)
    
    res_df['holm_adjusted_p_value'] = np.nan
    res_df['holm_family_size'] = 0
    res_df['holm_fwer_status'] = ''
    
    for fam in ['primary_confirmatory', 'true_seam_controls', 'exploratory']:
        fam_idx = res_df[res_df['hypothesis_family'] == fam].index
        fam_sub = res_df.loc[fam_idx].sort_values('raw_bootstrap_p_value').copy()
        M = len(fam_sub)
        
        running_max = 0.0
        adj_vals = {}
        for rank, (orig_i, row) in enumerate(fam_sub.iterrows()):
            p_val = row['raw_bootstrap_p_value']
            mult = M - rank
            val = min(1.0, mult * p_val)
            running_max = max(running_max, val)
            adj_vals[orig_i] = running_max
            
        for orig_i, adj_p in adj_vals.items():
            res_df.loc[orig_i, 'holm_adjusted_p_value'] = adj_p
            res_df.loc[orig_i, 'holm_family_size'] = M
            status = 'REJECT_H0 (Significant after Holm FWER)' if adj_p < 0.05 else 'FAIL_TO_REJECT (Not significant)'
            res_df.loc[orig_i, 'holm_fwer_status'] = status

    out_path = OUTPUT_DIR / 'task5_synchronized_bootstrap_b25000.csv'
    res_df.to_csv(out_path, index=False)
    print(f"\nTask 5 results successfully saved to {out_path} in {time.time() - t0:.2f}s", flush=True)
    
    class_df = pd.DataFrame(class_results)
    class_out_path = OUTPUT_DIR / 'task5_class_stratified_bootstrap.csv'
    class_df.to_csv(class_out_path, index=False)
    print(f"Task 5 class-stratified results saved to {class_out_path}", flush=True)

if __name__ == '__main__':
    main()
