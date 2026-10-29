# Duplicate and Data Leakage Audit Report

Date: 2026-10-29 (Asia/Kolkata)  
Auditors: Multidisciplinary Research Team (Data-Quality & Leakage Auditor, Biostatistician)

---

## 1. Executive Summary & Gate Decision

| Check | Result | Interpretation | Action / Status |
|---|---|---|---|
| **Cheng Within-Dataset Exact Duplicates** | **0** | No byte-identical or identical decoded-pixel slices exist within Cheng. | **PASS** |
| **Cheng Patient Overlap Across CV Folds** | **0** | All 3,064 slices grouped strictly by Patient ID (233 distinct PIDs). | **PASS** |
| **BRISC Within-Dataset Exact Duplicates** | **159 pairs** (278 unique images) | Substantial identical duplicate redundancy in official BRISC release. | **CRITICAL DEFECT IN BENCHMARK** |
| **BRISC Train-Test Leakage** | **110 pairs** (101 test images) | 10.1% of official test images are exact duplicates of training images. | **EXCLUSION POLICY APPLIED** |
| **Cross-Dataset Exact Overlap (Cheng vs BRISC)** | **0 pairs** | No identical decoded pixel records cross between datasets. | **PASS** |
| **Cross-Dataset Near-Duplicates (SSIM >= 0.85)** | **0 pairs** | Image hashes / SSIM confirm distinct imaging acquisitions and formatting. | **PASS** |

**Phase 2 Gate Decision: GO (Conditional on Split & Leakage Policy)**  
- Cheng evaluation will proceed with strict patient-grouped 5-fold cross-validation.
- BRISC evaluation will report both the **Official Test Benchmark (1,000 slices)** and the **Clean Uncontaminated Test Subset (899 slices)**, explicitly excluding the 101 contaminated samples from clean generalization claims.

---

## 2. Methodology

The audit applied multiple complementary levels of duplicate detection and verification:
1. **File-Level Cryptographic Hashes:** SHA-256 computed on raw input files.
2. **Decoded-Pixel Hashes:** SHA-256 computed on the contiguous 2D pixel array after consistent grayscale decoding.
3. **Perceptual Hash (pHash):** 64-bit thresholded average hash for candidate indexing.
4. **Calibrated Structural Similarity (SSIM & Metrics):**
   - Structural Similarity Index (SSIM) computed using standard luminance/contrast/structure formulation.
   - Mean Absolute Difference (MAD) and Maximum Pixel Difference.
   - Pearson Correlation Coefficient between image intensity profiles.

> [!NOTE]
> Coarse 8×8 average hash yields frequent candidate matches on brain MRI because T1-weighted cranial slices share an elliptical head silhouette against zero-intensity background. All perceptual candidates were therefore subjected to calibrated SSIM verification.

---

## 3. BRISC Duplicate and Split Leakage Audit

### 3.1 Exact Duplicate Discovery
In the official BRISC 2025 release (`brisc2025`):
- **159 exact duplicate pairs** were confirmed with identical decoded-pixel SHA-256 hashes (SSIM = 1.0000, MAD = 0.00).
- These pairs form **134 connected duplicate components** involving **278 unique sample files**.
- In several cases, identical images were cross-assigned conflicting anatomical plane annotations (e.g. `brisc2025_test_00030_gl_ax_t1` labelled axial vs `brisc2025_test_00092_gl_co_t1` labelled coronal).

### 3.2 Split Partition Leakage Breakdown
The 159 exact duplicate pairs distribute across official splits as follows:

| Duplicate Pair Partition | Pair Count | Samples Involved | Leakage Status |
|---|---:|---:|---|
| **Train–Train** | 41 | 73 | Within-training redundancy; grouped together in fold creation |
| **Train–Test** | **110** | **104 train, 101 test** | **Direct benchmark leakage (test sample memorization)** |
| **Test–Test** | 8 | 14 | Within-test redundancy; redundant test evaluation |

### 3.3 Contaminated Test Samples Breakdown
The 101 test samples with exact duplicates in the training set belong to:
- **Meningioma:** 96 samples (31.4% of all test meningioma slices!)
- **Pituitary:** 5 samples (1.7% of all test pituitary slices)
- **Glioma:** 0 samples
- **No Tumor:** 0 samples

Planes affected among leaked test samples:
- **Axial:** 63 samples
- **Coronal:** 22 samples
- **Sagittal:** 16 samples

### 3.4 Exclusion and Mitigation Policy
1. For benchmark reproducibility, the full 1,000-slice official test set is maintained in `manifests/brisc_manifest.csv`.
2. A separate column `exclusion_reason = "train_test_duplicate_leakage"` flags all 101 leaked test images.
3. For clean cross-architecture and counterfactual intervention analysis, the **Clean Test Subset (N = 899)** is evaluated separately, removing contaminated test images.
4. Among test images with usable segmentation masks (N = 860), exactly 101 are contaminated, yielding **759 clean mask-supported test images** (Glioma: 254, Meningioma: 210, Pituitary: 295; Axial: 283, Coronal: 235, Sagittal: 241).

---

## 4. Cheng Within-Dataset Patient Grouping Audit

- **Sample count:** 3,064 slices from 233 unique patients across 3 classes (glioma: 89 patients / 1,426 slices; meningioma: 82 patients / 708 slices; pituitary: 62 patients / 930 slices).
- **Exact duplicates:** 0 pairs.
- **Near-duplicate review:** Slices with SSIM >= 0.75 represent adjacent slices from the same MRI volume.
- **Split integrity:** 5-fold cross-validation generated with `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`.
- **Patient overlap check:** **PASS — 0 patients cross between folds**. Every patient's slices are quarantined strictly to a single fold.

---

## 5. Cross-Dataset Overlap Audit (Cheng vs BRISC)

- **Exact pixel duplicates:** **0**.
- **Near-duplicate screening:** Tested candidate pairs between Cheng and BRISC across low-distance perceptual hash buckets.
- **Empirical SSIM distribution:**
  - Range: 0.28 to 0.59 (Mean: 0.42).
  - No cross-dataset pair demonstrated SSIM >= 0.70.
- **Conclusion:** While BRISC documentation cites Figshare/Cheng as an organizational inspiration, the released images differ in acquisition, preprocessing, contrast adjustments, and compression. No exact slice cross-contamination was found.

---

## 6. Manifest File Locations & Checksums

- Detailed duplicate pairs: `manifests/duplicate_pairs.csv`
- Connected duplicate groups: `manifests/duplicate_groups.csv`
- Cheng splits manifest: `manifests/cheng_splits.csv`
- BRISC splits manifest: `manifests/brisc_splits.csv`
