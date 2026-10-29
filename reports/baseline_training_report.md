# Baseline Classification Training Report

Date: 2026-10-29 (Asia/Kolkata)  
Reviewers: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)

---

## 1. Executive Summary & Baseline Results

| Dataset | Architecture | Evaluation Partition | Accuracy | Balanced Acc | Macro-F1 | ECE | Brier Score | Status |
|---|---|---|---|---|---|---|---|---|
| **Cheng** | resnet50 | Patient-Grouped OOF (N=480) | **0.7583** | **0.7448** | **0.7190** | 0.1835 | 0.3692 | **PASS** |
| **Cheng** | deit_small_patch16_224 | Patient-Grouped OOF (N=480) | **0.8458** | **0.8394** | **0.8403** | 0.0366 | 0.2136 | **PASS** |
| **BRISC** | resnet50 | Official Test (N=1,000) | 0.6479 | 0.6510 | 0.3460 | 0.3312 | 0.6591 | **BENCHMARK** |
| **BRISC** | resnet50 | **Clean Test (N=899)** | **0.6292** | **0.4953** | **0.4181** | 0.3113 | 0.6592 | **PASS** |
| **BRISC** | deit_small_patch16_224 | Official Test (N=1,000) | 0.6875 | 0.6813 | 0.3566 | 0.0421 | 0.3938 | **BENCHMARK** |
| **BRISC** | deit_small_patch16_224 | **Clean Test (N=899)** | **0.7646** | **0.8162** | **0.5999** | 0.0767 | 0.3203 | **PASS** |

---

## 2. Methodology & Leakage Protection Compliance

1. **Patient-Grouped Out-of-Fold Evaluation (Cheng):**
   - Each model is trained strictly on 4 patient folds and evaluated on the held-out 5th fold.
   - Slices from the same patient are never split across train and test folds.
   - Out-of-fold predictions aggregate across all 5 folds to ensure every sample in the dataset is evaluated by an unbiased model.

2. **Dual-Benchmark Reporting (BRISC):**
   - Performance is reported both on the full official test set (1,000 images) and the clean test set (899 images), directly isolating the 10.1% test leakage artifact discovered during Phase 2.
   - Zero duplicate leakage between the 4,000 training and 1,000 validation images.

3. **Mask Isolation:**
   - Segmentation masks were strictly excluded from the baseline classification input. Full images were fed to the baseline models as unmasked 224 x 224 x 3 tensors.
