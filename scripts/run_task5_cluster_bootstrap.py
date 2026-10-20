"""
Task 5: Synchronized Paired Cluster Bootstrap (B = 25,000)
Recalculates primary intervention contrasts using synchronized patient-cluster resampling.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement' / 'matched_predictions.csv'
OUTPUT_DIR = ROOT / 'remaining_work_audit'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
B_REPLICATES = 25000

SCENARIOS = ['S0', 'S1', 'S2']

CONTRASTS = [
    {
        'contrast_id': 'C3_vs_C0',
        'desc': 'Original Scrambling Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'primary'
    },
    {
        'contrast_id': 'C1_vs_C0',
        'desc': 'Seam-Only Effect',
        'cond_A': 'C0_orig',
        'cond_B': 'C1_seam_only',
        'family': 'primary'
    },
    {
        'contrast_id': 'C2_vs_C0',
        'desc': 'Seam-Suppressed Spatial Rearrangement',
        'cond_A': 'C0_orig',
        'cond_B': 'C2_seam_suppressed',
        'family': 'primary'
    },
    {
        'contrast_id': 'C3_vs_C1',
        'desc': 'Incremental Scrambling vs Seam-Only Difference',
        'cond_A': 'C1_seam_only',
        'cond_B': 'C3_c5lp_scramble',
        'family': 'primary'
    },
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

def compute_mcnemar(y_true, y_pred_A, y_pred_B):
    """Compute McNemar chi2 with continuity correction and p-value."""
    corr_A = (y_pred_A == y_true)
    corr_B = (y_pred_B == y_true)
    n_10 = np.sum(corr_A & (~corr_B))
    n_01 = np.sum((~corr_A) & corr_B)
    
    if (n_10 + n_01) == 0:
        return 0.0, 1.0, int(n_10), int(n_01)
    
    chi2 = ((abs(n_10 - n_01) - 1.0) ** 2) / (n_10 + n_01)
    from scipy.stats import chi2 as chi2_dist
    p_val = float(1.0 - chi2_dist.cdf(chi2, df=1))
    return float(chi2), p_val, int(n_10), int(n_01)

def main():
    print(f"Loading predictions from {INPUT_CSV}...", flush=True)
    df = pd.read_csv(INPUT_CSV)
    
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
        
        print(f"Scenario {scen}: {K} unique clusters, {len(scen_df)} total prediction rows.", flush=True)
        
        # Precompute per-cluster confusion matrices for each condition
        cluster_cms = {}
        for cond in ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']:
            c_df = scen_df[scen_df['condition'] == cond].sort_values('sample_id')
            c_cms = np.zeros((K, 3, 3), dtype=np.int64)
            for c_idx, group in c_df.groupby('c_idx'):
                c_cms[c_idx] = compute_cm(group['true_label'].values, group['pred_label'].values)
            cluster_cms[cond] = c_cms
        
        # Generate shared cluster resampling indices for this scenario (B x K)
        boot_indices = rng.choice(K, size=(B_REPLICATES, K), replace=True)
        
        # Count occurrences of each cluster in each replicate: (B x K)
        # Using bincount row by row
        boot_weights = np.zeros((B_REPLICATES, K), dtype=np.int32)
        for b in range(B_REPLICATES):
            boot_weights[b] = np.bincount(boot_indices[b], minlength=K)
            
        print(f"  Weights generated for B={B_REPLICATES}. Running paired contrasts...", flush=True)
        
        # For each contrast
        for c_def in CONTRASTS:
            cid = c_def['contrast_id']
            cond_A = c_def['cond_A']
            cond_B = c_def['cond_B']
            
            # Full cohort point estimates
            cm_A_full = cluster_cms[cond_A].sum(axis=0)
            cm_B_full = cluster_cms[cond_B].sum(axis=0)
            f1_A_full, class_f1_A = f1_from_cm(cm_A_full)
            f1_B_full, class_f1_B = f1_from_cm(cm_B_full)
            point_delta = f1_A_full - f1_B_full
            
            # McNemar
            sub_A = scen_df[scen_df['condition'] == cond_A].sort_values('sample_id')
            sub_B = scen_df[scen_df['condition'] == cond_B].sort_values('sample_id')
            chi2_val, mcnemar_p, n_10, n_01 = compute_mcnemar(
                sub_A['true_label'].values,
                sub_A['pred_label'].values,
                sub_B['pred_label'].values
            )
            
            # Bootstrap evaluation
            cms_A_boot = np.tensordot(boot_weights, cluster_cms[cond_A], axes=([1], [0]))  # (B, 3, 3)
            cms_B_boot = np.tensordot(boot_weights, cluster_cms[cond_B], axes=([1], [0]))  # (B, 3, 3)
            
            deltas = np.zeros(B_REPLICATES, dtype=np.float64)
            class_deltas = np.zeros((B_REPLICATES, 3), dtype=np.float64)
            invalid_reps = 0
            
            for b in range(B_REPLICATES):
                f1_a, cls_a = f1_from_cm(cms_A_boot[b])
                f1_b, cls_b = f1_from_cm(cms_B_boot[b])
                deltas[b] = f1_a - f1_b
                for c in range(3):
                    class_deltas[b, c] = cls_a[c] - cls_b[c]
            
            ci_lower = float(np.percentile(deltas, 2.5))
            ci_upper = float(np.percentile(deltas, 97.5))
            
            # Finite-sample corrected bootstrap p-value
            if point_delta >= 0:
                p_one_sided = (np.sum(deltas <= 0) + 1) / (B_REPLICATES + 1)
            else:
                p_one_sided = (np.sum(deltas >= 0) + 1) / (B_REPLICATES + 1)
            raw_p_val = float(min(1.0, 2.0 * p_one_sided))
            
            results.append({
                'scenario': scen,
                'contrast_id': cid,
                'description': c_def['desc'],
                'hypothesis_family': c_def['family'],
                'condition_A': cond_A,
                'condition_B': cond_B,
                'macro_f1_A': f1_A_full,
                'macro_f1_B': f1_B_full,
                'signed_difference_A_minus_B': point_delta,
                'bootstrap_ci_lower': ci_lower,
                'bootstrap_ci_upper': ci_upper,
                'bootstrap_replicates': B_REPLICATES,
                'invalid_replicates': invalid_reps,
                'patient_clusters': K,
                'raw_bootstrap_p_value': raw_p_val,
                'mcnemar_chi2': chi2_val,
                'mcnemar_p_value': mcnemar_p,
                'mcnemar_n_10': n_10,
                'mcnemar_n_01': n_01,
                'se_bootstrap': float(np.std(deltas, ddof=1))
            })
            
            for c_idx, c_name in enumerate(['meningioma', 'glioma', 'pituitary']):
                class_results.append({
                    'scenario': scen,
                    'contrast_id': cid,
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
    
    # Apply Holm-Bonferroni correction across all 15 contrasts
    # Sort by raw p-value
    res_df = res_df.sort_values('raw_bootstrap_p_value').reset_index(drop=True)
    M = len(res_df)
    adj_p = np.zeros(M, dtype=np.float64)
    running_max = 0.0
    for i in range(M):
        p_val = res_df.loc[i, 'raw_bootstrap_p_value']
        mult = (M - i)
        val = min(1.0, mult * p_val)
        running_max = max(running_max, val)
        adj_p[i] = running_max
    res_df['holm_adjusted_p_value'] = adj_p
    res_df['holm_fwer_status'] = res_df['holm_adjusted_p_value'].apply(
        lambda p: 'REJECT_H0 (Significant after Holm FWER)' if p < 0.05 else 'FAIL_TO_REJECT (Not significant)'
    )
    
    # Also order back by scenario and contrast
    order_map = {f"{r['scenario']}_{r['contrast_id']}": idx for idx, r in enumerate(results)}
    res_df['sort_key'] = res_df.apply(lambda r: order_map[f"{r['scenario']}_{r['contrast_id']}"], axis=1)
    res_df = res_df.sort_values('sort_key').drop(columns=['sort_key']).reset_index(drop=True)
    
    out_path = OUTPUT_DIR / 'task5_synchronized_bootstrap_b25000.csv'
    res_df.to_csv(out_path, index=False)
    print(f"Task 5 results saved to {out_path} in {time.time() - t0:.2f}s", flush=True)
    
    class_df = pd.DataFrame(class_results)
    class_out_path = OUTPUT_DIR / 'task5_class_stratified_bootstrap.csv'
    class_df.to_csv(class_out_path, index=False)
    print(f"Task 5 class-stratified results saved to {class_out_path}", flush=True)

if __name__ == '__main__':
    main()
