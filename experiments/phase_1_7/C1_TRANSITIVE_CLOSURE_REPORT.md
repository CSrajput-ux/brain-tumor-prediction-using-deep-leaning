# C1 — Transitive Closure and Similarity Graph Analysis

**Phase:** 1.7 — Sensitivity Analysis and Pre-Registration  
**Date:** 2026-10-17  
**Dataset:** Cheng Brain Tumor MRI Dataset (3,064 axial slices, 233 patient IDs)  
**Candidate Pair Evidence:** `reports/duplicate_investigation/duplicate_pair_review.csv` (236 cross-patient/cross-fold pairs)  
**Status:** Evaluation Audit Complete — Critical Percolation Transition Identified  

---

## 1. Executive Summary

Condition **C1** requires computing connected components across the 236 candidate pairs at four pre-registered SSIM thresholds: **0.80, 0.75, 0.70, and 0.60**.

Key findings:
1. **SSIM ≥ 0.80 (Conservative, High Similarity):** Only 2 candidate pairs form edges, connecting 4 samples across 4 distinct patient IDs into 2 pairwise components of size 2. When combined with patient integrity constraints, the maximum combined group size is 38 slices, leaving 5-fold cross-validation balance essentially undisturbed.
2. **SSIM ≥ 0.75 (Moderate-High Similarity):** 27 candidate pairs form edges, creating 12 non-singleton similarity components affecting 37 samples across 23 patient IDs. When combined with patient constraints, the largest group contains 155 slices (8 patients, all glioma).
3. **SSIM ≥ 0.70 (Moderate Similarity):** 61 candidate pairs form edges, creating 21 non-singleton similarity components affecting 76 samples across 36 patient IDs. The largest combined evaluation group expands to 293 slices (17 patients), and critically, begins chaining across distinct tumor classes (268 glioma + 25 meningioma).
4. **SSIM ≥ 0.60 (Weak Similarity — Percolation Transition):** 119 candidate pairs form edges, producing 44 non-singleton similarity components affecting 148 samples across 75 patient IDs. In the combined evaluation graph, transitive percolation produces a **giant component of 807 slices** (53 patients, 649 glioma, 158 meningioma, 0 pituitary). This single group accounts for **26.3% of the entire dataset** and **45.5% of all glioma samples**, demonstrating conclusively that transitive closure at SSIM 0.60 captures broad normal brain anatomical resemblance (ventricular morphology, axial skull contours) rather than true duplicate acquisitions or shared patient identity.

---

## 2. Graph Construction and Inclusion Semantics

### Edge Creation Rule
For any two samples $s_a, s_b \in V$ ($|V| = 3,064$ slices), an undirected edge $e = (s_a, s_b)$ is created in the similarity graph $G_{\text{sim}}(\tau)$ if and only if:
$$(s_a, s_b) \in \mathcal{P}_{236} \quad \text{and} \quad \text{SSIM}(s_a, s_b) \ge \tau$$
where $\mathcal{P}_{236}$ is the authoritative set of 236 cross-patient / cross-fold candidate pairs identified in Phase 1.5/1.6, and $\tau \in \{0.80, 0.75, 0.70, 0.60\}$. The threshold comparison is strictly inclusive ($\ge$).

### Node Identifiers and Attributes
Every sample $s$ is identified by its stable, immutable `sample_id` (SHA-256 derived hex string). Each node retains its authoritative metadata attributes:
- `patient_id`: source patient pseudonym (e.g., `100360`, `MR024780B`)
- `class`: tumor class (`glioma`, `meningioma`, `pituitary`)
- `original_fold`: baseline evaluation fold (`fold_1` to `fold_5`)

---

## 3. Quantitative Results by Threshold

The table below summarizes graph connectivity and impact across all four thresholds:

| Metric | SSIM ≥ 0.80 | SSIM ≥ 0.75 | SSIM ≥ 0.70 | SSIM ≥ 0.60 |
|---|---:|---:|---:|---:|
| **Candidate Edges** | **2** | **27** | **61** | **119** |
| **Total Similarity Components** | **3,062** | **3,039** | **3,009** | **2,960** |
| Singleton Samples (Size = 1) | 3,060 | 3,027 | 2,988 | 2,916 |
| Non-Singleton Similarity Components | 2 | 12 | 21 | 44 |
| Samples in Non-Singleton Components | 4 | 37 | 76 | 148 |
| Components with Multiple Patient IDs | 2 | 12 | 21 | 44 |
| Components Spanning Multiple Original Folds | 2 | 12 | 21 | 44 |
| Distinct Patient IDs Affected | 4 | 23 | 36 | 75 |
| Max Similarity Component Size | 2 | 6 | 9 | 11 |
| **Combined Evaluation Groups** | **231** | **217** | **204** | **166** |
| Combined Groups with >1 Patient ID | 2 | 7 | 7 | 8 |
| Combined Groups Spanning >1 Original Fold | 2 | 7 | 7 | 8 |
| Patients in Multi-PID Combined Groups | 4 | 23 | 36 | 75 |
| Total Slices in Multi-PID Combined Groups | 63 | 398 | 591 | 1,156 |
| **Max Combined Group Size** | **38** | **155** | **293** | **807** |

---

## 4. Component Size Distributions

### Candidate Similarity Components (Image Evidence Only)
- **SSIM ≥ 0.80:**
  - Size 1: 3,060 components (3,060 samples)
  - Size 2: 2 components (4 samples)
- **SSIM ≥ 0.75:**
  - Size 1: 3,027 components (3,027 samples)
  - Size 2: 5 components (10 samples)
  - Size 3: 4 components (12 samples)
  - Size 4: 1 component (4 samples)
  - Size 5: 1 component (5 samples)
  - Size 6: 1 component (6 samples)
- **SSIM ≥ 0.70:**
  - Size 1: 2,988 components (2,988 samples)
  - Size 2: 11 components (22 samples)
  - Size 3: 3 components (9 samples)
  - Size 4: 1 component (4 samples)
  - Size 5: 2 components (10 samples)
  - Size 7: 2 components (14 samples)
  - Size 8: 1 component (8 samples)
  - Size 9: 1 component (9 samples)
- **SSIM ≥ 0.60:**
  - Size 1: 2,916 components (2,916 samples)
  - Size 2: 27 components (54 samples)
  - Size 3: 6 components (18 samples)
  - Size 4: 2 components (8 samples)
  - Size 5: 2 components (10 samples)
  - Size 6: 1 component (6 samples)
  - Size 7: 2 components (14 samples)
  - Size 8: 1 component (8 samples)
  - Size 9: 1 component (9 samples)
  - Size 10: 1 component (10 samples)
  - Size 11: 1 component (11 samples)

---

## 5. Three Distinct Grouping Concepts

It is scientifically vital to distinguish three fundamentally different grouping concepts:

```
[Concept 1: Patient Groups (PIDs)]        [Concept 2: Similarity Components]
   233 clinical patient IDs                    Connected components of image
   All slices per PID indivisible              SSIM >= tau graph (2 to 44 groups)
                 \                                     /
                  \                                   /
                   v                                 v
               [Concept 3: Combined Evaluation Groups]
                  Minimal indivisible units satisfying
                  BOTH PID-integrity and similarity-integrity
                  (231, 217, 204, or 166 groups)
```

1. **Original Patient Groups (Source PIDs):**
   - 233 clinical patient IDs provided in the dataset metadata.
   - Slices per patient range from 1 to 38 (median ~13).
   - This was the grouping basis used in the original 5-fold split (`prepared_full_run/patient_splits.csv`).
2. **Candidate Similarity Components (Image Evidence):**
   - Connected components formed purely by candidate pair edges with $\text{SSIM} \ge \tau$.
   - **Crucial Boundary:** These are *candidate similarity clusters*, NOT confirmed biological identities or verified duplicate acquisitions. Transitive chains (A similar to B, B similar to C) do NOT imply A is identical to C.
3. **Combined Evaluation Groups (Indivisible Split Units):**
   - The transitive union of Concept 1 and Concept 2.
   - If Patient 1 has slice $s_a$ and Patient 2 has slice $s_b$, and $(s_a, s_b)$ is in a similarity component, then *all* slices of Patient 1 and *all* slices of Patient 2 must be co-assigned to the same evaluation fold to prevent cross-fold leakage under that similarity hypothesis.
   - Slices affected expand dramatically from the candidate slices alone:
     - At $\tau = 0.80$: 4 candidate slices expand to 63 total patient slices (4 patients).
     - At $\tau = 0.75$: 37 candidate slices expand to 398 total patient slices (23 patients).
     - At $\tau = 0.70$: 76 candidate slices expand to 591 total patient slices (36 patients).
     - At $\tau = 0.60$: 148 candidate slices expand to 1,156 total patient slices (75 patients).

---

## 6. Class Composition and Cross-Class Chaining

A critical test of transitive closure validity is whether similarity components preserve tumor pathology:

### SSIM ≥ 0.80
- Both similarity components are strictly **monoclass** (both pairs are within `glioma`).
- No cross-class edges exist at $\tau \ge 0.80$.

### SSIM ≥ 0.75
- All 12 non-singleton similarity components are **monoclass**:
  - 8 components are purely `glioma`
  - 4 components are purely `meningioma`
- In the combined evaluation groups, Group 0 (155 slices) is 100% `glioma`, and Group 1 (54 slices) is 100% `meningioma`. No cross-class mixing occurs.

### SSIM ≥ 0.70
- Cross-class edges begin to appear due to generic slice resemblance:
  - Combined Group 0 (293 slices, 17 patients) mixes **268 glioma** and **25 meningioma** slices.
  - Combined Group 1 (120 slices, 7 patients) mixes **75 meningioma** and **45 glioma** slices.
  - Combined Group 2 (46 slices, 3 patients) mixes **25 meningioma** and **21 glioma** slices.

### SSIM ≥ 0.60 (Percolation Transition)
- Severe cross-class chaining occurs:
  - Combined Group 0 (807 slices, 53 patients) joins **649 glioma** and **158 meningioma** slices.
  - Combined Group 1 (146 slices, 10 patients) joins **87 meningioma** and **59 glioma** slices.
  - Combined Group 4 (36 slices, 2 patients) joins **23 glioma** and **13 meningioma** slices.

> **Diagnostic Insight:** Because a single patient cannot simultaneously have confirmed histopathological glioma and meningioma across independent clinical admissions without explicit multi-neoplasm documentation, the chaining of glioma and meningioma patients into a single 807-slice component at SSIM 0.60 is **definitive proof of false-positive transitive percolation through healthy brain parenchyma**, not shared patient identity.

---

## 7. The Giant Component Phenomenon at SSIM 0.60

In random graph theory and network percolation, when edge density exceeds a critical threshold, disconnected clusters suddenly coalesce into a **giant connected component**.

At $\tau = 0.60$:
- Edge count doubles from 61 to 119.
- 53 distinct patients coalesce into a single component of **807 slices**.
- This giant component encompasses **26.3% of the entire dataset** ($807 / 3,064$) and **45.5% of all glioma slices** ($649 / 1,426$).
- The component spans all 5 original evaluation folds.

### Scientific Implications:
1. **Percolation Artifact:** SSIM values around 0.60 in brain MRI reflect standard axial cross-sections through the lateral ventricles, basal ganglia, and skull vault. Slices look "60% similar" because they are human brains imaged in the axial plane, not because they are duplicate acquisitions.
2. **Evaluation Infeasibility:** Placing an 807-slice indivisible unit into any 5-fold cross-validation scheme guarantees severe fold size and class distortion (detailed in C2 report).
3. **Threshold Selection Constraint:** SSIM 0.60 must **not** be used as a grouping criterion for primary evaluation. It serves only as an extreme sensitivity boundary demonstrating percolation breakdown.

---

## 8. Artifact and Integrity Preservations

- Authoritative split manifest `prepared_full_run/patient_splits.csv` was **not modified**.
- Authoritative metadata `prepared_full_run/metadata.csv` was **not modified**.
- No patient IDs were merged, altered, or overwritten in any authoritative file.
- All transitive closure outputs are stored in `experiments/phase_1_7/component_summary_by_threshold.csv` and `experiments/phase_1_7/component_membership.csv`.
