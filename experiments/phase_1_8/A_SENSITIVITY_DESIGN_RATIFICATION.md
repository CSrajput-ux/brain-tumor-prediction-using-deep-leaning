# A — Sensitivity Design Ratification

**Phase:** 1.8 — Final Protocol Ratification  
**Date:** 2026-10-17  
**Auditor:** Independent Medical Imaging & ML Evaluation Specialist  
**Evaluated Manifests:**  
- `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_80.csv` (Scenario S1)
- `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_75.csv` (Scenario S2)
- `experiments/phase_1_7/candidate_grouped_manifests/split_regrouped_ssim_0_60.csv` (Scenario S3b — Stress Test)
- Authoritative baseline: `prepared_full_run/patient_splits.csv` (Scenario S0)

---

## 1. Formal Ratification of the Primary Sensitivity Range

We ratify the evaluation design under **Protocol C (Sensitivity Analysis across Grouping Assumptions)** with:
1. **Primary Evaluation Tier:**
   - **Scenario S0 (Baseline):** Authoritative patient-grouped 5-fold cross-validation (`patient_splits.csv`).
   - **Scenario S1 (Conservative, SSIM ≥ 0.80):** High-similarity regrouped 5-fold split (`split_regrouped_ssim_0_80.csv`).
   - **Scenario S2 (Intermediate Conservative, SSIM ≥ 0.75):** Extended-similarity regrouped 5-fold split (`split_regrouped_ssim_0_75.csv`).
2. **Exploratory Percolation Boundary (Stress Test Only):**
   - **Scenario S3b (SSIM ≥ 0.60):** Retained strictly as an exploratory boundary stress test (`split_regrouped_ssim_0_60.csv`). It is **excluded from primary hypothesis testing** due to the 807-slice giant component percolation phenomenon documented in Phase 1.7.

---

## 2. Independent Audit of Manifest Integrity

Every candidate regrouped manifest was independently re-evaluated against the 3,064 authoritative slices and 233 source patient IDs:

### Audit Verification Table

| Manifest | Total Samples | Unique Samples | Patient Crossings | Component Crossings | Max Group Size | Min Class/Fold | Max Fold Size Disparity |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Baseline (S0)** | 3,064 | 3,064 | **0** | N/A | 38 | 137 | 1 slice (613 vs 612) |
| **SSIM ≥ 0.80 (S1)** | 3,064 | 3,064 | **0** | **0** | 38 | 141 | 2 slices (614 vs 612) |
| **SSIM ≥ 0.75 (S2)** | 3,064 | 3,064 | **0** | **0** | 155 | 141 | 2 slices (614 vs 612) |
| **SSIM ≥ 0.60 (S3b)** | 3,064 | 3,064 | **0** | **0** | 807 | 137 | **474 slices** (992 vs 518) |

### Fold-Level Breakdown for Primary Manifests

#### Scenario S1: SSIM ≥ 0.80
- **Fold 1:** 612 slices (45 patients) — Glioma: 285, Meningioma: 142, Pituitary: 185
- **Fold 2:** 614 slices (47 patients) — Glioma: 286, Meningioma: 141, Pituitary: 187
- **Fold 3:** 613 slices (46 patients) — Glioma: 285, Meningioma: 142, Pituitary: 186
- **Fold 4:** 612 slices (47 patients) — Glioma: 284, Meningioma: 141, Pituitary: 187
- **Fold 5:** 613 slices (48 patients) — Glioma: 286, Meningioma: 142, Pituitary: 185

#### Scenario S2: SSIM ≥ 0.75
- **Fold 1:** 613 slices (48 patients) — Glioma: 286, Meningioma: 141, Pituitary: 186
- **Fold 2:** 612 slices (46 patients) — Glioma: 285, Meningioma: 142, Pituitary: 185
- **Fold 3:** 614 slices (46 patients) — Glioma: 286, Meningioma: 141, Pituitary: 187
- **Fold 4:** 612 slices (46 patients) — Glioma: 285, Meningioma: 142, Pituitary: 185
- **Fold 5:** 613 slices (47 patients) — Glioma: 284, Meningioma: 142, Pituitary: 187

---

## 3. Scope and Evidentiary Boundaries of the Scenario Gate

We conducted an independent audit of `scripts/verify_scenario_gates.py`. We formally ratify the following boundary constraints:

1. **Exact Pair and Threshold Scope:**
   - The gate verification assertion of *"zero residual cross-fold candidate leakage"* applies **strictly and exclusively** to the 236 candidate pairs in `reports/duplicate_investigation/duplicate_pair_review.csv` possessing an `export_ssim` at or above the designated scenario threshold ($\tau$).
   - It does **not** assert zero leakage for unexamined pairs in the dataset with pHash Hamming distance $> 4/64$ (which were screened out during initial duplicate triage).
2. **Non-Identity of Similarity Components:**
   - The grouping procedure groups samples purely to enforce evaluation partition independence under a conservative leakage hypothesis.
   - The report and manifests **do not claim** that similarity components represent true biological or clinical patients. Merging patients into an indivisible evaluation group is a safety control against potential correlation, not a re-identification of patients.
3. **Immutability of Authoritative Baseline:**
   - Authoritative `prepared_full_run/patient_splits.csv` (SHA-256: `c45e0eea02f00f7c3d80f20d3f4764f758d8471300a81ff4d25ea31c2387d622`) remains completely untouched.
   - All scenario regroupings exist strictly as independent, read-only manifest files under `experiments/phase_1_7/candidate_grouped_manifests/`.
