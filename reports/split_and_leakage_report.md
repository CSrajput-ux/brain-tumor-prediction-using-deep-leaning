# Split Policy and Benchmark Leakage Audit Report

**Date:** 2026-10-29 (Synchronized: 2026-11-01)

---

## 1. Cheng Patient-Isolated Cross-Validation Policy

To prevent patient-level memorization leakage (Yagis et al., 2021), 5-fold cross-validation was implemented using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped strictly by `patient_id`.

- **Cohort Hierarchy:**
  - Total Archive: 3,064 T1-weighted contrast-enhanced slices across 233 unique patients.
  - Zero Patient Overlap: Pairwise intersection checks confirmed zero patient overlap across any fold pair ($\text{Intersection} = \emptyset$).
- **Fold Composition (from `manifests/cheng_splits.csv`):**
  - Fold 1: 645 slices (47 patients; 156 meningioma, 285 glioma, 204 pituitary)
  - Fold 2: 536 slices (47 patients; 136 meningioma, 210 glioma, 190 pituitary)
  - Fold 3: 602 slices (46 patients; 154 meningioma, 269 glioma, 179 pituitary)
  - Fold 4: 685 slices (46 patients; 132 meningioma, 338 glioma, 215 pituitary)
  - Fold 5: 596 slices (47 patients; 130 meningioma, 324 glioma, 142 pituitary)
  - Sum: $645 + 536 + 602 + 685 + 596 = 3,064$ slices; $47 + 47 + 46 + 46 + 47 = 233$ patients.
- **Evaluated Baseline Prediction Subset:**
  - During fixed-batch baseline inference, 30 validation batches of 16 slices were evaluated, yielding an evaluated prediction subset of **480 slices across 41 unseen patients** (155 meningioma, 232 glioma, 93 pituitary) as recorded in `predictions/oof_predictions_resnet50_cheng.csv`.
- **Counterfactual Audit Cohort:**
  - From the evaluated held-out test predictions, an exact class-balanced cohort of **45 slices across 10 patients** (15 meningioma, 15 glioma, 15 pituitary) was audited across all 5 spatial perturbation regions.

---

## 2. Discovery of Duplicate Leakage in the BRISC Benchmark

An exhaustive perceptual hash (pHash, dHash, aHash) audit across all 6,000 BRISC slices revealed substantial benchmark contamination:

- **159 exact duplicate pairs** spanning 278 unique images.
- **110 duplicate pairs crossed the official train-test split boundary**.
- Exactly **101 test slices (10.1% of the official test set)** are byte-identical copies of training images.
- **Class Skew of Leakage:** 96 of the 101 leaked test slices belong to the meningioma class.
- **Resolution & Dual Benchmark Policy:**
  1. **Contaminated Official Test Set ($N=1,000$):** Retained solely for diagnostic comparison with previously published literature.
  2. **BRISC Train-Test Cross-Split De-duplicated Test Set ($N=899$):** Isolates all 101 cross-split leaked test slices (leaving 759 mask-supported clean slices) to establish true out-of-sample generalization across the train-test split. *(Note: Latent intra-test duplicate pairs cannot be exhaustively ruled out due to the lack of patient tracking identifiers in the public BRISC release).*
  3. **Clean Training/Validation Split:** 1,001 validation slices and 3,999 training slices extracted from the training pool with **zero train-validation duplicate leakage**.
