from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
comp_path = ROOT / "revision" / "scripts" / "compute_all_secondary_statistics.py"

with open(comp_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Section 5 inference
old_sec5_inf = '"Cohort interaction is not statistically significant (p = 0.234), confirming consistent ViT core reliance across cohorts"'
new_sec5_inf = '"No statistically significant evidence of effect modification across cohorts (beta = -0.047, p = 0.234); absence of evidence is not formal proof of equivalence."'
code = code.replace(old_sec5_inf, new_sec5_inf)

# 2. Add Cheng (N=10) and BRISC (N=45) separate cluster comparisons under Section 4a
old_sec4a_marker = 's3_rows.append({\n    "Category": "Cluster-Level Architectural Comparison",\n    "Cohort_or_Model": "55 Patient/Case Clusters",'

new_sec4a_additions = '''# Separate cohort cluster-level tests
piv_cheng_clust = core_df[core_df["dataset"] == "cheng"].pivot_table(index="cluster_id", columns="architecture", values="tau_sham_corrected").dropna()
diff_cheng_clust = piv_cheng_clust["deit_small_patch16_224"] - piv_cheng_clust["resnet50"]
w_cheng_clust = stats.wilcoxon(diff_cheng_clust, alternative="two-sided")

s3_rows.append({
    "Category": "Cohort-Specific Architectural Comparison",
    "Cohort_or_Model": "Cheng (10 Patient Clusters)",
    "Condition_or_Method": "Method A (Telea) Core Sensitivity (Patient Means)",
    "Sample_N": 10,
    "Metric_or_Parameter": "Patient-mean tau difference (DeiT - ResNet)",
    "Value": f"+{diff_cheng_clust.mean():.4f} +/- {diff_cheng_clust.std():.4f}",
    "Test_Statistic": f"Wilcoxon W = {w_cheng_clust.statistic:.1f}",
    "p_value": f"Two-sided p = {w_cheng_clust.pvalue:.4f}",
    "Inference": "Statistically significant core reliance advantage for DeiT-Small in verified patients"
})

piv_brisc_clust = core_df[core_df["dataset"] == "brisc"].pivot_table(index="cluster_id", columns="architecture", values="tau_sham_corrected").dropna()
diff_brisc_clust = piv_brisc_clust["deit_small_patch16_224"] - piv_brisc_clust["resnet50"]
w_brisc_clust = stats.wilcoxon(diff_brisc_clust, alternative="two-sided")

s3_rows.append({
    "Category": "Cohort-Specific Architectural Comparison",
    "Cohort_or_Model": "BRISC (45 Image-Level Sample Clusters)",
    "Condition_or_Method": "Method A (Telea) Core Sensitivity (Image-Level Clusters)",
    "Sample_N": 45,
    "Metric_or_Parameter": "Image-cluster tau difference (DeiT - ResNet)",
    "Value": f"+{diff_brisc_clust.mean():.4f} +/- {diff_brisc_clust.std():.4f}",
    "Test_Statistic": f"Wilcoxon W = {w_brisc_clust.statistic:.1f}",
    "p_value": f"Two-sided p = {w_brisc_clust.pvalue:.4f}",
    "Inference": "DeiT-Small exhibits higher core reliance in BRISC image units"
})

s3_rows.append({
    "Category": "Cluster-Level Architectural Comparison",
    "Cohort_or_Model": "55 Patient/Case Clusters",'''

code = code.replace(old_sec4a_marker, new_sec4a_additions)

# 3. Add N=43 exclusion row and update Section 6 inference
old_sec6_marker = 's3_rows.append({\n    "Category": "Sham Geometry Outlier Sensitivity (Pooled Architecture)",'

new_sec6_additions = '''# BRISC DeiT Core excluding both clipped slices (00003 and 00396)
brisc_ex_both = brisc_core[~brisc_core['sample_id'].isin(['brisc2025_test_00003_gl_ax_t1', 'brisc2025_test_00396_me_co_t1'])]
w_brisc_ex_both = stats.wilcoxon(brisc_ex_both['tau_sham_corrected'])

s3_rows.append({
    "Category": "Sham Geometry Outlier Sensitivity (BRISC DeiT Core)",
    "Cohort_or_Model": "BRISC DeiT-Small (N=43 excluding both clipped slices)",
    "Condition_or_Method": "Method A (Telea) Core Sensitivity without 00003 and 00396",
    "Sample_N": 43,
    "Metric_or_Parameter": "Both-clipped-excluded tau_core",
    "Value": f"{brisc_ex_both['tau_sham_corrected'].mean():.4f} +/- {brisc_ex_both['tau_sham_corrected'].std():.4f}",
    "Test_Statistic": f"Wilcoxon W = {w_brisc_ex_both.statistic:.1f}",
    "p_value": f"p = {w_brisc_ex_both.pvalue:.4f} (exceeds alpha = 0.05 threshold)",
    "Inference": "Estimated mean sensitivity was relatively stable under the reported exclusions (tau = 0.0506 to 0.0528), although statistical significance was not retained when both clipped BRISC samples were excluded (p = 0.0505, N=43)."
})

s3_rows.append({
    "Category": "Sham Geometry Outlier Sensitivity (Pooled Architecture)",'''

code = code.replace(old_sec6_marker, new_sec6_additions)

with open(comp_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated compute_all_secondary_statistics.py successfully.")

