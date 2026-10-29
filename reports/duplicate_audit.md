# Duplicate and Data Leakage Audit Report

Date: 2026-10-29 (Updated 2026-10-30)  
Auditors: Multidisciplinary Research Team (Data-Quality & Leakage Auditor, Biostatistician)

---

## 1. Executive Summary & Gate Decision

| Check | Result | Interpretation | Action / Status |
|---|---|---|---|
| **Cheng Within-Dataset Exact Duplicates** | **0** | No byte-identical or identical decoded-pixel slices exist within Cheng. | **PASS** |
| **Cheng Patient Overlap Across CV Folds** | **0** | All 3,064 slices grouped strictly by Patient ID (233 distinct PIDs). | **PASS** |
| **BRISC Within-Dataset Exact Duplicates** | **159 pairs** (278 unique images) | Identical duplicate pixel redundancy in evaluated archive files. | **QUALIFIED FINDING** |
| **BRISC Train-Test Leakage** | **110 pairs** (101 test images) | 10.1% of test images share identical pixel arrays with training images in evaluated archive. | **DUAL-BENCHMARK REPORTING** |
| **Cross-Dataset Exact Overlap (Cheng vs BRISC)** | **0 pairs** | No identical decoded pixel records cross between datasets. | **PASS** |
| **Cross-Dataset Near-Duplicates (SSIM >= 0.85)** | **0 pairs** | Image hashes / SSIM confirm distinct imaging acquisitions and formatting. | **PASS** |

**Provenance & Qualification Note:**  
The published BRISC data descriptor by Fateh et al. (*Scientific Data*, 2026, doi:10.1038/s41597-026-06753-y) describes applying deduplication prior to official train/test partitioning. Because external audits and data mirrors report varying exact-hash cleaning counts, the 159 duplicate pairs (101 test slices) identified via decoded SHA-256 pixel array comparison are treated as an empirical observation specific to the downloaded archive release rather than an undisputed benchmark-wide flaw.

**Phase 2 Gate Decision: GO (Conditional on Dual-Benchmark Policy)**  
- Cheng evaluation proceeds with strict patient-grouped 5-fold cross-validation.
- BRISC evaluation reports both the **Official Test Benchmark (1,000 slices)** and the **Clean De-duplicated Test Subset (899 slices)** side-by-side.

---

## 2. Methodology

The audit applied multiple complementary levels of duplicate detection and verification:
1. **File-Level Cryptographic Hashes:** SHA-256 computed on raw input files.
2. **Decoded-Pixel Hashes:** SHA-256 computed on the contiguous 2D pixel array after consistent grayscale decoding (`np.array_equal == True`).
3. **Perceptual Hash (pHash):** 64-bit thresholded average hash for candidate indexing.
4. **Calibrated Structural Similarity (SSIM & Metrics):**
   - Structural Similarity Index (SSIM) computed using standard luminance/contrast/structure formulation.
   - Mean Absolute Difference (MAD) and Maximum Pixel Difference.
   - Pearson Correlation Coefficient between image intensity profiles.

---

## 3. BRISC Duplicate and Split Leakage Audit

### 3.1 Exact Duplicate Discovery
In the evaluated BRISC 2025 release (`brisc2025`):
- **159 exact duplicate pairs** were confirmed with identical decoded-pixel SHA-256 hashes (SSIM = 1.0000, MAD = 0.00).
- These pairs form **134 connected duplicate components** involving **278 unique sample files**.
- In several cases, identical images were cross-assigned conflicting anatomical plane annotations (e.g. `brisc2025_test_00030_gl_ax_t1` labelled axial vs `brisc2025_test_00092_gl_co_t1` labelled coronal).

### 3.2 Split Partition Leakage Breakdown
The 159 exact duplicate pairs distribute across official splits as follows:

| Duplicate Pair Partition | Pair Count | Samples Involved | Leakage Status |
|---|---:|---:|---|
| **Train–Train** | 41 | 73 | Within-training redundancy; grouped together in fold creation |
| **Train–Test** | **110** | **104 train, 101 test** | **Archive train-test duplicate overlap (test sample memorization)** |
| **Test–Test** | 8 | 14 | Within-test redundancy; redundant test evaluation |

### 3.3 Contaminated Test Samples Breakdown
The 101 test samples with exact duplicates in the training set belong to:
- **Meningioma:** 96 samples (31.4% of all test meningioma slices in official test set)
- **Pituitary:** 5 samples
- **Glioma / No-Tumour:** 0 samples
