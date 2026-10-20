"""
Dual-Resolution Diagnostics Generator:
Computes edge, junction, interior, unchanged-area, and Fourier spectral diagnostics
at BOTH source resolution (512x512) and production model input resolution (224x224)
across all 6 standardized conditions:
1. C0_orig
2. C1_historical_dc_offset
3. C1_true_seam_w2
4. C1_true_seam_w3
5. C2_seam_suppressed
6. C3_c5lp_scramble
"""

import os
import sys
import time
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / 'remaining_work_audit'
PUB_TAB_DIR = ROOT / 'publication' / 'manuscript_v1' / 'tables'
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
PUB_TAB_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
PATCH_SIZE = 16

def compute_sobel_mag(arr: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(arr.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return np.sqrt(gx**2 + gy**2)

_HF_MASKS = {}

def get_hf_mask(h: int, w: int, cutoff_ratio: float = 0.25) -> np.ndarray:
    key = (h, w, cutoff_ratio)
    if key not in _HF_MASKS:
        cy, cx = h // 2, w // 2
        y, x = np.ogrid[:h, :w]
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        radius_cutoff = cutoff_ratio * min(h, w)
        _HF_MASKS[key] = (r > radius_cutoff)
    return _HF_MASKS[key]

def compute_hf_fourier(arr: np.ndarray, cutoff_ratio: float = 0.25) -> float:
    h, w = arr.shape
    hf_mask = get_hf_mask(h, w, cutoff_ratio)
    f = np.fft.fft2(arr.astype(np.float32))
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    return float(np.mean(mag[hf_mask]))

def main():
    print("=" * 75, flush=True)
    print("DUAL-RESOLUTION DIAGNOSTICS: Source (512x512) & Model Input (224x224)", flush=True)
    print("Computing metrics across all 6 standardized conditions for 3,064 slices...", flush=True)
    print("=" * 75, flush=True)
    
    t0 = time.time()
    meta_df = pd.read_csv(ROOT / 'prepared_full_run' / 'metadata.csv')
    num_samples = len(meta_df)
    
    elem31 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    
    # Store aggregated accumulators for the summary table
    cond_names = [
        'C0_orig',
        'C1_historical_dc_offset',
        'C1_true_seam_w2',
        'C1_true_seam_w3',
        'C2_seam_suppressed',
        'C3_c5lp_scramble'
    ]
    
    stats_source = {c: {'seam': [], 'junction': [], 'interior': [], 'hf': [], 'unchanged_frac': []} for c in cond_names}
    stats_input224 = {c: {'seam': [], 'junction': [], 'interior': [], 'hf': [], 'unchanged_frac': []} for c in cond_names}
    
    for idx, row in meta_df.iterrows():
        sid = row['sample_id']
        img_path = ROOT / 'prepared_full_run' / row['image_output_path']
        mask_path = ROOT / 'prepared_full_run' / row['mask_output_path']
        
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        total_pixels = h * w
        
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
        
        coord_to_perm = {pure_distant_coords[i]: distant_patches[perm[i]] for i in range(len(pure_distant_coords))}
        coord_to_orig = {pure_distant_coords[i]: distant_patches[i] for i in range(len(pure_distant_coords))}
        
        # 1. C0_orig
        i_c0 = img.copy()
        
        # 2. C3_c5lp_scramble
        i_c3 = img.copy()
        for i, (gy, gx) in enumerate(pure_distant_coords):
            i_c3[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE] = distant_patches[perm[i]]
            
        # 3. C1_historical_dc_offset (shifts entire 16x16 tile DC mean)
        i_c1_hist = img.copy().astype(np.float32)
        for i, (gy, gx) in enumerate(pure_distant_coords):
            y1, y2 = gy * PATCH_SIZE, (gy + 1) * PATCH_SIZE
            x1, x2 = gx * PATCH_SIZE, (gx + 1) * PATCH_SIZE
            mean_perm = float(np.mean(distant_patches[perm[i]]))
            mean_orig = float(np.mean(distant_patches[i]))
            delta_mu = mean_perm - mean_orig
            i_c1_hist[y1:y2, x1:x2] += delta_mu
        i_c1_hist = np.clip(i_c1_hist, 0, 255).astype(np.uint8)
        i_c1_hist[m_dil15 > 0] = img[m_dil15 > 0]
        
        # 4 & 5. C1_true_seam_w2 & w3 (strictly boundary pixels only)
        i_ts_w2 = img.copy().astype(np.float32)
        seam_mask_w2 = np.zeros_like(img, dtype=bool)
        i_ts_w3 = img.copy().astype(np.float32)
        seam_mask_w3 = np.zeros_like(img, dtype=bool)
        
        seam_junctions = np.zeros_like(img, dtype=bool)
        
        for gy, gx in pure_distant_coords:
            y1, y2 = gy * PATCH_SIZE, (gy + 1) * PATCH_SIZE
            x1, x2 = gx * PATCH_SIZE, (gx + 1) * PATCH_SIZE
            
            has_right = (gy, gx + 1) in distant_set
            has_bottom = (gy + 1, gx) in distant_set
            
            if has_right:
                ol = coord_to_orig[(gy, gx)][:, -1].astype(np.float32)
                oright = coord_to_orig[(gy, gx + 1)][:, 0].astype(np.float32)
                pl = coord_to_perm[(gy, gx)][:, -1].astype(np.float32)
                pr = coord_to_perm[(gy, gx + 1)][:, 0].astype(np.float32)
                step_w2 = (pr - pl) - (oright - ol)
                step_w3 = 1.8 * step_w2
                
                i_ts_w2[y1:y2, x2-1] -= 0.5 * step_w2
                i_ts_w2[y1:y2, x2] += 0.5 * step_w2
                seam_mask_w2[y1:y2, x2-1:x2+1] = True
                
                i_ts_w3[y1:y2, x2-1] -= 0.5 * step_w3
                i_ts_w3[y1:y2, x2] += 0.5 * step_w3
                seam_mask_w3[y1:y2, x2-1:x2+2] = True
                
            if has_bottom:
                ot = coord_to_orig[(gy, gx)][-1, :].astype(np.float32)
                obottom = coord_to_orig[(gy + 1, gx)][0, :].astype(np.float32)
                pt = coord_to_perm[(gy, gx)][-1, :].astype(np.float32)
                pbottom = coord_to_perm[(gy + 1, gx)][0, :].astype(np.float32)
                step_w2 = (pbottom - pt) - (obottom - ot)
                step_w3 = 1.8 * step_w2
                
                i_ts_w2[y2-1, x1:x2] -= 0.5 * step_w2
                i_ts_w2[y2, x1:x2] += 0.5 * step_w2
                seam_mask_w2[y2-1:y2+1, x1:x2] = True
                
                i_ts_w3[y2-1, x1:x2] -= 0.5 * step_w3
                i_ts_w3[y2, x1:x2] += 0.5 * step_w3
                seam_mask_w3[y2-1:y2+2, x1:x2] = True
                
            if has_right and has_bottom:
                seam_junctions[y2-1:y2+1, x2-1:x2+1] = True

        i_ts_w2 = np.clip(i_ts_w2, 0, 255).astype(np.uint8)
        i_ts_w3 = np.clip(i_ts_w3, 0, 255).astype(np.uint8)
        i_ts_w2[m_dil15 > 0] = img[m_dil15 > 0]
        i_ts_w3[m_dil15 > 0] = img[m_dil15 > 0]
        
        # 6. C2_seam_suppressed (Gaussian cross-fade on seams)
        i_c2 = i_c3.copy().astype(np.float32)
        # Apply Gaussian blending along seam band
        blurred_c3 = cv2.GaussianBlur(i_c3, (5, 5), sigmaX=1.5, sigmaY=1.5).astype(np.float32)
        # Blend strictly on seam band
        i_c2[seam_mask_w3] = 0.5 * i_c2[seam_mask_w3] + 0.5 * blurred_c3[seam_mask_w3]
        i_c2 = np.clip(i_c2, 0, 255).astype(np.uint8)
        i_c2[m_dil15 > 0] = img[m_dil15 > 0]

        # Interior mask (distant tiles away from seams)
        distant_mask = np.zeros_like(img, dtype=bool)
        for gy, gx in pure_distant_coords:
            distant_mask[gy*PATCH_SIZE:(gy+1)*PATCH_SIZE, gx*PATCH_SIZE:(gx+1)*PATCH_SIZE] = True
        interior_mask = distant_mask & (~seam_mask_w3) & (m_dil15 == 0)

        # Map conditions to images
        images = {
            'C0_orig': i_c0,
            'C1_historical_dc_offset': i_c1_hist,
            'C1_true_seam_w2': i_ts_w2,
            'C1_true_seam_w3': i_ts_w3,
            'C2_seam_suppressed': i_c2,
            'C3_c5lp_scramble': i_c3
        }

        # --- Source Resolution Diagnostics (512x512) ---
        for cname, cimg in images.items():
            sob = compute_sobel_mag(cimg)
            seam_e = float(np.mean(sob[seam_mask_w2])) if np.sum(seam_mask_w2) > 0 else 0.0
            junc_e = float(np.mean(sob[seam_junctions])) if np.sum(seam_junctions) > 0 else 0.0
            int_e = float(np.mean(sob[interior_mask])) if np.sum(interior_mask) > 0 else 0.0
            hf_e = compute_hf_fourier(cimg)
            unchanged = float(np.sum(cimg == img)) / total_pixels
            
            stats_source[cname]['seam'].append(seam_e)
            stats_source[cname]['junction'].append(junc_e)
            stats_source[cname]['interior'].append(int_e)
            stats_source[cname]['hf'].append(hf_e)
            stats_source[cname]['unchanged_frac'].append(unchanged)

        # --- Model Input Resolution Diagnostics (224x224) ---
        seam_mask_224 = cv2.resize(seam_mask_w2.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        junc_mask_224 = cv2.resize(seam_junctions.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        int_mask_224 = cv2.resize(interior_mask.astype(np.uint8), (224, 224), interpolation=cv2.INTER_NEAREST) > 0
        
        orig_224 = cv2.resize(img, (224, 224), interpolation=cv2.INTER_LINEAR)
        total_224 = 224 * 224

        for cname, cimg in images.items():
            cimg_224 = cv2.resize(cimg, (224, 224), interpolation=cv2.INTER_LINEAR)
            sob_224 = compute_sobel_mag(cimg_224)
            
            seam_e_224 = float(np.mean(sob_224[seam_mask_224])) if np.sum(seam_mask_224) > 0 else 0.0
            junc_e_224 = float(np.mean(sob_224[junc_mask_224])) if np.sum(junc_mask_224) > 0 else 0.0
            int_e_224 = float(np.mean(sob_224[int_mask_224])) if np.sum(int_mask_224) > 0 else 0.0
            hf_e_224 = compute_hf_fourier(cimg_224)
            unchanged_224 = float(np.sum(np.abs(cimg_224.astype(int) - orig_224.astype(int)) == 0)) / total_224
            
            stats_input224[cname]['seam'].append(seam_e_224)
            stats_input224[cname]['junction'].append(junc_e_224)
            stats_input224[cname]['interior'].append(int_e_224)
            stats_input224[cname]['hf'].append(hf_e_224)
            stats_input224[cname]['unchanged_frac'].append(unchanged_224)

        if (idx + 1) % 250 == 0 or (idx + 1) == num_samples:
            el = time.time() - t0
            rate = (idx + 1) / el if el > 0 else 0
            print(f"Processed {idx + 1} / {num_samples} slices in {el:.1f}s ({rate:.1f} slices/s)...", flush=True)

    # Compile Dual-Resolution Summary Table
    summary_rows = []
    for cname in cond_names:
        summary_rows.append({
            'condition': cname,
            'source_seam_sobel_mean': float(np.mean(stats_source[cname]['seam'])),
            'source_junction_sobel_mean': float(np.mean(stats_source[cname]['junction'])),
            'source_interior_sobel_mean': float(np.mean(stats_source[cname]['interior'])),
            'source_hf_fourier_mean': float(np.mean(stats_source[cname]['hf'])),
            'source_unchanged_area_fraction_mean': float(np.mean(stats_source[cname]['unchanged_frac'])),
            'input224_seam_sobel_mean': float(np.mean(stats_input224[cname]['seam'])),
            'input224_junction_sobel_mean': float(np.mean(stats_input224[cname]['junction'])),
            'input224_interior_sobel_mean': float(np.mean(stats_input224[cname]['interior'])),
            'input224_hf_fourier_mean': float(np.mean(stats_input224[cname]['hf'])),
            'input224_unchanged_fraction_mean': float(np.mean(stats_input224[cname]['unchanged_frac']))
        })

    sum_df = pd.DataFrame(summary_rows)
    
    out_audit = AUDIT_DIR / 'true_seam_and_intervention_diagnostics_dual_resolution.csv'
    sum_df.to_csv(out_audit, index=False)
    print(f"\nDual-resolution diagnostics saved to {out_audit}", flush=True)
    
    # Also update table7_image_diagnostics.csv in publication package
    pub_table7_path = PUB_TAB_DIR / 'table7_image_diagnostics.csv'
    sum_df.to_csv(pub_table7_path, index=False)
    print(f"Publication Table 7 updated at {pub_table7_path}", flush=True)
    
    # Print formatted table to terminal
    print("\nSummary Table:")
    print(sum_df[['condition', 'source_seam_sobel_mean', 'source_unchanged_area_fraction_mean', 'input224_seam_sobel_mean', 'input224_hf_fourier_mean']].to_string(index=False))

if __name__ == '__main__':
    main()
