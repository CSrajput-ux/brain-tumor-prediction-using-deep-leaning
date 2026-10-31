import os, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
REV_FIG_DIR = ROOT / "revision" / "figures"
os.makedirs(REV_FIG_DIR, exist_ok=True)

# Set clean scientific plotting style
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

# -------------------------------------------------------------------
# Figure 1: Study Design (copy existing verified fig1_study_design.png)
# -------------------------------------------------------------------
# We can copy fig1, fig2, fig3 from figures/
import shutil
shutil.copy(ROOT / "figures" / "fig1_study_design.png", REV_FIG_DIR / "fig1_study_design.png")
shutil.copy(ROOT / "figures" / "fig2_preprocessing_alignment.png", REV_FIG_DIR / "fig2_preprocessing_alignment.png")
shutil.copy(ROOT / "figures" / "fig3_calibration_reliability.png", REV_FIG_DIR / "fig3_calibration_reliability.png")

# -------------------------------------------------------------------
# Figure 4: Intervention & Residual Montage Gallery (old Fig 10)
# -------------------------------------------------------------------
shutil.copy(ROOT / "figures" / "fig10_intervention_gallery.png", REV_FIG_DIR / "fig4_intervention_gallery.png")

# -------------------------------------------------------------------
# Figure 5: Regional Evidence Sensitivity (old Fig 4)
# State pooled N=90 across both cohorts, define error bars (mean +- SEM), define stars
# -------------------------------------------------------------------
def plot_fig5_regional_evidence(out_path: Path):
    # Pooled multi-cohort Method A (Inpainting): DeiT vs ResNet across regions
    # Regions: Core, Immediate, Outer, Remote
    # DeiT: Core 0.0900 (SEM = 0.197/sqrt(90) = 0.0208), Immed 0.0226 (SEM = 0.080/sqrt(90) = 0.0084), Outer 0.0182 (SEM = 0.085/sqrt(90) = 0.0090), Remote 0.0134 (SEM = 0.060/sqrt(90) = 0.0063)
    # ResNet: Core 0.0161 (SEM = 0.046/sqrt(90) = 0.0048), Immed 0.0061 (SEM = 0.039/sqrt(90) = 0.0041), Outer 0.0064 (SEM = 0.071/sqrt(90) = 0.0075), Remote 0.0062 (SEM = 0.027/sqrt(90) = 0.0028)
    regions = ["Tumour Core\n(R_core)", "Immediate Margin\n(R_immediate, 4px)", "Outer Margin\n(R_outer, 12px)", "Remote Context\n(R_remote)"]
    x = np.arange(len(regions))
    width = 0.35
    
    deit_means = [0.0900, 0.0226, 0.0182, 0.0134]
    deit_sems = [0.197/np.sqrt(90), 0.080/np.sqrt(90), 0.085/np.sqrt(90), 0.060/np.sqrt(90)]
    
    resnet_means = [0.0161, 0.0061, 0.0064, 0.0062]
    resnet_sems = [0.046/np.sqrt(90), 0.039/np.sqrt(90), 0.071/np.sqrt(90), 0.027/np.sqrt(90)]
    
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    rects1 = ax.bar(x - width/2, deit_means, width, yerr=deit_sems, capsize=4, label="DeiT-Small (Vision Transformer)", color="#1E88E5", alpha=0.9, edgecolor="#0D47A1", linewidth=0.8)
    rects2 = ax.bar(x + width/2, resnet_means, width, yerr=resnet_sems, capsize=4, label="ResNet-50 (Convolutional Neural Network)", color="#D81B60", alpha=0.9, edgecolor="#880E4F", linewidth=0.8)
    
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.set_ylabel("Sham-Corrected Sensitivity (τ_r = Δ_r - Δ_sham)", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=9.5)
    ax.legend(loc="upper right", fontsize=9, frameon=True)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_ylim(-0.015, 0.125)
    
    # Add significance brackets for DeiT: Core p=7.45e-6 (***), Immed p=0.0166 (*)
    ax.text(x[0] - width/2, deit_means[0] + deit_sems[0] + 0.005, "***", ha="center", fontsize=11, fontweight="bold", color="#0D47A1")
    ax.text(x[1] - width/2, deit_means[1] + deit_sems[1] + 0.005, "*", ha="center", fontsize=11, fontweight="bold", color="#0D47A1")
    ax.text(x[2] - width/2, deit_means[2] + deit_sems[2] + 0.005, "ns", ha="center", fontsize=8.5, color="gray")
    ax.text(x[3] - width/2, deit_means[3] + deit_sems[3] + 0.005, "ns", ha="center", fontsize=8.5, color="gray")
    
    # ResNet: Core p=0.0026 (**)
    ax.text(x[0] + width/2, resnet_means[0] + resnet_sems[0] + 0.005, "**", ha="center", fontsize=11, fontweight="bold", color="#880E4F")
    ax.text(x[1] + width/2, resnet_means[1] + resnet_sems[1] + 0.005, "ns", ha="center", fontsize=8.5, color="gray")
    ax.text(x[2] + width/2, resnet_means[2] + resnet_sems[2] + 0.005, "ns", ha="center", fontsize=8.5, color="gray")
    ax.text(x[3] + width/2, resnet_means[3] + resnet_sems[3] + 0.005, "ns", ha="center", fontsize=8.5, color="gray")
    
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

plot_fig5_regional_evidence(REV_FIG_DIR / "fig5_regional_evidence_effects.png")

# -------------------------------------------------------------------
# Figure 6: Architecture Comparison (old Fig 5)
# -------------------------------------------------------------------
shutil.copy(ROOT / "figures" / "fig5_architecture_comparison.png", REV_FIG_DIR / "fig6_architecture_comparison.png")

# -------------------------------------------------------------------
# Figure 7: Perturbation Method Concordance (old Fig 6)
# -------------------------------------------------------------------
shutil.copy(ROOT / "figures" / "fig6_method_robustness.png", REV_FIG_DIR / "fig7_method_robustness.png")

# -------------------------------------------------------------------
# Figure 8: Plane Stratification (old Fig 7)
# -------------------------------------------------------------------
def plot_fig8_plane_stratification(out_path: Path):
    planes = ["Axial (N=15)", "Coronal (N=15)", "Sagittal (N=15)"]
    x = np.arange(len(planes))
    width = 0.25
    
    # From Table 3: DeiT Telea on BRISC
    core_tau = [0.0492, 0.0370, 0.0690]
    immed_tau = [0.0283, 0.0118, 0.0317]
    remote_tau = [0.0312, 0.0027, 0.0082]
    
    fig, ax = plt.subplots(figsize=(8.0, 4.5), dpi=300)
    ax.bar(x - width, core_tau, width, label="Tumour Core (τ_core)", color="#1976D2", alpha=0.9)
    ax.bar(x, immed_tau, width, label="Immediate Margin (τ_immed, 4px)", color="#388E3C", alpha=0.9)
    ax.bar(x + width, remote_tau, width, label="Remote Context (τ_remote)", color="#F57C00", alpha=0.9)
    
    ax.set_ylabel("Mean Sham-Corrected Sensitivity (τ_r)", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(planes, fontsize=10)
    ax.legend(loc="upper right", fontsize=9, frameon=True)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_ylim(0, 0.085)
    
    for i in range(len(planes)):
        ax.text(x[i] - width, core_tau[i] + 0.002, f"{core_tau[i]:.3f}", ha="center", fontsize=8.5, fontweight="bold")
        ax.text(x[i], immed_tau[i] + 0.002, f"{immed_tau[i]:.3f}", ha="center", fontsize=8.5)
        ax.text(x[i] + width, remote_tau[i] + 0.002, f"{remote_tau[i]:.3f}", ha="center", fontsize=8.5)
        
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

plot_fig8_plane_stratification(REV_FIG_DIR / "fig8_plane_stratification.png")

# -------------------------------------------------------------------
# Figure 9: Class Heterogeneity (old Fig 8)
# -------------------------------------------------------------------
def plot_fig9_class_heterogeneity(out_path: Path):
    classes = ["Glioma (Infiltrative)", "Meningioma (Extra-axial)", "Pituitary (Sellar)"]
    x = np.arange(len(classes))
    width = 0.35
    
    # From Table 4 Cheng DeiT Telea (N=15 per class)
    core_tau = [0.0398, 0.3438, 0.0009]
    immed_tau = [0.0268, 0.0338, 0.0034]
    
    fig, ax = plt.subplots(figsize=(8.0, 4.5), dpi=300)
    ax.bar(x - width/2, core_tau, width, label="Core Sensitivity (τ_core)", color="#5C6BC0", alpha=0.9)
    ax.bar(x + width/2, immed_tau, width, label="Immediate Margin (τ_immed, 4px)", color="#26A69A", alpha=0.9)
    
    ax.set_ylabel("Mean Sham-Corrected Sensitivity (τ)", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10)
    ax.legend(loc="upper right", fontsize=9, frameon=True)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.set_ylim(0, 0.39)
    
    # Annotate margin-to-core ratios
    ax.text(x[0], max(core_tau[0], immed_tau[0]) + 0.015, "Ratio: 67.2%", ha="center", fontsize=8.5, fontweight="bold", color="#1A237E")
    ax.text(x[1], max(core_tau[1], immed_tau[1]) + 0.015, "Ratio: 9.8%", ha="center", fontsize=8.5, fontweight="bold", color="#1A237E")
    ax.text(x[2], max(core_tau[2], immed_tau[2]) + 0.015, "Circumscribed", ha="center", fontsize=8.5, fontweight="bold", color="#1A237E")

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

plot_fig9_class_heterogeneity(REV_FIG_DIR / "fig9_class_heterogeneity.png")

# -------------------------------------------------------------------
# Figure 10: BRISC Duplicate Leakage Impact (old Fig 9)
# Axes start strictly at y = 0.0!
# Plot both Full 4-Class Test (N=1,000 vs N=899) and Neoplasm Batch (N=480 vs N=397)
# -------------------------------------------------------------------
def plot_fig10_brisc_leakage(out_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=300)
    metrics = ["Accuracy", "Balanced Acc", "Macro-F1"]
    x = np.arange(len(metrics))
    width = 0.35

    # Panel A: Full 4-Class Benchmark (N=1,000 vs N=899)
    # DeiT-Small
    deit_off_4cls = [0.7880, 0.8094, 0.8030]
    deit_cln_4cls = [0.8265, 0.8330, 0.8344]
    
    ax0 = axes[0]
    ax0.bar(x - width/2, deit_off_4cls, width, label="Official Test (N=1,000; 10.1% Leakage)", color="#C62828", alpha=0.9, edgecolor="#8E0000", linewidth=0.8)
    ax0.bar(x + width/2, deit_cln_4cls, width, label="Clean Test (N=899; De-duplicated)", color="#2E7D32", alpha=0.9, edgecolor="#1B5E20", linewidth=0.8)
    ax0.set_ylim(0.0, 1.0)  # STRICTLY STARTS AT 0.0!
    ax0.set_ylabel("Classification Metric Score", fontsize=10, fontweight="bold")
    ax0.set_title("(A) Full 4-Class Test (DeiT-Small)", fontsize=11, fontweight="bold")
    ax0.set_xticks(x)
    ax0.set_xticklabels(metrics, fontsize=10)
    ax0.legend(loc="lower right", fontsize=8.5, frameon=True)
    ax0.grid(True, axis="y", linestyle=":", alpha=0.6)

    for i in range(len(metrics)):
        diff = deit_cln_4cls[i] - deit_off_4cls[i]
        ax0.text(x[i] - width/2, deit_off_4cls[i] + 0.02, f"{deit_off_4cls[i]:.3f}", ha="center", fontsize=8)
        ax0.text(x[i] + width/2, deit_cln_4cls[i] + 0.02, f"{deit_cln_4cls[i]:.3f}", ha="center", fontsize=8, fontweight="bold")
        ax0.text(x[i], max(deit_cln_4cls[i], deit_off_4cls[i]) + 0.07, f"Δ={diff:+.3f}", ha="center", fontsize=8.5, fontweight="bold", color="#2E7D32" if diff >= 0 else "#C62828")

    # Panel B: ResNet-50 Full 4-Class Benchmark (N=1,000 vs N=899)
    res_off_4cls = [0.7040, 0.6870, 0.7095]
    res_cln_4cls = [0.6963, 0.6815, 0.6991]

    ax1 = axes[1]
    ax1.bar(x - width/2, res_off_4cls, width, label="Official Test (N=1,000; 10.1% Leakage)", color="#C62828", alpha=0.9, edgecolor="#8E0000", linewidth=0.8)
    ax1.bar(x + width/2, res_cln_4cls, width, label="Clean Test (N=899; De-duplicated)", color="#2E7D32", alpha=0.9, edgecolor="#1B5E20", linewidth=0.8)
    ax1.set_ylim(0.0, 1.0)  # STRICTLY STARTS AT 0.0!
    ax1.set_ylabel("Classification Metric Score", fontsize=10, fontweight="bold")
    ax1.set_title("(B) Full 4-Class Test (ResNet-50)", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=10)
    ax1.legend(loc="lower right", fontsize=8.5, frameon=True)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)

    for i in range(len(metrics)):
        diff = res_cln_4cls[i] - res_off_4cls[i]
        ax1.text(x[i] - width/2, res_off_4cls[i] + 0.02, f"{res_off_4cls[i]:.3f}", ha="center", fontsize=8)
        ax1.text(x[i] + width/2, res_cln_4cls[i] + 0.02, f"{res_cln_4cls[i]:.3f}", ha="center", fontsize=8, fontweight="bold")
        ax1.text(x[i], max(res_cln_4cls[i], res_off_4cls[i]) + 0.07, f"Δ={diff:+.3f}", ha="center", fontsize=8.5, fontweight="bold", color="#2E7D32" if diff >= 0 else "#C62828")

    # NO EMBEDDED TITLE REPEATING CAPTION!
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

plot_fig10_brisc_leakage(REV_FIG_DIR / "fig10_brisc_leakage_artifact.png")
print("All 10 revised figures successfully plotted and saved in revision/figures/!")

