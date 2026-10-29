# Split Policy and Benchmark Leakage Audit Report

**Date:** 2026-10-29  

---

## 1. Cheng Patient-Isolated Cross-Validation Policy

To prevent patient-level memorization leakage (Yagis et al., 2021), 5-fold cross-validation was implemented using `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped by `patient_id`.

- **Fold Composition:**
  - Fold 1: 645 slices (49 patients; 141 meningioma, 307 glioma, 197 pituitary)
  - Fold 2: 597 slices (45 patients; 141 meningioma, 273 glioma, 183 pituitary)
  - Fold 3: 618 slices (47 patients; 144 meningioma, 287 glioma, 187 pituitary)
  - Fold 4: 613 slices (46 patients; 142 meningioma, 287 glioma, 184 pituitary)
  - Fold 5: 591 slices (46 patients; 140 meningioma, 272 glioma, 179 pituitary)
- **Leakage Verification:** Pairwise intersection check confirmed **zero patient overlap** across folds ($\text{Intersection} = \emptyset$).

---

## 2. Discovery of Duplicate Leakage in the BRISC Benchmark

An exhaustive perceptual hash (pHash, dHash, aHash) audit across all 6,000 BRISC slices revealed substantial benchmark contamination:

- **159 exact duplicate pairs** spanning 278 unique images.
- **110 duplicate pairs crossed the official train-test split boundary**.
- Exactly **101 test slices (10.1% of the official test set)** are byte-identical copies of training images.
- **Class Skew of Leakage:** 96 of the 101 leaked test slices belong to the meningioma class.
- **Resolution & Dual Benchmark Policy:**
  1. **Contaminated Official Test Set ($N=1,000$):** Retained solely for diagnostic comparison with previously published literature.
  2. **BRISC Clean Test Set ($N=899$):** Isolates all 101 leaked test slices (759 mask-supported clean slices) to establish true out-of-sample generalization.
  3. **Clean Training/Validation Split:** 1,001 validation slices and 3,999 training slices extracted from the training pool with **zero train-validation duplicate leakage**.

