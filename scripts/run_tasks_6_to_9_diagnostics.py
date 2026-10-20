"""
Tasks 6-9: Comprehensive Image Diagnostics & Resolution Stratification
Recomputes diagnostics at both source resolution and actual 224x224 model input:
- Task 6: 224x224 production model input diagnostics (seam, interior, high-freq Fourier)
- Task 7: Unchanged-area fraction, modified-area fraction, junction seam energy, mask overlaps
- Task 8: High-frequency Fourier spectral diagnostics with explicit cutoff definitions
- Task 9: Stratified performance & diagnostics for 512x512 (3,049 slices) vs 256x256 (15 slices)
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
import torchvision.transforms as T

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / 'remaining_work_audit'
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
PATCH_SIZE = 16

def compute_sobel_mag(arr: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return np.sqrt(gx**2 + gy**2)

def compute_hf_fourier(arr: np.ndarray, cutoff_ratio: float = 0.25) -> float:
    """Compute high-frequency Fourier energy (> cutoff_ratio * Nyquist)."""
    h, w = arr.shape
    cy, cx = h // 2, w // 2
    f = np.fft.fft2(arr.astype(np.float32))
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    
    y, x = np.ogrid[:h, :w]
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    radius_cutoff = cutoff_ratio * min(h, w)
    hf_mask = r > radius_cutoff
    return float(np.mean(mag[hf_mask]))

def main():
    print("=" * 75, flush=True)
    print("TASKS 6-9: Comprehensive Image Diagnostics & Resolution Stratification", flush=True)
    t0 = time.time()
    
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    num_samples = len(meta_df)
    print(f"Loaded metadata for {num_samples} samples.", flush=True)
    
    elem31 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    rect3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    # Normalization transform matching train_baseline.py
    norm_transform = T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    to_tensor = T.ToTensor()
    
    per_image_task7 = []
    per_image_task8 = []
    task6_records = []
    
    for idx, row in meta_df.iterrows():
        sid = row['sample_id']
        pid = row['patient_id']
        cls_name = row['class_name']
        src_shape = row['image_shape']
        
        img_path = ROOT / 'prepared_full_run' / row['image_output_path']
        mask_path = ROOT / 'prepared_full_run' / row['mask_output_path']
        
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        
        h, w = img.shape
        m_dil15 = cv2.dilate(mask, elem31)
        
        gy_max, gx_max = h // PATCH_SIZE, w // PATCH_SIZE
        pure_distant_coords = []
        distant_set = set()
        for gy in range(gy_max):
            for gx in range(gx_max):
                y1, y2 = gy * PATCH_SIZE, (gy + 1) * PATCH_SIZE
                x1, x2 = gx * PATCH_SIZE, (gx + 1) * PATCH_SIZE
                if np.sum(m_dil15[y1:y2, x1:x2]) == 0:
                    pure_distant_coords.append((gy, gx))
                    distant_set.add((gy, gx))
        
        distant_patches = [img[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE] for gy, gx in pure_distant_coords]
        slice_seed = int(hashlib.sha256(f"{sid}_{SEED}".encode()).hexdigest()[:8], 16) % 2147483647
        rng = np.random.RandomState(slice_seed)
        perm = rng.permutation(len(pure_distant_coords))
        
        # Build C0
        i_c0 = img.copy()
        
        # Build C3
        i_c3 = img.copy()
        for i, (gy, gx) in enumerate(pure_distant_coords):
            i_c3[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE] = distant_patches[perm[i]]
            
        # Build Seam Grid (1px and 3px)
        seam_1px = np.zeros_like(img, dtype=np.uint8)
        seam_junctions = np.zeros_like(img, dtype=np.uint8)
        
        for gy, gx in pure_distant_coords:
            y1, y2 = gy * PATCH_SIZE, (gy + 1) * PATCH_SIZE
            x1, x2 = gx * PATCH_SIZE, (gx + 1) * PATCH_SIZE
            has_right = (gy, gx + 1) in distant_set
            has_bottom = (gy + 1, gx) in distant_set
            
            if has_right:
                seam_1px[y1:y2, x2-1:x2] = 1
            if has_bottom:
                seam_1px[y2-1:y2, x1:x2] = 1
            if has_right and has_bottom:
                seam_junctions[y2-1:y2, x2-1:x2] = 1
                
        seam_1px[m_dil15 > 0] = 0
        seam_junctions[m_dil15 > 0] = 0
        
        seam_eval_mask = (cv2.dilate(seam_1px, rect3) > 0)
        seam_eval_mask[m_dil15 > 0] = False
        junction_eval_mask = (cv2.dilate(seam_junctions, rect3) > 0)
        junction_eval_mask[m_dil15 > 0] = False
        
        distant_interior_mask = np.zeros_like(img, dtype=bool)
        for gy, gx in pure_distant_coords:
            y1, y2 = gy * PATCH_SIZE, (gy + 1) * PATCH_SIZE
            x1, x2 = gx * PATCH_SIZE, (gx + 1) * PATCH_SIZE
            distant_interior_mask[y1+2:y2-2, x1+2:x2-2] = True
        distant_interior_mask[m_dil15 > 0] = False
        
        # Build C1 (Historical DC-offset)
        i_c1 = img.copy().astype(np.float32)
        for i, (gy, gx) in enumerate(pure_distant_coords):
            orig_p = img[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE]
            perm_p = distant_patches[perm[i]]
            mean_diff = float(np.mean(perm_p)) - float(np.mean(orig_p))
            i_c1[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE] += mean_diff
        i_c1 = np.clip(i_c1, 0, 255).astype(np.uint8)
        i_c1[m_dil15 > 0] = img[m_dil15 > 0]
        
        # Build C2 (Seam-suppressed blur blend)
        blur_c3 = cv2.GaussianBlur(i_c3, (9, 9), sigmaX=2.5)
        dist_to_seam = cv2.distanceTransform(1 - seam_1px, cv2.DIST_L2, 3)
        blend_weight = np.clip(1.0 - dist_to_seam / 4.0, 0.0, 1.0)
        blend_weight[m_dil15 > 0] = 0.0
        i_c2 = (i_c3.astype(np.float32) * (1.0 - blend_weight) + blur_c3.astype(np.float32) * blend_weight).astype(np.uint8)
        i_c2[m_dil15 > 0] = img[m_dil15 > 0]
        
        cond_dict = {
            'C0_orig': i_c0,
            'C1_seam_only': i_c1,
            'C2_seam_suppressed': i_c2,
            'C3_c5lp_scramble': i_c3
        }
        
        total_px = h * w
        tumor_px = int(np.sum(mask > 0))
        margin_px = int(np.sum((m_dil15 > 0) & (mask == 0)))
        seam_band_px = int(np.sum(seam_eval_mask))
        junction_px = int(np.sum(junction_eval_mask))
        interior_px = int(np.sum(distant_interior_mask))
        
        # ----------------------------------------------------
        # Source-Resolution Calculations (Task 7 & 8)
        # ----------------------------------------------------
        for cname, arr in cond_dict.items():
            diff = np.abs(arr.astype(np.float32) - img.astype(np.float32))
            mod_px = int(np.sum(diff > 0))
            unchanged_px = total_px - mod_px
            unchanged_frac = unchanged_px / total_px
            mod_frac = mod_px / total_px
            
            tumor_overlap = int(np.sum((diff > 0) & (mask > 0)))
            margin_overlap = int(np.sum((diff > 0) & (m_dil15 > 0) & (mask == 0)))
            
            sob = compute_sobel_mag(arr)
            seam_energy = float(np.mean(sob[seam_eval_mask])) if seam_band_px > 0 else 0.0
            junction_energy = float(np.mean(sob[junction_eval_mask])) if junction_px > 0 else 0.0
            interior_energy = float(np.mean(sob[distant_interior_mask])) if interior_px > 0 else 0.0
            hf_energy = compute_hf_fourier(arr, cutoff_ratio=0.25)
            
            per_image_task7.append({
                'sample_id': sid,
                'patient_id': pid,
                'class_name': cls_name,
                'source_shape': src_shape,
                'condition': cname,
                'total_pixels': total_px,
                'modified_pixels': mod_px,
                'unchanged_pixels': unchanged_px,
                'unchanged_area_fraction': unchanged_frac,
                'modified_area_fraction': mod_frac,
                'tumor_overlap_pixels': tumor_overlap,
                'margin_overlap_pixels': margin_overlap,
                'seam_band_pixels': seam_band_px,
                'junction_pixels': junction_px,
                'interior_pixels': interior_px,
                'seam_sobel_energy': seam_energy,
                'junction_sobel_energy': junction_energy,
                'interior_sobel_energy': interior_energy,
                'high_freq_fourier_energy': hf_energy
            })
            
            per_image_task8.append({
                'sample_id': sid,
                'condition': cname,
                'source_resolution': f"{h}x{w}",
                'fourier_cutoff_ratio': 0.25,
                'high_freq_spectral_energy': hf_energy
            })

        # ----------------------------------------------------
        # 224x224 Production Input Calculations (Task 6)
        # ----------------------------------------------------
        # Resize all to 224x224 bilinear
        # Resize masks to 224x224 nearest
        mask_224 = cv2.resize(mask, (224, 224), interpolation=cv2.INTER_NEAREST)
        m_dil15_224 = cv2.resize(m_dil15, (224, 224), interpolation=cv2.INTER_NEAREST)
        seam_eval_224 = cv2.resize(seam_eval_mask.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        junction_224 = cv2.resize(junction_eval_mask.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        interior_224 = cv2.resize(distant_interior_mask.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        
        img_224_orig = np.array(Image.fromarray(img).resize((224, 224), Image.Resampling.BILINEAR))
        
        for cname, arr in cond_dict.items():
            # Production pipeline: uint8 -> PIL bilinear 224x224 RGB -> tensor -> Normalize
            pil_img = Image.fromarray(arr).convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
            arr_224_gray = np.array(pil_img.convert('L'))
            
            # Pixel space 224x224 diagnostics
            diff_224 = np.abs(arr_224_gray.astype(np.float32) - img_224_orig.astype(np.float32))
            mod_px_224 = int(np.sum(diff_224 > 0))
            unchanged_frac_224 = (224 * 224 - mod_px_224) / (224 * 224)
            
            sob_224 = compute_sobel_mag(arr_224_gray)
            seam_energy_224 = float(np.mean(sob_224[seam_eval_224])) if np.sum(seam_eval_224) > 0 else 0.0
            junction_energy_224 = float(np.mean(sob_224[junction_224])) if np.sum(junction_224) > 0 else 0.0
            interior_energy_224 = float(np.mean(sob_224[interior_224])) if np.sum(interior_224) > 0 else 0.0
            hf_energy_224 = compute_hf_fourier(arr_224_gray, cutoff_ratio=0.25)
            
            # Model normalized tensor diagnostics
            tensor_rgb = to_tensor(pil_img)  # (3, 224, 224) in [0, 1]
            norm_tensor = norm_transform(tensor_rgb)
            norm_std = float(torch.std(norm_tensor).item())
            norm_mean = float(torch.mean(norm_tensor).item())
            
            task6_records.append({
                'sample_id': sid,
                'condition': cname,
                'model_input_resolution': '224x224',
                'interpolation': 'BILINEAR',
                'unchanged_fraction_224': unchanged_frac_224,
                'seam_sobel_224': seam_energy_224,
                'junction_sobel_224': junction_energy_224,
                'interior_sobel_224': interior_energy_224,
                'high_freq_fourier_224': hf_energy_224,
                'tensor_mean': norm_mean,
                'tensor_std': norm_std
            })
            
        if (idx + 1) % 500 == 0 or (idx + 1) == num_samples:
            print(f"Processed {idx + 1} / {num_samples} slices...", flush=True)

    df_t7 = pd.DataFrame(per_image_task7)
    df_t8 = pd.DataFrame(per_image_task8)
    df_t6 = pd.DataFrame(task6_records)
    
    # Save per-image tables
    df_t7.to_csv(AUDIT_DIR / 'task7_per_image_diagnostics.csv', index=False)
    df_t8.to_csv(AUDIT_DIR / 'task8_fourier_high_frequency_diagnostics.csv', index=False)
    df_t6.to_csv(AUDIT_DIR / 'task6_per_image_224x224_diagnostics.csv', index=False)
    
    # Generate Table 7 (Condition Summary at 224x224 and Source Resolution)
    summary_rows = []
    for cname in ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']:
        sub_t7 = df_t7[df_t7['condition'] == cname]
        sub_t6 = df_t6[df_t6['condition'] == cname]
        
        summary_rows.append({
            'condition': cname,
            'source_seam_sobel_mean': float(sub_t7['seam_sobel_energy'].mean()),
            'source_seam_sobel_std': float(sub_t7['seam_sobel_energy'].std()),
            'source_junction_sobel_mean': float(sub_t7['junction_sobel_energy'].mean()),
            'source_interior_sobel_mean': float(sub_t7['interior_sobel_energy'].mean()),
            'source_hf_fourier_mean': float(sub_t7['high_freq_fourier_energy'].mean()),
            'source_unchanged_area_fraction_mean': float(sub_t7['unchanged_area_fraction'].mean()),
            'input224_seam_sobel_mean': float(sub_t6['seam_sobel_224'].mean()),
            'input224_junction_sobel_mean': float(sub_t6['junction_sobel_224'].mean()),
            'input224_interior_sobel_mean': float(sub_t6['interior_sobel_224'].mean()),
            'input224_hf_fourier_mean': float(sub_t6['high_freq_fourier_224'].mean()),
            'input224_unchanged_fraction_mean': float(sub_t6['unchanged_fraction_224'].mean())
        })
    
    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(AUDIT_DIR / 'table7_recomputed_224x224_diagnostics.csv', index=False)
    print(f"Table 7 recomputed diagnostics saved to {AUDIT_DIR / 'table7_recomputed_224x224_diagnostics.csv'}", flush=True)

    # ----------------------------------------------------
    # Task 9: Resolution-Stratified Metrics & Diagnostics
    # ----------------------------------------------------
    # Read matched predictions from Phase 9
    preds_df = pd.read_csv(ROOT / 'experiments' / 'phase_9_seam_spatial_disentanglement' / 'matched_predictions.csv')
    meta_sub = meta_df[['sample_id', 'image_shape']].copy()
    preds_merged = preds_df.merge(meta_sub, on='sample_id', how='left')
    
    res_strat_records = []
    
    from sklearn.metrics import f1_score, accuracy_score
    
    for scen in ['S0', 'S1', 'S2']:
        for cond in ['C0_orig', 'C1_seam_only', 'C2_seam_suppressed', 'C3_c5lp_scramble']:
            scen_cond = preds_merged[(preds_merged['scenario'] == scen) & (preds_merged['condition'] == cond)]
            
            for cohort_name, cohort_filter in [
                ('Pooled Cohort (All)', scen_cond),
                ('512x512 Slices Only', scen_cond[scen_cond['image_shape'] == '[512, 512]']),
                ('256x256 Slices Only (Pt 108931)', scen_cond[scen_cond['image_shape'] == '[256, 256]'])
            ]:
                n_slices = len(cohort_filter)
                if n_slices == 0:
                    continue
                acc = accuracy_score(cohort_filter['true_label'], cohort_filter['pred_label'])
                macro_f1 = f1_score(cohort_filter['true_label'], cohort_filter['pred_label'], average='macro', zero_division=0)
                
                # Per class F1
                cls_f1s = f1_score(cohort_filter['true_label'], cohort_filter['pred_label'], average=None, zero_division=0)
                
                res_strat_records.append({
                    'scenario': scen,
                    'condition': cond,
                    'cohort': cohort_name,
                    'slice_count': n_slices,
                    'accuracy': float(acc),
                    'macro_f1': float(macro_f1),
                    'f1_meningioma': float(cls_f1s[0]) if len(cls_f1s) > 0 else 0.0,
                    'f1_glioma': float(cls_f1s[1]) if len(cls_f1s) > 1 else 0.0,
                    'f1_pituitary': float(cls_f1s[2]) if len(cls_f1s) > 2 else 0.0
                })
                
    df_t9 = pd.DataFrame(res_strat_records)
    t9_path = AUDIT_DIR / 'task9_resolution_stratified_metrics.csv'
    df_t9.to_csv(t9_path, index=False)
    print(f"Task 9 resolution-stratified metrics saved to {t9_path}", flush=True)
    print(f"Tasks 6-9 completed successfully in {time.time() - t0:.2f}s", flush=True)

if __name__ == '__main__':
    main()
