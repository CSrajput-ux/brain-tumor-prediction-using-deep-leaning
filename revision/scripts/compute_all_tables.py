import os, sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from scipy.stats import wilcoxon, ttest_1samp
from statsmodels.stats.multitest import multipletests

ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
REV_DIR = ROOT / "revision"
os.makedirs(REV_DIR / "tables", exist_ok=True)
os.makedirs(REV_DIR / "scripts", exist_ok=True)
os.makedirs(REV_DIR / "reports", exist_ok=True)

eff = pd.read_csv(ROOT / "predictions" / "intervention_effects.csv")
qc = pd.read_csv(ROOT / "manifests" / "intervention_qc.csv")

# -------------------------------------------------------------
# SUPPLEMENTARY TABLE S1: FULL 32 INFERENTIAL REGION COMPARISONS
# -------------------------------------------------------------
def compute_table_s1():
    rows = []
    datasets = ['cheng', 'brisc']
    architectures = ['deit_small_patch16_224', 'resnet50']
    methods = ['telea_inpaint', 'matched_texture_fill']
    regions = ['core', 'immediate', 'outer', 'remote']

    for ds in datasets:
        for arch in architectures:
            for meth in methods:
                for reg in regions:
                    sub = eff[(eff['dataset'] == ds) & (eff['architecture'] == arch) & (eff['method'] == meth) & (eff['region'] == reg)]
                    n = len(sub)
                    delta_raw = sub['delta_raw'].values
                    tau = sub['tau_sham_corrected'].values
                    mean_raw = float(np.mean(delta_raw))
                    sd_raw = float(np.std(delta_raw, ddof=1))
                    mean_tau = float(np.mean(tau))
                    sd_tau = float(np.std(tau, ddof=1))
                    flip_rate = float(np.mean(sub['is_flipped'].astype(int)) * 100.0)
                    
                    diffs = tau
                    non_zero = diffs[diffs != 0]
                    if len(non_zero) > 0:
                        stat, p_val = wilcoxon(tau, alternative='two-sided')
                        p_val = float(p_val)
                    else:
                        p_val = 1.0
                    
                    dz = float(mean_tau / sd_tau) if sd_tau > 0 else 0.0
                    
                    rows.append({
                        'dataset': ds.upper(),
                        'model': 'DeiT-Small' if 'deit' in arch else 'ResNet-50',
                        'method': 'Method A (Telea)' if 'telea' in meth else 'Method B (Texture)',
                        'region': reg.capitalize(),
                        'n': n,
                        'mean_raw': mean_raw,
                        'sd_raw': sd_raw,
                        'mean_tau': mean_tau,
                        'sd_tau': sd_tau,
                        'flip_rate': flip_rate,
                        'raw_p': p_val,
                        'cohen_dz': dz
                    })

    df_s1 = pd.DataFrame(rows)
    # Apply Holm correction across pre-specified 32-test family
    _, p_adj_holm, _, _ = multipletests(df_s1['raw_p'], alpha=0.05, method='holm')
    df_s1['holm_adj_p'] = p_adj_holm
    df_s1.to_csv(REV_DIR / "tables" / "table_s1_inferential_family32.csv", index=False)
    print("Table S1 (32 comparisons) saved successfully.")
    return df_s1

# -------------------------------------------------------------
# TABLE 2: PRIMARY HIGHLIGHTED INFERENTIAL SENSITIVITIES
# -------------------------------------------------------------
def compute_table_2(df_s1):
    # Select primary comparisons representing main text analyses
    # Cheng DeiT Method A (4 regions)
    # Cheng DeiT Method B (Core)
    # Cheng ResNet Method A (Core, Immediate)
    # Cheng ResNet Method B (Core)
    # BRISC DeiT Method A (4 regions)
    # BRISC ResNet Method A (Core)
    # Plus pooled multi-cohort rows (N=90)
    
    # Calculate pooled (N=90) rows
    pooled_rows = []
    for arch in ['deit_small_patch16_224', 'resnet50']:
        sub = eff[(eff['architecture'] == arch) & (eff['method'] == 'telea_inpaint') & (eff['region'] == 'core')]
        n = len(sub)
        mean_raw = float(np.mean(sub['delta_raw']))
        sd_raw = float(np.std(sub['delta_raw'], ddof=1))
        mean_tau = float(np.mean(sub['tau_sham_corrected']))
        sd_tau = float(np.std(sub['tau_sham_corrected'], ddof=1))
        flip_rate = float(np.mean(sub['is_flipped'].astype(int)) * 100.0)
        stat, p_val = wilcoxon(sub['tau_sham_corrected'])
        dz = float(mean_tau / sd_tau)
        pooled_rows.append({
            'Dataset': f'Pooled (N={n})',
            'Model': 'DeiT-Small' if 'deit' in arch else 'ResNet-50',
            'Method': 'Method A (Telea)',
            'Region': 'Core',
            'Raw Sensitivity (Δr)': f"{mean_raw:.4f} ± {sd_raw:.4f}",
            'Sham-Corrected (τr)': f"{mean_tau:.4f} ± {sd_tau:.4f}",
            'Flip Rate': f"{flip_rate:.1f}%",
            'Raw Wilcoxon p': f"{p_val:.2e}" if p_val < 0.001 else f"{p_val:.4f}",
            'Family Holm p': 'N/A (Multi-cohort)',
            'Cohen dz': f"{dz:.3f}"
        })

    # Pick designated rows from S1
    selected_indices = [
        0, 1, 2, 3,  # Cheng DeiT Telea (Core, Immediate, Outer, Remote)
        4,           # Cheng DeiT Texture (Core)
        8, 9,        # Cheng ResNet Telea (Core, Immediate)
        12,          # Cheng ResNet Texture (Core)
        16, 17, 18, 19, # BRISC DeiT Telea (Core, Immediate, Outer, Remote)
        24           # BRISC ResNet Telea (Core)
    ]
    
    t2_rows = []
    for idx in selected_indices:
        r = df_s1.iloc[idx]
        p_raw_str = f"{r['raw_p']:.2e}" if r['raw_p'] < 0.001 else f"{r['raw_p']:.4f}"
        p_holm_str = f"{r['holm_adj_p']:.2e}" if r['holm_adj_p'] < 0.001 else f"{r['holm_adj_p']:.4f}"
        t2_rows.append({
            'Dataset': f"{r['dataset']} (N={r['n']})",
            'Model': r['model'],
            'Method': r['method'],
            'Region': r['region'],
            'Raw Sensitivity (Δr)': f"{r['mean_raw']:.4f} ± {r['sd_raw']:.4f}",
            'Sham-Corrected (τr)': f"{r['mean_tau']:.4f} ± {r['sd_tau']:.4f}",
            'Flip Rate': f"{r['flip_rate']:.1f}%",
            'Raw Wilcoxon p': p_raw_str,
            'Family Holm p': p_holm_str,
            'Cohen dz': f"{r['cohen_dz']:.3f}"
        })
    
    # Append pooled rows
    for pr in pooled_rows:
        t2_rows.append(pr)
        
    df_t2 = pd.DataFrame(t2_rows)
    df_t2.to_csv(REV_DIR / "tables" / "table_2_primary_sensitivity.csv", index=False)
    print("Table 2 saved successfully.")
    return df_t2

# -------------------------------------------------------------
# TABLE 3: IMAGING PLANE STRATIFICATION (BRISC)
# -------------------------------------------------------------
def compute_table_3():
    # Evaluate DeiT-Small Method A on BRISC (15 slices per plane)
    brisc_deit_telea = eff[(eff['dataset'] == 'brisc') & (eff['architecture'] == 'deit_small_patch16_224') & (eff['method'] == 'telea_inpaint')]
    
    t3_rows = []
    for plane in ['axial', 'coronal', 'sagittal']:
        p_sub = brisc_deit_telea[brisc_deit_telea['plane'] == plane]
        n = len(p_sub['sample_id'].unique())
        c_tau = float(p_sub[p_sub['region'] == 'core']['tau_sham_corrected'].mean())
        m_tau = float(p_sub[p_sub['region'] == 'immediate']['tau_sham_corrected'].mean())
        r_tau = float(p_sub[p_sub['region'] == 'remote']['tau_sham_corrected'].mean())
        t3_rows.append([plane.capitalize(), n, c_tau, m_tau, r_tau])
        
    # Add overall BRISC DeiT Telea mean row (matches Table 2 exactly!)
    n_tot = len(brisc_deit_telea['sample_id'].unique())
    c_tot = float(brisc_deit_telea[brisc_deit_telea['region'] == 'core']['tau_sham_corrected'].mean())
    m_tot = float(brisc_deit_telea[brisc_deit_telea['region'] == 'immediate']['tau_sham_corrected'].mean())
    r_tot = float(brisc_deit_telea[brisc_deit_telea['region'] == 'remote']['tau_sham_corrected'].mean())
    t3_rows.append(["Total BRISC Mean (Table 2)", n_tot, c_tot, m_tot, r_tot])
    
    df_t3 = pd.DataFrame(t3_rows, columns=["Acquisition plane", "Sample count (N)", "Mean core τcore", "Mean immediate margin τimmed", "Mean remote τremote"])
    df_t3.to_csv(REV_DIR / "tables" / "table_3_plane_stratification.csv", index=False)
    print("Table 3 computed and saved successfully:")
    print(df_t3.to_string())
    return df_t3

# -------------------------------------------------------------
# TABLE 4: TUMOUR CLASS HETEROGENEITY (CHENG & POOLED)
# -------------------------------------------------------------
def compute_table_4():
    # Class heterogeneity on Cheng (DeiT-Small, Method A; N=15 per class)
    cheng_deit_telea = eff[(eff['dataset'] == 'cheng') & (eff['architecture'] == 'deit_small_patch16_224') & (eff['method'] == 'telea_inpaint')]
    
    t4_rows = []
    for cls in ['glioma', 'meningioma', 'pituitary']:
        c_sub = cheng_deit_telea[cheng_deit_telea['true_class'] == cls]
        n = len(c_sub['sample_id'].unique())
        c_tau = float(c_sub[c_sub['region'] == 'core']['tau_sham_corrected'].mean())
        m_tau = float(c_sub[c_sub['region'] == 'immediate']['tau_sham_corrected'].mean())
        ratio = (m_tau / max(c_tau, 1e-4)) * 100.0
        cls_name = "Glioma" if cls == "glioma" else ("Meningioma" if cls == "meningioma" else "Pituitary adenoma")
        t4_rows.append(["Cheng", cls_name, n, c_tau, m_tau, ratio])
        
    # Overall Cheng DeiT Telea mean row (matches Table 2 exactly!)
    n_tot = len(cheng_deit_telea['sample_id'].unique())
    c_tot = float(cheng_deit_telea[cheng_deit_telea['region'] == 'core']['tau_sham_corrected'].mean())
    m_tot = float(cheng_deit_telea[cheng_deit_telea['region'] == 'immediate']['tau_sham_corrected'].mean())
    ratio_tot = (m_tot / max(c_tot, 1e-4)) * 100.0
    t4_rows.append(["Cheng", "Overall Cheng Mean (Table 2)", n_tot, c_tot, m_tot, ratio_tot])
    
    # Also include Pooled Multi-Cohort breakdown (Cheng + BRISC, N=30 per class)
    deit_telea_all = eff[(eff['architecture'] == 'deit_small_patch16_224') & (eff['method'] == 'telea_inpaint')]
    for cls in ['glioma', 'meningioma', 'pituitary']:
        c_sub = deit_telea_all[deit_telea_all['true_class'] == cls]
        n = len(c_sub['sample_id'].unique())
        c_tau = float(c_sub[c_sub['region'] == 'core']['tau_sham_corrected'].mean())
        m_tau = float(c_sub[c_sub['region'] == 'immediate']['tau_sham_corrected'].mean())
        ratio = (m_tau / max(c_tau, 1e-4)) * 100.0
        cls_name = "Glioma" if cls == "glioma" else ("Meningioma" if cls == "meningioma" else "Pituitary adenoma")
        t4_rows.append(["Pooled Multi-Cohort", cls_name, n, c_tau, m_tau, ratio])
        
    # Pooled Overall Mean
    n_all = len(deit_telea_all['sample_id'].unique())
    c_all = float(deit_telea_all[deit_telea_all['region'] == 'core']['tau_sham_corrected'].mean())
    m_all = float(deit_telea_all[deit_telea_all['region'] == 'immediate']['tau_sham_corrected'].mean())
    ratio_all = (m_all / max(c_all, 1e-4)) * 100.0
    t4_rows.append(["Pooled Multi-Cohort", "Overall Pooled Mean (Table 2)", n_all, c_all, m_all, ratio_all])
    
    df_t4 = pd.DataFrame(t4_rows, columns=["Cohort", "Tumour class", "Sample count (N)", "Core sensitivity (τcore)", "Immediate margin (τimmed)", "Margin-to-core ratio (%)"])
    df_t4.to_csv(REV_DIR / "tables" / "table_4_class_heterogeneity.csv", index=False)
    print("Table 4 computed and saved successfully:")
    print(df_t4.to_string())
    return df_t4

# -------------------------------------------------------------
# SUPPLEMENTARY TABLE S2: REGION AREA & PER-PIXEL SENSITIVITY
# -------------------------------------------------------------
def compute_table_s2():
    qc_unique_masks = qc.drop_duplicates(subset=['sample_id', 'dataset', 'region'])
    
    # Area distributions
    area_rows = []
    for ds in ['cheng', 'brisc', 'Combined (N=120)']:
        sub = qc_unique_masks if ds.startswith('Combined') else qc_unique_masks[qc_unique_masks['dataset'] == ds]
        for reg in ['core', 'immediate', 'outer', 'remote', 'sham']:
            r_sub = sub[sub['region'] == reg]['mask_pixels']
            n = len(r_sub)
            mean_a = float(r_sub.mean())
            sd_a = float(r_sub.std())
            med_a = float(r_sub.median())
            q25, q75 = float(r_sub.quantile(0.25)), float(r_sub.quantile(0.75))
            iqr_a = q75 - q25
            min_a = float(r_sub.min())
            max_a = float(r_sub.max())
            area_rows.append([
                ds.upper(), reg.capitalize(), n, mean_a, sd_a, med_a, iqr_a, min_a, max_a
            ])
            
    df_s2_area = pd.DataFrame(area_rows, columns=["Cohort", "Anatomical Region", "N", "Mean (px)", "SD", "Median", "IQR", "Min", "Max"])
    df_s2_area.to_csv(REV_DIR / "tables" / "table_s2_region_areas.csv", index=False)
    print("Table S2 (Region Areas) saved successfully.")
    
    # Per-pixel sensitivity table
    merged = eff.merge(qc_unique_masks[['sample_id', 'region', 'mask_pixels']], on=['sample_id', 'region'], how='left')
    merged['tau_per_kpx'] = (merged['tau_sham_corrected'] / merged['mask_pixels']) * 1000.0
    deit_telea = merged[(merged['architecture'] == 'deit_small_patch16_224') & (merged['method'] == 'telea_inpaint')]
    
    px_rows = []
    for ds in ['cheng', 'brisc']:
        sub = deit_telea[deit_telea['dataset'] == ds]
        for reg in ['core', 'immediate', 'outer', 'remote', 'sham']:
            r_sub = sub[sub['region'] == reg]
            tau_mean = float(r_sub['tau_sham_corrected'].mean())
            px_mean = float(r_sub['mask_pixels'].mean())
            tau_kpx = float(r_sub['tau_per_kpx'].mean())
            px_rows.append([ds.upper(), reg.capitalize(), len(r_sub), tau_mean, px_mean, tau_kpx])
            
    df_s2_px = pd.DataFrame(px_rows, columns=["Cohort", "Region", "N", "Mean Sham-Corrected τ", "Mean Area (px)", "Sensitivity per 1,000 px"])
    df_s2_px.to_csv(REV_DIR / "tables" / "table_s2_perpixel_sensitivity.csv", index=False)
    print("Table S2 (Per-pixel Sensitivity) saved successfully:")
    print(df_s2_px.to_string())

if __name__ == "__main__":
    df_s1 = compute_table_s1()
    compute_table_2(df_s1)
    compute_table_3()
    compute_table_4()
    compute_table_s2()
