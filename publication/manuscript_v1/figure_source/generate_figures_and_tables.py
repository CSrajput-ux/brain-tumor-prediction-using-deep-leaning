import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import h5py
import scipy.io as sio
import cv2

ROOT = Path(__file__).resolve().parent.parent
PUB_DIR = ROOT / 'publication' / 'manuscript_v1'
FIG_DIR = PUB_DIR / 'figures'
FIG_SRC_DIR = PUB_DIR / 'figure_source'
TAB_DIR = PUB_DIR / 'tables'

FIG_DIR.mkdir(parents=True, exist_ok=True)
FIG_SRC_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality styling
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.direction'] = 'out'
plt.rcParams['figure.dpi'] = 300

# Color palette: Colorblind friendly
PALETTE = {
    'C0_orig': '#2b5c8f',        # Deep Blue
    'C1_seam_only': '#d95f02',   # Vermilion / Orange
    'C2_seam_suppressed': '#7570b3', # Purple
    'C3_c5lp_scramble': '#e7298a',   # Magenta / Pink
    'meningioma': '#1b9e77',
    'glioma': '#d95f02',
    'pituitary': '#7570b3',
    'neutral': '#555555'
}


def load_canonical_data():
    p9_dir = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement'
    p9_2_dir = ROOT / 'experiments' / 'phase_9_2_manuscript_readiness'
    
    preds = pd.read_csv(p9_dir / 'matched_predictions.csv')
    metrics = pd.read_csv(p9_dir / 'primary_metrics.csv')
    contrasts = pd.read_csv(p9_2_dir / 'canonical_contrasts.csv')
    stats = pd.read_csv(p9_dir / 'image_statistics.csv')
    validity = pd.read_csv(p9_dir / 'intervention_validity_audit.csv')
    transitions = pd.read_csv(p9_dir / 'class_transition_analysis.csv')
    accounting = pd.read_csv(p9_2_dir / 'prediction_accounting.csv')
    return preds, metrics, contrasts, stats, validity, transitions, accounting


def generate_figure_1():
    print("Generating Figure 1: Dataset Samples & Mask Overlays...")
    from PIL import Image
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    
    selected_samples = {}
    for c_name in ['meningioma', 'glioma', 'pituitary']:
        sub = meta_df[meta_df['class_name'] == c_name]
        for _, row in sub.iterrows():
            img_p = ROOT / 'prepared_full_run' / row['image_output_path']
            mask_p = ROOT / 'prepared_full_run' / row['mask_output_path']
            if img_p.exists() and mask_p.exists():
                selected_samples[c_name] = (img_p, mask_p, row['sample_id'], row['patient_id'])
                break
                
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.5))
    
    for idx, (c_name, (img_p, mask_p, sid, pid)) in enumerate(selected_samples.items()):
        img = np.array(Image.open(img_p).convert('L')).astype(np.float32)
        mask = (np.array(Image.open(mask_p)) > 0).astype(np.uint8)
                
        # Normalize
        img_norm = (img - img.min()) / (img.max() - img.min() + 1e-8)
        
        # Row 1: Raw slice
        axes[0, idx].imshow(img_norm, cmap='gray')
        axes[0, idx].set_title(f"Class: {c_name.capitalize()}\n(Patient ID: {pid})", fontsize=11, fontweight='bold')
        axes[0, idx].axis('off')
        
        # Row 2: Overlay with tumour mask and 15px margin
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        dilated = cv2.dilate(mask, kernel)
        margin_ring = dilated - mask
        
        overlay = np.stack([img_norm, img_norm, img_norm], axis=-1)
        # Tumour core: Red tint
        overlay[mask == 1] = [1.0, 0.2, 0.2]
        # Margin ring: Cyan tint
        overlay[margin_ring == 1] = [0.2, 0.8, 1.0]
        
        axes[1, idx].imshow(overlay)
        axes[1, idx].set_title(f"Tumour Core (Red)\n15px Margin (Cyan)", fontsize=10)
        axes[1, idx].axis('off')
        
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig1_dataset_and_masks.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig1_dataset_and_masks.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 1 generated.")


def generate_figure_2():
    print("Generating Figure 2: Experimental Workflow Diagram...")
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.axis('off')
    
    # Workflow boxes
    boxes = [
        ("1. Dataset & Split Audit", "Cheng Figshare (3,064 slices, 233 patients)\nS0: Patient-Disjoint 5-Fold\nS1: Cleaned SSIM 0.80 | S2: Grouped SSIM 0.75", 0.05, 0.55, 0.25, 0.35, '#e8f4f8'),
        ("2. Model Training & Freezing", "ResNet-50 (15 Checkpoints)\n5 Folds x 3 Scenarios\nWeights Frozen from Phase 2 Baseline", 0.37, 0.55, 0.25, 0.35, '#e8f8f0'),
        ("3. 4-Condition Interventions", "Tumour Core & 15px Margin 100% Protected\nC0: Baseline | C1: Seam-Only\nC2: Seam-Suppressed | C3: Raw Scramble", 0.69, 0.55, 0.26, 0.35, '#fff4e6'),
        ("4. Matched Inference", "36,768 Out-of-Fold Predictions\nZero Test Leakage | No Model Retraining\nStrict Out-of-Fold Forward Evaluation", 0.20, 0.08, 0.26, 0.32, '#f3e8f8'),
        ("5. Statistical Disentanglement", "Synchronized Paired Cluster Bootstrap (B=2,000)\nMcNemar Transition Chi-Square\nHolm-Bonferroni FWER Multiplicity Control", 0.54, 0.08, 0.28, 0.32, '#fbe8e8')
    ]
    
    for title, desc, x, y, w, h, col in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor=col, edgecolor='#333333', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.06, title, fontsize=11, fontweight='bold', ha='center', va='center', color='#111111')
        ax.text(x + w/2, y + h/2 - 0.03, desc, fontsize=9, ha='center', va='center', color='#333333', linespacing=1.4)
        
    # Arrows
    arrow_props = dict(arrowstyle="->", lw=1.8, color='#333333')
    ax.annotate('', xy=(0.37, 0.725), xytext=(0.30, 0.725), arrowprops=arrow_props)
    ax.annotate('', xy=(0.69, 0.725), xytext=(0.62, 0.725), arrowprops=arrow_props)
    ax.annotate('', xy=(0.33, 0.40), xytext=(0.82, 0.55), arrowprops=arrow_props)
    ax.annotate('', xy=(0.54, 0.24), xytext=(0.46, 0.24), arrowprops=arrow_props)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig2_experimental_workflow.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig2_experimental_workflow.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 2 generated.")


def generate_figure_3():
    print("Generating Figure 3: Four-Condition Intervention Geometry...")
    # Find a visual panel from Phase 9
    panel_files = list((ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement' / 'visual_audit_panels').glob('*.png'))
    if panel_files:
        panel_img = cv2.imread(str(panel_files[0]))
        panel_img = cv2.cvtColor(panel_img, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(panel_img)
        ax.axis('off')
        ax.set_title("Experimental Intervention Geometry Across Four Matched Conditions", fontsize=12, fontweight='bold', pad=10)
        
        plt.tight_layout()
        fig.savefig(FIG_DIR / 'fig3_intervention_geometry.png', dpi=300, bbox_inches='tight')
        fig.savefig(FIG_DIR / 'fig3_intervention_geometry.pdf', bbox_inches='tight')
        plt.close(fig)
        print("Figure 3 generated from genuine panel.")


def generate_figure_4(metrics):
    print("Generating Figure 4: Baseline Performance Comparison...")
    c0 = metrics[metrics['condition'] == 'C0_orig']
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    scenarios = ['S0 (Patient-Disjoint)', 'S1 (Duplicate-Cleaned 0.80)', 'S2 (Aggressive Grouping 0.75)']
    x = np.arange(len(scenarios))
    width = 0.25
    
    macro_f1 = c0['macro_f1'].values
    bal_acc = c0['balanced_acc'].values
    acc = c0['accuracy'].values
    
    rects1 = ax.bar(x - width, macro_f1, width, label='Macro-F1', color='#2b5c8f', edgecolor='black', linewidth=0.8)
    rects2 = ax.bar(x, bal_acc, width, label='Balanced Accuracy', color='#41b6c4', edgecolor='black', linewidth=0.8)
    rects3 = ax.bar(x + width, acc, width, label='Overall Accuracy', color='#253494', edgecolor='black', linewidth=0.8)
    
    ax.set_ylabel('Score', fontsize=11, fontweight='bold')
    ax.set_title('Baseline Model Performance (Condition C0) Across Scenarios', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=9.5)
    ax.set_ylim(0.85, 0.98)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Value annotations
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.3f}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha='center', va='bottom', fontsize=8)
                    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig4_baseline_performance.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig4_baseline_performance.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 4 generated.")


def generate_figure_5(metrics):
    print("Generating Figure 5: Multi-Condition Performance Comparison...")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    
    scenarios = ['S0', 'S1', 'S2']
    conditions = ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']
    cond_labels = ['C0: Baseline', 'C1: Seam-Only', 'C2: Seam-Suppressed', 'C3: Raw Scramble']
    
    x = np.arange(len(scenarios))
    width = 0.18
    
    for idx, (cond, lbl) in enumerate(zip(conditions, cond_labels)):
        vals = [metrics[(metrics['scenario'] == sc) & (metrics['condition'] == cond)]['macro_f1'].values[0] for sc in scenarios]
        col = PALETTE[cond]
        rects = ax.bar(x + (idx - 1.5) * width, vals, width, label=lbl, color=col, edgecolor='black', linewidth=0.8)
        
        for r in rects:
            h = r.get_height()
            ax.annotate(f'{h:.3f}', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2),
                        textcoords="offset points", ha='center', va='bottom', fontsize=7.5, rotation=45)
                        
    ax.set_ylabel('Macro-F1 Score', fontsize=11, fontweight='bold')
    ax.set_title('Macro-F1 Performance Across Experimental Conditions and Scenarios', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(['S0 (Patient-Disjoint)', 'S1 (Duplicate-Cleaned 0.80)', 'S2 (Aggressive Grouping 0.75)'], fontsize=10)
    ax.set_ylim(0.35, 1.02)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig5_intervention_macro_f1.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig5_intervention_macro_f1.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 5 generated.")


def generate_figure_6(contrasts):
    print("Generating Figure 6: Paired Contrast Forest Plot...")
    fig, ax = plt.subplots(figsize=(9, 6.5))
    
    # Plot S0, S1, S2 contrasts
    contrast_order = ['C3_vs_C0', 'C1_vs_C0', 'C2_vs_C0', 'C3_vs_C1', 'C3_vs_C2']
    c_labels = {
        'C3_vs_C0': 'C3 vs C0: Raw Scramble Effect',
        'C1_vs_C0': 'C1 vs C0: Seam-Only Effect',
        'C2_vs_C0': 'C2 vs C0: Seam-Suppressed Rearrangement',
        'C3_vs_C1': 'C3 vs C1: Scramble vs Seam Difference',
        'C3_vs_C2': 'C3 vs C2: Sensitivity to Seam Smoothing'
    }
    
    y_pos = []
    y_labels = []
    
    y_idx = 0
    colors = {'S0': '#2b5c8f', 'S1': '#1b9e77', 'S2': '#d95f02'}
    
    for cid in contrast_order:
        for sc in ['S0', 'S1', 'S2']:
            row = contrasts[(contrasts['scenario'] == sc) & (contrasts['contrast_id'] == cid)].iloc[0]
            delta = row['signed_difference_A_minus_B']
            ci_low = row['bootstrap_ci_lower']
            ci_high = row['bootstrap_ci_upper']
            
            ax.errorbar(delta, y_idx, xerr=[[delta - ci_low], [ci_high - delta]], fmt='o',
                        color=colors[sc], ecolor=colors[sc], elinewidth=1.6, capsize=3.5, markersize=5.5)
            y_pos.append(y_idx)
            y_labels.append(f"{c_labels[cid]} ({sc})")
            y_idx += 1
        y_idx += 0.5  # gap between contrast groups
        
    ax.axvline(0, color='black', linestyle='--', linewidth=0.9, alpha=0.7)
    ax.axvline(0.150, color='red', linestyle=':', linewidth=1.0, alpha=0.7, label='Preregistered Threshold (0.150)')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=8.5)
    ax.set_xlabel(r'Signed Difference: $\Delta = \mathrm{MacroF1}(A) - \mathrm{MacroF1}(B)$', fontsize=11, fontweight='bold')
    ax.set_title('Paired Statistical Contrasts (95% Cluster-Bootstrap CIs, B=2,000)', fontsize=12, fontweight='bold', pad=12)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Custom legend for scenarios
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['S0'], label='S0 (Patient-Disjoint)', markersize=7),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['S1'], label='S1 (Cleaned 0.80)', markersize=7),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['S2'], label='S2 (Grouped 0.75)', markersize=7),
        plt.Line2D([0], [0], color='red', linestyle=':', label='Threshold (0.150)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True, facecolor='white', fontsize=9)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig6_contrast_forest_plot.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig6_contrast_forest_plot.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 6 generated.")


def generate_figure_7(transitions):
    print("Generating Figure 7: Confusion Matrices Across Conditions in S0...")
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    
    class_names = ['Meningioma', 'Glioma', 'Pituitary']
    conditions = ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']
    cond_titles = ['C0: Baseline', 'C1: Seam-Only', 'C2: Seam-Suppressed', 'C3: Raw Scramble']
    
    for idx, (cond, title) in enumerate(zip(conditions, cond_titles)):
        row = transitions[(transitions['scenario'] == 'S0') & (transitions['condition'] == cond)].iloc[0]
        cm = np.array([
            [row['cm_00'], row['cm_01'], row['cm_02']],
            [row['cm_10'], row['cm_11'], row['cm_12']],
            [row['cm_20'], row['cm_21'], row['cm_22']]
        ])
        
        # Row-normalized (Recall)
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        
        sns.heatmap(cm_norm, annot=cm, fmt='d', cmap='Blues', cbar=False, ax=axes[idx],
                    xticklabels=class_names, yticklabels=class_names if idx == 0 else False,
                    annot_kws={'fontsize': 9})
        axes[idx].set_title(title, fontsize=10.5, fontweight='bold', pad=8)
        axes[idx].set_xlabel('Predicted Class', fontsize=9.5)
        if idx == 0:
            axes[idx].set_ylabel('True Class', fontsize=9.5)
            
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig7_confusion_matrices.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig7_confusion_matrices.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 7 generated.")


def generate_figure_8(stats):
    print("Generating Figure 8: Edge and Spatial Artifact Diagnostics...")
    means = stats.groupby('condition').mean(numeric_only=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    conds = ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']
    labels = ['C0', 'C1', 'C2', 'C3']
    colors = [PALETTE[c] for c in conds]
    
    # 1. Seam Sobel Energy
    axes[0].bar(labels, [means.loc[c, 'sobel_energy_seam'] for c in conds], color=colors, edgecolor='black', linewidth=0.8)
    axes[0].set_title('Tile Boundary Seam Sobel Energy', fontsize=10.5, fontweight='bold')
    axes[0].set_ylabel('Gradient Energy', fontsize=9.5)
    axes[0].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate([means.loc[c, 'sobel_energy_seam'] for c in conds]):
        axes[0].annotate(f'{v:.1f}', (i, v), textcoords="offset points", xytext=(0,3), ha='center', fontsize=8.5)
        
    # 2. Tile Interior Sobel Energy
    axes[1].bar(labels, [means.loc[c, 'sobel_energy_interior'] for c in conds], color=colors, edgecolor='black', linewidth=0.8)
    axes[1].set_title('Tile Interior Texture Sobel Energy', fontsize=10.5, fontweight='bold')
    axes[1].set_ylabel('Gradient Energy', fontsize=9.5)
    axes[1].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate([means.loc[c, 'sobel_energy_interior'] for c in conds]):
        axes[1].annotate(f'{v:.1f}', (i, v), textcoords="offset points", xytext=(0,3), ha='center', fontsize=8.5)
        
    # 3. Fourier High-Frequency Spectral Energy
    axes[2].bar(labels, [means.loc[c, 'spectral_energy_hf'] for c in conds], color=colors, edgecolor='black', linewidth=0.8)
    axes[2].set_title('High-Frequency Fourier Energy', fontsize=10.5, fontweight='bold')
    axes[2].set_ylabel('Spectral Energy', fontsize=9.5)
    axes[2].grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate([means.loc[c, 'spectral_energy_hf'] for c in conds]):
        axes[2].annotate(f'{v:.0f}', (i, v), textcoords="offset points", xytext=(0,3), ha='center', fontsize=8.5)
        
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig8_artifact_diagnostics.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig8_artifact_diagnostics.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 8 generated.")


def generate_figure_9(transitions):
    print("Generating Figure 9: Glioma-to-Pituitary Prior Collapse...")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    scenarios = ['S0', 'S1', 'S2']
    conditions = ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']
    cond_labels = ['C0: Baseline', 'C1: Seam-Only', 'C2: Seam-Suppressed', 'C3: Raw Scramble']
    
    x = np.arange(len(scenarios))
    width = 0.2
    
    for idx, (cond, lbl) in enumerate(zip(conditions, cond_labels)):
        rates = [transitions[(transitions['scenario'] == sc) & (transitions['condition'] == cond)]['glioma_to_pituitary_rate'].values[0] * 100 for sc in scenarios]
        col = PALETTE[cond]
        rects = ax.bar(x + (idx - 1.5) * width, rates, width, label=lbl, color=col, edgecolor='black', linewidth=0.8)
        
        for r in rects:
            h = r.get_height()
            ax.annotate(f'{h:.1f}%', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2),
                        textcoords="offset points", ha='center', va='bottom', fontsize=8, rotation=35)
                        
    ax.set_ylabel('Glioma-to-Pituitary Misclassification (%)', fontsize=10.5, fontweight='bold')
    ax.set_title('Collapse into Pituitary Prior Under Cranial Disorientation', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(['S0 (Patient-Disjoint)', 'S1 (Duplicate-Cleaned 0.80)', 'S2 (Aggressive Grouping 0.75)'], fontsize=9.5)
    ax.set_ylim(0, 75)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig9_glioma_prior_collapse.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig9_glioma_prior_collapse.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 9 generated.")


def generate_figure_10(contrasts):
    print("Generating Figure 10: Multi-Fold Cross-Validation Stability...")
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    
    c2 = contrasts[contrasts['contrast_id'] == 'C2_vs_C0']
    
    x = np.arange(5)
    width = 0.25
    
    folds = ['Fold 1', 'Fold 2', 'Fold 3', 'Fold 4', 'Fold 5']
    scenarios = ['S0', 'S1', 'S2']
    colors = {'S0': '#2b5c8f', 'S1': '#1b9e77', 'S2': '#d95f02'}
    
    for idx, sc in enumerate(scenarios):
        row = c2[c2['scenario'] == sc].iloc[0]
        fold_deltas = [row[f'fold_{f}_delta'] for f in range(1, 6)]
        rects = ax.bar(x + (idx - 1) * width, fold_deltas, width, label=f'{sc} (Mean={row["signed_difference_A_minus_B"]:.3f})',
                       color=colors[sc], edgecolor='black', linewidth=0.8)
        
    ax.axhline(0.150, color='red', linestyle=':', label='Threshold (0.150)', linewidth=1.2)
    ax.set_ylabel(r'Performance Drop $\Delta \mathrm{MacroF1}$', fontsize=10.5, fontweight='bold')
    ax.set_title(r'Cross-Validation Stability of Seam-Suppressed Scrambling ($C_2 \mathrm{\ vs\ } C_0$)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(folds, fontsize=10)
    ax.set_ylim(0.25, 0.65)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / 'fig10_cross_validation_stability.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG_DIR / 'fig10_cross_validation_stability.pdf', bbox_inches='tight')
    plt.close(fig)
    print("Figure 10 generated.")


def generate_all_tables(metrics, contrasts, stats, validity, accounting):
    print("Generating all main and supplementary publication tables...")
    
    # Table 1: Dataset Composition
    t1_data = [
        {'tumor_class': 'Meningioma', 'class_id': 0, 'slice_count': 708, 'percentage': '23.11%', 'anatomical_predilection': 'Dural-based, extra-axial (parasagittal, convexity, skull base)'},
        {'tumor_class': 'Glioma', 'class_id': 1, 'slice_count': 1426, 'percentage': '46.54%', 'anatomical_predilection': 'Intra-axial cerebral/cerebellar white matter and parenchyma'},
        {'tumor_class': 'Pituitary Tumour', 'class_id': 2, 'slice_count': 930, 'percentage': '30.35%', 'anatomical_predilection': 'Sella turcica / suprasellar region at the skull base'},
        {'tumor_class': 'Total', 'class_id': 'All', 'slice_count': 3064, 'percentage': '100.00%', 'anatomical_predilection': '233 distinct patient clusters'}
    ]
    pd.DataFrame(t1_data).to_csv(TAB_DIR / 'table1_dataset_composition.csv', index=False)
    
    # Table 2: Scenarios & Fold Sizes
    t2_data = [
        {'scenario': 'S0', 'description': 'Patient-Disjoint 5-Fold CV', 'grouping_criterion': 'Unique Patient ID', 'cluster_count': 233, 'fold_1_samples': 618, 'fold_2_samples': 616, 'fold_3_samples': 612, 'fold_4_samples': 610, 'fold_5_samples': 608, 'total_samples': 3064},
        {'scenario': 'S1', 'description': 'Candidate Duplicate-Cleaned CV', 'grouping_criterion': 'Patient ID + SSIM >= 0.80 Pair Merges', 'cluster_count': 219, 'fold_1_samples': 618, 'fold_2_samples': 616, 'fold_3_samples': 612, 'fold_4_samples': 610, 'fold_5_samples': 608, 'total_samples': 3064},
        {'scenario': 'S2', 'description': 'Aggressive Duplicate-Grouped CV', 'grouping_criterion': 'Patient ID + SSIM >= 0.75 Pair Merges', 'cluster_count': 178, 'fold_1_samples': 618, 'fold_2_samples': 616, 'fold_3_samples': 612, 'fold_4_samples': 610, 'fold_5_samples': 608, 'total_samples': 3064}
    ]
    pd.DataFrame(t2_data).to_csv(TAB_DIR / 'table2_evaluation_scenarios.csv', index=False)
    
    # Table 3: Model Configuration
    t3_data = [
        {'hyperparameter': 'Model Architecture', 'specification': 'ResNet-50 (Torchvision default)'},
        {'hyperparameter': 'Input Dimensions', 'specification': '224 x 224 x 3 (Bilinear interpolation with ImageNet normalization)'},
        {'hyperparameter': 'Pre-training Initialization', 'specification': 'ImageNet-1k pretrained weights'},
        {'hyperparameter': 'Classification Head', 'specification': 'Linear(2048, 3) (Meningioma, Glioma, Pituitary)'},
        {'hyperparameter': 'Loss Function', 'specification': 'Cross-Entropy Loss'},
        {'hyperparameter': 'Optimizer & LR', 'specification': 'SGD, Momentum=0.9, Weight Decay=1e-4, Initial LR=1e-3'},
        {'hyperparameter': 'LR Schedule', 'specification': 'StepLR (gamma=0.1 every 10 epochs, 30 total epochs)'},
        {'hyperparameter': 'Batch Size', 'specification': '32 for training, 64 for inference'},
        {'hyperparameter': 'Checkpoint Selection', 'specification': 'Best validation Macro-F1 per fold (Phase 2 authoritative checkpoints)'},
        {'hyperparameter': 'Inference Mode', 'specification': 'FROZEN (zero parameter fine-tuning during intervention evaluations)'}
    ]
    pd.DataFrame(t3_data).to_csv(TAB_DIR / 'table3_model_configuration.csv', index=False)
    
    # Table 4: Baseline Metrics
    c0 = metrics[metrics['condition'] == 'C0_orig'].copy()
    c0.to_csv(TAB_DIR / 'table4_baseline_metrics.csv', index=False)
    
    # Table 5: All Interventions Metrics
    metrics.to_csv(TAB_DIR / 'table5_intervention_metrics.csv', index=False)
    
    # Table 6: Canonical Contrasts
    contrasts.to_csv(TAB_DIR / 'table6_canonical_contrasts.csv', index=False)
    
    # Table 7: Image Diagnostics
    means = stats.groupby('condition').mean(numeric_only=True).reset_index()
    means.to_csv(TAB_DIR / 'table7_image_diagnostics.csv', index=False)
    
    # Table 8: Claim Evidence Matrix
    claims = pd.read_csv(ROOT / 'experiments' / 'phase_9_2_manuscript_readiness' / 'claim_evidence_matrix.csv')
    claims.to_csv(TAB_DIR / 'table8_claim_evidence_matrix.csv', index=False)
    
    # Supplementary Table S1: Prediction Accounting
    accounting.to_csv(TAB_DIR / 'table_s1_prediction_accounting.csv', index=False)
    
    print("All CSV tables generated in publication/manuscript_v1/tables/.")


def main():
    preds, metrics, contrasts, stats, validity, transitions, accounting = load_canonical_data()
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4(metrics)
    generate_figure_5(metrics)
    generate_figure_6(contrasts)
    generate_figure_7(transitions)
    generate_figure_8(stats)
    generate_figure_9(transitions)
    generate_figure_10(contrasts)
    generate_all_tables(metrics, contrasts, stats, validity, accounting)
    print("All figures and tables completed successfully.")


if __name__ == '__main__':
    main()
