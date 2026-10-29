# Baseline Classification Training Report

Date: 2026-10-29 (Updated 2026-10-30)  
Reviewers: Multidisciplinary Research Team (Computer-Vision Engineer, Biostatistician)

---

## 1. Executive Summary & Baseline Results

### Primary Benchmark Partitions

| Dataset | Architecture | Evaluation Partition | Accuracy | Balanced Acc | Macro-F1 | ECE (10-bin) | Brier Score | Status |
|---|---|---|---|---|---|---|---|---|
| **Cheng** | ResNet-50 | Patient-Isolated Held-Out Fold 1 ($N=480$) | 0.7583 | 0.7448 | 0.7190 | 0.1835 | 0.3692 | **PASS** |
| **Cheng** | DeiT-Small | Patient-Isolated Held-Out Fold 1 ($N=480$) | **0.8458** | **0.8394** | **0.8403** | **0.0366** | **0.2136** | **PASS** |
| **BRISC** | ResNet-50 | Official Test ($N=1,000$, Full 4-Class) | 0.7040 | 0.6870 | 0.7095 | 0.3875 | 0.6510 | **BENCHMARK** |
| **BRISC** | ResNet-50 | Clean Test ($N=899$, De-duplicated) | 0.6963 | 0.6815 | 0.6991 | 0.3790 | 0.6505 | **PASS** |
| **BRISC** | DeiT-Small | Official Test ($N=1,000$, Full 4-Class) | 0.7880 | 0.8094 | 0.8030 | 0.0719 | 0.2864 | **BENCHMARK** |
| **BRISC** | DeiT-Small | Clean Test ($N=899$, De-duplicated) | **0.8265** | **0.8330** | **0.8344** | **0.0901** | **0.2448** | **PASS** |

### Mask-Supported Neoplasm Evaluation Subsets (Audited in `predictions/test_predictions_*_neoplasm_480.csv`)

| Dataset | Architecture | Evaluation Partition | Accuracy | Balanced Acc | Macro-F1 | ECE (10-bin) | Brier Score | Notes |
|---|---|---|---|---|---|---|---|---|
| **BRISC** | ResNet-50 | Mask-Supported Neoplasm Batch ($N=480$) | 0.6479 | 0.6510 | 0.3460 | 0.3312 | 0.6591 | 254 Gliomas, 226 Meningiomas |
| **BRISC** | ResNet-50 | Clean Neoplasm Batch ($N=397$) | 0.6247 | 0.6349 | 0.4383 | 0.3061 | 0.6595 | 83 duplicate meningiomas excluded |
| **BRISC** | DeiT-Small | Mask-Supported Neoplasm Batch ($N=480$) | 0.6875 | 0.6813 | 0.3566 | 0.0421 | 0.3938 | 254 Gliomas, 226 Meningiomas |
| **BRISC** | DeiT-Small | Clean Neoplasm Batch ($N=397$) | 0.7456 | 0.7294 | 0.3716 | 0.0718 | 0.3303 | 83 duplicate meningiomas excluded |

---

## 2. Methodology & Leakage Protection Compliance

1. **Patient-Isolated Out-of-Fold Evaluation (Cheng):**
   - Each model is trained strictly on 4 patient folds and evaluated on the held-out 5th fold.
   - Slices from the same patient are never split across train and test folds.
   - The saved prediction export reflects the held-out Fold 1 test partition ($N=480$ slices, 49 unseen patients).

2. **Dual-Benchmark Reporting (BRISC):**
   - Performance is reported both on the full official test set (1,000 images, preserved in `predictions/test_predictions_*_brisc.csv`) and the clean test set (899 images, preserved in `predictions/test_predictions_*_brisc_clean.csv`).
   - Zero duplicate leakage between the 4,000 training and 1,000 validation images.

3. **Mask Isolation:**
   - Segmentation masks were strictly excluded from the baseline classification input. Full images were fed to the baseline models as unmasked $224 \times 224 \times 3$ tensors.
