#!/usr/bin/env python3
"""
Phase 6: Targeted Spatial Control Validation Study
==================================================
Runs inference and statistical verification for:
1. Experiment A: Luminance-Preserved Distant Context (C5LP)
2. Experiment B: Boundary-Controlled Navier-Stokes Margin Infill (C3NS)
3. Experiment C: Margin Thickness Sweep (r=5, 10, 15, 20 px) with matched placebos
Plus baseline and reference controls (C0, C1, C2, C5, C3_r15, C4_r15).

Total conditions evaluated: 14 conditions across 3,064 samples x 3 scenarios = 128,688 forward passes.
Performs synchronized paired patient-cluster bootstrap (B=2,000, seed=42).
Produces all required manifests, metrics, image statistics, and paired contrasts.
"""

import os
import sys
import time
import json
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
from scipy.ndimage import gaussian_filter

# Seed and Device
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    DEVICE = torch.device('cuda')
else:
    DEVICE = torch.device('cpu')

ROOT = Path('.')
OUTPUT_DIR = ROOT / 'experiments' / 'phase_6_spatial_controls'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = ['meningioma', 'glioma', 'pituitary']
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_NAMES)}

SCENARIOS = {
    'S0': {
        'name': 'Random Patient Split',
        'manifest': ROOT / 'prepared_full_run' / 'patient_splits.csv',
        'cluster_col': 'patient_id'
    },
    'S1': {
        'name': 'Regrouped Leakage-Free (SSIM 0.80)',
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_80.csv',
        'cluster_col': 'combined_group_id'
    },
    'S2': {
        'name': 'Aggressively Regrouped (SSIM 0.75)',
        'manifest': ROOT / 'experiments' / 'phase_1_7' / 'candidate_grouped_manifests' / 'split_regrouped_ssim_0_75.csv',
        'cluster_col': 'combined_group_id'
    }
}

CONDITIONS = [
    'I_orig',
    'I_tumor_removed',
    'I_placebo_focal',
    'I_distant_perturbed',
    'I_distant_luminance_preserved',
    'I_margin_r15_removed',
    'I_margin_r15_ns_inpaint',
    'I_margin_r15_placebo',
    'I_margin_r05_removed',
    'I_margin_r05_placebo',
    'I_margin_r10_removed',
    'I_margin_r10_placebo',
    'I_margin_r20_removed',
    'I_margin_r20_placebo'
]

RADII = [5, 10, 15, 20]

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_placebo_mask(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Generate matched placebo mask in contralateral hemisphere with shift if overlap."""
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
                if dy < h:
                    test_p = np.roll(placebo, -dy, axis=0)
                    test_p[-dy:, :] = 0
                    if not np.any(np.logical_and(mask > 0, test_p > 0)):
                        placebo = test_p
                        shift_applied = -dy
                        break
            else:
                if dy < h:
                    test_p = np.roll(placebo, dy, axis=0)
                    test_p[:dy, :] = 0
                    if not np.any(np.logical_and(mask > 0, test_p > 0)):
                        placebo = test_p
                        shift_applied = dy
                        break
    return placebo, shift_applied

def compute_boundary_step(image: np.ndarray, boundary_mask: np.ndarray) -> float:
    """Mean Sobel gradient magnitude along outer 1-pixel boundary of the given mask."""
    if np.sum(boundary_mask) == 0:
        return 0.0
    gx = cv2.Sobel(image.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(image.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx**2 + gy**2)
    dil = cv2.dilate(boundary_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    edge = ((dil > 0) & (boundary_mask == 0))
    return float(np.mean(mag[edge])) if np.any(edge) else 0.0

def load_data_and_generate_controls():
    """Load metadata, build all 14 conditions and image statistics for 3,064 samples."""
    print("=" * 70, flush=True)
    print("PHASE 6: Generating targeted spatial controls for 3,064 MRI slices...", flush=True)
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    
    # Pre-generate structuring elements for radii
    struct_elems = {
        r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        for r in RADII
    }
    
    data_store = {}
    manifest_rows = []
    image_stats_rows = []
    margin_sweep_rows = []
    
    t0 = time.time()
    for idx, row in meta_df.iterrows():
        sid = row['sample_id']
        cls_name = row['class_name']
        cls_label = CLASS_TO_IDX[cls_name]
        pid = row['patient_id']
        
        img_path = ROOT / 'prepared_full_run' / row['image_output_path']
        mask_path = ROOT / 'prepared_full_run' / row['mask_output_path']
        
        img = np.array(Image.open(img_path).convert('L'))
        mask = np.array(Image.open(mask_path))
        mask_bin = (mask > 0).astype(np.uint8)
        
        # 1. Base Placebo mask
        placebo_bin, shift_applied = generate_placebo_mask(mask_bin)
        
        # 2. Dilation rings for margin sweep (r=5, 10, 15, 20)
        m_dil = {}
        m_margin = {}
        p_dil = {}
        p_margin = {}
        for r in RADII:
            elem = struct_elems[r]
            m_dil[r] = cv2.dilate(mask_bin, elem, iterations=1)
            m_margin[r] = ((m_dil[r] > 0) & (mask_bin == 0)).astype(np.uint8)
            
            p_dil[r] = cv2.dilate(placebo_bin, elem, iterations=1)
            p_margin[r] = ((p_dil[r] > 0) & (placebo_bin == 0) & (mask_bin == 0)).astype(np.uint8)
            
        # 3. Experiment A: C5LP (16x16 patch scrambling outside m_dil[15])
        patch_size = 16
        h, w = img.shape
        grid_y, grid_x = h // patch_size, w // patch_size
        pure_distant_coords = []
        for gy in range(grid_y):
            for gx in range(grid_x):
                y1, y2 = gy * patch_size, (gy + 1) * patch_size
                x1, x2 = gx * patch_size, (gx + 1) * patch_size
                if not np.any(m_dil[15][y1:y2, x1:x2] > 0):
                    pure_distant_coords.append((gy, gx))
        
        # Seed deterministic per sample_id
        sid_hash_int = int(hashlib.sha256(str(sid).encode('utf-8')).hexdigest()[:8], 16)
        sample_seed = (SEED + sid_hash_int) % (2**32)
        rng = np.random.RandomState(sample_seed)
        perm = rng.permutation(len(pure_distant_coords))
        
        i_c5lp = img.copy()
        distant_patches = [img[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size].copy() for gy, gx in pure_distant_coords]
        for i, (gy, gx) in enumerate(pure_distant_coords):
            i_c5lp[gy*patch_size:(gy+1)*patch_size, gx*patch_size:(gx+1)*patch_size] = distant_patches[perm[i]]
            
        # 4. Experiment B: C3NS (Navier-Stokes inpainting over 15px margin ring)
        if np.sum(m_margin[15]) > 0:
            i_c3ns = cv2.inpaint(img, m_margin[15], inpaintRadius=3, flags=cv2.INPAINT_NS)
        else:
            i_c3ns = img.copy()
            
        # 5. Build condition array dict (512x512 uint8)
        img_dict_raw = {
            'I_orig': img.copy(),
            'I_tumor_removed': (img * (1 - mask_bin)).astype(np.uint8),
            'I_placebo_focal': (img * (1 - placebo_bin)).astype(np.uint8),
            'I_distant_perturbed': np.where(m_dil[15] > 0, img, np.clip(img * 0.50, 0, 255).astype(np.uint8)),
            'I_distant_luminance_preserved': i_c5lp,
            'I_margin_r15_removed': (img * (1 - m_margin[15])).astype(np.uint8),
            'I_margin_r15_ns_inpaint': i_c3ns,
            'I_margin_r15_placebo': (img * (1 - p_margin[15])).astype(np.uint8),
            'I_margin_r05_removed': (img * (1 - m_margin[5])).astype(np.uint8),
            'I_margin_r05_placebo': (img * (1 - p_margin[5])).astype(np.uint8),
            'I_margin_r10_removed': (img * (1 - m_margin[10])).astype(np.uint8),
            'I_margin_r10_placebo': (img * (1 - p_margin[10])).astype(np.uint8),
            'I_margin_r20_removed': (img * (1 - m_margin[20])).astype(np.uint8),
            'I_margin_r20_placebo': (img * (1 - p_margin[20])).astype(np.uint8),
        }
        
        # Verify invariants
        assert np.max(np.abs(i_c5lp[m_dil[15] > 0] - img[m_dil[15] > 0])) == 0, f"C5LP modified protected zone in {sid}!"
        assert np.isclose(np.mean(i_c5lp), np.mean(img)), f"C5LP global mean changed in {sid}!"
        assert np.max(np.abs(i_c3ns[mask_bin > 0] - img[mask_bin > 0])) == 0, f"C3NS modified tumor in {sid}!"
        assert np.max(np.abs(i_c3ns[(mask_bin == 0) & (m_margin[15] == 0)] - img[(mask_bin == 0) & (m_margin[15] == 0)])) == 0, f"C3NS modified outside in {sid}!"
        
        # Build PIL images (resized to 224x224 for ResNet-50)
        pil_dict = {
            cond: Image.fromarray(arr).convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
            for cond, arr in img_dict_raw.items()
        }
        
        data_store[sid] = {
            'images': pil_dict,
            'raw_img': img,
            'mask': mask_bin,
            'class_name': cls_name,
            'class_label': cls_label,
            'patient_id': pid
        }
        
        # Collect manifest metrics
        total_px = 512 * 512
        tumor_px = int(np.sum(mask_bin > 0))
        plac_focal_px = int(np.sum(placebo_bin > 0))
        c5lp_scrambled_px = len(pure_distant_coords) * 256
        
        manifest_rows.append({
            'sample_id': sid,
            'patient_id': pid,
            'class_name': cls_name,
            'class_label': cls_label,
            'tumor_area_pixels': tumor_px,
            'tumor_area_fraction': tumor_px / total_px,
            'placebo_focal_area_pixels': plac_focal_px,
            'placebo_shift_applied': shift_applied,
            'margin_r15_pixels': int(np.sum(m_margin[15] > 0)),
            'c5lp_scrambled_patches': len(pure_distant_coords),
            'c5lp_scrambled_pixels': c5lp_scrambled_px,
            'c5lp_scrambled_fraction': c5lp_scrambled_px / total_px,
            'c3ns_inpainted_pixels': int(np.sum(m_margin[15] > 0))
        })
        
        # Collect Image Statistics across conditions
        for cond, arr in img_dict_raw.items():
            diff = np.abs(arr.astype(np.float32) - img.astype(np.float32))
            changed_px = int(np.sum(diff > 0))
            
            # Step discontinuity on the intervention mask boundary
            if 'margin_r15' in cond or cond == 'I_margin_r15_ns_inpaint':
                step = compute_boundary_step(arr, m_margin[15])
            elif 'tumor' in cond:
                step = compute_boundary_step(arr, mask_bin)
            elif 'placebo_focal' in cond:
                step = compute_boundary_step(arr, placebo_bin)
            else:
                step = 0.0
                
            image_stats_rows.append({
                'sample_id': sid,
                'condition': cond,
                'mean_intensity': float(np.mean(arr)),
                'std_intensity': float(np.std(arr)),
                'p05_intensity': float(np.percentile(arr, 5)),
                'p50_intensity': float(np.median(arr)),
                'p95_intensity': float(np.percentile(arr, 95)),
                'changed_pixel_count': changed_px,
                'changed_pixel_fraction': changed_px / total_px,
                'mean_abs_difference': float(np.mean(diff)),
                'boundary_step_gradient': step
            })
            
        # Collect Margin Sweep geometry
        for r in RADII:
            margin_area = int(np.sum(m_margin[r] > 0))
            plac_area = int(np.sum(p_margin[r] > 0))
            step_margin = compute_boundary_step(img_dict_raw[f'I_margin_r{r:02d}_removed'], m_margin[r])
            step_plac = compute_boundary_step(img_dict_raw[f'I_margin_r{r:02d}_placebo'], p_margin[r])
            
            margin_sweep_rows.append({
                'sample_id': sid,
                'radius_pixels': r,
                'margin_area_pixels': margin_area,
                'margin_area_fraction': margin_area / total_px,
                'placebo_area_pixels': plac_area,
                'placebo_area_fraction': plac_area / total_px,
                'area_ratio_placebo_to_margin': (plac_area / margin_area) if margin_area > 0 else 1.0,
                'overlap_with_tumor_pixels': int(np.sum((m_margin[r] > 0) & (mask_bin > 0))),
                'placebo_overlap_with_tumor_pixels': int(np.sum((p_margin[r] > 0) & (mask_bin > 0))),
                'boundary_step_margin': step_margin,
                'boundary_step_placebo': step_plac
            })
            
        if (idx + 1) % 500 == 0 or (idx + 1) == len(meta_df):
            print(f"Processed {idx + 1}/{len(meta_df)} slices ({time.time() - t0:.1f}s)...", flush=True)
            
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_df.to_csv(OUTPUT_DIR / 'intervention_manifest.csv', index=False)
    
    stats_df = pd.DataFrame(image_stats_rows)
    stats_df.to_csv(OUTPUT_DIR / 'image_statistics.csv', index=False)
    
    sweep_df = pd.DataFrame(margin_sweep_rows)
    sweep_df.to_csv(OUTPUT_DIR / 'margin_thickness_sweep.csv', index=False)
    
    print("Spatial control generation complete. Manifest and statistics saved.", flush=True)
    return data_store

def load_checkpoint(scenario: str, fold_num: int) -> nn.Module:
    """Load frozen checkpoint from Phase 2."""
    ckpt_path = ROOT / 'experiments' / 'phase_2_baseline' / scenario / f"fold_{fold_num}_best_checkpoint.pt"
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
    model = models.resnet50()
    model.fc = nn.Linear(model.fc.in_features, 3)
    model.load_state_dict(ckpt['model_state_dict'])
    model = model.to(DEVICE).eval()
    return model

def run_frozen_checkpoint_inference(data_store: dict):
    """Run model inference on all frozen checkpoints across S0, S1, S2 for all 14 conditions."""
    print("=" * 70, flush=True)
    print("Running frozen ResNet-50 inference (128,688 forward passes)...", flush=True)
    eval_transform = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    all_matched_predictions = []
    t0_all = time.time()
    
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
            model = load_checkpoint(sc, fold)
            
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
                        
                        all_matched_predictions.append({
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
                            'is_correct': int(pred_lbl == true_lbl),
                            'prob_meningioma': float(prob_vec[0]),
                            'prob_glioma': float(prob_vec[1]),
                            'prob_pituitary': float(prob_vec[2])
                        })
            print(f"  Completed Scenario {sc} Fold {fold}/5", flush=True)
            
    print(f"\nAll inference complete in {time.time() - t0_all:.1f}s. Total predictions: {len(all_matched_predictions)}", flush=True)
    pred_df = pd.DataFrame(all_matched_predictions)
    pred_df.to_csv(OUTPUT_DIR / 'matched_predictions.csv', index=False)
    return pred_df

def macro_f1_from_cms(cms: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized Macro-F1 and per-class F1 from confusion matrix array (B, 3, 3)."""
    tps = np.diagonal(cms, axis1=1, axis2=2)
    col_sums = np.sum(cms, axis=1)
    row_sums = np.sum(cms, axis=2)
    with np.errstate(divide='ignore', invalid='ignore'):
        prec = np.where(col_sums > 0, tps / col_sums, 0.0)
        rec = np.where(row_sums > 0, tps / row_sums, 0.0)
        f1_denom = prec + rec
        class_f1s = np.where(f1_denom > 0, 2.0 * prec * rec / f1_denom, 0.0)
    macro_f1s = np.mean(class_f1s, axis=1)
    return macro_f1s, class_f1s

def run_synchronized_cluster_bootstrap(pred_df: pd.DataFrame, n_boot: int = 2000):
    """Run synchronized cluster bootstrap across scenarios and calculate paired contrasts."""
    print("=" * 70, flush=True)
    print(f"Running synchronized paired cluster bootstrap (B={n_boot}, seed={SEED})...", flush=True)
    
    paired_contrasts = {
        'metadata': {
            'phase': 6,
            'study_name': 'targeted_spatial_control_validation',
            'bootstrap_replicates': n_boot,
            'seed': SEED,
            'conditions': CONDITIONS,
            'scenarios': list(SCENARIOS.keys())
        },
        'results': {}
    }
    
    metrics_by_condition_rows = []
    
    for sc, sc_info in SCENARIOS.items():
        print(f"\nBootstrapping Scenario {sc}...", flush=True)
        paired_contrasts['results'][sc] = {
            'metrics_by_condition': {},
            'paired_contrasts': {},
            'experiment_a_distant_context': {},
            'experiment_b_margin_inpaint': {},
            'experiment_c_thickness_sweep': {}
        }
        
        sc_df = pred_df[pred_df['scenario'] == sc]
        
        # Unique clusters and mapping
        clusters = np.sort(sc_df['cluster_id'].unique())
        n_clusters = len(clusters)
        cluster_to_idx = {c: i for i, c in enumerate(clusters)}
        
        # Precompute per-cluster confusion matrix for each condition: shape (n_clusters, 3, 3)
        cond_cms = {}
        for cond in CONDITIONS:
            c_df = sc_df[sc_df['condition'] == cond]
            # Verify 3,064 records
            assert len(c_df) == 3064, f"Scenario {sc} condition {cond} has {len(c_df)} records!"
            
            c_indices = c_df['cluster_id'].map(cluster_to_idx).values
            trues = c_df['true_label'].values
            preds = c_df['pred_label'].values
            
            # CM bins 0..8
            bin_idx = trues * 3 + preds
            cms_grid = np.zeros((n_clusters, 9), dtype=np.int32)
            np.add.at(cms_grid, (c_indices, bin_idx), 1)
            cond_cms[cond] = cms_grid.reshape(n_clusters, 3, 3)
            
        # Point estimates (sum over all clusters)
        point_cms = {cond: np.sum(cond_cms[cond], axis=0, keepdims=True) for cond in CONDITIONS}
        point_metrics = {}
        for cond in CONDITIONS:
            macro_f1, class_f1s = macro_f1_from_cms(point_cms[cond])
            total_corr = np.sum(np.diagonal(point_cms[cond][0]))
            acc = total_corr / 3064.0
            
            # Balanced accuracy
            row_sums = np.sum(point_cms[cond][0], axis=1)
            tps = np.diagonal(point_cms[cond][0])
            bacc = float(np.mean(tps / row_sums))
            
            point_metrics[cond] = {
                'macro_f1': float(macro_f1[0]),
                'class_f1_meningioma': float(class_f1s[0, 0]),
                'class_f1_glioma': float(class_f1s[0, 1]),
                'class_f1_pituitary': float(class_f1s[0, 2]),
                'accuracy': float(acc),
                'balanced_accuracy': float(bacc)
            }
            
        # Synchronized cluster bootstrap resampling
        rng = np.random.RandomState(SEED)
        resample_indices = rng.choice(n_clusters, size=(n_boot, n_clusters), replace=True)
        
        # Resampled confusion matrices: shape (n_boot, 3, 3) for each condition
        boot_macro_f1s = {}
        boot_class_f1s = {}
        for cond in CONDITIONS:
            boot_cms = np.sum(cond_cms[cond][resample_indices], axis=1) # (n_boot, 3, 3)
            m_f1s, c_f1s = macro_f1_from_cms(boot_cms)
            boot_macro_f1s[cond] = m_f1s
            boot_class_f1s[cond] = c_f1s
            
            ci_macro = np.percentile(m_f1s, [2.5, 97.5])
            ci_pit = np.percentile(c_f1s[:, 2], [2.5, 97.5])
            
            paired_contrasts['results'][sc]['metrics_by_condition'][cond] = {
                'point_macro_f1': point_metrics[cond]['macro_f1'],
                'ci95_macro_f1': [float(ci_macro[0]), float(ci_macro[1])],
                'point_pituitary_f1': point_metrics[cond]['class_f1_pituitary'],
                'ci95_pituitary_f1': [float(ci_pit[0]), float(ci_pit[1])],
                'point_glioma_f1': point_metrics[cond]['class_f1_glioma'],
                'point_meningioma_f1': point_metrics[cond]['class_f1_meningioma'],
                'balanced_accuracy': point_metrics[cond]['balanced_accuracy']
            }
            
            metrics_by_condition_rows.append({
                'scenario': sc,
                'condition': cond,
                'macro_f1': point_metrics[cond]['macro_f1'],
                'ci95_lower': float(ci_macro[0]),
                'ci95_upper': float(ci_macro[1]),
                'balanced_accuracy': point_metrics[cond]['balanced_accuracy'],
                'f1_meningioma': point_metrics[cond]['class_f1_meningioma'],
                'f1_glioma': point_metrics[cond]['class_f1_glioma'],
                'f1_pituitary': point_metrics[cond]['class_f1_pituitary'],
                'pituitary_ci95_lower': float(ci_pit[0]),
                'pituitary_ci95_upper': float(ci_pit[1])
            })
            
        # Compute Paired Contrasts: Delta = Metric(CondA) - Metric(CondB)
        def eval_contrast(cond_a: str, cond_b: str, is_pituitary: bool = False):
            if is_pituitary:
                pt_a = point_metrics[cond_a]['class_f1_pituitary']
                pt_b = point_metrics[cond_b]['class_f1_pituitary']
                pt_diff = pt_a - pt_b
                diff_dist = boot_class_f1s[cond_a][:, 2] - boot_class_f1s[cond_b][:, 2]
            else:
                pt_a = point_metrics[cond_a]['macro_f1']
                pt_b = point_metrics[cond_b]['macro_f1']
                pt_diff = pt_a - pt_b
                diff_dist = boot_macro_f1s[cond_a] - boot_macro_f1s[cond_b]
                
            ci = np.percentile(diff_dist, [2.5, 97.5])
            
            # Paired transitions for McNemar
            df_a = sc_df[sc_df['condition'] == cond_a].sort_values('sample_id')
            df_b = sc_df[sc_df['condition'] == cond_b].sort_values('sample_id')
            corr_a = df_a['is_correct'].values
            corr_b = df_b['is_correct'].values
            
            n00 = int(np.sum((corr_a == 0) & (corr_b == 0)))
            n01 = int(np.sum((corr_a == 0) & (corr_b == 1))) # flipped incorrect to correct
            n10 = int(np.sum((corr_a == 1) & (corr_b == 0))) # flipped correct to incorrect
            n11 = int(np.sum((corr_a == 1) & (corr_b == 1)))
            
            # McNemar with continuity correction
            b, c = n10, n01
            if (b + c) > 0:
                chi2 = ((abs(b - c) - 1.0) ** 2) / (b + c)
            else:
                chi2 = 0.0
                
            return {
                'cond_a': cond_a,
                'cond_b': cond_b,
                'point_diff': float(pt_diff),
                'ci95': [float(ci[0]), float(ci[1])],
                'bootstrap_std': float(np.std(diff_dist)),
                'transitions': {'n00': n00, 'n01': n01, 'n10': n10, 'n11': n11},
                'mcnemar_stat': float(chi2)
            }
            
        # Core Contrasts
        paired_contrasts['results'][sc]['paired_contrasts']['tumor_removal'] = eval_contrast('I_orig', 'I_tumor_removed')
        paired_contrasts['results'][sc]['paired_contrasts']['placebo_focal'] = eval_contrast('I_orig', 'I_placebo_focal')
        
        # Net Tumor Reliance
        t_dist = (boot_macro_f1s['I_orig'] - boot_macro_f1s['I_tumor_removed']) - (boot_macro_f1s['I_orig'] - boot_macro_f1s['I_placebo_focal'])
        t_pt = point_metrics['I_placebo_focal']['macro_f1'] - point_metrics['I_tumor_removed']['macro_f1']
        t_ci = np.percentile(t_dist, [2.5, 97.5])
        paired_contrasts['results'][sc]['paired_contrasts']['net_tumor_reliance'] = {
            'point_diff': float(t_pt),
            'ci95': [float(t_ci[0]), float(t_ci[1])],
            'preregistered_threshold': 0.0500,
            'exceeds_threshold': bool(t_ci[0] > 0.0500)
        }
        
        # Experiment A: Distant Context vs Luminance-Preserved Scrambling
        c5_contrast = eval_contrast('I_orig', 'I_distant_perturbed')
        c5lp_contrast = eval_contrast('I_orig', 'I_distant_luminance_preserved')
        c5_vs_c5lp = eval_contrast('I_distant_luminance_preserved', 'I_distant_perturbed')
        
        pit_c5 = eval_contrast('I_orig', 'I_distant_perturbed', is_pituitary=True)
        pit_c5lp = eval_contrast('I_orig', 'I_distant_luminance_preserved', is_pituitary=True)
        pit_diff = eval_contrast('I_distant_luminance_preserved', 'I_distant_perturbed', is_pituitary=True)
        
        paired_contrasts['results'][sc]['experiment_a_distant_context'] = {
            'c5_dimming_contrast': c5_contrast,
            'c5lp_scrambling_contrast': c5lp_contrast,
            'c5lp_vs_c5_difference': c5_vs_c5lp,
            'pituitary_c5_dimming': pit_c5,
            'pituitary_c5lp_scrambling': pit_c5lp,
            'pituitary_attenuation_artifact_magnitude': pit_diff
        }
        
        # Experiment B: Margin Infill (C3_r15 vs C3NS vs C4_r15)
        c3_r15_contrast = eval_contrast('I_orig', 'I_margin_r15_removed')
        c3ns_contrast = eval_contrast('I_orig', 'I_margin_r15_ns_inpaint')
        c4_r15_contrast = eval_contrast('I_orig', 'I_margin_r15_placebo')
        
        # Net Margin for 15px ring
        net_m15_dist = (boot_macro_f1s['I_orig'] - boot_macro_f1s['I_margin_r15_removed']) - (boot_macro_f1s['I_orig'] - boot_macro_f1s['I_margin_r15_placebo'])
        net_m15_pt = point_metrics['I_margin_r15_placebo']['macro_f1'] - point_metrics['I_margin_r15_removed']['macro_f1']
        net_m15_ci = np.percentile(net_m15_dist, [2.5, 97.5])
        
        # Step artifact difference: C3_r15 vs C3NS
        step_diff_dist = boot_macro_f1s['I_margin_r15_ns_inpaint'] - boot_macro_f1s['I_margin_r15_removed']
        step_diff_pt = point_metrics['I_margin_r15_ns_inpaint']['macro_f1'] - point_metrics['I_margin_r15_removed']['macro_f1']
        step_diff_ci = np.percentile(step_diff_dist, [2.5, 97.5])
        
        paired_contrasts['results'][sc]['experiment_b_margin_inpaint'] = {
            'c3_r15_zero_fill': c3_r15_contrast,
            'c3ns_inpaint': c3ns_contrast,
            'c4_r15_placebo': c4_r15_contrast,
            'net_margin_r15_zero_fill': {
                'point_diff': float(net_m15_pt),
                'ci95': [float(net_m15_ci[0]), float(net_m15_ci[1])]
            },
            'step_artifact_magnitude_c3ns_minus_c3': {
                'point_diff': float(step_diff_pt),
                'ci95': [float(step_diff_ci[0]), float(step_diff_ci[1])]
            }
        }
        
        # Experiment C: Margin Thickness Sweep
        sweep_results = {}
        for r in RADII:
            c3_cond = f'I_margin_r{r:02d}_removed'
            c4_cond = f'I_margin_r{r:02d}_placebo'
            c3_c = eval_contrast('I_orig', c3_cond)
            c4_c = eval_contrast('I_orig', c4_cond)
            
            net_dist = (boot_macro_f1s['I_orig'] - boot_macro_f1s[c3_cond]) - (boot_macro_f1s['I_orig'] - boot_macro_f1s[c4_cond])
            net_pt = point_metrics[c4_cond]['macro_f1'] - point_metrics[c3_cond]['macro_f1']
            net_ci = np.percentile(net_dist, [2.5, 97.5])
            
            sweep_results[f'radius_{r}px'] = {
                'c3_contrast': c3_c,
                'c4_placebo_contrast': c4_c,
                'net_margin_reliance': {
                    'point_diff': float(net_pt),
                    'ci95': [float(net_ci[0]), float(net_ci[1])]
                }
            }
        paired_contrasts['results'][sc]['experiment_c_thickness_sweep'] = sweep_results
        
    # Save outputs
    with open(OUTPUT_DIR / 'paired_contrasts.json', 'w') as f:
        json.dump(paired_contrasts, f, indent=2)
        
    metrics_df = pd.DataFrame(metrics_by_condition_rows)
    metrics_df.to_csv(OUTPUT_DIR / 'metrics_by_condition.csv', index=False)
    
    print("\nStatistical reproduction and contrasts complete. Saved JSON and CSV.", flush=True)
    return paired_contrasts

def generate_checksums():
    """Generate SHA-256 checksums for all deliverables."""
    print("=" * 70, flush=True)
    print("Computing SHA-256 checksums for Phase 6 deliverables...", flush=True)
    files_to_hash = [
        'preregistration.md',
        'intervention_config.yaml',
        'intervention_manifest.csv',
        'matched_predictions.csv',
        'metrics_by_condition.csv',
        'paired_contrasts.json',
        'margin_thickness_sweep.csv',
        'image_statistics.csv',
        'intervention_quality_audit.md',
        'claim_evidence_matrix.md',
        'PHASE_6_REPORT.md'
    ]
    checksums = {}
    for fname in files_to_hash:
        fpath = OUTPUT_DIR / fname
        if fpath.exists():
            checksums[fname] = {
                'sha256': compute_sha256(fpath),
                'size_bytes': fpath.stat().st_size
            }
        else:
            print(f"Warning: {fname} not found yet for checksums.")
            
    with open(OUTPUT_DIR / 'checksums.json', 'w') as f:
        json.dump(checksums, f, indent=2)
    print("Checksums written to checksums.json", flush=True)

if __name__ == '__main__':
    t_start = time.time()
    store = load_data_and_generate_controls()
    preds = run_frozen_checkpoint_inference(store)
    contrasts = run_synchronized_cluster_bootstrap(preds, n_boot=2000)
    print(f"\nPhase 6 script complete in {time.time() - t_start:.1f}s.")
