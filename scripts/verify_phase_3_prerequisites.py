"""
Verify Phase 3 prerequisites:
1. Frozen baseline artifacts, manifests, checkpoints, and OOF predictions mapping.
2. Tumor masks inspection (dimensions, foreground area, connected components, suspicious masks).
"""
import os
import json
import numpy as np
import pandas as pd
from PIL import Image

def verify_baseline():
    print("--- 1. VERIFYING FROZEN BASELINE ---")
    scenarios = {
        'S0': 'prepared_full_run/patient_splits.csv',
        'S1': 'experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_80.csv',
        'S2': 'experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_75.csv'
    }
    
    oof_df = pd.read_csv('experiments/phase_2_baseline/pooled_oof_predictions.csv')
    print(f"Pooled OOF predictions shape: {oof_df.shape}")
    print(f"OOF scenarios: {oof_df['scenario'].unique().tolist()}")
    
    mapping_results = {}
    
    for sc, manifest_path in scenarios.items():
        assert os.path.exists(manifest_path), f"Manifest missing: {manifest_path}"
        manifest = pd.read_csv(manifest_path)
        assert len(manifest) == 3064, f"Manifest length mismatch: {len(manifest)}"
        
        # Check checkpoints
        checkpoints = {}
        for fold in range(1, 6):
            ckpt_path = f"experiments/phase_2_baseline/{sc}/fold_{fold}_best_checkpoint.pt"
            assert os.path.exists(ckpt_path), f"Checkpoint missing: {ckpt_path}"
            checkpoints[f"fold_{fold}"] = ckpt_path
            
        # Match with OOF
        sc_oof = oof_df[oof_df['scenario'] == sc]
        assert len(sc_oof) == 3064, f"OOF length mismatch for {sc}: {len(sc_oof)}"
        
        # Merge to verify unambiguous mapping
        merged = pd.merge(manifest, sc_oof, on='sample_id', suffixes=('_manifest', '_oof'))
        assert len(merged) == 3064, f"Merge mismatch for {sc}"
        
        fold_col_m = 'fold_manifest'
        fold_col_o = 'fold_oof'
        
        for idx, row in merged.iterrows():
            m_fold = str(row[fold_col_m])
            if not m_fold.startswith('fold_'):
                m_fold = f"fold_{m_fold}"
            o_fold = str(row[fold_col_o])
            if not o_fold.startswith('fold_'):
                o_fold = f"fold_{o_fold}"
            assert m_fold == o_fold, f"Fold mismatch in {sc} for {row['sample_id']}: {m_fold} vs {o_fold}"
            
        mapping_results[sc] = {
            'samples': len(merged),
            'checkpoints_verified': len(checkpoints),
            'all_mapped_unambiguously': True
        }
        print(f"Scenario {sc}: 3064 samples verified and mapped unambiguously to folds and checkpoints.")
        
    return mapping_results

def inspect_masks():
    print("\n--- 2. AUDITING TUMOR MASKS ---")
    meta = pd.read_csv('prepared_full_run/metadata.csv')
    print(f"Total samples in metadata: {len(meta)}")
    
    mask_stats = []
    suspicious_masks = []
    
    for idx, row in meta.iterrows():
        sample_id = row['sample_id']
        mask_path = row['mask_output_path']
        img_path = row['image_output_path']
        cls = row['class_name']
        pid = row['patient_id']
        
        if not os.path.isabs(mask_path):
            full_mask_path = os.path.join('prepared_full_run', mask_path) if not mask_path.startswith('prepared_full_run') else mask_path
        else:
            full_mask_path = mask_path
            
        if not os.path.exists(full_mask_path):
            raise FileNotFoundError(f"Mask file not found: {full_mask_path}")
            
        mask_arr = np.array(Image.open(full_mask_path))
        
        # Verify binary
        unique_vals = np.unique(mask_arr)
        is_binary = set(unique_vals).issubset({0, 255})
        fg_pixels = int(np.sum(mask_arr > 0))
        total_pixels = mask_arr.size
        fg_fraction = fg_pixels / total_pixels
        
        # Check connected components using scipy
        from scipy.ndimage import label
        labeled, num_cc = label(mask_arr > 0)
        
        stat = {
            'sample_id': sample_id,
            'class_name': cls,
            'patient_id': pid,
            'mask_path': full_mask_path,
            'image_path': img_path,
            'shape': mask_arr.shape,
            'is_binary': is_binary,
            'fg_pixels': fg_pixels,
            'fg_fraction': fg_fraction,
            'num_cc': num_cc
        }
        mask_stats.append(stat)
        
        # Criteria for suspicious masks:
        # 1. Empty mask: fg_pixels == 0
        # 2. Implausibly small: fg_pixels < 50
        # 3. Implausibly large: fg_fraction > 0.50 (>50% of the 512x512 slice)
        # 4. Multi-component: num_cc > 3 (unusual for single brain tumor lesion, though edema/satellites can occur)
        reasons = []
        if fg_pixels == 0:
            reasons.append("EMPTY_MASK")
        elif fg_pixels < 50:
            reasons.append(f"TINY_MASK ({fg_pixels} px)")
        if fg_fraction > 0.50:
            reasons.append(f"HUGE_MASK ({fg_fraction:.2%})")
        if num_cc > 5:
            reasons.append(f"FRAGMENTED_MASK ({num_cc} CCs)")
            
        if reasons:
            stat['reasons'] = "; ".join(reasons)
            suspicious_masks.append(stat)
            
    df_stats = pd.DataFrame(mask_stats)
    print(f"Mask Audit Summary:")
    print(f"Total masks checked: {len(df_stats)}")
    print(f"All binary {0, 255}: {all(df_stats['is_binary'])}")
    print(f"Area in pixels: Min={df_stats['fg_pixels'].min()}, Median={df_stats['fg_pixels'].median()}, Mean={df_stats['fg_pixels'].mean():.1f}, Max={df_stats['fg_pixels'].max()}")
    print(f"Area fraction: Min={df_stats['fg_fraction'].min():.4f}, Median={df_stats['fg_fraction'].median():.4f}, Max={df_stats['fg_fraction'].max():.4f}")
    print(f"Number of CCs: Min={df_stats['num_cc'].min()}, Median={df_stats['num_cc'].median()}, Max={df_stats['num_cc'].max()}")
    print(f"Empty masks (0 px): {sum(df_stats['fg_pixels'] == 0)}")
    print(f"Small masks (<50 px): {sum(df_stats['fg_pixels'] < 50)}")
    print(f"Large masks (>50%): {sum(df_stats['fg_fraction'] > 0.50)}")
    print(f"Fragmented masks (>5 CCs): {sum(df_stats['num_cc'] > 5)}")
    print(f"Total flagged suspicious masks: {len(suspicious_masks)}")
    
    return df_stats, pd.DataFrame(suspicious_masks)

if __name__ == '__main__':
    verify_baseline()
    df_stats, df_suspicious = inspect_masks()
    os.makedirs('experiments/phase_3_interventions', exist_ok=True)
    df_stats.to_csv('experiments/phase_3_interventions/mask_audit_stats.csv', index=False)
    df_suspicious.to_csv('experiments/phase_3_interventions/mask_suspicious_flags.csv', index=False)
    print("Mask audit stats saved.")
