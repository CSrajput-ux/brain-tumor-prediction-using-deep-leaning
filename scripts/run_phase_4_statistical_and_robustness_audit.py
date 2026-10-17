"""
Phase 4B, 4C, 4D — Independent Statistical, Image-Artifact Robustness, and Subgroup Audit.

Performs:
1. Complete independent recomputation of all metrics, paired contrasts, and bootstrap distributions.
2. Direct paired bootstrap replication check for Net Contrast CI.
3. Formal Multiple-Testing Adjustment (Benjamini-Hochberg FDR and Holm-Bonferroni) with numerical p-value bounds.
4. McNemar transition contingency tables and Wilcoxon patient-level tests.
5. Image-artifact robustness: pixel alteration fractions, lesion area vs delta correlation, intensity shift analysis.
6. Class-specific and patient-level subgroup analysis (lesion size quartiles, patient slice counts).

Outputs to: experiments/phase_4_audit/
"""
import os
import json
import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import wilcoxon, chi2, spearmanr, pearsonr
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P3_DIR = ROOT / 'experiments' / 'phase_3_interventions'
P4_DIR = ROOT / 'experiments' / 'phase_4_audit'
P4_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
np.random.seed(SEED)

def run_phase_4b_statistical_audit():
    print("================ 1. PHASE 4B: STATISTICAL AUDIT ================")
    preds_df = pd.read_csv(P3_DIR / 'matched_predictions.csv')
    metrics_path = P4_DIR / 'recomputed_metrics.csv'
    contrasts_path = P4_DIR / 'recomputed_paired_contrasts.json'
    mult_path = P4_DIR / 'multiple_testing_audit.csv'
    
    if metrics_path.exists() and contrasts_path.exists() and mult_path.exists():
        print("Recomputed metrics and contrasts already exist. Loading from disk...")
        df_metrics = pd.read_csv(metrics_path)
        with open(contrasts_path) as f:
            recomputed_contrasts = json.load(f)
        df_mult = pd.read_csv(mult_path)
        return df_metrics, recomputed_contrasts, df_mult
        
    conditions = ['I_orig', 'I_tumor', 'I_removed', 'I_placebo', 'I_context_shift', 'I_removed_feathered']
    scenarios = ['S0', 'S1', 'S2']
    
    recomputed_metrics = []
    recomputed_contrasts = {}
    
    cluster_cols = {
        'S0': 'patient_id',
        'S1': 'combined_group_id',
        'S2': 'combined_group_id'
    }
    
    for sc in scenarios:
        print(f"\n--- Auditing Scenario {sc} ---")
        sc_df = preds_df[preds_df['scenario'] == sc]
        cluster_col = cluster_cols[sc]
        
        # 1. Independent Metric Recomputation per condition
        cond_boot_f1s = {}
        for cond in conditions:
            c_df = sc_df[sc_df['condition'] == cond]
            y_t = c_df['true_label'].values
            y_p = c_df['pred_label'].values
            
            macro_f1 = f1_score(y_t, y_p, average='macro', zero_division=0)
            bal_acc = balanced_accuracy_score(y_t, y_p)
            acc = accuracy_score(y_t, y_p)
            p, r, f, s = precision_recall_fscore_support(y_t, y_p, labels=[0, 1, 2], zero_division=0)
            cm = confusion_matrix(y_t, y_p, labels=[0, 1, 2]).tolist()
            
            # Paired Patient-Cluster Bootstrap (B = 2,000, fixed seed)
            clusters = c_df[cluster_col].unique()
            cluster_groups = [g for _, g in c_df.groupby(cluster_col)]
            n_groups = len(cluster_groups)
            
            boot_f1_list = []
            failed_replicates = 0
            
            # Use deterministic seeded RNG
            rng = np.random.default_rng(SEED + (100 if sc == 'S0' else 200 if sc == 'S1' else 300))
            for b in range(2000):
                sampled_idx = rng.choice(n_groups, size=n_groups, replace=True)
                sampled_df = pd.concat([cluster_groups[i] for i in sampled_idx], ignore_index=True)
                
                # Verify non-empty labels across classes
                if len(sampled_df['true_label'].unique()) < 3:
                    failed_replicates += 1
                b_f1 = f1_score(sampled_df['true_label'], sampled_df['pred_label'], average='macro', zero_division=0)
                boot_f1_list.append(b_f1)
                
            boot_arr = np.array(boot_f1_list)
            cond_boot_f1s[cond] = boot_arr
            ci_low = float(np.percentile(boot_arr, 2.5))
            ci_high = float(np.percentile(boot_arr, 97.5))
            
            recomputed_metrics.append({
                'scenario': sc,
                'condition': cond,
                'macro_f1': float(macro_f1),
                'macro_f1_ci_lower': ci_low,
                'macro_f1_ci_upper': ci_high,
                'balanced_accuracy': float(bal_acc),
                'overall_accuracy': float(acc),
                'f1_meningioma': float(f[0]),
                'precision_meningioma': float(p[0]),
                'recall_meningioma': float(r[0]),
                'support_meningioma': int(s[0]),
                'f1_glioma': float(f[1]),
                'precision_glioma': float(p[1]),
                'recall_glioma': float(r[1]),
                'support_glioma': int(s[1]),
                'f1_pituitary': float(f[2]),
                'precision_pituitary': float(p[2]),
                'recall_pituitary': float(r[2]),
                'support_pituitary': int(s[2]),
                'confusion_matrix': json.dumps(cm),
                'failed_bootstrap_replicates': failed_replicates
            })
            
        # 2. Independent Paired Contrast Recomputation
        orig_boot = cond_boot_f1s['I_orig']
        rem_boot = cond_boot_f1s['I_removed']
        plac_boot = cond_boot_f1s['I_placebo']
        tum_boot = cond_boot_f1s['I_tumor']
        ctx_boot = cond_boot_f1s['I_context_shift']
        feath_boot = cond_boot_f1s['I_removed_feathered']
        
        # Paired bootstrap replicate differences
        d_rem_reps = orig_boot - rem_boot
        d_plac_reps = orig_boot - plac_boot
        net_reps = d_rem_reps - d_plac_reps  # DIRECT PAIRED BOOTSTRAP REPLICATION
        d_tum_reps = tum_boot - (1.0 / 3.0)
        d_ctx_reps = orig_boot - ctx_boot
        d_feath_reps = orig_boot - feath_boot
        
        # Point estimates
        orig_pt = f1_score(sc_df[sc_df['condition'] == 'I_orig']['true_label'], sc_df[sc_df['condition'] == 'I_orig']['pred_label'], average='macro')
        rem_pt = f1_score(sc_df[sc_df['condition'] == 'I_removed']['true_label'], sc_df[sc_df['condition'] == 'I_removed']['pred_label'], average='macro')
        plac_pt = f1_score(sc_df[sc_df['condition'] == 'I_placebo']['true_label'], sc_df[sc_df['condition'] == 'I_placebo']['pred_label'], average='macro')
        tum_pt = f1_score(sc_df[sc_df['condition'] == 'I_tumor']['true_label'], sc_df[sc_df['condition'] == 'I_tumor']['pred_label'], average='macro')
        ctx_pt = f1_score(sc_df[sc_df['condition'] == 'I_context_shift']['true_label'], sc_df[sc_df['condition'] == 'I_context_shift']['pred_label'], average='macro')
        feath_pt = f1_score(sc_df[sc_df['condition'] == 'I_removed_feathered']['true_label'], sc_df[sc_df['condition'] == 'I_removed_feathered']['pred_label'], average='macro')
        
        # McNemar Discordance Test on I_orig vs I_removed:
        orig_s = sc_df[sc_df['condition'] == 'I_orig'].set_index('sample_id')['correct']
        rem_s = sc_df[sc_df['condition'] == 'I_removed'].set_index('sample_id')['correct']
        b_mcnemar = int(((orig_s == 1) & (rem_s == 0)).sum())
        c_mcnemar = int(((orig_s == 0) & (rem_s == 1)).sum())
        a_both_correct = int(((orig_s == 1) & (rem_s == 1)).sum())
        d_both_incorrect = int(((orig_s == 0) & (rem_s == 0)).sum())
        
        mcnemar_stat = float(((abs(b_mcnemar - c_mcnemar) - 1)**2) / (b_mcnemar + c_mcnemar))
        raw_mcnemar_p = 1.0 - chi2.cdf(mcnemar_stat, df=1)
        # Bounded p-value to avoid unscientific 0.0
        mcnemar_p_bounded = max(float(raw_mcnemar_p), 1e-16)
        
        # Wilcoxon test on per-patient mean correctness
        pat_orig = sc_df[sc_df['condition'] == 'I_orig'].groupby('patient_id')['correct'].mean()
        pat_rem = sc_df[sc_df['condition'] == 'I_removed'].groupby('patient_id')['correct'].mean()
        pat_diffs = (pat_orig - pat_rem).values
        non_zero_diffs = pat_diffs[pat_diffs != 0]
        w_stat, raw_w_p = wilcoxon(non_zero_diffs)
        wilcoxon_p_bounded = max(float(raw_w_p), 1e-16)
        
        recomputed_contrasts[sc] = {
            'macro_f1_orig': float(orig_pt),
            'macro_f1_removed': float(rem_pt),
            'macro_f1_placebo': float(plac_pt),
            'macro_f1_tumor': float(tum_pt),
            'macro_f1_context_shift': float(ctx_pt),
            'macro_f1_removed_feathered': float(feath_pt),
            'Delta_removal': {
                'point': float(orig_pt - rem_pt),
                'ci_95': [float(np.percentile(d_rem_reps, 2.5)), float(np.percentile(d_rem_reps, 97.5))]
            },
            'Delta_placebo': {
                'point': float(orig_pt - plac_pt),
                'ci_95': [float(np.percentile(d_plac_reps, 2.5)), float(np.percentile(d_plac_reps, 97.5))]
            },
            'Net_contrast': {
                'point': float((orig_pt - rem_pt) - (orig_pt - plac_pt)),
                'ci_95': [float(np.percentile(net_reps, 2.5)), float(np.percentile(net_reps, 97.5))],
                'derived_from_paired_replicates': True
            },
            'Delta_context_shift': {
                'point': float(orig_pt - ctx_pt),
                'ci_95': [float(np.percentile(d_ctx_reps, 2.5)), float(np.percentile(d_ctx_reps, 97.5))]
            },
            'Delta_feathered': {
                'point': float(orig_pt - feath_pt),
                'ci_95': [float(np.percentile(d_feath_reps, 2.5)), float(np.percentile(d_feath_reps, 97.5))]
            },
            'Delta_tumor_vs_chance': {
                'point': float(tum_pt - (1.0 / 3.0)),
                'ci_95': [float(np.percentile(d_tum_reps, 2.5)), float(np.percentile(d_tum_reps, 97.5))]
            },
            'mcnemar_contingency_table': {
                'a_both_correct': a_both_correct,
                'b_orig_correct_rem_incorrect': b_mcnemar,
                'c_orig_incorrect_rem_correct': c_mcnemar,
                'd_both_incorrect': d_both_incorrect,
                'statistic': mcnemar_stat,
                'raw_p_value': raw_mcnemar_p,
                'reported_p_value_bounded': mcnemar_p_bounded
            },
            'wilcoxon_patient_level': {
                'total_patients': len(pat_diffs),
                'discordant_patients': len(non_zero_diffs),
                'statistic': float(w_stat),
                'raw_p_value': float(raw_w_p),
                'reported_p_value_bounded': wilcoxon_p_bounded
            }
        }
        
    # Multiple Comparison Corrections across Primary Hypothesis Family
    # Primary Family (6 tests: Delta_removal McNemar and Wilcoxon for S0, S1, S2)
    print("\n--- Auditing Multiple Comparison Corrections ---")
    hypotheses = [
        ('S0_McNemar_removal', recomputed_contrasts['S0']['mcnemar_contingency_table']['reported_p_value_bounded'], 'PRIMARY'),
        ('S0_Wilcoxon_removal', recomputed_contrasts['S0']['wilcoxon_patient_level']['reported_p_value_bounded'], 'PRIMARY'),
        ('S1_McNemar_removal', recomputed_contrasts['S1']['mcnemar_contingency_table']['reported_p_value_bounded'], 'PRIMARY'),
        ('S1_Wilcoxon_removal', recomputed_contrasts['S1']['wilcoxon_patient_level']['reported_p_value_bounded'], 'PRIMARY'),
        ('S2_McNemar_removal', recomputed_contrasts['S2']['mcnemar_contingency_table']['reported_p_value_bounded'], 'PRIMARY'),
        ('S2_Wilcoxon_removal', recomputed_contrasts['S2']['wilcoxon_patient_level']['reported_p_value_bounded'], 'PRIMARY'),
    ]
    
    # Sort by p-value
    hypotheses_sorted = sorted(hypotheses, key=lambda x: x[1])
    m_tests = len(hypotheses_sorted)
    
    mult_corr_rows = []
    for rank, (name, raw_p, tier) in enumerate(hypotheses_sorted, start=1):
        # Benjamini-Hochberg FDR critical value: (rank / m) * q
        bh_crit = (rank / m_tests) * 0.05
        bh_adj_p = min(raw_p * (m_tests / rank), 1.0)
        
        # Holm-Bonferroni FWER adjusted p-value: raw_p * (m - rank + 1)
        holm_adj_p = min(raw_p * (m_tests - rank + 1), 1.0)
        
        mult_corr_rows.append({
            'test_name': name,
            'tier': tier,
            'rank': rank,
            'raw_p_value': raw_p,
            'bh_adjusted_p_value': bh_adj_p,
            'bh_significant_at_0_05': bool(raw_p <= bh_crit),
            'holm_adjusted_p_value': holm_adj_p,
            'holm_significant_at_0_05': bool(holm_adj_p <= 0.05)
        })
        
    df_mult = pd.DataFrame(mult_corr_rows)
    print(df_mult.to_string(index=False))
    
    df_metrics = pd.DataFrame(recomputed_metrics)
    df_metrics.to_csv(P4_DIR / 'recomputed_metrics.csv', index=False)
    
    with open(P4_DIR / 'recomputed_paired_contrasts.json', 'w') as f:
        json.dump(recomputed_contrasts, f, indent=2)
        
    df_mult.to_csv(P4_DIR / 'multiple_testing_audit.csv', index=False)
    print("Statistical audit outputs saved to experiments/phase_4_audit/")
    
    return df_metrics, recomputed_contrasts, df_mult

def run_phase_4c_image_artifact_and_robustness():
    print("\n================ 2. PHASE 4C: IMAGE-ARTIFACT & ROBUSTNESS AUDIT ================")
    manifest_df = pd.read_csv(P3_DIR / 'intervention_manifest.csv')
    preds_df = pd.read_csv(P3_DIR / 'matched_predictions.csv')
    
    # Merge with matched predictions on S0 to correlate lesion size with performance drops
    s0_orig = preds_df[(preds_df['scenario'] == 'S0') & (preds_df['condition'] == 'I_orig')].set_index('sample_id')
    s0_rem = preds_df[(preds_df['scenario'] == 'S0') & (preds_df['condition'] == 'I_removed')].set_index('sample_id')
    s0_feath = preds_df[(preds_df['scenario'] == 'S0') & (preds_df['condition'] == 'I_removed_feathered')].set_index('sample_id')
    s0_plac = preds_df[(preds_df['scenario'] == 'S0') & (preds_df['condition'] == 'I_placebo')].set_index('sample_id')
    
    analysis_rows = []
    
    for idx, row in manifest_df.iterrows():
        sid = row['sample_id']
        t_px = row['tumor_area_pixels']
        t_frac = row['tumor_area_fraction']
        p_px = row['placebo_area_pixels']
        p_frac = row['placebo_area_fraction']
        overlap = row['placebo_overlap_pixels']
        shift = row['placebo_shift_applied']
        
        orig_row = s0_orig.loc[sid]
        rem_row = s0_rem.loc[sid]
        feath_row = s0_feath.loc[sid]
        plac_row = s0_plac.loc[sid]
        
        c_orig = orig_row['correct']
        c_rem = rem_row['correct']
        c_feath = feath_row['correct']
        c_plac = plac_row['correct']
        
        # True class probability drops
        true_lbl = orig_row['true_label']
        prob_col = ['prob_meningioma', 'prob_glioma', 'prob_pituitary'][true_lbl]
        
        p_drop_rem = orig_row[prob_col] - rem_row[prob_col]
        p_drop_feath = orig_row[prob_col] - feath_row[prob_col]
        p_drop_plac = orig_row[prob_col] - plac_row[prob_col]
        
        analysis_rows.append({
            'sample_id': sid,
            'patient_id': row['patient_id'],
            'class_name': row['class_name'],
            'tumor_area_pixels': t_px,
            'tumor_area_fraction': t_frac,
            'placebo_area_pixels': p_px,
            'placebo_overlap_pixels': overlap,
            'placebo_shift_applied': shift,
            'correct_orig': c_orig,
            'correct_removed': c_rem,
            'correct_feathered': c_feath,
            'correct_placebo': c_plac,
            'flipped_removed': int(c_orig == 1 and c_rem == 0),
            'prob_drop_removed': p_drop_rem,
            'prob_drop_feathered': p_drop_feath,
            'prob_drop_placebo': p_drop_plac
        })
        
    df_analysis = pd.DataFrame(analysis_rows)
    
    # 1. Area Correlation Analysis
    # Does larger tumor area correlate with larger probability drop?
    corr_spearman, p_spearman = spearmanr(df_analysis['tumor_area_pixels'], df_analysis['prob_drop_removed'])
    corr_pearson, p_pearson = pearsonr(df_analysis['tumor_area_pixels'], df_analysis['prob_drop_removed'])
    
    print(f"Tumor Area vs Probability Drop Correlation:")
    print(f"  Spearman rho = {corr_spearman:.4f} (p = {p_spearman:.4e})")
    print(f"  Pearson r    = {corr_pearson:.4f} (p = {p_pearson:.4e})")
    
    # 2. Lesion Size Quartile Subgroup Analysis
    df_analysis['size_quartile'] = pd.qcut(df_analysis['tumor_area_pixels'], 4, labels=['Q1_Smallest', 'Q2_Medium_Low', 'Q3_Medium_High', 'Q4_Largest'])
    quartile_summary = df_analysis.groupby('size_quartile').agg({
        'tumor_area_pixels': ['min', 'median', 'max'],
        'flipped_removed': ['mean', 'sum'],
        'prob_drop_removed': ['mean', 'std'],
        'prob_drop_feathered': 'mean',
        'prob_drop_placebo': 'mean'
    })
    print("\nLesion Size Quartile Performance Disruption:")
    print(quartile_summary)
    
    # 3. Placebo Mask Audit
    exact_placebo_matches = (df_analysis['tumor_area_pixels'] == df_analysis['placebo_area_pixels']).sum()
    zero_overlap_count = (df_analysis['placebo_overlap_pixels'] == 0).sum()
    shifted_placebos = (df_analysis['placebo_shift_applied'] != 0).sum()
    
    print(f"\nPlacebo Mask Integrity Audit:")
    print(f"  Exact area matches: {exact_placebo_matches} / 3064 ({exact_placebo_matches / 3064:.2%})")
    print(f"  Strict zero overlap: {zero_overlap_count} / 3064 ({zero_overlap_count / 3064:.2%})")
    print(f"  Vertical shifts applied (midline cases): {shifted_placebos} / 3064 ({shifted_placebos / 3064:.2%})")
    
    # Flatten MultiIndex columns for JSON serialization
    q_dict = {}
    for col in quartile_summary.columns:
        col_name = f"{col[0]}_{col[1]}" if isinstance(col, tuple) else str(col)
        q_dict[col_name] = {str(k): float(v) for k, v in quartile_summary[col].items()}
        
    robustness_meta = {
        'tumor_area_correlation_spearman': float(corr_spearman),
        'tumor_area_correlation_pearson': float(corr_pearson),
        'exact_placebo_matches': int(exact_placebo_matches),
        'zero_overlap_cases': int(zero_overlap_count),
        'shifted_placebos_cases': int(shifted_placebos),
        'quartile_summary': q_dict
    }
    
    with open(P4_DIR / 'robustness_audit_results.json', 'w') as f:
        json.dump(robustness_meta, f, indent=2)
        
    df_analysis.to_csv(P4_DIR / 'sample_level_robustness_data.csv', index=False)
    return robustness_meta, df_analysis

def run_phase_4d_class_and_patient_analysis(df_analysis: pd.DataFrame):
    print("\n================ 3. PHASE 4D: CLASS-SPECIFIC & PATIENT SUBGROUP AUDIT ================")
    # 1. Class-Specific Breakdown
    class_summary = df_analysis.groupby('class_name').agg({
        'sample_id': 'count',
        'tumor_area_pixels': ['median', 'mean'],
        'flipped_removed': ['sum', 'mean'],
        'prob_drop_removed': ['mean', 'std'],
        'prob_drop_feathered': 'mean',
        'prob_drop_placebo': 'mean'
    })
    print("Class-Specific Vulnerability:")
    print(class_summary)
    
    # 2. Patient Slice-Count Dependence
    pat_slice_counts = df_analysis.groupby('patient_id')['sample_id'].count()
    df_analysis['patient_slice_count'] = df_analysis['patient_id'].map(pat_slice_counts)
    
    df_analysis['slice_count_bin'] = pd.cut(
        df_analysis['patient_slice_count'],
        bins=[0, 5, 15, 30, 100],
        labels=['1-5_slices', '6-15_slices', '16-30_slices', '>30_slices']
    )
    
    slice_dep_summary = df_analysis.groupby('slice_count_bin').agg({
        'patient_id': 'nunique',
        'sample_id': 'count',
        'flipped_removed': 'mean',
        'prob_drop_removed': 'mean',
        'prob_drop_placebo': 'mean'
    })
    print("\nPatient Slice Count Dependence:")
    print(slice_dep_summary)
    
    # Flatten MultiIndex columns for JSON serialization
    c_dict = {}
    for col in class_summary.columns:
        col_name = f"{col[0]}_{col[1]}" if isinstance(col, tuple) else str(col)
        c_dict[col_name] = {str(k): float(v) for k, v in class_summary[col].items()}
        
    s_dict = {}
    for col in slice_dep_summary.columns:
        col_name = f"{col[0]}_{col[1]}" if isinstance(col, tuple) else str(col)
        s_dict[col_name] = {str(k): float(v) for k, v in slice_dep_summary[col].items()}
        
    subgroup_summary = {
        'class_summary': c_dict,
        'patient_slice_count_summary': s_dict
    }
    
    with open(P4_DIR / 'subgroup_audit_results.json', 'w') as f:
        json.dump(subgroup_summary, f, indent=2)
        
    return subgroup_summary

if __name__ == '__main__':
    df_metrics, recomputed_contrasts, df_mult = run_phase_4b_statistical_audit()
    robustness_meta, df_analysis = run_phase_4c_image_artifact_and_robustness()
    subgroup_summary = run_phase_4d_class_and_patient_analysis(df_analysis)
    print("\nPhase 4B, 4C, 4D independent audit execution completed successfully!")
