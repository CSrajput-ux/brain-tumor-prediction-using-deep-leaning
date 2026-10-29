# Dataset Split and Partition Integrity Report

Date: 2026-10-29 (Asia/Kolkata)  
Protocol: Patient-grouped CV (Cheng) and Leakage-controlled Train/Val/Test (BRISC)

---

## 1. Cheng Brain Tumour Dataset (5-Fold Patient-Grouped CV)

- Total slices: 3,064  
- Distinct patients: 233  
- Splitting algorithm: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`  
- Grouping variable: `patient_id` (observed `PID` field in MATLAB 7.3 metadata)  
- **Patient Overlap Verification:** **PASS (0 patients cross folds)**  

| Fold | Unique Patients | Total Slices | Glioma | Meningioma | Pituitary |
|---|---:|---:|---:|---:|---:|
| fold_1 | 47 | 645 | 285 | 156 | 204 |
| fold_2 | 47 | 536 | 210 | 136 | 190 |
| fold_3 | 46 | 602 | 269 | 154 | 179 |
| fold_4 | 46 | 685 | 338 | 132 | 215 |
| fold_5 | 47 | 596 | 324 | 130 | 142 |

---

## 2. BRISC Dataset Partitioning & Leakage Screening

- Published benchmark counts: 5,000 train / 1,000 test (4 classes: glioma, meningioma, pituitary, no_tumor)  
- Validation split: Deterministically drawn from train set using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` on duplicate groups  
- **Train–Val Duplicate Leakage:** **PASS (0 duplicate leakage)**  
- **Official Test Set Contamination:** **101 test slices** are exact byte duplicates of training slices  
- **Clean Test Subset:** **899 slices** (free from train leakage)  
- **Mask-Supported Clean Test Subset:** **759 slices** (eligible for counterfactual intervention audit)  

| Partition | Slices | Glioma | Meningioma | Pituitary | No Tumor | Axial | Coronal | Sagittal | Leakage Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Official train | 4000 | 918 | 1063 | 1165 | 854 | 1275 | 1344 | 1381 | Clean (0 duplicate leakage) |
| Official val | 1000 | 229 | 266 | 292 | 213 | 320 | 332 | 348 | Clean (0 duplicate leakage) |
| Official test | 1000 | 254 | 306 | 300 | 140 | 398 | 305 | 297 | 101 leaked test slices |
| **Clean Test Subset** | **899** | 254 | 210 | 295 | 140 | 335 | 283 | 281 | **Clean (Leaked excluded)** |

---

## 3. Compliance and Gate Verification

1. **No random slice-level splitting:** Both datasets use structured grouping.
2. **Cheng out-of-fold evaluation:** Every slice evaluated in out-of-fold inference will be predicted by a model that never saw any slice from that patient.
3. **Dual reporting for BRISC:** Performance will be reported both on the full official 1,000 test set and the clean 899 test set, quantifying the exact performance inflation caused by leaked duplicates in the benchmark.
