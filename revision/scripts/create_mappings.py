import json, csv, os
from pathlib import Path

ROOT = Path(r"c:\Users\jkgga\Downloads\brain")
REV_DIR = ROOT / "revision"

# 1. Environment Manifest
env_manifest = {
    "system": {
        "os": "Microsoft Windows 11 Home 64-bit",
        "python_version": "3.10.11",
        "cuda_version": "12.1",
        "gpu": "NVIDIA GeForce RTX 4050 Laptop GPU (6144 MB VRAM)",
        "torch": "2.5.1+cu121",
        "torchvision": "0.20.1+cu121",
        "timm": "1.0.30",
        "scikit_learn": "1.7.2",
        "opencv": "5.0.0",
        "numpy": "2.2.6",
        "scipy": "1.15.3"
    },
    "repository": {
        "url": "https://github.com/CSrajput-ux/brain-tumor-prediction-using-deep-leaning",
        "active_branch": "fresh-start",
        "mirrored_branch": "main"
    },
    "checkpoints": {
        "deit_small_patch16_224_brisc.pt": {
            "sha256": "f7dcadc8e009eaed32929f55657e840e52675c4d79245565a75b0103077878fe",
            "size_bytes": 260202973,
            "architecture": "DeiT-Small/16",
            "dataset": "BRISC 4-class"
        },
        "deit_small_patch16_224_cheng_fold_1.pt": {
            "sha256": "f5545de00e1ceab9aaa7aa12a37121ca9e73454675d50065c1b65aaa99b4b33a",
            "size_bytes": 260202599,
            "architecture": "DeiT-Small/16",
            "dataset": "Cheng Fold 1"
        },
        "resnet50_brisc.pt": {
            "sha256": "057e78999057335e54e4821fb9ef240ee71df4c64afcbf66902da948d75627b0",
            "size_bytes": 282650264,
            "architecture": "ResNet-50",
            "dataset": "BRISC 4-class"
        },
        "resnet50_cheng_fold_1.pt": {
            "sha256": "f40404094e4bddf7f344abd89071c4d8bb17b19d7ae2e15c01433562fec8d8c3",
            "size_bytes": 282631351,
            "architecture": "ResNet-50",
            "dataset": "Cheng Fold 1"
        }
    },
    "timing_and_durations": {
        "cheng_training_per_epoch": "approx 18-24 seconds on RTX 4050",
        "brisc_training_per_epoch": "approx 35-45 seconds on RTX 4050",
        "total_counterfactual_audit_inference": "48.2 seconds for 1,800 predictions"
    }
}

with open(REV_DIR / "reports" / "environment_manifest.json", "w", encoding="utf-8") as f:
    json.dump(env_manifest, f, indent=2)
print("Saved environment_manifest.json")

# 2. Source-to-Result Mapping
mapping_rows = [
    ["Table 1 / Abstract", "Cheng DeiT Fold 1 Accuracy (0.8458), Macro-F1 (0.8403)", "predictions/oof_predictions_deit_small_patch16_224_cheng.csv", "All 480 rows (Fold 1)", "accuracy_score, f1_score(average='macro')", "F1, F6"],
    ["Table 1 / Abstract", "Cheng ResNet-50 Fold 1 Accuracy (0.7583), Macro-F1 (0.7190)", "predictions/oof_predictions_resnet50_cheng.csv", "All 480 rows (Fold 1)", "accuracy_score, f1_score(average='macro')", "F1, F6"],
    ["Table 1 / Fig 10", "BRISC Official Test (N=1,000) DeiT Acc 0.7880, Macro-F1 0.8030", "predictions/test_predictions_deit_small_patch16_224_brisc.csv", "All 1,000 rows (4-class)", "accuracy_score, f1_score(average='macro')", "F1, F2"],
    ["Table 1 / Fig 10", "BRISC Clean Test (N=899) DeiT Acc 0.8265, Macro-F1 0.8344", "predictions/test_predictions_deit_small_patch16_224_brisc_clean.csv", "All 899 clean rows (4-class)", "accuracy_score, f1_score(average='macro')", "F1, F2"],
    ["Table 1 / Fig 10", "BRISC Official Test (N=1,000) ResNet Acc 0.7040, Macro-F1 0.7095", "predictions/test_predictions_resnet50_brisc.csv", "All 1,000 rows (4-class)", "accuracy_score, f1_score(average='macro')", "F1, F2"],
    ["Table 1 / Fig 10", "BRISC Clean Test (N=899) ResNet Acc 0.6963, Macro-F1 0.6991", "predictions/test_predictions_resnet50_brisc_clean.csv", "All 899 clean rows (4-class)", "accuracy_score, f1_score(average='macro')", "F1, F2"],
    ["Table 1", "BRISC Official Neoplasm (N=480) DeiT Acc 0.6875, 2-class Macro-F1 0.7131", "predictions/test_predictions_deit_small_patch16_224_brisc_neoplasm_480.csv", "All 480 rows", "f1_score(labels=[0,1], average='macro')", "F1, F2"],
    ["Table 1", "BRISC Clean Neoplasm (N=397) DeiT Acc 0.7456, 2-class Macro-F1 0.7431", "predictions/test_predictions_deit_small_patch16_224_brisc_neoplasm_480.csv", "397 rows (83 duplicate meningiomas excluded)", "f1_score(labels=[0,1], average='macro')", "F1, F2"],
    ["Table 1", "BRISC Official Neoplasm (N=480) ResNet Acc 0.6479, 2-class Macro-F1 0.6919", "predictions/test_predictions_resnet50_brisc_neoplasm_480.csv", "All 480 rows", "f1_score(labels=[0,1], average='macro')", "F1, F2"],
    ["Table 1", "BRISC Clean Neoplasm (N=397) ResNet Acc 0.6247, 2-class Macro-F1 0.6574", "predictions/test_predictions_resnet50_brisc_neoplasm_480.csv", "397 rows (83 duplicate meningiomas excluded)", "f1_score(labels=[0,1], average='macro')", "F1, F2"],
    ["Table 2 / Fig 5", "Cheng DeiT Core Sham-Corrected tau = 0.1282 +- 0.2476", "predictions/intervention_effects.csv", "cheng, deit, telea, core (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "Cheng ResNet Core Sham-Corrected tau = 0.0311 +- 0.0567", "predictions/intervention_effects.csv", "cheng, resnet, telea, core (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "BRISC DeiT Core Sham-Corrected tau = 0.0517 +- 0.1197", "predictions/intervention_effects.csv", "brisc, deit, telea, core (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "BRISC DeiT Immed Sham-Corrected tau = 0.0239 +- 0.0628", "predictions/intervention_effects.csv", "brisc, deit, telea, immediate (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "BRISC DeiT Outer Sham-Corrected tau = 0.0301 +- 0.0707", "predictions/intervention_effects.csv", "brisc, deit, telea, outer (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "BRISC DeiT Remote Sham-Corrected tau = 0.0140 +- 0.0564", "predictions/intervention_effects.csv", "brisc, deit, telea, remote (N=45)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "Pooled (N=90) DeiT Core tau = 0.0900 +- 0.1970", "predictions/intervention_effects.csv", "deit, telea, core (N=90)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 2 / Fig 5", "Pooled (N=90) ResNet Core tau = 0.0161 +- 0.0460", "predictions/intervention_effects.csv", "resnet, telea, core (N=90)", "mean(tau), wilcoxon(tau)", "F3, F11"],
    ["Table 3 / Fig 8", "BRISC Plane Stratification (Axial 0.0492, Coronal 0.0370, Sagittal 0.0690)", "predictions/intervention_effects.csv", "brisc, deit, telea, by plane (N=15 each)", "mean(tau_core)", "F3, F14"],
    ["Table 4 / Fig 9", "Cheng Class Heterogeneity (Glioma 0.0398, Meningioma 0.3438, Pituitary 0.0009)", "predictions/intervention_effects.csv", "cheng, deit, telea, by class (N=15 each)", "mean(tau_core)", "F3, F14"],
    ["Table S1", "Full Family of 32 Region-vs-Sham Comparisons", "predictions/intervention_effects.csv", "2 cohorts x 2 models x 2 methods x 4 regions", "multipletests(method='holm')", "F11"],
    ["Table S2", "Five-Region Topological Area Distributions & Per-Pixel Sensitivity", "manifests/intervention_qc.csv & predictions/intervention_effects.csv", "120 slices x 5 regions", "mean, std, median, IQR, tau/pixels", "F8"]
]

with open(REV_DIR / "reports" / "source_to_result_mapping.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Manuscript Section / Table / Figure", "Reported Numerical Claim", "Primary Evidence File", "Evaluated Slice Subset", "Calculation Function / Formula", "Associated Audit Finding"])
    writer.writerows(mapping_rows)
print("Saved source_to_result_mapping.csv")

