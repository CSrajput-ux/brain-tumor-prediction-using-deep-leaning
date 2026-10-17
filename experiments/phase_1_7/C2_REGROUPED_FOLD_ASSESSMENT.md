# C2 — Regrouped Fold Feasibility and Balance Assessment

**Phase:** 1.7 — Sensitivity Analysis and Pre-Registration  
**Date:** 2026-10-17  
**Status:** Complete — Thresholds 0.80, 0.75, and 0.70 Fully Viable; Threshold 0.60 Severely Distorted  
**Splits Evaluated:** 5-fold cross-validation across 4 grouping thresholds  

---

## 1. Executive Summary

Condition **C2** requires evaluating whether the combined evaluation groups at each SSIM threshold can be assigned as indivisible units to 5 evaluation folds while satisfying six strict scientific criteria:
1. **Zero Component Crossing:** No similarity component crosses evaluation folds.
2. **Zero Patient ID Crossing:** No source patient ID crosses evaluation folds.
3. **Complete Accounting:** All 3,064 eligible samples are assigned to exactly one fold.
4. **Class Representation:** Every class has $\ge 50$ samples in every fold, if feasible.
5. **Transparency:** Fold-level patient, slice, and class distributions are fully reported.
6. **Imbalance Quantification:** Size disparity and class skew are documented.

### Feasibility Verdict
- **SSIM ≥ 0.80:** **PASSED — EXCELLENT BALANCE.** Fold sizes [612, 614, 613, 612, 613]; max disparity = 2 slices; all classes $\ge 141$ slices/fold.
- **SSIM ≥ 0.75:** **PASSED — EXCELLENT BALANCE.** Fold sizes [613, 612, 614, 612, 613]; max disparity = 2 slices; all classes $\ge 141$ slices/fold.
- **SSIM ≥ 0.70:** **PASSED — EXCELLENT BALANCE.** Fold sizes [612, 613, 613, 613, 613]; max disparity = 1 slice; all classes $\ge 141$ slices/fold.
- **SSIM ≥ 0.60:** **MATHEMATICALLY ASSIGNABLE BUT SCIENTIFICALLY COMPROMISED.** Folds 1–4 contain 518 slices each; Fold 5 contains **992 slices** (91.5% larger). Max disparity is **474 slices**. Fold 5 absorbs 45.5% of all glioma in the dataset.

> **Project Acceptance Constraint Note:** The project threshold of $\ge 50$ slices per class per fold is an empirical operational acceptance gate, NOT proof of formal statistical power or asymptotic sample sufficiency. Small sample counts in high-dimensional medical imaging can still exhibit elevated variance.

---

## 2. Fold Assignment Methodology

To avoid data leakage, bias, and arbitrary manual placement, fold assignments were generated using a deterministic, documented algorithm:

1. **Unit of Assignment:** Indivisible combined evaluation groups (Concept 3 from C1).
2. **Stratification Algorithm:** `sklearn.model_selection.StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`
3. **Deterministic Pre-Ordering:** All samples ordered deterministically by `sample_id` before partitioning.
4. **Constraint Enforcement:**
   - Group boundaries are absolute: no component or patient is split.
   - No samples are filtered, discarded, or synthesized.

---

## 3. Quantitative Fold Breakdown by Threshold

### Baseline Reference (Original Patient-Grouped Split, $\tau = \text{None}$)
- Folds 1–5: [613, 613, 613, 613, 612] slices.
- 233 clinical patient IDs grouped without similarity constraints.
- Pretraining gate passed all checks except the 236 unresolved candidate pairs.

---

### Scenario S1: SSIM ≥ 0.80 Regrouped Split
*Manifest: `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_80.csv`*

| Fold | Patients | Total Slices | Glioma | Meningioma | Pituitary | Class Imbalance Ratio (G:M:P) |
|---|---:|---:|---:|---:|---:|---|
| **Fold 1** | 45 | 612 | 285 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Fold 2** | 47 | 614 | 286 | 141 | 187 | 2.03 : 1.00 : 1.33 |
| **Fold 3** | 46 | 613 | 285 | 142 | 186 | 2.01 : 1.00 : 1.31 |
| **Fold 4** | 47 | 612 | 284 | 141 | 187 | 2.01 : 1.00 : 1.33 |
| **Fold 5** | 48 | 613 | 286 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Total** | **233** | **3,064** | **1,426** | **708** | **930** | **2.01 : 1.00 : 1.31** |

- Patient crossing violations: **0**
- Component crossing violations: **0**
- Minimum class count in any fold: **141** (meningioma in Folds 2 and 4, well above 50)
- Maximum fold size disparity: **2 slices** (614 vs 612)

---

### Scenario S2: SSIM ≥ 0.75 Regrouped Split
*Manifest: `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_75.csv`*

| Fold | Patients | Total Slices | Glioma | Meningioma | Pituitary | Class Imbalance Ratio (G:M:P) |
|---|---:|---:|---:|---:|---:|---|
| **Fold 1** | 48 | 613 | 286 | 141 | 186 | 2.03 : 1.00 : 1.32 |
| **Fold 2** | 46 | 612 | 285 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Fold 3** | 46 | 614 | 286 | 141 | 187 | 2.03 : 1.00 : 1.33 |
| **Fold 4** | 46 | 612 | 285 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Fold 5** | 47 | 613 | 284 | 142 | 187 | 2.00 : 1.00 : 1.32 |
| **Total** | **233** | **3,064** | **1,426** | **708** | **930** | **2.01 : 1.00 : 1.31** |

- Patient crossing violations: **0**
- Component crossing violations: **0**
- Minimum class count in any fold: **141** (meningioma, well above 50)
- Maximum fold size disparity: **2 slices** (614 vs 612)
- Note: Accommodates Group 0 (155 slices, 8 patients, all glioma) placed cleanly into Fold 1 with zero spillover.

---

### Scenario S3a: SSIM ≥ 0.70 Regrouped Split
*Manifest: `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_70.csv`*

| Fold | Patients | Total Slices | Glioma | Meningioma | Pituitary | Class Imbalance Ratio (G:M:P) |
|---|---:|---:|---:|---:|---:|---|
| **Fold 1** | 47 | 612 | 285 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Fold 2** | 46 | 613 | 285 | 141 | 187 | 2.02 : 1.00 : 1.33 |
| **Fold 3** | 48 | 613 | 284 | 142 | 187 | 2.00 : 1.00 : 1.32 |
| **Fold 4** | 46 | 613 | 286 | 142 | 185 | 2.01 : 1.00 : 1.30 |
| **Fold 5** | 46 | 613 | 286 | 141 | 186 | 2.03 : 1.00 : 1.32 |
| **Total** | **233** | **3,064** | **1,426** | **708** | **930** | **2.01 : 1.00 : 1.31** |

- Patient crossing violations: **0**
- Component crossing violations: **0**
- Minimum class count in any fold: **141** (meningioma, well above 50)
- Maximum fold size disparity: **1 slice** (613 vs 612)
- Note: Accommodates Group 0 (293 slices, 17 patients, mixing glioma and meningioma) without violating class minimums.

---

### Scenario S3b: SSIM ≥ 0.60 Regrouped Split
*Manifest: `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_60.csv`*

| Fold | Patients | Total Slices | Glioma | Meningioma | Pituitary | Class Imbalance Ratio (G:M:P) |
|---|---:|---:|---:|---:|---:|---|
| **Fold 1** | 43 | 518 | 195 | 137 | 186 | 1.42 : 1.00 : 1.36 |
| **Fold 2** | 41 | 518 | 194 | 138 | 186 | 1.41 : 1.00 : 1.35 |
| **Fold 3** | 43 | 518 | 194 | 137 | 187 | 1.42 : 1.00 : 1.36 |
| **Fold 4** | 41 | 518 | 194 | 138 | 186 | 1.41 : 1.00 : 1.35 |
| **Fold 5** | **65** | **992** | **649** | **158** | **185** | **4.11 : 1.00 : 1.17** |
| **Total** | **233** | **3,064** | **1,426** | **708** | **930** | **2.01 : 1.00 : 1.31** |

- Patient crossing violations: **0**
- Component crossing violations: **0**
- Minimum class count in any fold: **137** (meningioma in Folds 1 and 3, nominally $\ge 50$)
- Maximum fold size disparity: **474 slices** (Fold 5 has 992 vs 518 in Folds 1–4; a 91.5% size jump!)
- **Glioma Concentration:** Fold 5 contains $649 / 1,426 = 45.5\%$ of all glioma samples in the dataset.

---

## 4. In-Depth Evaluation of the Threshold 0.60 Conflict

At SSIM 0.60, the algorithm satisfies the formal check $\min(\text{class count}) \ge 50$, but fails fundamental evaluation symmetry:

1. **Asymmetric Training Sets:**
   - When Fold 5 is the test set ($N_{\text{test}} = 992$), the training set has $N_{\text{train}} = 2,072$ slices, containing only 777 glioma slices (37.5% glioma).
   - When Fold 1 is the test set ($N_{\text{test}} = 518$), the training set has $N_{\text{train}} = 2,546$ slices, containing 1,231 glioma slices (48.4% glioma).
2. **Evaluation Weighting Skew:**
   - Test performance on Fold 5 contributes nearly double the sample-level evaluations compared to any other fold.
3. **Percolation Distortion:**
   - Because the 807-slice component combines patients who share only generic anatomical background, this grouping imposes severe artificial constraints on the machine learning evaluation that have no clinical or imaging justification.

---

## 5. Assessment of Alternative Evaluation Designs

Given the percolation observed at SSIM 0.60, we systematically assess alternative remedies:

| Design Option | Mechanism | Feasibility | Scientific Trade-off |
|---|---|---|---|
| **Option 1: 5-Fold with SSIM 0.60** | Accept Fold 5 size jump (992 slices) | Technically feasible | High risk of training asymmetry and variance skew |
| **Option 2: 3-Fold or 2-Fold Split** | Merge folds to absorb 807-slice block | Feasible | Loses training data fraction (66% or 50% train vs 80%), reducing statistical efficiency |
| **Option 3: Exclusion Scenario (S4)** | Exclude candidate slices/patients | Feasible | Drops 291 slices (9.5% of dataset), alters dataset composition |
| **Option 4: Bounded Protocol C (Recommended)** | Restrict primary sensitivity range to $\tau \in [0.75, 0.80]$; treat $\tau = 0.60$ as exploratory stress test | **Optimal** | Preserves 5-fold balance across primary scenarios while transparently demonstrating sensitivity bounds |

### Recommendation
Adopt **Option 4**:
- Pre-register **Scenario S0 (Baseline)**, **Scenario S1 ($\tau = 0.80$)**, and **Scenario S2 ($\tau = 0.75$)** as the primary sensitivity family.
- Run **Scenario S3 ($\tau = 0.70$)** as a secondary confirmation.
- Retain **$\tau = 0.60$** strictly as a recorded boundary stress-test that demonstrates what happens when grouping is pushed past the physical percolation limit.
- Under no circumstances split connected components or discard samples silently.
