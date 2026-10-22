import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import chi2 as chi2_dist, norm
from scipy.stats import binom as binom_dist
from scipy.special import gammaln, logsumexp

ROOT = Path(__file__).resolve().parent.parent
P9_CSV = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement' / 'matched_predictions.csv'
TRUE_SEAM_CSV = ROOT / 'remaining_work_audit' / 'true_seam_oof_predictions.csv'
OUTPUT_DIR = ROOT / 'remaining_work_audit'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
B_REPLICATES = 25000
SCENARIOS = ['S0', 'S1', 'S2']

# Family definitions:
# Primary confirmatory: 4 contrasts x 3 scenarios = 12 comparisons
# True-seam controls:   4 contrasts x 3 scenarios = 12 comparisons
# Exploratory:          1 contrast  x 3 scenarios = 3  comparisons
CONTRASTS = [
    {'contrast_id': 'C3_vs_C0', 'desc': 'Raw Scrambling Effect', 'cond_A': 'C0_orig', 'cond_B': 'C3_c5lp_scramble', 'family': 'primary_confirmatory'},
    {'contrast_id': 'C1_hist_vs_C0', 'desc': 'Historical Whole-Tile DC-Offset Effect', 'cond_A': 'C0_orig', 'cond_B': 'C1_historical_dc_offset', 'family': 'primary_confirmatory'},
    {'contrast_id': 'C2_vs_C0', 'desc': 'Seam-Suppressed Spatial Rearrangement Effect', 'cond_A': 'C0_orig', 'cond_B': 'C2_seam_suppressed', 'family': 'primary_confirmatory'},
    {'contrast_id': 'C3_vs_C1_hist', 'desc': 'Incremental Scrambling vs Historical DC Offset', 'cond_A': 'C1_historical_dc_offset', 'cond_B': 'C3_c5lp_scramble', 'family': 'primary_confirmatory'},
    {'contrast_id': 'C1_true_w2_vs_C0', 'desc': 'Pure 2-Pixel Boundary Seam Effect', 'cond_A': 'C0_orig', 'cond_B': 'C1_true_seam_w2', 'family': 'true_seam_controls'},
    {'contrast_id': 'C1_true_w3_vs_C0', 'desc': 'Amplified Boundary-Seam Effect (gain 1.8; legacy w3)', 'cond_A': 'C0_orig', 'cond_B': 'C1_true_seam_w3', 'family': 'true_seam_controls'},
    {'contrast_id': 'C3_vs_C1_true_w2', 'desc': 'Incremental Scrambling vs Seam Control (gain 1.0; legacy w2)', 'cond_A': 'C1_true_seam_w2', 'cond_B': 'C3_c5lp_scramble', 'family': 'true_seam_controls'},
    {'contrast_id': 'C2_vs_C1_true_w2', 'desc': 'Spatial Rearrangement vs Seam Control (gain 1.0; legacy w2)', 'cond_A': 'C1_true_seam_w2', 'cond_B': 'C2_seam_suppressed', 'family': 'true_seam_controls'},
    {'contrast_id': 'C3_vs_C2', 'desc': 'Sensitivity to Local Boundary Blending', 'cond_A': 'C2_seam_suppressed', 'cond_B': 'C3_c5lp_scramble', 'family': 'exploratory'},
]


def compute_cm(y_true, y_pred, num_classes=3):
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def f1_from_cm(cm):
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


def compute_mcnemar_exact_logspace(n_10, n_01):
    # ISSUE 1 FIX: Exact two-sided McNemar p-value computed in log space.
    # Convention: N = n_10 + n_01; k = min(n_10, n_01).
    # Two-sided exact binomial tail: sum of probabilities <= P(X=k) under Binomial(N, 0.5).
    # Since Binomial(N, 0.5) is symmetric:
    #   if k < N/2: P = 2 * sum_{i=0}^k (N choose i) * 0.5^N
    #   if k == N/2: P = 1.0 (ties / balanced discordance)
    # Computed robustly in log-space via gammaln and logsumexp to avoid underflow
    # when tail probability is below IEEE-754 float64 subnormal range (~1e-324).
    #
    # Separate output fields:
    #   mcnemar_exact_log10_p  : always-finite log10(p), preserving extreme significance
    #   mcnemar_exact_underflow: True iff IEEE-754 float underflowed to 0.0
    #   mcnemar_exact_binomial_p: exact float (0.0 if underflowed; use log10 field)
    #   mcnemar_asymptotic_chi2_p: Edwards continuity-corrected chi2 p-value (SEPARATE, NEVER substituted)
    #   mcnemar_discordant_n10, mcnemar_discordant_n01: observed discordant pair counts
    N = n_10 + n_01
    if N == 0:
        return 0.0, 1.0, False, 0.0, 1.0, '1.000', n_10, n_01
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

    if exact_underflow:
        p_display = f'< 10^({log10_p_exact:.1f}) [exact log-p; float64 underflow]'
    elif exact_p_float < 1e-15:
        p_display = '< 1e-15'
    else:
        p_display = f'{exact_p_float:.4e}'

    return log10_p_exact, exact_p_float, exact_underflow, chi2_stat, chi2_p, p_display, n_10, n_01


def load_consolidated_predictions():
    p9_df = pd.read_csv(P9_CSV)
    p9_df['condition'] = p9_df['condition'].replace({'C1_seam_only': 'C1_historical_dc_offset'})
    ts_df = pd.read_csv(TRUE_SEAM_CSV)
    common_cols = ['scenario', 'fold', 'condition', 'sample_id', 'cluster_id',
                   'true_label', 'class_name', 'pred_label', 'pred_class',
                   'prob_meningioma', 'prob_glioma', 'prob_pituitary', 'correct']
    return pd.concat([p9_df[common_cols], ts_df[common_cols]], ignore_index=True)


def main():
    print('=' * 75, flush=True)
    print('TASK 5: Synchronized Paired Cluster Bootstrap (B=25,000)', flush=True)
    print('ISSUE 1 FIX: Log-space exact McNemar. chi2 NEVER substituted for exact p.', flush=True)
    print('ISSUE 2 FIX: Bootstrap 95% CI = PRIMARY uncertainty. raw_p = exploratory bound.', flush=True)
    print('=' * 75, flush=True)
    df = load_consolidated_predictions()
    print(f'Total rows: {len(df)} across {df["condition"].nunique()} conditions.', flush=True)
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
        print(f'\nScenario {scen}: {K} clusters, {len(scen_df)} rows.', flush=True)

        cluster_cms = {}
        for cond in df['condition'].unique():
            c_df = scen_df[scen_df['condition'] == cond].sort_values('sample_id')
            c_cms = np.zeros((K, 3, 3), dtype=np.int64)
            for c_idx, group in c_df.groupby('c_idx'):
                c_cms[c_idx] = compute_cm(group['true_label'].values, group['pred_label'].values)
            cluster_cms[cond] = c_cms

        # Resampling unit: patient cluster (S0:233, S1:231, S2:217 clusters).
        # Both conditions in each contrast receive identical cluster draws (paired sync).
        boot_indices = rng.choice(K, size=(B_REPLICATES, K), replace=True)
        boot_weights = np.zeros((B_REPLICATES, K), dtype=np.int32)
        for b in range(B_REPLICATES):
            boot_weights[b] = np.bincount(boot_indices[b], minlength=K)

        for c_def in CONTRASTS:
            cid = c_def['contrast_id']
            cond_A = c_def['cond_A']
            cond_B = c_def['cond_B']
            family = c_def['family']
            cm_A_full = cluster_cms[cond_A].sum(axis=0)
            cm_B_full = cluster_cms[cond_B].sum(axis=0)
            f1_A_full, class_f1_A = f1_from_cm(cm_A_full)
            f1_B_full, class_f1_B = f1_from_cm(cm_B_full)
            point_delta = f1_A_full - f1_B_full

            sub_A = scen_df[scen_df['condition'] == cond_A].sort_values('sample_id')
            sub_B = scen_df[scen_df['condition'] == cond_B].sort_values('sample_id')
            y_true = sub_A['true_label'].values
            corr_A = (sub_A['pred_label'].values == y_true)
            corr_B = (sub_B['pred_label'].values == y_true)
            n_10 = int(np.sum(corr_A & (~corr_B)))
            n_01 = int(np.sum((~corr_A) & corr_B))
            (log10_p_exact, exact_p_float, exact_underflow,
             chi2_val, chi2_p, p_display, _, _) = compute_mcnemar_exact_logspace(n_10, n_01)

            cms_A_boot = np.tensordot(boot_weights, cluster_cms[cond_A], axes=([1], [0]))
            cms_B_boot = np.tensordot(boot_weights, cluster_cms[cond_B], axes=([1], [0]))
            deltas = np.zeros(B_REPLICATES)
            class_deltas = np.zeros((B_REPLICATES, 3))
            for b in range(B_REPLICATES):
                f1_a, cls_a = f1_from_cm(cms_A_boot[b])
                f1_b, cls_b = f1_from_cm(cms_B_boot[b])
                deltas[b] = f1_a - f1_b
                for c in range(3):
                    class_deltas[b, c] = cls_a[c] - cls_b[c]

            # PRIMARY uncertainty: 95% percentile CI
            ci_lower = float(np.percentile(deltas, 2.5))
            ci_upper = float(np.percentile(deltas, 97.5))
            se_boot = float(np.std(deltas, ddof=1))
            # SECONDARY exploratory: Davison-Hinkley bound (NOT a formal null p-value)
            p_one_sided = ((np.sum(deltas <= 0) + 1) / (B_REPLICATES + 1) if point_delta >= 0
                           else (np.sum(deltas >= 0) + 1) / (B_REPLICATES + 1))
            raw_p_empirical = float(min(1.0, 2.0 * p_one_sided))
            z_score = float(point_delta / se_boot) if se_boot > 0 else 0.0
            wald_p = float(2.0 * norm.sf(abs(z_score)))
            wald_p_display = '< 1e-15' if wald_p < 1e-15 else f'{wald_p:.4e}'

            results.append({
                'scenario': scen, 'contrast_id': cid, 'description': c_def['desc'],
                'hypothesis_family': family, 'condition_A': cond_A, 'condition_B': cond_B,
                'macro_f1_A': f1_A_full, 'macro_f1_B': f1_B_full,
                'signed_difference_A_minus_B': point_delta,
                'bootstrap_ci_lower': ci_lower, 'bootstrap_ci_upper': ci_upper,
                'se_bootstrap': se_boot, 'bootstrap_z_score': z_score,
                'wald_asymptotic_p_value': wald_p, 'wald_p_display': wald_p_display,
                'bootstrap_replicates': B_REPLICATES, 'invalid_replicates': 0, 'patient_clusters': K,
                'raw_bootstrap_p_value': raw_p_empirical,
                # Issue 1 canonical McNemar fields
                'mcnemar_exact_log10_p': log10_p_exact,
                'mcnemar_exact_underflow': exact_underflow,
                'mcnemar_exact_binomial_p': exact_p_float,
                'mcnemar_asymptotic_chi2_p': chi2_p,
                'mcnemar_discordant_n10': n_10,
                'mcnemar_discordant_n01': n_01,
                # Legacy backward-compatible fields
                'mcnemar_chi2': chi2_val, 'mcnemar_p_display': p_display,
                'mcnemar_chi2_p_float': chi2_p, 'mcnemar_n_10': n_10, 'mcnemar_n_01': n_01,
                'inference_method': 'synchronized_paired_cluster_bootstrap_percentile_b25000',
            })
            for c_idx, c_name in enumerate(['meningioma', 'glioma', 'pituitary']):
                class_results.append({
                    'scenario': scen, 'contrast_id': cid, 'hypothesis_family': family,
                    'class_name': c_name, 'condition_A': cond_A, 'condition_B': cond_B,
                    'class_f1_A': class_f1_A[c_idx], 'class_f1_B': class_f1_B[c_idx],
                    'signed_delta': class_f1_A[c_idx] - class_f1_B[c_idx],
                    'ci_lower': float(np.percentile(class_deltas[:, c_idx], 2.5)),
                    'ci_upper': float(np.percentile(class_deltas[:, c_idx], 97.5)),
                })

    res_df = pd.DataFrame(results)
    # Holm-Bonferroni FWER within declared families.
    # NOTE: Input p-values are Davison-Hinkley bounds (not formal null p-values).
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
            val = min(1.0, (M - rank) * row['raw_bootstrap_p_value'])
            running_max = max(running_max, val)
            adj_vals[orig_i] = running_max
        for orig_i, adj_p in adj_vals.items():
            res_df.loc[orig_i, 'holm_adjusted_p_value'] = adj_p
            res_df.loc[orig_i, 'holm_family_size'] = M
            res_df.loc[orig_i, 'holm_fwer_status'] = (
                'REJECT_H0 (Significant after Holm FWER)' if adj_p < 0.05
                else 'FAIL_TO_REJECT (Not significant)')

    out_path = OUTPUT_DIR / 'task5_synchronized_bootstrap_b25000.csv'
    res_df.to_csv(out_path, index=False)
    elapsed = time.time() - t0
    print(f'\nResults saved to {out_path} in {elapsed:.2f}s', flush=True)

    uf = res_df[res_df['mcnemar_exact_underflow'] == True]
    print(f'Underflowed rows ({len(uf)}) - use mcnemar_exact_log10_p for these:')
    for _, row in uf.iterrows():
        print(f'  {row.scenario} {row.contrast_id}: log10_p={row.mcnemar_exact_log10_p:.2f} '
              f'n10={row.mcnemar_discordant_n10} n01={row.mcnemar_discordant_n01}')
    if len(uf) == 0:
        print('  None - all exact p representable in IEEE-754 double')

    nuf = res_df[(res_df['mcnemar_exact_underflow'] == False) & (res_df['mcnemar_exact_binomial_p'] != 0.0)]
    susp = nuf[nuf['mcnemar_exact_binomial_p'] == nuf['mcnemar_asymptotic_chi2_p']]
    if len(susp) > 0:
        print(f'CRITICAL WARNING: {len(susp)} rows where exact_p == chi2_p (fallback!)')
        print(susp[['scenario', 'contrast_id', 'mcnemar_exact_binomial_p', 'mcnemar_asymptotic_chi2_p']])
    else:
        print('Verification PASSED: No chi2 fallback substitution detected.')

    pd.DataFrame(class_results).to_csv(OUTPUT_DIR / 'task5_class_stratified_bootstrap.csv', index=False)
    print('Done.', flush=True)


if __name__ == '__main__':
    main()
