"""
Phase 3 — Controlled Tumour-Region vs Context Intervention Study.

Executes the matched 5-condition battery (+ artifact sensitivity check) across
Scenarios S0, S1, S2 using strictly frozen ResNet-50 checkpoints from Phase 2.

Conditions:
- I_orig: Unmanipulated original MRI slice
- I_tumor: Isolated tumor (context set to 0)
- I_removed: Ablated tumor (tumor set to 0)
- I_placebo: Contralateral matched normal tissue set to 0
- I_context_shift: Context contrast reduced by 20% (0.8x), tumor unmodified
- I_removed_feathered: Ablated tumor with Gaussian-feathered border (sigma=2) and mean parenchymal infill

Outputs:
- experiments/phase_3_interventions/intervention_manifest.csv
- experiments/phase_3_interventions/matched_predictions.csv
- experiments/phase_3_interventions/metrics_by_condition.csv
- experiments/phase_3_interventions/paired_differences.json
- Diagnostic plots and checksums
"""
import os
import sys
import json
import time
import hashlib
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.stats import wilcoxon

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)

# Set seeds
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

ROOT = Path(__file__).resolve().parents[1]
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CLASS_NAMES = ['meningioma', 'glioma', 'pituitary']
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: name for idx, name in enumerate(CLASS_NAMES)}

SCENARIOS = {
    'S0': {
        'manifest': ROOT / 'prepared_full_run' / 'patient_splits.csv',
        'cluster_col': 'patient_id'
    },
    'S1': {
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_80.csv',
        'cluster_col': 'combined_group_id'
    },
    'S2': {
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_75.csv',
        'cluster_col': 'combined_group_id'
    }
}

OUTPUT_DIR = ROOT / 'experiments' / 'phase_3_interventions'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_placebo_mask(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Generate matched placebo mask in contralateral hemisphere (mirror along vertical midline x' = W - 1 - x).
    If overlap with original tumor occurs, shift vertically until zero overlap is achieved.
    Returns: (placebo_mask, vertical_shift_applied)
    """
    h, w = mask.shape
    placebo = np.fliplr(mask)
    shift_applied = 0
    
    overlap = np.logical_and(mask > 0, placebo > 0)
    if np.any(overlap):
        y_indices, _ = np.where(mask > 0)
        y_center = np.mean(y_indices)
        shift_step = 10
        for dy in range(shift_step, h, shift_step):
            if y_center > h / 2:
                # Tumor in lower half, shift placebo up
                if dy < h:
                    test_p = np.roll(placebo, -dy, axis=0)
                    test_p[-dy:, :] = 0
                    if not np.any(np.logical_and(mask > 0, test_p > 0)):
                        placebo = test_p
                        shift_applied = -dy
                        break
            else:
                # Tumor in upper half, shift placebo down
                if dy < h:
                    test_p = np.roll(placebo, dy, axis=0)
                    test_p[:dy, :] = 0
                    if not np.any(np.logical_and(mask > 0, test_p > 0)):
                        placebo = test_p
                        shift_applied = dy
                        break
                        
    return placebo, shift_applied

def create_feathered_infill(img: np.ndarray, mask: np.ndarray, sigma: float = 2.0) -> np.ndarray:
    """
    Sensitivity control: Gaussian-feathered boundary with mean parenchymal infill.
    """
    # Estimate mean parenchymal intensity (non-zero, non-tumor tissue)
    brain_parenchyma = img[(img > 20) & (mask == 0)]
    fill_val = float(np.mean(brain_parenchyma)) if len(brain_parenchyma) > 0 else 100.0
    
    # Smooth the binary mask with Gaussian blur to avoid sharp step discontinuities
    mask_float = mask.astype(np.float32)
    feathered_mask = gaussian_filter(mask_float, sigma=sigma)
    feathered_mask = np.clip(feathered_mask, 0.0, 1.0)
    
    # Infill: blend image and fill_val using feathered mask
    infilled = img.astype(np.float32) * (1.0 - feathered_mask) + fill_val * feathered_mask
    return np.clip(infilled, 0, 255).astype(np.uint8)

def load_all_data():
    """Load metadata, images, and masks into RAM."""
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    print(f"Loading {len(meta_df)} images and masks into RAM...")
    t0 = time.time()
    
    data_store = {}
    manifest_rows = []
    
    for idx, row in meta_df.iterrows():
        sid = row['sample_id']
        cls_name = row['class_name']
        cls_label = CLASS_TO_IDX[cls_name]
        pid = row['patient_id']
        
        img_rel = row['image_output_path']
        mask_rel = row['mask_output_path']
        
        img_path = ROOT / 'prepared_full_run' / img_rel
        mask_path = ROOT / 'prepared_full_run' / mask_rel
        
        # Load grayscale images as uint8 numpy arrays
        img_arr = np.array(Image.open(img_path).convert('L'))
        mask_arr = np.array(Image.open(mask_path))
        if mask_arr.max() > 1:
            mask_bin = (mask_arr > 0).astype(np.uint8)
        else:
            mask_bin = mask_arr.astype(np.uint8)
            
        # Generate matched placebo
        placebo_bin, shift_applied = generate_placebo_mask(mask_bin)
        
        # Area calculations
        total_px = mask_bin.size
        tumor_px = int(np.sum(mask_bin > 0))
        placebo_px = int(np.sum(placebo_bin > 0))
        overlap_px = int(np.sum(np.logical_and(mask_bin > 0, placebo_bin > 0)))
        
        data_store[sid] = {
            'image': img_arr,
            'mask': mask_bin,
            'placebo_mask': placebo_bin,
            'class_name': cls_name,
            'class_label': cls_label,
            'patient_id': pid
        }
        
        manifest_rows.append({
            'sample_id': sid,
            'patient_id': pid,
            'class_name': cls_name,
            'class_label': cls_label,
            'image_output_path': img_rel,
            'mask_output_path': mask_rel,
            'image_height': img_arr.shape[0],
            'image_width': img_arr.shape[1],
            'tumor_area_pixels': tumor_px,
            'tumor_area_fraction': tumor_px / total_px,
            'placebo_area_pixels': placebo_px,
            'placebo_area_fraction': placebo_px / total_px,
            'placebo_overlap_pixels': overlap_px,
            'placebo_shift_applied': shift_applied,
            'fraction_altered_I_tumor': (total_px - tumor_px) / total_px,
            'fraction_altered_I_removed': tumor_px / total_px,
            'fraction_altered_I_placebo': placebo_px / total_px,
            'fraction_altered_I_context_shift': (total_px - tumor_px) / total_px
        })
        
    print(f"Data cached in {time.time() - t0:.2f}s.")
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_df.to_csv(OUTPUT_DIR / 'intervention_manifest.csv', index=False)
    print(f"Intervention manifest saved to {OUTPUT_DIR / 'intervention_manifest.csv'}.")
    
    return data_store, manifest_df

def load_checkpoint(scenario: str, fold_num: int) -> nn.Module:
    """Load verified frozen checkpoint from Phase 2."""
    ckpt_path = ROOT / 'experiments' / 'phase_2_baseline' / scenario / f"fold_{fold_num}_best_checkpoint.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
        
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
    model = models.resnet50()
    model.fc = nn.Linear(model.fc.in_features, 3)
    model.load_state_dict(ckpt['model_state_dict'])
    model = model.to(DEVICE).eval()
    return model

def build_condition_images(img: np.ndarray, mask: np.ndarray, placebo_mask: np.ndarray) -> dict[str, Image.Image]:
    """Build all 6 condition images for a single slice as 224x224 RGB PIL Images."""
    # 1. I_orig
    i_orig = img
    
    # 2. I_tumor: keep tumor, zero context
    i_tumor = img * mask
    
    # 3. I_removed: zero tumor, keep context
    i_removed = img * (1 - mask)
    
    # 4. I_placebo: zero contralateral normal tissue, keep true tumor + context
    i_placebo = img * (1 - placebo_mask)
    
    # 5. I_context_shift: dim context by 20% (0.8x), keep tumor exact
    i_context_shift = np.where(mask > 0, img, np.clip(img * 0.80, 0, 255).astype(np.uint8))
    
    # 6. I_removed_feathered: feathered infill sensitivity check
    i_removed_feathered = create_feathered_infill(img, mask, sigma=2.0)
    
    conditions = {
        'I_orig': i_orig,
        'I_tumor': i_tumor,
        'I_removed': i_removed,
        'I_placebo': i_placebo,
        'I_context_shift': i_context_shift,
        'I_removed_feathered': i_removed_feathered
    }
    
    pil_images = {}
    for c_name, arr in conditions.items():
        # Convert grayscale array to RGB PIL image and resize to (224, 224)
        pil_img = Image.fromarray(arr).convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
        pil_images[c_name] = pil_img
        
    return pil_images

def run_scenario_interventions(data_store: dict):
    """Run full intervention inference across S0, S1, S2."""
    eval_transform = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    all_matched_predictions = []
    
    conditions_order = ['I_orig', 'I_tumor', 'I_removed', 'I_placebo', 'I_context_shift', 'I_removed_feathered']
    
    t0_all = time.time()
    
    for sc, sc_info in SCENARIOS.items():
        print(f"\n================ Running Scenario {sc} ================")
        manifest = pd.read_csv(sc_info['manifest'])
        cluster_col = sc_info['cluster_col']
        
        # Manifest has fold like 'fold_1' or 1
        for fold in range(1, 6):
            fold_str = f"fold_{fold}"
            # Identify test samples for this fold
            if 'fold' in manifest.columns:
                fold_matches = manifest['fold'].astype(str).isin([str(fold), fold_str])
            elif 'test_fold' in manifest.columns:
                fold_matches = manifest['test_fold'].astype(str).isin([str(fold), fold_str])
            else:
                raise KeyError(f"Fold column missing in {sc_info['manifest']}")
                
            test_subset = manifest[fold_matches].copy()
            print(f"Scenario {sc} {fold_str}: {len(test_subset)} test samples. Loading checkpoint...")
            
            model = load_checkpoint(sc, fold)
            
            # Prepare batches for all samples and conditions
            # We will process sample-by-sample or batch of samples
            samples_list = test_subset['sample_id'].tolist()
            
            # To run efficiently, batch across conditions for chunks of samples
            batch_size = 32  # 32 samples * 6 conditions = 192 tensors per batch
            for chunk_start in range(0, len(samples_list), batch_size):
                chunk_sids = samples_list[chunk_start:chunk_start + batch_size]
                
                # Build batch tensors
                batch_tensors = []
                batch_meta = []
                
                for sid in chunk_sids:
                    sample_data = data_store[sid]
                    img = sample_data['image']
                    mask = sample_data['mask']
                    placebo_mask = sample_data['placebo_mask']
                    
                    pil_imgs = build_condition_images(img, mask, placebo_mask)
                    
                    m_row = test_subset[test_subset['sample_id'] == sid].iloc[0]
                    cluster_id = str(m_row[cluster_col])
                    
                    for c_name in conditions_order:
                        tensor = eval_transform(pil_imgs[c_name])
                        batch_tensors.append(tensor)
                        batch_meta.append({
                            'sample_id': sid,
                            'patient_id': sample_data['patient_id'],
                            'combined_group_id': cluster_id,
                            'true_class': sample_data['class_name'],
                            'true_label': sample_data['class_label'],
                            'condition': c_name,
                            'scenario': sc,
                            'fold': fold_str,
                            'checkpoint_id': f"{sc}_{fold_str}"
                        })
                        
                batch_tensor = torch.stack(batch_tensors).to(DEVICE)
                
                with torch.no_grad():
                    with torch.amp.autocast('cuda'):
                        logits = model(batch_tensor)
                        probs = torch.softmax(logits, dim=1).cpu().numpy()
                        logits_np = logits.cpu().float().numpy()
                        
                for i, meta in enumerate(batch_meta):
                    p = probs[i]
                    l = logits_np[i]
                    pred_label = int(np.argmax(p))
                    pred_class = IDX_TO_CLASS[pred_label]
                    correct = int(pred_label == meta['true_label'])
                    
                    # Shannon entropy: - sum p * log2(p)
                    # Add epsilon to prevent log(0)
                    eps = 1e-12
                    entropy = -float(np.sum(p * np.log2(np.clip(p, eps, 1.0))))
                    
                    record = {
                        **meta,
                        'pred_class': pred_class,
                        'pred_label': pred_label,
                        'correct': correct,
                        'prob_meningioma': float(p[0]),
                        'prob_glioma': float(p[1]),
                        'prob_pituitary': float(p[2]),
                        'logit_meningioma': float(l[0]),
                        'logit_glioma': float(l[1]),
                        'logit_pituitary': float(l[2]),
                        'entropy': entropy
                    }
                    all_matched_predictions.append(record)
                    
            del model
            torch.cuda.empty_cache()
            
    print(f"\nAll inference completed in {time.time() - t0_all:.2f}s.")
    df_preds = pd.DataFrame(all_matched_predictions)
    
    # Add matched transitions and flip relative to I_orig
    print("Computing matched transitions and flip flags relative to I_orig...")
    # Pivot to get I_orig correct and pred_label per sample/scenario
    orig_preds = df_preds[df_preds['condition'] == 'I_orig'].set_index(['scenario', 'sample_id'])
    
    flips = []
    transitions = []
    prob_shifts_true = []
    
    for idx, row in df_preds.iterrows():
        sc = row['scenario']
        sid = row['sample_id']
        cond = row['condition']
        
        orig_row = orig_preds.loc[(sc, sid)]
        orig_pred_label = orig_row['pred_label']
        orig_correct = orig_row['correct']
        
        # Did prediction change from I_orig?
        is_flip = int(row['pred_label'] != orig_pred_label)
        flips.append(is_flip)
        
        # Transition type
        if orig_correct == 1 and row['correct'] == 1:
            tt = 'correct_to_correct'
        elif orig_correct == 1 and row['correct'] == 0:
            tt = 'correct_to_incorrect'
        elif orig_correct == 0 and row['correct'] == 1:
            tt = 'incorrect_to_correct'
        else:
            tt = 'incorrect_to_incorrect'
        transitions.append(tt)
        
        # Probability shift on the true class
        true_lbl = row['true_label']
        prob_cols = ['prob_meningioma', 'prob_glioma', 'prob_pituitary']
        true_prob_cond = row[prob_cols[true_lbl]]
        true_prob_orig = orig_row[prob_cols[true_lbl]]
        prob_shifts_true.append(float(true_prob_cond - true_prob_orig))
        
    df_preds['flip_relative_to_orig'] = flips
    df_preds['transition_type'] = transitions
    df_preds['prob_shift_true_class'] = prob_shifts_true
    
    preds_out = OUTPUT_DIR / 'matched_predictions.csv'
    df_preds.to_csv(preds_out, index=False)
    print(f"Matched predictions saved to {preds_out} ({len(df_preds)} rows).")
    
    return df_preds

def compute_cluster_bootstrap_ci(sub_df: pd.DataFrame, cluster_col: str, n_boot: int = 2000) -> tuple[float, float, list[float]]:
    """Compute 95% Patient/Group Cluster Bootstrap CI for Macro-F1."""
    clusters = sub_df[cluster_col].unique()
    n_clusters = len(clusters)
    
    # Pre-index by cluster for fast sampling
    cluster_groups = [group for _, group in sub_df.groupby(cluster_col)]
    n_groups = len(cluster_groups)
    
    boot_macro_f1s = []
    
    for _ in range(n_boot):
        sampled_indices = np.random.choice(n_groups, size=n_groups, replace=True)
        sampled_dfs = [cluster_groups[i] for i in sampled_indices]
        sample_df = pd.concat(sampled_dfs, ignore_index=True)
        
        f1 = f1_score(sample_df['true_label'], sample_df['pred_label'], average='macro', zero_division=0)
        boot_macro_f1s.append(f1)
        
    ci_lower = float(np.percentile(boot_macro_f1s, 2.5))
    ci_upper = float(np.percentile(boot_macro_f1s, 97.5))
    return ci_lower, ci_upper, boot_macro_f1s

def compute_metrics_and_paired_differences(df_preds: pd.DataFrame):
    """Compute condition metrics, paired contrasts, and bootstrap distributions."""
    metrics_rows = []
    paired_results = {}
    
    conditions = ['I_orig', 'I_tumor', 'I_removed', 'I_placebo', 'I_context_shift', 'I_removed_feathered']
    
    for sc in ['S0', 'S1', 'S2']:
        print(f"\nComputing metrics and statistics for {sc}...")
        sc_df = df_preds[df_preds['scenario'] == sc]
        cluster_col = SCENARIOS[sc]['cluster_col']
        
        paired_results[sc] = {}
        
        # Store bootstrap replicate arrays per condition for paired contrasts
        boot_replicates_by_cond = {}
        
        # 1. Global Metrics per condition
        for cond in conditions:
            cond_df = sc_df[sc_df['condition'] == cond]
            
            y_true = cond_df['true_label'].values
            y_pred = cond_df['pred_label'].values
            
            macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
            bal_acc = balanced_accuracy_score(y_true, y_pred)
            acc = accuracy_score(y_true, y_pred)
            
            p, r, f, supp = precision_recall_fscore_support(y_true, y_pred, labels=[0, 1, 2], zero_division=0)
            cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist()
            
            # Flip stats
            flip_rate = float(np.mean(cond_df['flip_relative_to_orig']))
            trans_counts = cond_df['transition_type'].value_counts().to_dict()
            c2i = trans_counts.get('correct_to_incorrect', 0)
            i2c = trans_counts.get('incorrect_to_correct', 0)
            
            # Bootstrap CI for condition
            ci_low, ci_high, boot_f1s = compute_cluster_bootstrap_ci(cond_df, cluster_col, n_boot=2000)
            boot_replicates_by_cond[cond] = np.array(boot_f1s)
            
            metrics_rows.append({
                'scenario': sc,
                'fold': 'pooled',
                'condition': cond,
                'macro_f1': macro_f1,
                'macro_f1_ci_lower': ci_low,
                'macro_f1_ci_upper': ci_high,
                'balanced_accuracy': bal_acc,
                'overall_accuracy': acc,
                'f1_meningioma': f[0],
                'precision_meningioma': p[0],
                'recall_meningioma': r[0],
                'f1_glioma': f[1],
                'precision_glioma': p[1],
                'recall_glioma': r[1],
                'f1_pituitary': f[2],
                'precision_pituitary': p[2],
                'recall_pituitary': r[2],
                'flip_rate': flip_rate,
                'correct_to_incorrect': c2i,
                'incorrect_to_correct': i2c,
                'mean_entropy': float(cond_df['entropy'].mean()),
                'confusion_matrix': json.dumps(cm)
            })
            
            # Per-fold metrics
            for fold in range(1, 6):
                fold_str = f"fold_{fold}"
                f_df = cond_df[cond_df['fold'] == fold_str]
                yf_true = f_df['true_label'].values
                yf_pred = f_df['pred_label'].values
                f_f1 = f1_score(yf_true, yf_pred, average='macro', zero_division=0)
                f_bal = balanced_accuracy_score(yf_true, yf_pred)
                f_acc = accuracy_score(yf_true, yf_pred)
                pf, rf, ff, _ = precision_recall_fscore_support(yf_true, yf_pred, labels=[0, 1, 2], zero_division=0)
                
                metrics_rows.append({
                    'scenario': sc,
                    'fold': fold_str,
                    'condition': cond,
                    'macro_f1': f_f1,
                    'macro_f1_ci_lower': None,
                    'macro_f1_ci_upper': None,
                    'balanced_accuracy': f_bal,
                    'overall_accuracy': f_acc,
                    'f1_meningioma': ff[0],
                    'precision_meningioma': pf[0],
                    'recall_meningioma': rf[0],
                    'f1_glioma': ff[1],
                    'precision_glioma': pf[1],
                    'recall_glioma': rf[1],
                    'f1_pituitary': ff[2],
                    'precision_pituitary': pf[2],
                    'recall_pituitary': rf[2],
                    'flip_rate': float(np.mean(f_df['flip_relative_to_orig'])),
                    'correct_to_incorrect': int(sum(f_df['transition_type'] == 'correct_to_incorrect')),
                    'incorrect_to_correct': int(sum(f_df['transition_type'] == 'incorrect_to_correct')),
                    'mean_entropy': float(f_df['entropy'].mean()),
                    'confusion_matrix': json.dumps(confusion_matrix(yf_true, yf_pred, labels=[0, 1, 2]).tolist())
                })
                
        # 2. Paired Differences & Hypothesis Contrasts
        # Pre-registered contrasts:
        # 1. Delta_removal = Macro-F1(I_orig) - Macro-F1(I_removed)
        # 2. Delta_placebo = Macro-F1(I_orig) - Macro-F1(I_placebo)
        # 3. Delta_tumor = Macro-F1(I_tumor) - Chance (1/3)
        # 4. Delta_context_shift = Macro-F1(I_orig) - Macro-F1(I_context_shift)
        # 5. Net_tumor_reliance = Delta_removal - Delta_placebo
        # 6. Sensitivity check: Delta_removal_feathered = Macro-F1(I_orig) - Macro-F1(I_removed_feathered)
        
        orig_f1 = boot_replicates_by_cond['I_orig']
        rem_f1 = boot_replicates_by_cond['I_removed']
        plac_f1 = boot_replicates_by_cond['I_placebo']
        tum_f1 = boot_replicates_by_cond['I_tumor']
        ctx_f1 = boot_replicates_by_cond['I_context_shift']
        feath_f1 = boot_replicates_by_cond['I_removed_feathered']
        
        delta_removal_reps = orig_f1 - rem_f1
        delta_placebo_reps = orig_f1 - plac_f1
        delta_tumor_reps = tum_f1 - (1.0 / 3.0)
        delta_ctx_reps = orig_f1 - ctx_f1
        net_reliance_reps = delta_removal_reps - delta_placebo_reps
        delta_feathered_reps = orig_f1 - feath_f1
        
        # McNemar Discordance Test on I_orig vs I_removed:
        # b = correct in orig, incorrect in removed
        # c = incorrect in orig, correct in removed
        # Chi2 = (|b - c| - 1)^2 / (b + c)
        rem_df = sc_df[sc_df['condition'] == 'I_removed']
        b_mcnemar = int(sum(rem_df['transition_type'] == 'correct_to_incorrect'))
        c_mcnemar = int(sum(rem_df['transition_type'] == 'incorrect_to_correct'))
        mcnemar_stat = float(((abs(b_mcnemar - c_mcnemar) - 1)**2) / (b_mcnemar + c_mcnemar)) if (b_mcnemar + c_mcnemar) > 0 else 0.0
        from scipy.stats import chi2
        mcnemar_pval = float(1.0 - chi2.cdf(mcnemar_stat, df=1))
        
        # Wilcoxon signed-rank on per-patient accuracy difference between orig and removed
        orig_pats = sc_df[sc_df['condition'] == 'I_orig'].groupby('patient_id')['correct'].mean()
        rem_pats = sc_df[sc_df['condition'] == 'I_removed'].groupby('patient_id')['correct'].mean()
        diffs = orig_pats - rem_pats
        try:
            w_stat, w_pval = wilcoxon(diffs[diffs != 0])
            w_stat, w_pval = float(w_stat), float(w_pval)
        except Exception:
            w_stat, w_pval = 0.0, 1.0
            
        # Point estimates
        orig_pt = f1_score(sc_df[sc_df['condition'] == 'I_orig']['true_label'], sc_df[sc_df['condition'] == 'I_orig']['pred_label'], average='macro')
        rem_pt = f1_score(sc_df[sc_df['condition'] == 'I_removed']['true_label'], sc_df[sc_df['condition'] == 'I_removed']['pred_label'], average='macro')
        plac_pt = f1_score(sc_df[sc_df['condition'] == 'I_placebo']['true_label'], sc_df[sc_df['condition'] == 'I_placebo']['pred_label'], average='macro')
        tum_pt = f1_score(sc_df[sc_df['condition'] == 'I_tumor']['true_label'], sc_df[sc_df['condition'] == 'I_tumor']['pred_label'], average='macro')
        ctx_pt = f1_score(sc_df[sc_df['condition'] == 'I_context_shift']['true_label'], sc_df[sc_df['condition'] == 'I_context_shift']['pred_label'], average='macro')
        feath_pt = f1_score(sc_df[sc_df['condition'] == 'I_removed_feathered']['true_label'], sc_df[sc_df['condition'] == 'I_removed_feathered']['pred_label'], average='macro')
        
        delta_rem_pt = float(orig_pt - rem_pt)
        delta_plac_pt = float(orig_pt - plac_pt)
        delta_tum_pt = float(tum_pt - (1.0 / 3.0))
        delta_ctx_pt = float(orig_pt - ctx_pt)
        net_rel_pt = float(delta_rem_pt - delta_plac_pt)
        delta_feath_pt = float(orig_pt - feath_pt)
        
        # Pre-registered 3-Zone Decision:
        # Zone 1: Delta_removal < 0.05
        # Zone 2: 0.05 <= Delta_removal < 0.10
        # Zone 3: Delta_removal >= 0.10
        if delta_rem_pt < 0.05:
            zone = "Zone 1 (Predominant Context Shortcut Reliance)"
            zone_code = "ZONE_1"
        elif delta_rem_pt < 0.10:
            zone = "Zone 2 (Dual / Shared Reliance)"
            zone_code = "ZONE_2"
        else:
            zone = "Zone 3 (Primary Intratumoral Reliance)"
            zone_code = "ZONE_3"
            
        ci_rem = [float(np.percentile(delta_removal_reps, 2.5)), float(np.percentile(delta_removal_reps, 97.5))]
        ci_plac = [float(np.percentile(delta_placebo_reps, 2.5)), float(np.percentile(delta_placebo_reps, 97.5))]
        ci_tum = [float(np.percentile(delta_tumor_reps, 2.5)), float(np.percentile(delta_tumor_reps, 97.5))]
        ci_ctx = [float(np.percentile(delta_ctx_reps, 2.5)), float(np.percentile(delta_ctx_reps, 97.5))]
        ci_net = [float(np.percentile(net_reliance_reps, 2.5)), float(np.percentile(net_reliance_reps, 97.5))]
        ci_feath = [float(np.percentile(delta_feathered_reps, 2.5)), float(np.percentile(delta_feathered_reps, 97.5))]
        
        # Check if CI spans zones
        spans_boundary = False
        if ci_rem[0] < 0.05 and ci_rem[1] >= 0.05:
            spans_boundary = True
        elif ci_rem[0] < 0.10 and ci_rem[1] >= 0.10:
            spans_boundary = True
            
        paired_results[sc] = {
            'macro_f1_orig': float(orig_pt),
            'macro_f1_removed': float(rem_pt),
            'macro_f1_placebo': float(plac_pt),
            'macro_f1_tumor': float(tum_pt),
            'macro_f1_context_shift': float(ctx_pt),
            'macro_f1_removed_feathered': float(feath_pt),
            
            'Delta_removal': {
                'point_estimate': delta_rem_pt,
                'ci_95': ci_rem,
                'definition': 'Macro-F1(I_orig) - Macro-F1(I_removed)'
            },
            'Delta_placebo': {
                'point_estimate': delta_plac_pt,
                'ci_95': ci_plac,
                'definition': 'Macro-F1(I_orig) - Macro-F1(I_placebo)'
            },
            'Delta_tumor': {
                'point_estimate': delta_tum_pt,
                'ci_95': ci_tum,
                'definition': 'Macro-F1(I_tumor) - Chance(0.3333)'
            },
            'Delta_context_shift': {
                'point_estimate': delta_ctx_pt,
                'ci_95': ci_ctx,
                'definition': 'Macro-F1(I_orig) - Macro-F1(I_context_shift)'
            },
            'Net_tumor_reliance': {
                'point_estimate': net_rel_pt,
                'ci_95': ci_net,
                'definition': 'Delta_removal - Delta_placebo'
            },
            'Delta_removal_feathered': {
                'point_estimate': delta_feath_pt,
                'ci_95': ci_feath,
                'definition': 'Macro-F1(I_orig) - Macro-F1(I_removed_feathered)'
            },
            
            'mcnemar_test_removal': {
                'discordant_b_correct_to_incorrect': b_mcnemar,
                'discordant_c_incorrect_to_correct': c_mcnemar,
                'statistic': mcnemar_stat,
                'p_value': mcnemar_pval
            },
            'wilcoxon_patient_f1_diff': {
                'statistic': w_stat,
                'p_value': w_pval
            },
            
            'zone_assignment': {
                'zone_code': zone_code,
                'zone_name': zone,
                'spans_zone_boundary': spans_boundary
            }
        }
        
    # Save CSV and JSON
    df_metrics = pd.DataFrame(metrics_rows)
    df_metrics.to_csv(OUTPUT_DIR / 'metrics_by_condition.csv', index=False)
    print(f"Metrics by condition saved to {OUTPUT_DIR / 'metrics_by_condition.csv'}.")
    
    with open(OUTPUT_DIR / 'paired_differences.json', 'w') as f:
        json.dump(paired_results, f, indent=2)
    print(f"Paired differences saved to {OUTPUT_DIR / 'paired_differences.json'}.")
    
    return df_metrics, paired_results

if __name__ == '__main__':
    data_store, manifest_df = load_all_data()
    df_preds = run_scenario_interventions(data_store)
    df_metrics, paired_results = compute_metrics_and_paired_differences(df_preds)
    print("\nPhase 3 intervention study execution completed successfully!")
