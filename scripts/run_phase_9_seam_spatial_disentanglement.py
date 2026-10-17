"""
Phase 9 — Controlled Experiment: Seam Artifacts vs Spatial-Layout Disruption
Authoritative execution pipeline evaluating C0 (Baseline), C1 (Seam-Only),
C2 (Seam-Suppressed), and C3 (C5LP Scramble) across 3,064 MRI slices,
3 scenarios (S0, S1, S2), and 15 frozen ResNet-50 checkpoints.
"""

import os
import sys
import time
import json
import math
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
import cv2
import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms as T
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement'
PANEL_DIR = OUTPUT_DIR / 'visual_audit_panels'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PANEL_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
BOOTSTRAP_REPLICATES = 2000
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

CLASS_NAMES = ['meningioma', 'glioma', 'pituitary']
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}

SCENARIOS = {
    'S0': {
        'name': 'Patient-Disjoint Split',
        'manifest': ROOT / 'prepared_full_run' / 'patient_splits.csv',
        'cluster_col': 'patient_id'
    },
    'S1': {
        'name': 'Duplicate-Cleaned (SSIM 0.80)',
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_80.csv',
        'cluster_col': 'combined_group_id'
    },
    'S2': {
        'name': 'Aggressive Grouping (SSIM 0.75)',
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_75.csv',
        'cluster_col': 'combined_group_id'
    }
}

CONDITIONS = ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']


def compute_sobel_mag(arr: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return np.sqrt(gx**2 + gy**2)


def compute_spectral_energy(arr: np.ndarray, high_freq_mask: np.ndarray) -> float:
    f = np.fft.fft2(arr.astype(np.float32))
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    return float(np.mean(mag[high_freq_mask]))


def load_data_and_generate_phase9_conditions():
    """Build C0, C1, C2, C3 and comprehensive diagnostics for all 3,064 samples."""
    print("=" * 75, flush=True)
    print("PHASE 9: Generating C0, C1, C2, C3 conditions & image diagnostics...", flush=True)
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    
    elem31 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    rect3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    patch_size = 16
    
    # Precompute high-frequency spectral masks for supported shapes
    masks_hf = {}
    for s_dim in [512, 256]:
        cy, cx = s_dim // 2, s_dim // 2
        y_g, x_g = np.ogrid[:s_dim, :s_dim]
        r_g = np.sqrt((x_g - cx)**2 + (y_g - cy)**2)
        masks_hf[s_dim] = r_g > (s_dim * 0.25)
    
    data_store = {}
    validity_rows = []
    stats_rows = []
    
    t0 = time.time()
    for idx, row in meta_df.iterrows():
        sid = row['sample_id']
        cls_name = row['class_name']
        cls_label = CLASS_TO_IDX[cls_name]
        pid = row['patient_id']
        
        img_path = ROOT / 'prepared_full_run' / row['image_output_path']
        mask_path = ROOT / 'prepared_full_run' / row['mask_output_path']
        
        img = np.array(Image.open(img_path).convert('L'))
        mask = (np.array(Image.open(mask_path)) > 0).astype(np.uint8)
        
        h, w = img.shape
        grid_y, grid_x = h // patch_size, w // patch_size
        high_freq_mask = masks_hf.get(h, None)
        if high_freq_mask is None:
            cy, cx = h // 2, w // 2
            y_g, x_g = np.ogrid[:h, :w]
            r_g = np.sqrt((x_g - cx)**2 + (y_g - cy)**2)
            high_freq_mask = r_g > (min(h, w) * 0.25)
        
        # 15px protected margin
        m_dil15 = cv2.dilate(mask, elem31, iterations=1)
        
        # Eligible distant coords
        pure_distant_coords = []
        for gy in range(grid_y):
            for gx in range(grid_x):
                y1, y2 = gy * patch_size, (gy + 1) * patch_size
                x1, x2 = gx * patch_size, (gx + 1) * patch_size
                if not np.any(m_dil15[y1:y2, x1:x2] > 0):
                    pure_distant_coords.append((gy, gx))
                    
        distant_set = set(pure_distant_coords)
        
        # Deterministic permutation per sample (matching Phase 6 C5LP exactly)
        sid_hash_int = int(hashlib.sha256(str(sid).encode('utf-8')).hexdigest()[:8], 16)
        sample_seed = (SEED + sid_hash_int) % (2**32)
        rng = np.random.RandomState(sample_seed)
        perm = rng.permutation(len(pure_distant_coords))
        
        distant_patches = [
            img[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size].copy()
            for gy, gx in pure_distant_coords
        ]
        
        # C0: Original baseline
        i_c0 = img.copy()
        
        # C3: Original C5LP scramble
        i_c3 = img.copy()
        for i, (gy, gx) in enumerate(pure_distant_coords):
            i_c3[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size] = distant_patches[perm[i]]
            
        # Seam grid mask (1-pixel seam lines between adjacent distant tiles)
        seam_1px = np.zeros_like(img, dtype=np.uint8)
        for gy, gx in pure_distant_coords:
            y1, y2 = gy * patch_size, (gy + 1) * patch_size
            x1, x2 = gx * patch_size, (gx + 1) * patch_size
            if (gy, gx + 1) in distant_set:
                seam_1px[y1:y2, x2-1:x2] = 1
            if (gy + 1, gx) in distant_set:
                seam_1px[y2-1:y2, x1:x2] = 1
        seam_1px[m_dil15 > 0] = 0
        
        # Seam evaluation mask (3px wide)
        seam_eval_mask = (cv2.dilate(seam_1px, rect3) > 0)
        seam_eval_mask[m_dil15 > 0] = False
        
        # Interior distant mask (away from seams)
        distant_interior_mask = np.zeros_like(img, dtype=bool)
        for gy, gx in pure_distant_coords:
            y1, y2 = gy * patch_size, (gy + 1) * patch_size
            x1, x2 = gx * patch_size, (gx + 1) * patch_size
            distant_interior_mask[y1+2:y2-2, x1+2:x2-2] = True
        distant_interior_mask[m_dil15 > 0] = False
        
        # C1: Seam-Only Control
        # Injects C5LP inter-tile DC offsets onto unpermuted anatomical tiles
        i_c1 = img.copy().astype(np.float32)
        for i, (gy, gx) in enumerate(pure_distant_coords):
            orig_p = img[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size]
            perm_p = distant_patches[perm[i]]
            mean_diff = float(np.mean(perm_p)) - float(np.mean(orig_p))
            i_c1[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size] += mean_diff
        i_c1 = np.clip(i_c1, 0, 255).astype(np.uint8)
        i_c1[m_dil15 > 0] = img[m_dil15 > 0]
        
        # C2: Seam-Suppressed Spatial Rearrangement
        # Distance-weighted boundary blending along seam grid (ksize=9, sigma=2.5, width=4px)
        blur_c3 = cv2.GaussianBlur(i_c3, (9, 9), sigmaX=2.5)
        dist_to_seam = cv2.distanceTransform(1 - seam_1px, cv2.DIST_L2, 3)
        blend_weight = np.clip(1.0 - dist_to_seam / 4.0, 0.0, 1.0)
        blend_weight[m_dil15 > 0] = 0.0
        
        i_c2 = (i_c3.astype(np.float32) * (1.0 - blend_weight) + blur_c3.astype(np.float32) * blend_weight).astype(np.uint8)
        i_c2[m_dil15 > 0] = img[m_dil15 > 0]
        
        # Invariants verification
        assert np.max(np.abs(i_c1[mask > 0] - img[mask > 0])) == 0, f"C1 modified tumor in {sid}!"
        assert np.max(np.abs(i_c1[m_dil15 > 0] - img[m_dil15 > 0])) == 0, f"C1 modified margin in {sid}!"
        assert np.max(np.abs(i_c2[mask > 0] - img[mask > 0])) == 0, f"C2 modified tumor in {sid}!"
        assert np.max(np.abs(i_c2[m_dil15 > 0] - img[m_dil15 > 0])) == 0, f"C2 modified margin in {sid}!"
        assert np.max(np.abs(i_c3[mask > 0] - img[mask > 0])) == 0, f"C3 modified tumor in {sid}!"
        assert np.max(np.abs(i_c3[m_dil15 > 0] - img[m_dil15 > 0])) == 0, f"C3 modified margin in {sid}!"
        
        # Build PIL images resized to 224x224
        cond_arrays = {
            'C0_orig': i_c0,
            'C1_seam_only': i_c1,
            'C2_seam_suppressed': i_c2,
            'C3_c5lp_scramble': i_c3
        }
        
        pil_dict = {
            c: Image.fromarray(arr).convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
            for c, arr in cond_arrays.items()
        }
        
        data_store[sid] = {
            'images': pil_dict,
            'class_label': cls_label,
            'class_name': cls_name,
            'patient_id': pid
        }
        
        # Collect validity and image statistics
        total_px = h * w
        pure_distant_px = len(pure_distant_coords) * 256
        
        validity_rows.append({
            'sample_id': sid,
            'patient_id': pid,
            'class_name': cls_name,
            'tumor_pixels': int(np.sum(mask > 0)),
            'margin_15_pixels': int(np.sum((m_dil15 > 0) & (mask == 0))),
            'distant_eligible_patches': len(pure_distant_coords),
            'distant_eligible_pixels': pure_distant_px,
            'c1_tumor_altered': int(np.sum(i_c1[mask > 0] != img[mask > 0])),
            'c1_margin_altered': int(np.sum(i_c1[m_dil15 > 0] != img[m_dil15 > 0])),
            'c2_tumor_altered': int(np.sum(i_c2[mask > 0] != img[mask > 0])),
            'c2_margin_altered': int(np.sum(i_c2[m_dil15 > 0] != img[m_dil15 > 0])),
            'c3_tumor_altered': int(np.sum(i_c3[mask > 0] != img[mask > 0])),
            'c3_margin_altered': int(np.sum(i_c3[m_dil15 > 0] != img[m_dil15 > 0])),
            'validity_status': 'PASS'
        })
        
        for cname, arr in cond_arrays.items():
            diff = np.abs(arr.astype(np.float32) - img.astype(np.float32))
            changed_px = int(np.sum(diff > 0))
            sob_mag = compute_sobel_mag(arr)
            
            stats_rows.append({
                'sample_id': sid,
                'condition': cname,
                'mean_intensity': float(np.mean(arr)),
                'std_intensity': float(np.std(arr)),
                'changed_pixel_count': changed_px,
                'changed_pixel_fraction': changed_px / total_px,
                'mean_abs_difference': float(np.mean(diff)),
                'sobel_energy_whole': float(np.mean(sob_mag)),
                'sobel_energy_seam': float(np.mean(sob_mag[seam_eval_mask])) if np.any(seam_eval_mask) else 0.0,
                'sobel_energy_interior': float(np.mean(sob_mag[distant_interior_mask])) if np.any(distant_interior_mask) else 0.0,
                'spectral_energy_hf': compute_spectral_energy(arr, high_freq_mask)
            })
            
        if (idx + 1) % 500 == 0 or (idx + 1) == len(meta_df):
            print(f"Generated {idx + 1}/{len(meta_df)} slices ({time.time() - t0:.1f}s)...", flush=True)
            
    val_df = pd.DataFrame(validity_rows)
    val_df.to_csv(OUTPUT_DIR / 'intervention_validity_audit.csv', index=False)
    
    stat_df = pd.DataFrame(stats_rows)
    stat_df.to_csv(OUTPUT_DIR / 'image_statistics.csv', index=False)
    
    print("Conditions & statistics saved cleanly.", flush=True)
    return data_store, meta_df


def generate_visual_audit_panels(meta_df: pd.DataFrame, data_store: dict):
    """Generate high-resolution visual audit panels across multiple tumor classes."""
    print("Generating visual audit contact sheet and panels...", flush=True)
    elem31 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    
    # Select 2 representative slices per class (6 total)
    selected_sids = []
    for cls in CLASS_NAMES:
        subset = meta_df[meta_df['class_name'] == cls]
        selected_sids.extend(subset['sample_id'].iloc[:2].tolist())
        
    panel_imgs = []
    for sid in selected_sids:
        row = meta_df[meta_df['sample_id'] == sid].iloc[0]
        cls = row['class_name']
        img_p = ROOT / 'prepared_full_run' / row['image_output_path']
        mask_p = ROOT / 'prepared_full_run' / row['mask_output_path']
        
        orig = np.array(Image.open(img_p).convert('L'))
        mask = (np.array(Image.open(mask_p)) > 0).astype(np.uint8)
        m_dil = cv2.dilate(mask, elem31)
        
        # Load conditions from data_store
        pil_c0 = data_store[sid]['images']['C0_orig']
        pil_c1 = data_store[sid]['images']['C1_seam_only']
        pil_c2 = data_store[sid]['images']['C2_seam_suppressed']
        pil_c3 = data_store[sid]['images']['C3_c5lp_scramble']
        
        arr_c0 = np.array(pil_c0.convert('L'))
        arr_c1 = np.array(pil_c1.convert('L'))
        arr_c2 = np.array(pil_c2.convert('L'))
        arr_c3 = np.array(pil_c3.convert('L'))
        
        diff_c1 = np.clip(np.abs(arr_c1.astype(float) - arr_c0.astype(float)) * 3, 0, 255).astype(np.uint8)
        diff_c2 = np.clip(np.abs(arr_c2.astype(float) - arr_c0.astype(float)) * 3, 0, 255).astype(np.uint8)
        diff_c3 = np.clip(np.abs(arr_c3.astype(float) - arr_c0.astype(float)) * 3, 0, 255).astype(np.uint8)
        
        sob_c0 = cv2.normalize(compute_sobel_mag(arr_c0), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        sob_c1 = cv2.normalize(compute_sobel_mag(arr_c1), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        sob_c2 = cv2.normalize(compute_sobel_mag(arr_c2), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        sob_c3 = cv2.normalize(compute_sobel_mag(arr_c3), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Row 1: Images (C0, C1, C2, C3)
        row1 = np.hstack([arr_c0, arr_c1, arr_c2, arr_c3])
        # Row 2: Difference maps
        row2 = np.hstack([np.zeros_like(arr_c0), diff_c1, diff_c2, diff_c3])
        # Row 3: Sobel maps
        row3 = np.hstack([sob_c0, sob_c1, sob_c2, sob_c3])
        
        panel = np.vstack([row1, row2, row3])
        out_p = PANEL_DIR / f"panel_sample_{sid}_{cls}.png"
        Image.fromarray(panel).save(out_p)
        panel_imgs.append(panel)
        
    # Build consolidated contact sheet (6 panels stacked)
    contact_sheet = np.vstack(panel_imgs)
    Image.fromarray(contact_sheet).save(OUTPUT_DIR / 'condition_visual_audit_contact_sheet.png')
    # Save PDF version as required
    Image.fromarray(contact_sheet).save(OUTPUT_DIR / 'condition_visual_audit.pdf')
    print("Visual audit panels and PDF saved.", flush=True)


def run_frozen_checkpoint_inference(data_store: dict):
    """Run model inference on 15 frozen checkpoints across S0, S1, S2 for C0, C1, C2, C3."""
    print("=" * 75, flush=True)
    print("Running frozen ResNet-50 inference (36,768 forward passes)...", flush=True)
    
    eval_transform = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    all_predictions = []
    t0_inf = time.time()
    
    for sc, sc_info in SCENARIOS.items():
        print(f"\nEvaluating Scenario {sc} ({sc_info['name']})...", flush=True)
        manifest = pd.read_csv(sc_info['manifest'])
        cluster_col = sc_info['cluster_col']
        
        for fold in range(1, 6):
            fold_str = f"fold_{fold}"
            if 'fold' in manifest.columns:
                fold_matches = manifest['fold'].astype(str).isin([str(fold), fold_str])
            elif 'test_fold' in manifest.columns:
                fold_matches = manifest['test_fold'].astype(str).isin([str(fold), fold_str])
            else:
                raise KeyError(f"Fold column missing in {sc_info['manifest']}")
                
            test_subset = manifest[fold_matches]
            
            # Load frozen checkpoint
            ckpt_p = ROOT / 'experiments' / 'phase_2_baseline' / sc / f"fold_{fold}_best_checkpoint.pt"
            ckpt = torch.load(ckpt_p, map_location='cpu', weights_only=True)
            model = models.resnet50()
            model.fc = nn.Linear(model.fc.in_features, 3)
            model.load_state_dict(ckpt['model_state_dict'])
            model = model.to(DEVICE).eval()
            
            batch_size = 64
            samples_list = test_subset.to_dict('records')
            
            for cond in CONDITIONS:
                for b_start in range(0, len(samples_list), batch_size):
                    batch_samples = samples_list[b_start:b_start + batch_size]
                    batch_t = torch.stack([
                        eval_transform(data_store[s['sample_id']]['images'][cond])
                        for s in batch_samples
                    ]).to(DEVICE)
                    
                    with torch.no_grad():
                        with torch.amp.autocast('cuda'):
                            logits = model(batch_t)
                            probs = torch.softmax(logits, dim=1).cpu().numpy()
                            preds = np.argmax(probs, axis=1)
                            
                    for i, s in enumerate(batch_samples):
                        sid = s['sample_id']
                        cid = s[cluster_col]
                        true_lbl = data_store[sid]['class_label']
                        pred_lbl = int(preds[i])
                        prob_vec = probs[i]
                        
                        all_predictions.append({
                            'scenario': sc,
                            'fold': fold,
                            'condition': cond,
                            'sample_id': sid,
                            'patient_id': data_store[sid]['patient_id'],
                            'cluster_id': cid,
                            'true_label': true_lbl,
                            'class_name': CLASS_NAMES[true_lbl],
                            'pred_label': pred_lbl,
                            'pred_class': CLASS_NAMES[pred_lbl],
                            'prob_meningioma': float(prob_vec[0]),
                            'prob_glioma': float(prob_vec[1]),
                            'prob_pituitary': float(prob_vec[2]),
                            'correct': int(pred_lbl == true_lbl)
                        })
                        
    pred_df = pd.DataFrame(all_predictions)
    pred_df.to_csv(OUTPUT_DIR / 'matched_predictions.csv', index=False)
    print(f"Inference complete in {time.time() - t0_inf:.1f}s. Saved {len(pred_df)} predictions.", flush=True)
    return pred_df


def compute_metrics(y_true, y_pred):
    classes = [0, 1, 2]
    f1s = []
    recalls = []
    precisions = []
    for c in classes:
        tp = np.sum((y_true == c) & (y_pred == c))
        fp = np.sum((y_true != c) & (y_pred == c))
        fn = np.sum((y_true == c) & (y_pred != c))
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        f1s.append(f1)
        recalls.append(rec)
        precisions.append(prec)
    macro_f1 = float(np.mean(f1s))
    balanced_acc = float(np.mean(recalls))
    overall_acc = float(np.mean(y_true == y_pred))
    return {
        'macro_f1': macro_f1,
        'balanced_acc': balanced_acc,
        'accuracy': overall_acc,
        'f1_meningioma': f1s[0],
        'f1_glioma': f1s[1],
        'f1_pituitary': f1s[2],
        'recall_meningioma': recalls[0],
        'recall_glioma': recalls[1],
        'recall_pituitary': recalls[2],
        'prec_meningioma': precisions[0],
        'prec_glioma': precisions[1],
        'prec_pituitary': precisions[2],
    }


def run_statistical_analysis(pred_df: pd.DataFrame):
    """Compute primary metrics, synchronized paired cluster bootstrap, McNemar tests, and class transitions."""
    print("=" * 75, flush=True)
    print("Running synchronized paired cluster bootstrap (B=2,000) & statistical tests...", flush=True)
    
    primary_metrics_rows = []
    contrasts_rows = []
    bootstrap_rows = []
    transition_rows = []
    patient_effect_rows = []
    
    for sc in ['S0', 'S1', 'S2']:
        sc_df = pred_df[pred_df['scenario'] == sc]
        
        # 1. Primary metrics per condition
        cond_perf = {}
        for cond in CONDITIONS:
            sub = sc_df[sc_df['condition'] == cond]
            m = compute_metrics(sub['true_label'].values, sub['pred_label'].values)
            cond_perf[cond] = m
            primary_metrics_rows.append({
                'scenario': sc,
                'condition': cond,
                **m
            })
            
        # 2. Confusion matrices & class transitions (Glioma -> Pituitary)
        for cond in CONDITIONS:
            sub = sc_df[sc_df['condition'] == cond]
            y_t = sub['true_label'].values
            y_p = sub['pred_label'].values
            
            # Confusion matrix
            cm = np.zeros((3, 3), dtype=int)
            for t, p in zip(y_t, y_p):
                cm[t, p] += 1
                
            glioma_total = np.sum(y_t == 1)
            glioma_to_pit = np.sum((y_t == 1) & (y_p == 2))
            glioma_to_men = np.sum((y_t == 1) & (y_p == 0))
            
            transition_rows.append({
                'scenario': sc,
                'condition': cond,
                'glioma_total': int(glioma_total),
                'glioma_to_pituitary': int(glioma_to_pit),
                'glioma_to_pituitary_rate': float(glioma_to_pit / glioma_total),
                'glioma_to_meningioma': int(glioma_to_men),
                'glioma_to_meningioma_rate': float(glioma_to_men / glioma_total),
                'cm_00': int(cm[0, 0]), 'cm_01': int(cm[0, 1]), 'cm_02': int(cm[0, 2]),
                'cm_10': int(cm[1, 0]), 'cm_11': int(cm[1, 1]), 'cm_12': int(cm[1, 2]),
                'cm_20': int(cm[2, 0]), 'cm_21': int(cm[2, 1]), 'cm_22': int(cm[2, 2]),
            })
            
        # 3. Synchronized Paired Cluster Bootstrap
        clusters = sc_df['cluster_id'].unique()
        n_clusters = len(clusters)
        
        # Group by cluster for fast resampling
        cluster_groups = {c: sc_df[sc_df['cluster_id'] == c] for c in clusters}
        
        boot_deltas = {
            'C3_vs_C0': [],
            'C1_vs_C0': [],
            'C2_vs_C0': [],
            'C3_vs_C1': [],
            'C3_vs_C2': []
        }
        
        rng = np.random.RandomState(SEED)
        t0_boot = time.time()
        for b in range(BOOTSTRAP_REPLICATES):
            boot_clusts = rng.choice(clusters, size=n_clusters, replace=True)
            boot_df = pd.concat([cluster_groups[c] for c in boot_clusts], ignore_index=True)
            
            # Compute macro-F1 concurrently across conditions
            f1_dict = {}
            for cond in CONDITIONS:
                sub_c = boot_df[boot_df['condition'] == cond]
                f1_dict[cond] = compute_metrics(sub_c['true_label'].values, sub_c['pred_label'].values)['macro_f1']
                
            boot_deltas['C3_vs_C0'].append(f1_dict['C0_orig'] - f1_dict['C3_c5lp_scramble'])
            boot_deltas['C1_vs_C0'].append(f1_dict['C0_orig'] - f1_dict['C1_seam_only'])
            boot_deltas['C2_vs_C0'].append(f1_dict['C0_orig'] - f1_dict['C2_seam_suppressed'])
            boot_deltas['C3_vs_C1'].append(f1_dict['C1_seam_only'] - f1_dict['C3_c5lp_scramble'])
            boot_deltas['C3_vs_C2'].append(f1_dict['C2_seam_suppressed'] - f1_dict['C3_c5lp_scramble'])
            
        print(f"Bootstrap for {sc} completed in {time.time() - t0_boot:.1f}s.", flush=True)
        
        # McNemar transitions & Contrast metrics
        pivot_df = sc_df.pivot(index=['sample_id', 'cluster_id', 'true_label'], columns='condition', values='correct').reset_index()
        
        def run_mcnemar(c_a, c_b):
            n_10 = np.sum((pivot_df[c_a] == 1) & (pivot_df[c_b] == 0))
            n_01 = np.sum((pivot_df[c_a] == 0) & (pivot_df[c_b] == 1))
            chi2 = float((abs(n_10 - n_01) - 1)**2 / (n_10 + n_01)) if (n_10 + n_01) > 0 else 0.0
            pval = float(1.0 - stats.chi2.cdf(chi2, df=1)) if chi2 > 0 else 1.0
            return chi2, pval, int(n_10), int(n_01)
            
        contrast_pairs = [
            ('C3_vs_C0', 'C0_orig', 'C3_c5lp_scramble', 'Original Scrambling Effect'),
            ('C1_vs_C0', 'C0_orig', 'C1_seam_only', 'Seam-Only Effect'),
            ('C2_vs_C0', 'C0_orig', 'C2_seam_suppressed', 'Seam-Suppressed Spatial Rearrangement'),
            ('C3_vs_C1', 'C1_seam_only', 'C3_c5lp_scramble', 'Scramble vs Seam-Only Difference'),
            ('C3_vs_C2', 'C2_seam_suppressed', 'C3_c5lp_scramble', 'Sensitivity to Seam Suppression'),
        ]
        
        for c_id, cond_a, cond_b, desc in contrast_pairs:
            pt_est = cond_perf[cond_a]['macro_f1'] - cond_perf[cond_b]['macro_f1']
            b_arr = np.array(boot_deltas[c_id])
            ci_low = float(np.percentile(b_arr, 2.5))
            ci_high = float(np.percentile(b_arr, 97.5))
            chi2, pval, n_ab, n_ba = run_mcnemar(cond_a, cond_b)
            
            contrasts_rows.append({
                'scenario': sc,
                'contrast_id': c_id,
                'description': desc,
                'condition_a': cond_a,
                'condition_b': cond_b,
                'delta_macro_f1': float(pt_est),
                'ci_2_5': ci_low,
                'ci_97_5': ci_high,
                'mcnemar_chi2': chi2,
                'mcnemar_p_value': pval,
                'a_correct_b_wrong': n_ab,
                'b_correct_a_wrong': n_ba
            })
            
            for b_idx, val in enumerate(b_arr):
                bootstrap_rows.append({
                    'scenario': sc,
                    'contrast_id': c_id,
                    'replicate': b_idx,
                    'delta_macro_f1': float(val)
                })
                
        # 4. Patient-level distributions
        pat_summary = sc_df.groupby(['patient_id', 'condition'])['correct'].mean().unstack()
        for pid, row_p in pat_summary.iterrows():
            patient_effect_rows.append({
                'scenario': sc,
                'patient_id': pid,
                'c0_correct_rate': float(row_p.get('C0_orig', np.nan)),
                'c1_correct_rate': float(row_p.get('C1_seam_only', np.nan)),
                'c2_correct_rate': float(row_p.get('C2_seam_suppressed', np.nan)),
                'c3_correct_rate': float(row_p.get('C3_c5lp_scramble', np.nan)),
            })
            
    pd.DataFrame(primary_metrics_rows).to_csv(OUTPUT_DIR / 'primary_metrics.csv', index=False)
    pd.DataFrame(contrasts_rows).to_csv(OUTPUT_DIR / 'paired_contrasts.csv', index=False)
    pd.DataFrame(transition_rows).to_csv(OUTPUT_DIR / 'class_transition_analysis.csv', index=False)
    pd.DataFrame(bootstrap_rows).to_csv(OUTPUT_DIR / 'bootstrap_results.csv', index=False)
    pd.DataFrame(patient_effect_rows).to_csv(OUTPUT_DIR / 'patient_level_effects.csv', index=False)
    print("All statistical outputs saved successfully.", flush=True)
    return pd.DataFrame(contrasts_rows), pd.DataFrame(primary_metrics_rows), pd.DataFrame(transition_rows)


def main():
    t_start = time.time()
    print("=" * 75, flush=True)
    print("STARTING PHASE 9 CONTROLLED DISENTANGLEMENT EXPERIMENT", flush=True)
    print(f"Device: {DEVICE}", flush=True)
    
    # Check if predictions are already generated
    pred_path = OUTPUT_DIR / 'matched_predictions.csv'
    if pred_path.exists():
        pred_df = pd.read_csv(pred_path)
        if len(pred_df) == 36768:
            print(f"Loaded existing {len(pred_df)} matched predictions from disk.", flush=True)
        else:
            data_store, meta_df = load_data_and_generate_phase9_conditions()
            generate_visual_audit_panels(meta_df, data_store)
            pred_df = run_frozen_checkpoint_inference(data_store)
    else:
        # 1. Load data & generate conditions
        data_store, meta_df = load_data_and_generate_phase9_conditions()
        # 2. Visual audits
        generate_visual_audit_panels(meta_df, data_store)
        # 3. Model inference
        pred_df = run_frozen_checkpoint_inference(data_store)
    
    # 4. Statistical analysis
    contrasts_df, metrics_df, transitions_df = run_statistical_analysis(pred_df)
    
    total_time = time.time() - t_start
    log_text = f"Phase 9 experiment completed successfully in {total_time:.1f}s.\n"
    print("=" * 75, flush=True)
    print(log_text, flush=True)
    with open(OUTPUT_DIR / 'execution_log.txt', 'w') as f:
        f.write(log_text)


if __name__ == '__main__':
    main()
