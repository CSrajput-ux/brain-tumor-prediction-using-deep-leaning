"""
Generate publication-quality diagnostic plots for Phase 3 Intervention Study.
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'experiments' / 'phase_3_interventions'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Contrasts and CIs plot
def plot_contrasts():
    metrics_df = pd.read_csv(OUT_DIR / 'metrics_by_condition.csv')
    pooled = metrics_df[metrics_df['fold'] == 'pooled'].copy()
    
    cond_order = ['I_orig', 'I_placebo', 'I_context_shift', 'I_removed_feathered', 'I_removed', 'I_tumor']
    cond_labels = ['I_orig\n(Baseline)', 'I_placebo\n(Control)', 'I_context_shift\n(Context -20%)', 'I_removed_feathered\n(Infill)', 'I_removed\n(Tumor Zeroed)', 'I_tumor\n(Isolated)']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True, dpi=150)
    
    colors = ['#2b5c8f', '#4e9a51', '#3ba2a8', '#f28e2b', '#e15759', '#76b7b2']
    
    for i, sc in enumerate(['S0', 'S1', 'S2']):
        ax = axes[i]
        sc_data = pooled[pooled['scenario'] == sc].set_index('condition').loc[cond_order].reset_index()
        
        y = sc_data['macro_f1'].values
        y_low = sc_data['macro_f1_ci_lower'].values
        y_high = sc_data['macro_f1_ci_upper'].values
        
        yerr = [y - y_low, y_high - y]
        
        bars = ax.bar(range(len(cond_order)), y, yerr=yerr, capsize=5, color=colors, alpha=0.85, edgecolor='black', linewidth=1)
        
        ax.set_xticks(range(len(cond_order)))
        ax.set_xticklabels(cond_labels, rotation=25, ha='right', fontsize=9)
        ax.set_title(f"Scenario {sc} ({'Patient Grouped' if sc == 'S0' else 'SSIM ' + ('0.80' if sc == 'S1' else '0.75')})", fontsize=11, fontweight='bold')
        ax.set_ylim(0.0, 1.05)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.axhline(1/3, color='gray', linestyle=':', label='Chance (0.333)')
        
        # Annotate values
        for idx, bar in enumerate(bars):
            val = y[idx]
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.03, f"{val:.3f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
            
    axes[0].set_ylabel("Macro-Averaged F1 Score (with 95% Cluster CI)", fontsize=10)
    plt.suptitle("Controlled Tumour-Region vs Context Intervention Study: Macro-F1 across Conditions", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'intervention_contrasts_plot.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("Contrasts plot saved.")

# 2. Confusion Matrices Plot for S0
def plot_confusion_matrices():
    metrics_df = pd.read_csv(OUT_DIR / 'metrics_by_condition.csv')
    s0_pooled = metrics_df[(metrics_df['scenario'] == 'S0') & (metrics_df['fold'] == 'pooled')]
    
    conditions = ['I_orig', 'I_placebo', 'I_context_shift', 'I_removed_feathered', 'I_removed', 'I_tumor']
    titles = ['A. I_orig (Baseline)', 'B. I_placebo (Contralateral)', 'C. I_context_shift (0.8x)', 'D. I_removed (Feathered)', 'E. I_removed (Zero-filled)', 'F. I_tumor (Isolated)']
    
    classes = ['Meningioma', 'Glioma', 'Pituitary']
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), dpi=150)
    axes = axes.flatten()
    
    for idx, cond in enumerate(conditions):
        row = s0_pooled[s0_pooled['condition'] == cond].iloc[0]
        cm = np.array(json.loads(row['confusion_matrix']))
        
        ax = axes[idx]
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                    xticklabels=classes, yticklabels=classes, ax=ax, annot_kws={'size': 10, 'weight': 'bold'})
        ax.set_title(f"{titles[idx]}\nMacro-F1: {row['macro_f1']:.3f} | Bal Acc: {row['balanced_accuracy']:.3f}", fontsize=10, fontweight='bold')
        ax.set_xlabel('Predicted Diagnostic Class', fontsize=9)
        ax.set_ylabel('True Pathology Class', fontsize=9)
        
    plt.suptitle("Scenario S0 Pooled Confusion Matrices Across Matched Conditions (N = 3,064)", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'confusion_matrices_plot.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("Confusion matrices plot saved.")

# 3. Class-Level Reliance Comparison Plot
def plot_per_class_reliance():
    metrics_df = pd.read_csv(OUT_DIR / 'metrics_by_condition.csv')
    pooled = metrics_df[metrics_df['fold'] == 'pooled']
    
    s0 = pooled[pooled['scenario'] == 'S0']
    
    orig = s0[s0['condition'] == 'I_orig'].iloc[0]
    rem = s0[s0['condition'] == 'I_removed'].iloc[0]
    plac = s0[s0['condition'] == 'I_placebo'].iloc[0]
    feath = s0[s0['condition'] == 'I_removed_feathered'].iloc[0]
    
    classes = ['Meningioma', 'Glioma', 'Pituitary']
    orig_f1s = [orig['f1_meningioma'], orig['f1_glioma'], orig['f1_pituitary']]
    rem_f1s = [rem['f1_meningioma'], rem['f1_glioma'], rem['f1_pituitary']]
    plac_f1s = [plac['f1_meningioma'], plac['f1_glioma'], plac['f1_pituitary']]
    feath_f1s = [feath['f1_meningioma'], feath['f1_glioma'], feath['f1_pituitary']]
    
    delta_rem = np.array(orig_f1s) - np.array(rem_f1s)
    delta_plac = np.array(orig_f1s) - np.array(plac_f1s)
    delta_feath = np.array(orig_f1s) - np.array(feath_f1s)
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    b1 = ax.bar(x - width, delta_rem, width, label='Delta_removal (Tumor Ablated)', color='#e15759', alpha=0.9, edgecolor='black')
    b2 = ax.bar(x, delta_feath, width, label='Delta_feathered (Feathered Infill)', color='#f28e2b', alpha=0.9, edgecolor='black')
    b3 = ax.bar(x + width, delta_plac, width, label='Delta_placebo (Contralateral Control)', color='#4e9a51', alpha=0.9, edgecolor='black')
    
    ax.set_ylabel('Performance Drop (Delta F1 Score relative to I_orig)', fontsize=10)
    ax.set_title('Pathology-Specific Reliance: Tumor Ablation vs Controls (Scenario S0)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10, fontweight='bold')
    ax.legend(frameon=True, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Annotate bars
    for bars in [b1, b2, b3]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.005, f"{h:.3f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
            
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'per_class_reliance_plot.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("Per-class reliance plot saved.")

if __name__ == '__main__':
    plot_contrasts()
    plot_confusion_matrices()
    plot_per_class_reliance()
    print("All diagnostic plots successfully generated.")
